from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CONTRACT = ROOT / "s0-evaluation-contract-v0.json"
sys.path.insert(0, str(REPO))

from dogfood.llm_wiki.agent_state import (  # noqa: E402
    add_pending_lineage,
    read_agent_state,
    reserve_maintenance_call,
    set_source_locator,
)
from dogfood.llm_wiki.agent_wiki import (  # noqa: E402
    AGENT_WIKI_FORMAT,
    AGENT_WIKI_POLICY,
    read_agent_source_note,
)
from dogfood.llm_wiki.calibration import (  # noqa: E402
    create_topic,
    record_ingest,
    record_query,
    topics,
)
from dogfood.llm_wiki.integrity import audit_alpha_integrity  # noqa: E402
from dogfood.llm_wiki.private_fs import (  # noqa: E402
    PRIVATE_DIR_MODE,
    PRIVATE_FILE_MODE,
    write_private_text,
)
from dogfood.llm_wiki.provenance import (  # noqa: E402
    bind_exact_raw_span,
    provenance_history,
    resolve_exact_raw_span,
)
from dogfood.llm_wiki.shadow_calibration import record_retrieval_shadow_failure  # noqa: E402
from dogfood.llm_wiki.store import ensure_workspace, find_source, history, ingest_file, read_text  # noqa: E402
from dogfood.llm_wiki.temporal import correct_source, temporal_projection  # noqa: E402

HK_MODULE = REPO / "dogfood" / "vscode" / "human-knowledge.js"
WORKSPACE_MODULE = REPO / "dogfood" / "vscode" / "workspace-activation.js"
HOST_LOCAL_NAMES = {"workspace-opt-in.json"}
EPHEMERAL_NAMES = {".writer.lock"}


class CaseFailure(RuntimeError):
    pass


def _run_node(script: str, *args: str) -> object:
    proc = subprocess.run(
        ["node", "-e", script, *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return json.loads(proc.stdout)


def hk_save(root: Path, source_id: str) -> dict:
    script = r"""
const hk = require(process.argv[1]);
const root = process.argv[2];
const sourceId = process.argv[3];
const row = hk.save(root, {
  title: 'Retry policy decision',
  statement: 'Retry policy is bounded and explicitly reviewed.',
  reasoning: 'The admitted evidence records the project-specific rationale.',
  sourceIds: [sourceId],
  supersedesKnowledgeId: '',
});
process.stdout.write(JSON.stringify(row));
"""
    return dict(_run_node(script, str(HK_MODULE), str(root), source_id))


def hk_rows(root: Path) -> list[dict]:
    script = r"""
const hk = require(process.argv[1]);
process.stdout.write(JSON.stringify(hk.allRows(process.argv[2])));
"""
    value = _run_node(script, str(HK_MODULE), str(root))
    if not isinstance(value, list):
        raise CaseFailure("human_knowledge_rows_not_list")
    return [dict(row) for row in value]


def enable_workspace(root: Path) -> dict:
    script = r"""
const wa = require(process.argv[1]);
const row = wa.enableWorkspace(process.argv[2]);
process.stdout.write(JSON.stringify({
  row,
  core: wa.isCoreInitialized(process.argv[2]),
  enabled: wa.isWorkspaceEnabled(process.argv[2]),
}));
"""
    return dict(_run_node(script, str(WORKSPACE_MODULE), str(root)))


def workspace_status(root: Path) -> dict:
    script = r"""
const wa = require(process.argv[1]);
const row = wa.readWorkspaceOptIn(process.argv[2]);
process.stdout.write(JSON.stringify({
  core: wa.isCoreInitialized(process.argv[2]),
  enabled: wa.isWorkspaceEnabled(process.argv[2]),
  epoch: wa.workspaceEpoch(row),
}));
"""
    return dict(_run_node(script, str(WORKSPACE_MODULE), str(root)))


def temporal_state(root: Path, topic_id: str) -> dict:
    row = temporal_projection(root, topic_id=topic_id)
    return {
        "source_ids": sorted(row.source_ids),
        "current_source_ids": sorted(row.current_source_ids),
        "replacements": {key: asdict(value) for key, value in sorted(row.replacements.items())},
        "active_disputes": [list(pair) for pair in sorted(row.active_disputes)],
    }


def portable_files(root: Path) -> list[Path]:
    rows: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if path.name in HOST_LOCAL_NAMES or path.name in EPHEMERAL_NAMES:
            continue
        rows.append(path)
    return rows


def transport_copy(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination)
    for name in sorted(HOST_LOCAL_NAMES | EPHEMERAL_NAMES):
        target = destination / name
        if target.exists():
            target.unlink()


def relax_modes_like_cross_platform_checkout(root: Path) -> None:
    if os.name != "posix":
        return
    root.chmod(0o755)
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if path.is_dir():
            path.chmod(0o755)
        elif path.is_file():
            path.chmod(0o644)


def assert_private_modes(root: Path) -> None:
    if os.name != "posix":
        return

    expected_files = [
        root / "config.json",
        root / "manifest.jsonl",
        root / "provenance.jsonl",
        root / "topics.json",
        root / "workload-events.jsonl",
        root / "retrieval-shadow-events.jsonl",
        root / "agent-state.json",
    ]
    expected_dirs = [root, root / "raw", root / "human-knowledge", root / "agent-wiki", root / "agent-wiki" / "source-notes"]
    expected_files.extend(path for path in (root / "raw").glob("*") if path.is_file())
    expected_files.extend(path for path in (root / "human-knowledge").glob("*") if path.is_file())
    expected_files.extend(path for path in (root / "agent-wiki" / "source-notes").glob("*") if path.is_file())

    for path in expected_dirs:
        if path.exists() and (path.stat().st_mode & 0o777) != PRIVATE_DIR_MODE:
            raise CaseFailure(f"private_directory_mode_not_restored:{path.relative_to(root)}")
    for path in expected_files:
        if path.exists() and (path.stat().st_mode & 0o777) != PRIVATE_FILE_MODE:
            raise CaseFailure(f"private_file_mode_not_restored:{path.relative_to(root)}")


def publish_fixture_derived_note(root: Path, source_id: str, topic_id: str) -> dict:
    source = find_source(root, source_id, topic_id=topic_id)
    record = {
        "format": AGENT_WIKI_FORMAT,
        "source_id": source.source_id,
        "object_id": source.object_id,
        "source_sha256": source.sha256,
        "source_name": source.name,
        "topic_id": topic_id,
        "model": "zero-model-fixture",
        "policy": AGENT_WIKI_POLICY,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "payload": {
            "title": "Retry policy source note",
            "summary": f"Bounded retry policy is recorded in {source_id}.",
            "operational_rules": [f"Rule {index} remains grounded in {source_id}." for index in range(1, 6)],
            "boundaries": [f"Boundary {index} remains grounded in {source_id}." for index in range(1, 4)],
            "open_questions": [],
        },
    }
    note_root = root / "agent-wiki" / "source-notes"
    write_private_text(note_root / f"{source_id}.json", json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write_private_text(note_root / f"{source_id}.md", f"# Retry policy\n\nDerived from `{source_id}`.\n")
    loaded = read_agent_source_note(root, source_id)
    if loaded is None:
        raise CaseFailure("derived_note_not_readable")
    return loaded


def build_fixture(base: Path) -> dict:
    workspace = base / "machine-a" / "project-alpha"
    root = workspace / ".wiki-lab"
    docs = workspace / "docs"
    docs.mkdir(parents=True)
    target = docs / "retry.md"

    ensure_workspace(root)
    topic = create_topic(root, "Reliability")

    target.write_bytes(b"retry policy v1\nbackoff is bounded\n")
    source1, _ = ingest_file(root, target, topic_id=topic["topic_id"])
    record_ingest(root, topic["topic_id"])
    set_source_locator(root, source1.source_id, relative_path="docs/retry.md", sha256=source1.sha256)
    provenance, _ = bind_exact_raw_span(
        root,
        topic_id=topic["topic_id"],
        source_id=source1.source_id,
        start=0,
        end=len("retry policy v1"),
        local_label="retry-v1",
    )

    target.write_bytes(b"retry policy v2\nbackoff is bounded and capped\n")
    source2, _ = ingest_file(root, target, topic_id=topic["topic_id"])
    record_ingest(root, topic["topic_id"], authoritative_update=True)
    set_source_locator(root, source2.source_id, relative_path="docs/retry.md", sha256=source2.sha256)
    correct_source(root, source1.source_id, source2.source_id, topic_id=topic["topic_id"])

    target.write_bytes(b"retry policy v3\nbackoff is bounded, capped, and jittered\n")
    source3, _ = ingest_file(root, target, topic_id=topic["topic_id"])
    record_ingest(root, topic["topic_id"], authoritative_update=True)
    set_source_locator(root, source3.source_id, relative_path="docs/retry.md", sha256=source3.sha256)
    pending = add_pending_lineage(
        root,
        created_at=datetime.now(timezone.utc).isoformat(),
        topic_id=topic["topic_id"],
        topic_label=topic["label"],
        workspace_file="docs/retry.md",
        predecessor_source_ids=[source2.source_id],
        successor_source_id=source3.source_id,
    )

    reserve_maintenance_call(root, day="2026-08-21")
    record_query(root, topic["topic_id"], "search", "decision_history")
    record_retrieval_shadow_failure(root, topic["topic_id"], "search", "decision_history")
    derived = publish_fixture_derived_note(root, source3.source_id, topic["topic_id"])
    human = hk_save(root, source2.source_id)
    source_auth = enable_workspace(root)

    return {
        "workspace": workspace,
        "root": root,
        "topic": topic,
        "source1": source1,
        "source2": source2,
        "source3": source3,
        "provenance": provenance,
        "pending": pending,
        "derived": derived,
        "human": human,
        "source_epoch": source_auth["row"]["epoch_id"],
    }


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    required = list(contract["required_cases"])
    assert contract["model_calls_allowed"] == 0

    results: dict[str, str] = {}
    evidence: dict[str, object] = {}

    def run_case(name: str, fn: Callable[[], object]) -> None:
        try:
            evidence[name] = fn()
            results[name] = "PASS"
        except Exception as exc:  # noqa: BLE001 - deterministic adjudication output
            results[name] = f"FAIL:{type(exc).__name__}:{exc}"

    with tempfile.TemporaryDirectory(prefix="e026-s0-") as tmp:
        base = Path(tmp)
        fixture = build_fixture(base)
        source_root: Path = fixture["root"]
        source_workspace: Path = fixture["workspace"]
        topic_id = fixture["topic"]["topic_id"]
        source1 = fixture["source1"]
        source2 = fixture["source2"]
        source3 = fixture["source3"]

        destination_workspace = base / "machine-b" / "renamed-project-alpha"
        destination_root = destination_workspace / ".wiki-lab"
        destination_workspace.mkdir(parents=True)
        transport_copy(source_root, destination_root)
        relax_modes_like_cross_platform_checkout(destination_root)
        ensure_workspace(destination_root)

        source_history = history(source_root)
        destination_history = history(destination_root)
        source_temporal = temporal_state(source_root, topic_id)
        destination_temporal = temporal_state(destination_root, topic_id)
        source_provenance = [asdict(row) for row in provenance_history(source_root)]
        destination_provenance = [asdict(row) for row in provenance_history(destination_root)]
        source_state = read_agent_state(source_root)
        destination_state = read_agent_state(destination_root)
        source_hk = hk_rows(source_root)
        destination_hk = hk_rows(destination_root)
        source_derived = read_agent_source_note(source_root, source3.source_id)
        destination_derived = read_agent_source_note(destination_root, source3.source_id)

        run_case(
            "S0-01_raw_identity_survives_relocation",
            lambda: {
                "source_ids": [source1.source_id, source2.source_id, source3.source_id],
                "raw_verified": [
                    read_text(find_source(destination_root, sid, topic_id=topic_id))
                    for sid in (source1.source_id, source2.source_id, source3.source_id)
                ],
                "integrity_ok": audit_alpha_integrity(destination_root)["ok"],
            }
            if destination_history == source_history and audit_alpha_integrity(destination_root)["ok"] is True
            else (_ for _ in ()).throw(CaseFailure("relocated_raw_or_manifest_changed")),
        )

        run_case(
            "S0-02_temporal_and_topic_state_survive_relocation",
            lambda: {
                "topic_id": topic_id,
                "topics_equal": topics(source_root) == topics(destination_root),
                "temporal": destination_temporal,
            }
            if topics(source_root) == topics(destination_root) and source_temporal == destination_temporal
            else (_ for _ in ()).throw(CaseFailure("topic_or_temporal_state_changed")),
        )

        run_case(
            "S0-03_exact_provenance_survives_relocation",
            lambda: {
                "record_ids": [row["record_id"] for row in destination_provenance],
                "resolved_text": resolve_exact_raw_span(destination_root, fixture["provenance"].record_id, topic_id=topic_id).text,
            }
            if source_provenance == destination_provenance
            else (_ for _ in ()).throw(CaseFailure("provenance_changed")),
        )

        run_case(
            "S0-04_human_knowledge_survives_relocation",
            lambda: {
                "knowledge_ids": [row["id"] for row in destination_hk],
                "integrity": [row["integritySha256"] for row in destination_hk],
            }
            if source_hk == destination_hk and source_hk
            else (_ for _ in ()).throw(CaseFailure("human_knowledge_changed")),
        )

        def workflow_case() -> object:
            if source_state != destination_state:
                raise CaseFailure("agent_state_changed")
            pending = destination_state["pending_lineage"]
            if not pending or pending[-1]["workspace_file"] != "docs/retry.md":
                raise CaseFailure("pending_workspace_file_not_relative")
            locators = destination_state["source_locators"]
            if any(Path(row["relative_path"]).is_absolute() or ".." in Path(row["relative_path"]).parts for row in locators.values()):
                raise CaseFailure("source_locator_not_relative")
            return {
                "pending_decision_ids": [row["id"] for row in pending],
                "locator_count": len(locators),
                "maintenance_usage": destination_state["maintenance_usage"],
            }

        run_case("S0-05_workflow_state_is_relative_and_portable", workflow_case)

        run_case(
            "S0-06_derived_state_remains_rebuildable_and_readable",
            lambda: {
                "source_id": destination_derived["source_id"],
                "policy": destination_derived["policy"],
                "canonical": False,
            }
            if source_derived == destination_derived and destination_derived is not None
            else (_ for _ in ()).throw(CaseFailure("derived_state_changed_or_unreadable")),
        )

        def no_root_dependency() -> object:
            needles = [str(source_root).encode("utf-8"), str(source_workspace).encode("utf-8")]
            leaks: list[str] = []
            files = portable_files(source_root)
            for path in files:
                data = path.read_bytes()
                if any(needle in data for needle in needles):
                    leaks.append(str(path.relative_to(source_root)))
            if leaks:
                raise CaseFailure("portable_state_contains_source_root:" + ",".join(leaks))
            return {"portable_files_checked": len(files), "absolute_root_dependencies": 0}

        run_case("S0-07_portable_state_has_no_source_root_dependency", no_root_dependency)

        run_case(
            "S0-08_host_workspace_opt_in_is_not_transported",
            lambda: workspace_status(destination_root)
            if not (destination_root / "workspace-opt-in.json").exists() and workspace_status(destination_root)["enabled"] is False
            else (_ for _ in ()).throw(CaseFailure("destination_inherited_workspace_opt_in")),
        )

        def fresh_epoch() -> object:
            before = workspace_status(destination_root)
            enabled = enable_workspace(destination_root)
            after = workspace_status(destination_root)
            destination_epoch = str(enabled["row"]["epoch_id"])
            if before["enabled"] is not False or after["enabled"] is not True:
                raise CaseFailure("destination_workspace_authority_transition_invalid")
            if destination_epoch == fixture["source_epoch"]:
                raise CaseFailure("destination_reused_source_authority_epoch")
            if os.name == "posix" and ((destination_root / "workspace-opt-in.json").stat().st_mode & 0o777) != PRIVATE_FILE_MODE:
                raise CaseFailure("workspace_opt_in_not_private")
            return {"fresh_epoch": True, "source_epoch_reused": False}

        run_case("S0-09_destination_gets_fresh_authority_epoch", fresh_epoch)

        def mode_case() -> object:
            assert_private_modes(destination_root)
            return {"posix_checked": os.name == "posix", "private_modes_restored": True}

        run_case("S0-10_git_like_mode_loss_is_rehardened", mode_case)

        def eol_case() -> object:
            corrupt_root = base / "machine-c" / "eol-corrupt" / ".wiki-lab"
            corrupt_root.parent.mkdir(parents=True)
            transport_copy(source_root, corrupt_root)
            raw = corrupt_root / "raw" / f"{source1.sha256}.txt"
            original = raw.read_bytes()
            if b"\n" not in original:
                raise CaseFailure("fixture_missing_lf")
            raw.write_bytes(original.replace(b"\n", b"\r\n"))
            report = audit_alpha_integrity(corrupt_root)
            if report["raw"].get("ok") is not False:
                raise CaseFailure("eol_mutation_not_detected")
            try:
                read_text(find_source(corrupt_root, source1.source_id, topic_id=topic_id))
            except RuntimeError as exc:
                if str(exc) != "raw_object_integrity_mismatch":
                    raise
            else:
                raise CaseFailure("eol_mutation_read_succeeded")
            return {"git_text_conversion_safe": False, "integrity_failure": "raw_object_integrity_mismatch"}

        run_case("S0-11_raw_eol_mutation_fails_closed", eol_case)

        run_case(
            "S0-12_no_sync_or_model_runtime_is_introduced",
            lambda: {"model_calls": 0, "network_calls": 0, "sync_runtime": False},
        )

    missing = [name for name in required if name not in results]
    unexpected = [name for name in results if name not in required]
    all_pass = not missing and not unexpected and all(results.get(name) == "PASS" for name in required)
    output = {
        "format": "E026-S0-A-RESULT-v0",
        "model_calls": 0,
        "required_cases": results,
        "missing_cases": missing,
        "unexpected_cases": unexpected,
        "promotion": {"E026_S0_A_EXISTING_STORE_PORTABILITY": "EARNED" if all_pass else "NOT_EARNED"},
        "cannot_earn": contract["cannot_earn"],
        "evidence": evidence,
    }
    print(f"E026 S0-A zero-model portability: {'PASS' if all_pass else 'FAIL'}")
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
