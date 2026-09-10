from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterator

from .private_fs import ensure_private_directory, ensure_private_file, write_private_text
from .remote_snapshot import SnapshotError, read_snapshot, write_snapshot
from .store import ensure_workspace, history

HELPER_PROTOCOL = "LLM-WIKI-REMOTE-HELPER-v1"
CATALOG_VERSION = 1
MAX_REQUEST_BYTES = 1024 * 1024
MAX_UPLOAD_BYTES = 64 * 1024 * 1024
PROJECT_STORE_RE = re.compile(r"^project-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
SOURCE_ID_RE = re.compile(r"^src-[0-9A-Za-z-]+$")
HK_ID_RE = re.compile(r"^hk-[0-9]+-[0-9a-f]+$")
HK_FORMAT = "llm-wiki-human-knowledge-v1"


def _authority_home() -> Path:
    override = os.environ.get("LLM_WIKI_REMOTE_HOME", "").strip()
    if override:
        root = Path(override).expanduser()
    else:
        data_home = os.environ.get("XDG_DATA_HOME", "").strip()
        root = Path(data_home).expanduser() / "llm-wiki" if data_home else Path.home() / ".local" / "share" / "llm-wiki"
        root = root / "personal-wiki"
    ensure_private_directory(root)
    ensure_private_directory(root / "stores")
    ensure_private_directory(root / "locks")
    ensure_private_directory(root / "tmp")
    return root


def _catalog_path(home: Path) -> Path:
    return home / "catalog.json"


def _empty_catalog() -> dict:
    return {"version": CATALOG_VERSION, "stores": []}


def _validate_store_id(value: object) -> str:
    store_id = str(value or "")
    if not PROJECT_STORE_RE.fullmatch(store_id):
        raise RuntimeError("remote_store_id_invalid")
    return store_id


def _read_catalog(home: Path) -> dict:
    path = _catalog_path(home)
    if not path.exists():
        return _empty_catalog()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("remote_catalog_corrupt") from exc
    if not isinstance(raw, dict) or raw.get("version") != CATALOG_VERSION or not isinstance(raw.get("stores"), list):
        raise RuntimeError("remote_catalog_corrupt")
    seen: set[str] = set()
    stores = []
    for row in raw["stores"]:
        if not isinstance(row, dict):
            raise RuntimeError("remote_catalog_corrupt")
        store_id = _validate_store_id(row.get("store_id"))
        if store_id in seen:
            raise RuntimeError("remote_catalog_corrupt")
        seen.add(store_id)
        display_name = str(row.get("display_name") or "").strip()
        created_at = str(row.get("created_at") or "")
        bootstrap_complete = row.get("bootstrap_complete") is True
        if not display_name or len(display_name) > 120 or not created_at:
            raise RuntimeError("remote_catalog_corrupt")
        stores.append(
            {
                "store_id": store_id,
                "display_name": display_name,
                "created_at": created_at,
                "bootstrap_complete": bootstrap_complete,
            }
        )
    return {"version": CATALOG_VERSION, "stores": stores}


def _write_catalog(home: Path, catalog: dict) -> None:
    validated = _read_catalog_from_value(catalog)
    write_private_text(_catalog_path(home), json.dumps(validated, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _read_catalog_from_value(raw: dict) -> dict:
    if not isinstance(raw, dict) or raw.get("version") != CATALOG_VERSION or not isinstance(raw.get("stores"), list):
        raise RuntimeError("remote_catalog_corrupt")
    # Reuse validation without writing potentially invalid state.
    seen: set[str] = set()
    stores = []
    for row in raw["stores"]:
        if not isinstance(row, dict):
            raise RuntimeError("remote_catalog_corrupt")
        store_id = _validate_store_id(row.get("store_id"))
        if store_id in seen:
            raise RuntimeError("remote_catalog_corrupt")
        seen.add(store_id)
        display_name = str(row.get("display_name") or "").strip()
        created_at = str(row.get("created_at") or "")
        if not display_name or len(display_name) > 120 or not created_at:
            raise RuntimeError("remote_catalog_corrupt")
        stores.append(
            {
                "store_id": store_id,
                "display_name": display_name,
                "created_at": created_at,
                "bootstrap_complete": row.get("bootstrap_complete") is True,
            }
        )
    return {"version": CATALOG_VERSION, "stores": stores}


def _find_store(catalog: dict, store_id: str) -> dict:
    matches = [row for row in catalog["stores"] if row["store_id"] == store_id]
    if len(matches) != 1:
        raise RuntimeError("remote_store_not_found")
    return matches[0]


def _store_root(home: Path, store_id: str) -> Path:
    _validate_store_id(store_id)
    return home / "stores" / store_id


@contextlib.contextmanager
def _store_lock(home: Path, store_id: str) -> Iterator[None]:
    if os.name != "posix":
        raise RuntimeError("remote_helper_linux_only")
    import fcntl  # Linux/POSIX-only by product contract.

    lock_path = home / "locks" / f"{store_id}.lock"
    ensure_private_file(lock_path)
    with lock_path.open("r+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _json_response(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _read_request(stream: BinaryIO) -> dict:
    line = stream.readline(MAX_REQUEST_BYTES + 1)
    if not line or len(line) > MAX_REQUEST_BYTES or not line.endswith(b"\n"):
        raise RuntimeError("remote_request_invalid")
    try:
        value = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("remote_request_invalid") from exc
    if not isinstance(value, dict) or value.get("protocol") != HELPER_PROTOCOL:
        raise RuntimeError("remote_request_invalid")
    return value


def _create_store(home: Path, request: dict) -> dict:
    display_name = str(request.get("display_name") or "Project Memory").strip()[:120]
    if not display_name:
        raise RuntimeError("remote_store_display_name_invalid")
    bootstrap = request.get("bootstrap") is True
    catalog = _read_catalog(home)
    import uuid

    store_id = f"project-{uuid.uuid4()}"
    root = _store_root(home, store_id)
    ensure_private_directory(root)
    if not bootstrap:
        ensure_workspace(root)
    row = {
        "store_id": store_id,
        "display_name": display_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "bootstrap_complete": not bootstrap,
    }
    catalog["stores"].append(row)
    _write_catalog(home, catalog)
    return row


def _mark_bootstrap_complete(home: Path, store_id: str) -> None:
    catalog = _read_catalog(home)
    row = _find_store(catalog, store_id)
    row["bootstrap_complete"] = True
    _write_catalog(home, catalog)


def _require_ready_store(home: Path, store_id: str) -> tuple[dict, Path]:
    catalog = _read_catalog(home)
    row = _find_store(catalog, store_id)
    if row.get("bootstrap_complete") is not True:
        raise RuntimeError("remote_store_bootstrap_incomplete")
    root = _store_root(home, store_id)
    if not root.is_dir():
        raise RuntimeError("remote_store_missing")
    return row, root


def _allowed_core_invocation(module_name: str, args: list[str]) -> bool:
    if not args or any("\x00" in item for item in args):
        return False
    command = args[0]
    if module_name == "dogfood.llm_wiki.cli":
        if command in {"init", "integrity", "ingest", "search", "discover", "context", "history"}:
            return True
        if command == "topic" and len(args) >= 2 and args[1] in {"add", "list"}:
            return True
        if command == "source" and len(args) >= 2 and args[1] in {"show", "list", "status", "supersede", "correct", "change", "dispute"}:
            return True
        return False
    if module_name == "dogfood.llm_wiki.agent_state_cli":
        return command in {"locator-list", "locator-set", "pending-list", "pending-add", "pending-resolve", "usage-status", "usage-reserve"}
    if module_name == "dogfood.llm_wiki.agent_memory_cli":
        return command in {"read", "compare"}
    if module_name == "dogfood.llm_wiki.agent_wiki_cli":
        return command in {"build", "show", "search"}
    return False


def _materialize_uploads(home: Path, request: dict, stream: BinaryIO, args: list[str]) -> tuple[list[str], tempfile.TemporaryDirectory[str] | None]:
    uploads = request.get("uploads") or []
    if not isinstance(uploads, list) or len(uploads) > 8:
        raise RuntimeError("remote_upload_manifest_invalid")
    if not uploads:
        return args, None
    temp = tempfile.TemporaryDirectory(prefix="remote-op-", dir=home / "tmp")
    temp_root = Path(temp.name)
    ensure_private_directory(temp_root)
    replacements: dict[str, str] = {}
    total = 0
    try:
        for index, row in enumerate(uploads):
            if not isinstance(row, dict):
                raise RuntimeError("remote_upload_manifest_invalid")
            token = str(row.get("token") or "")
            name = Path(str(row.get("name") or f"upload-{index}")).name
            sha = str(row.get("sha256") or "")
            size = int(row.get("size") or 0)
            if not token.startswith("__LLM_WIKI_UPLOAD_") or size < 0 or len(sha) != 64:
                raise RuntimeError("remote_upload_manifest_invalid")
            total += size
            if total > MAX_UPLOAD_BYTES:
                raise RuntimeError("remote_upload_too_large")
            remaining = size
            chunks: list[bytes] = []
            while remaining:
                chunk = stream.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise RuntimeError("remote_upload_truncated")
                chunks.append(chunk)
                remaining -= len(chunk)
            payload = b"".join(chunks)
            if hashlib.sha256(payload).hexdigest() != sha:
                raise RuntimeError("remote_upload_hash_mismatch")
            target = temp_root / f"{index:02d}-{name}"
            from .private_fs import write_private_bytes

            write_private_bytes(target, payload)
            replacements[token] = str(target)
        trailing = stream.read(1)
        if trailing:
            raise RuntimeError("remote_upload_trailing_bytes")
        return [replacements.get(item, item) for item in args], temp
    except Exception:
        temp.cleanup()
        raise


def _run_core(home: Path, request: dict, stream: BinaryIO) -> dict:
    store_id = _validate_store_id(request.get("store_id"))
    _, root = _require_ready_store(home, store_id)
    module_name = str(request.get("module") or "")
    raw_args = request.get("args")
    if not isinstance(raw_args, list) or any(not isinstance(item, str) for item in raw_args):
        raise RuntimeError("remote_core_args_invalid")
    args = [str(item) for item in raw_args]
    if not _allowed_core_invocation(module_name, args):
        raise RuntimeError("remote_core_operation_not_allowed")
    args, temp = _materialize_uploads(home, request, stream, args)
    try:
        with _store_lock(home, store_id):
            proc = subprocess.run(
                [sys.executable, "-m", module_name, "--root", str(root), *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=90,
                check=False,
            )
        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")
        if proc.returncode != 0:
            return {
                "ok": False,
                "error": "remote_core_failed",
                "returncode": proc.returncode,
                "stdout": stdout[-16_384:],
                "stderr": stderr[-16_384:],
            }
        return {"ok": True, "stdout": stdout, "stderr": stderr[-16_384:]}
    finally:
        if temp is not None:
            temp.cleanup()


def _hk_integrity(record: dict) -> str:
    payload = json.dumps(
        [
            record["format"],
            record["id"],
            record["title"],
            record["statement"],
            record["reasoning"],
            record["sourceIds"],
            record["supersedesKnowledgeId"],
            record["authorship"],
            record["createdAt"],
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hk_rows(root: Path) -> list[dict]:
    directory = root / "human-knowledge"
    if not directory.exists():
        return []
    rows: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise RuntimeError("remote_human_knowledge_corrupt") from exc
        required = {"format", "id", "title", "statement", "reasoning", "sourceIds", "supersedesKnowledgeId", "authorship", "createdAt", "integritySha256"}
        if not isinstance(row, dict) or set(row) != required or row.get("format") != HK_FORMAT or row.get("authorship") != "user_confirmed":
            raise RuntimeError("remote_human_knowledge_corrupt")
        if row.get("integritySha256") != _hk_integrity(row):
            raise RuntimeError("remote_human_knowledge_corrupt")
        rows.append(row)
    ids = {row["id"] for row in rows}
    if len(ids) != len(rows):
        raise RuntimeError("remote_human_knowledge_corrupt")
    successors: dict[str, list[str]] = {}
    for row in rows:
        previous = str(row.get("supersedesKnowledgeId") or "")
        if not previous:
            continue
        if previous not in ids or previous == row["id"]:
            raise RuntimeError("remote_human_knowledge_corrupt")
        successors.setdefault(previous, []).append(row["id"])
    if any(len(value) > 1 for value in successors.values()):
        raise RuntimeError("remote_human_knowledge_corrupt")
    return rows


def _hk_current(rows: list[dict]) -> list[dict]:
    superseded = {str(row.get("supersedesKnowledgeId") or "") for row in rows if row.get("supersedesKnowledgeId")}
    return [row for row in rows if row["id"] not in superseded]


def _save_human_knowledge(home: Path, request: dict) -> dict:
    store_id = _validate_store_id(request.get("store_id"))
    _, root = _require_ready_store(home, store_id)
    title = str(request.get("title") or "").strip()
    statement = str(request.get("statement") or "").strip()
    reasoning = str(request.get("reasoning") or "").strip()
    supersedes = str(request.get("supersedes_knowledge_id") or "").strip()
    source_ids_raw = request.get("source_ids") or []
    if not title or len(title) > 240 or not statement or len(statement) > 1800 or len(reasoning) > 1600 or len(statement) + len(reasoning) > 3400:
        raise RuntimeError("remote_human_knowledge_input_invalid")
    if not isinstance(source_ids_raw, list) or len(source_ids_raw) > 12:
        raise RuntimeError("remote_human_knowledge_input_invalid")
    source_ids = [str(value) for value in source_ids_raw]
    if any(not SOURCE_ID_RE.fullmatch(value) for value in source_ids):
        raise RuntimeError("remote_human_knowledge_input_invalid")
    if supersedes and not HK_ID_RE.fullmatch(supersedes):
        raise RuntimeError("remote_human_knowledge_input_invalid")

    with _store_lock(home, store_id):
        events = history(root)
        known_sources = {str(row.get("source_id")) for row in events if row.get("event") == "ingest"}
        if any(source_id not in known_sources for source_id in source_ids):
            raise RuntimeError("remote_human_knowledge_source_missing")
        rows = _hk_rows(root)
        current = {row["id"]: row for row in _hk_current(rows)}
        if supersedes and supersedes not in current:
            raise RuntimeError("remote_human_knowledge_supersedes_not_current")

        record = {
            "format": HK_FORMAT,
            "id": f"hk-{int(time.time() * 1000)}-{secrets.token_hex(5)}",
            "title": title,
            "statement": statement,
            "reasoning": reasoning,
            "sourceIds": source_ids,
            "supersedesKnowledgeId": supersedes,
            "authorship": "user_confirmed",
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "integritySha256": "",
        }
        record["integritySha256"] = _hk_integrity(record)
        directory = root / "human-knowledge"
        ensure_private_directory(directory)
        markdown_lines = [
            f"# {record['title']}",
            "> **HUMAN KNOWLEDGE — USER CONFIRMED**",
            "> This record represents wording the user explicitly confirmed for durable personal knowledge. It is not raw external evidence.",
        ]
        if supersedes:
            markdown_lines.append(f"> Replaces prior Human Knowledge: `{supersedes}`")
        markdown_lines.extend(
            [
                "## Current statement",
                record["statement"],
                "## Why / reasoning",
                record["reasoning"] or "No separate reasoning was recorded.",
                "## Supporting LLM Wiki sources",
            ]
        )
        markdown_lines.extend([f"- `{source_id}`" for source_id in source_ids] or ["- None recorded."])
        write_private_text(directory / f"{record['id']}.md", "\n".join(markdown_lines) + "\n")
        write_private_text(directory / f"{record['id']}.json", json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return record


def dispatch(request: dict, stream: BinaryIO) -> None:
    home = _authority_home()
    op = str(request.get("op") or "")
    if op == "health":
        _json_response(
            {
                "ok": True,
                "protocol": HELPER_PROTOCOL,
                "platform": sys.platform,
                "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            }
        )
        return
    if op == "list_stores":
        catalog = _read_catalog(home)
        _json_response({"ok": True, "stores": [dict(row) for row in catalog["stores"] if row.get("bootstrap_complete") is True]})
        return
    if op == "create_store":
        row = _create_store(home, request)
        _json_response({"ok": True, "store": row})
        return
    if op == "bootstrap_store":
        store_id = _validate_store_id(request.get("store_id"))
        catalog = _read_catalog(home)
        row = _find_store(catalog, store_id)
        if row.get("bootstrap_complete") is True:
            raise RuntimeError("remote_store_already_initialized")
        with _store_lock(home, store_id):
            manifest = read_snapshot(stream, _store_root(home, store_id), preserve_host_local=False)
            _mark_bootstrap_complete(home, store_id)
        _json_response({"ok": True, "snapshot_id": manifest["snapshot_id"]})
        return
    if op == "snapshot_export":
        store_id = _validate_store_id(request.get("store_id"))
        _, root = _require_ready_store(home, store_id)
        with _store_lock(home, store_id):
            write_snapshot(root, sys.stdout.buffer)
        return
    if op == "run_core":
        _json_response(_run_core(home, request, stream))
        return
    if op == "save_human_knowledge":
        record = _save_human_knowledge(home, request)
        _json_response({"ok": True, "record": record})
        return
    raise RuntimeError("remote_operation_not_allowed")


def main() -> int:
    try:
        request = _read_request(sys.stdin.buffer)
        dispatch(request, sys.stdin.buffer)
        return 0
    except (RuntimeError, SnapshotError, OSError, ValueError, subprocess.SubprocessError) as exc:
        try:
            _json_response({"ok": False, "error": str(exc)[:500]})
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
