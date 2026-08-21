from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CONTRACT = ROOT / "f0-evaluation-contract-v0.json"
HANDOFF = REPO / "HANDOFF.md"


class ScopeError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_store(root: Path, sources: dict[str, str], *, damage_manifest: bool = False) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "raw").mkdir(exist_ok=True)
    (root / "config.json").write_text('{"format":"e025-f0-fixture"}\n', encoding="utf-8")
    rows = []
    for source_id, text in sorted(sources.items()):
        relative = f"raw/{source_id}.txt"
        data = text.encode("utf-8")
        (root / relative).write_bytes(data)
        digest = sha256_bytes(data)
        if damage_manifest and source_id == sorted(sources)[0]:
            digest = "0" * 64
        rows.append({"source_id": source_id, "relative_path": relative, "sha256": digest})
    (root / "manifest.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def manifest_rows(root: Path) -> list[dict[str, str]]:
    if not root.exists():
        raise ScopeError("library_store_unavailable")
    if not (root / "config.json").is_file() or not (root / "manifest.jsonl").is_file():
        raise ScopeError("library_store_damaged")
    try:
        rows = [json.loads(line) for line in (root / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if line]
    except Exception as exc:  # noqa: BLE001 - bounded fixture failure
        raise ScopeError("library_store_damaged") from exc
    for row in rows:
        relative = str(row.get("relative_path", ""))
        file_path = root / relative
        if not relative or not file_path.is_file():
            raise ScopeError("library_store_damaged")
        if sha256_bytes(file_path.read_bytes()) != row.get("sha256"):
            raise ScopeError("library_store_damaged")
    return rows


def verified_read(root: Path, source_id: str) -> dict[str, str]:
    rows = manifest_rows(root)
    row = next((item for item in rows if item.get("source_id") == source_id), None)
    if row is None:
        raise ScopeError("scoped_source_not_found")
    data = (root / row["relative_path"]).read_bytes()
    return {"source_id": source_id, "sha256": sha256_bytes(data), "text": data.decode("utf-8")}


def snapshot_tree(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha256_bytes(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@dataclass(frozen=True)
class Registration:
    store_id: str
    alias: str
    root: Path
    read_exposure: bool


class LibraryCatalog:
    def __init__(self) -> None:
        self.registrations: list[Registration] = []
        self.root_touches = 0

    def register(self, store_id: str, alias: str, root: Path, *, read_exposure: bool = True) -> None:
        if not store_id.startswith("libstore-"):
            raise AssertionError("fixture store IDs must be opaque libstore-* values")
        self.registrations.append(Registration(store_id, alias, root, read_exposure))

    @staticmethod
    def _grant_valid(library_grant: dict[str, object] | None, workspace_epoch: str) -> bool:
        return bool(
            library_grant
            and library_grant.get("enabled") is True
            and library_grant.get("workspace_enabled_at") == workspace_epoch
        )

    def resolve_alias(
        self,
        alias: str,
        *,
        query_grant_valid: bool,
        library_grant: dict[str, object] | None,
        workspace_epoch: str,
    ) -> Registration:
        if not query_grant_valid:
            raise ScopeError("query_reasoning_grant_required")
        if not self._grant_valid(library_grant, workspace_epoch):
            raise ScopeError("library_access_grant_required")
        matches = [
            row for row in self.registrations
            if row.read_exposure and row.alias.casefold() == alias.casefold()
        ]
        if not matches:
            raise ScopeError("library_store_not_registered")
        if len(matches) != 1:
            raise ScopeError("library_store_alias_ambiguous")
        return matches[0]

    def resolve_scope(
        self,
        scope_ref: dict[str, str] | None,
        *,
        query_grant_valid: bool,
        library_grant: dict[str, object] | None,
        workspace_epoch: str,
    ) -> Registration:
        if not scope_ref or scope_ref.get("kind") != "library_store" or not scope_ref.get("store_id"):
            raise ScopeError("external_scope_ref_required")
        if not query_grant_valid:
            raise ScopeError("query_reasoning_grant_required")
        if not self._grant_valid(library_grant, workspace_epoch):
            raise ScopeError("library_access_grant_required")
        matches = [
            row for row in self.registrations
            if row.read_exposure and row.store_id == scope_ref["store_id"]
        ]
        if len(matches) != 1:
            raise ScopeError("library_store_not_registered")
        return matches[0]

    def read_scoped(
        self,
        scope_ref: dict[str, str] | None,
        source_id: str,
        *,
        query_grant_valid: bool,
        library_grant: dict[str, object] | None,
        workspace_epoch: str,
    ) -> dict[str, object]:
        registration = self.resolve_scope(
            scope_ref,
            query_grant_valid=query_grant_valid,
            library_grant=library_grant,
            workspace_epoch=workspace_epoch,
        )
        self.root_touches += 1
        row = verified_read(registration.root, source_id)
        return {
            "scope_ref": {"kind": "library_store", "store_id": registration.store_id},
            "source_id": row["source_id"],
            "sha256": row["sha256"],
            "text": row["text"],
        }


class CurrentStoreWriter:
    def __init__(self, current_root: Path) -> None:
        self.current_root = current_root

    def _append(self, name: str, value: str) -> None:
        target = self.current_root / "f0-current-writes" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(value + "\n")

    def remember_source(self, value: str) -> None:
        self._append("sources.log", value)

    def remember_human_knowledge(self, value: str) -> None:
        self._append("human-knowledge.log", value)

    def resolve_lineage(self, value: str) -> None:
        self._append("lineage.log", value)


class ModelProbe:
    def __init__(self) -> None:
        self.calls = 0

    def launch(self) -> None:
        self.calls += 1
        raise AssertionError("F0 must never launch a model")


def expect_scope_error(code: str, call: Callable[[], object]) -> str:
    try:
        call()
    except ScopeError as exc:
        assert str(exc) == code, (code, str(exc))
        return str(exc)
    raise AssertionError(f"expected ScopeError({code})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regression-gate-pass", action="store_true")
    parser.add_argument("--diff-boundary-pass", action="store_true")
    args = parser.parse_args()

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    required = list(contract["required_cases"])
    assert contract["model_calls_allowed"] == 0
    assert contract["reviewed_main_sha"] == "7f0c4045a6341a16c92e4582a92fcd99e6352fcb"

    results: dict[str, str] = {}
    evidence: dict[str, object] = {}

    def run_case(name: str, fn: Callable[[], object]) -> None:
        try:
            evidence[name] = fn()
            results[name] = "PASS"
        except Exception as exc:  # noqa: BLE001 - collect deterministic adjudication
            results[name] = f"FAIL:{type(exc).__name__}:{exc}"

    with tempfile.TemporaryDirectory(prefix="e025-f0-") as tmp:
        temp = Path(tmp)
        root_a = temp / "private" / "alpha-authority-core"
        root_b = temp / "workspace-b" / ".wiki-lab"
        root_c = temp / "private" / "collision-authority-core"
        root_unregistered = temp / "private" / "unregistered-authority-core"
        root_damaged = temp / "private" / "damaged-authority-core"
        root_missing = temp / "private" / "missing-authority-core"

        make_store(root_a, {"src-a-only": "A-only evidence", "src-shared": "A shared identity bytes"})
        make_store(root_b, {"src-b-only": "B-only evidence", "src-shared": "B shared identity bytes"})
        make_store(root_c, {"src-c-only": "C collision evidence"})
        make_store(root_unregistered, {"src-u-only": "unregistered but valid"})
        make_store(root_damaged, {"src-damaged": "damaged authority"}, damage_manifest=True)

        catalog = LibraryCatalog()
        catalog.register("libstore-a7f19d", "Project A", root_a)
        catalog.register("libstore-missing91", "Missing Project", root_missing)
        catalog.register("libstore-damaged4c", "Damaged Project", root_damaged)

        epoch_1 = "workspace-enabled-epoch-1"
        epoch_2 = "workspace-enabled-epoch-2"
        grant_epoch_1 = {"enabled": True, "workspace_enabled_at": epoch_1}
        grant_off = {"enabled": False, "workspace_enabled_at": epoch_1}
        probe = ModelProbe()

        def f001() -> object:
            before = catalog.root_touches
            row = verified_read(root_b, "src-b-only")
            assert row["text"] == "B-only evidence"
            assert catalog.root_touches == before
            return {"external_root_touches": catalog.root_touches - before}

        run_case("F0-01_current_store_isolation", f001)

        def f002() -> object:
            before = catalog.root_touches
            err = expect_scope_error(
                "library_store_not_registered",
                lambda: catalog.resolve_alias(
                    "Unregistered Project",
                    query_grant_valid=True,
                    library_grant=grant_epoch_1,
                    workspace_epoch=epoch_1,
                ),
            )
            assert root_unregistered.exists()
            assert catalog.root_touches == before
            return {"failure": err, "external_root_touches": 0}

        run_case("F0-02_unregistered_store_invisible", f002)

        def f003() -> object:
            before = catalog.root_touches
            err = expect_scope_error(
                "library_access_grant_required",
                lambda: catalog.resolve_alias(
                    "Project A",
                    query_grant_valid=True,
                    library_grant=grant_off,
                    workspace_epoch=epoch_1,
                ),
            )
            assert catalog.root_touches == before
            return {"failure": err, "external_root_touches": 0}

        run_case("F0-03_library_grant_off", f003)

        def f004() -> object:
            resolved = catalog.resolve_alias(
                "Project A",
                query_grant_valid=True,
                library_grant=grant_epoch_1,
                workspace_epoch=epoch_1,
            )
            assert resolved.store_id == "libstore-a7f19d"
            row = catalog.read_scoped(
                {"kind": "library_store", "store_id": resolved.store_id},
                "src-a-only",
                query_grant_valid=True,
                library_grant=grant_epoch_1,
                workspace_epoch=epoch_1,
            )
            assert row["text"] == "A-only evidence"
            return row

        run_case("F0-04_named_registered_store_only", f004)

        def f005() -> object:
            catalog.register("libstore-c2e8f1", "Project A", root_c)
            before = catalog.root_touches
            err = expect_scope_error(
                "library_store_alias_ambiguous",
                lambda: catalog.resolve_alias(
                    "Project A",
                    query_grant_valid=True,
                    library_grant=grant_epoch_1,
                    workspace_epoch=epoch_1,
                ),
            )
            assert catalog.root_touches == before
            return {"failure": err, "external_root_touches": 0}

        run_case("F0-05_ambiguous_alias_fail_closed", f005)

        def f006() -> object:
            scope = {"kind": "library_store", "store_id": "libstore-missing91"}
            err = expect_scope_error(
                "library_store_unavailable",
                lambda: catalog.read_scoped(
                    scope,
                    "src-any",
                    query_grant_valid=True,
                    library_grant=grant_epoch_1,
                    workspace_epoch=epoch_1,
                ),
            )
            assert verified_read(root_b, "src-b-only")["text"] == "B-only evidence"
            return {"failure": err, "current_store_usable": True}

        run_case("F0-06_unavailable_store_contained", f006)

        def f007() -> object:
            scope = {"kind": "library_store", "store_id": "libstore-damaged4c"}
            err = expect_scope_error(
                "library_store_damaged",
                lambda: catalog.read_scoped(
                    scope,
                    "src-damaged",
                    query_grant_valid=True,
                    library_grant=grant_epoch_1,
                    workspace_epoch=epoch_1,
                ),
            )
            assert verified_read(root_b, "src-b-only")["text"] == "B-only evidence"
            return {"failure": err, "current_store_usable": True}

        run_case("F0-07_damaged_external_store_contained", f007)

        valid_scope = {"kind": "library_store", "store_id": "libstore-a7f19d"}

        def f008() -> object:
            err = expect_scope_error(
                "external_scope_ref_required",
                lambda: catalog.read_scoped(
                    None,
                    "src-a-only",
                    query_grant_valid=True,
                    library_grant=grant_epoch_1,
                    workspace_epoch=epoch_1,
                ),
            )
            row = catalog.read_scoped(
                valid_scope,
                "src-a-only",
                query_grant_valid=True,
                library_grant=grant_epoch_1,
                workspace_epoch=epoch_1,
            )
            assert row["scope_ref"] == valid_scope
            return {"bare_ref_failure": err, "terminal_scope": row["scope_ref"]}

        run_case("F0-08_external_terminal_scope_required", f008)

        def f009() -> object:
            before = verified_read(root_b, "src-b-only")["sha256"]
            err = expect_scope_error(
                "scoped_source_not_found",
                lambda: catalog.read_scoped(
                    valid_scope,
                    "src-b-only",
                    query_grant_valid=True,
                    library_grant=grant_epoch_1,
                    workspace_epoch=epoch_1,
                ),
            )
            after = verified_read(root_b, "src-b-only")["sha256"]
            assert before == after
            return {"failure": err, "current_store_fallback": False}

        run_case("F0-09_no_cross_store_source_fallback", f009)

        def f010() -> object:
            external = catalog.read_scoped(
                valid_scope,
                "src-shared",
                query_grant_valid=True,
                library_grant=grant_epoch_1,
                workspace_epoch=epoch_1,
            )
            current = verified_read(root_b, "src-shared")
            assert external["text"] == "A shared identity bytes"
            assert current["text"] == "B shared identity bytes"
            assert external["sha256"] != current["sha256"]
            assert external["scope_ref"] == valid_scope
            return {"scope_ref": external["scope_ref"], "sha256": external["sha256"]}

        run_case("F0-10_scoped_verified_read", f010)

        def f011() -> object:
            before = snapshot_tree(root_a)
            writer = CurrentStoreWriter(root_b)
            writer.remember_source("source-admission")
            writer.remember_human_knowledge("human-knowledge")
            writer.resolve_lineage("lineage-resolution")
            after = snapshot_tree(root_a)
            assert before == after
            assert (root_b / "f0-current-writes" / "sources.log").is_file()
            assert (root_b / "f0-current-writes" / "human-knowledge.log").is_file()
            assert (root_b / "f0-current-writes" / "lineage.log").is_file()
            return {"external_store_mutations": 0, "current_store_mutations": 3}

        run_case("F0-11_current_store_write_isolation", f011)

        def f012() -> object:
            assert catalog.resolve_scope(
                valid_scope,
                query_grant_valid=True,
                library_grant=grant_epoch_1,
                workspace_epoch=epoch_1,
            ).store_id == "libstore-a7f19d"
            err = expect_scope_error(
                "library_access_grant_required",
                lambda: catalog.resolve_scope(
                    valid_scope,
                    query_grant_valid=True,
                    library_grant=grant_epoch_1,
                    workspace_epoch=epoch_2,
                ),
            )
            return {"failure_after_reenable": err, "stale_grant_revived": False}

        run_case("F0-12_stale_library_grant_invalidated", f012)

        def f013() -> object:
            err = expect_scope_error(
                "library_access_grant_required",
                lambda: catalog.resolve_scope(
                    valid_scope,
                    query_grant_valid=True,
                    library_grant=None,
                    workspace_epoch=epoch_1,
                ),
            )
            return {"failure": err, "external_evidence_exposed": False}

        run_case("F0-13_query_plane_grant_alone_insufficient", f013)

        def f014() -> object:
            err = expect_scope_error(
                "query_reasoning_grant_required",
                lambda: catalog.resolve_scope(
                    valid_scope,
                    query_grant_valid=False,
                    library_grant=grant_epoch_1,
                    workspace_epoch=epoch_1,
                ),
            )
            return {"failure": err, "model_capable_exposure_authorized": False}

        run_case("F0-14_library_registration_alone_insufficient", f014)

        def f015() -> object:
            samples: list[object] = []
            samples.append(catalog.read_scoped(
                valid_scope,
                "src-a-only",
                query_grant_valid=True,
                library_grant=grant_epoch_1,
                workspace_epoch=epoch_1,
            ))
            for code, scope in [
                ("library_store_unavailable", {"kind": "library_store", "store_id": "libstore-missing91"}),
                ("library_store_damaged", {"kind": "library_store", "store_id": "libstore-damaged4c"}),
            ]:
                samples.append(expect_scope_error(
                    code,
                    lambda scope=scope: catalog.read_scoped(
                        scope,
                        "src-any",
                        query_grant_valid=True,
                        library_grant=grant_epoch_1,
                        workspace_epoch=epoch_1,
                    ),
                ))
            rendered = json.dumps(samples, sort_keys=True)
            for private_root in [root_a, root_c, root_unregistered, root_damaged, root_missing]:
                assert str(private_root) not in rendered
            return {"absolute_root_leaks": 0}

        run_case("F0-15_private_root_redacted", f015)

        run_case(
            "F0-16_zero_model_calls",
            lambda: {"model_calls": probe.calls} if probe.calls == 0 else (_ for _ in ()).throw(AssertionError(probe.calls)),
        )

        def f017() -> object:
            assert args.regression_gate_pass, "CI regression gate was not attested by the caller"
            return {"regression_gate": "PASS"}

        run_case("F0-17_existing_0_1_17_regression_gate_green", f017)

        def f018() -> object:
            assert args.diff_boundary_pass, "F0 no-runtime-diff boundary was not attested by the caller"
            handoff = HANDOFF.read_text(encoding="utf-8")
            for phrase in [
                "**G2 Persistence: NOT_EARNED; parked.**",
                "**G3 Identity / Routing: NOT_OPENED.**",
                "paid E023 semantic calls: **paused**",
                "E024 L1 iterative Librarian remains not earned",
                "authorization is resolved **before retrieval, scoring, candidate counts, diagnostics, or model exposure**",
            ]:
                assert phrase in handoff, phrase
            return {"runtime_federation_diff": False, "g2_g3_reopened": False}

        run_case("F0-18_e023_semantic_gates_remain_closed", f018)

        rendered_evidence = json.dumps(evidence, sort_keys=True)
        for private_root in [root_a, root_c, root_unregistered, root_damaged, root_missing]:
            if str(private_root) in rendered_evidence:
                results["F0-15_private_root_redacted"] = "FAIL:absolute_root_leak"

    missing = [name for name in required if name not in results]
    extra = [name for name in results if name not in required]
    all_pass = not missing and not extra and all(results[name] == "PASS" for name in required) and probe.calls == 0
    promotion = "EARNED" if all_pass else "NOT_EARNED"

    output = {
        "format": "E025-F0-result-v0",
        "model_calls": probe.calls,
        "required_cases": results,
        "missing_cases": missing,
        "unexpected_cases": extra,
        "promotion": {"E025_F0_NAMED_STORE_SCOPE_CONTRACT": promotion},
        "cannot_earn": contract["cannot_earn"],
    }
    print(f"E025 F0 zero-model validation: {'PASS' if all_pass else 'FAIL'}")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
