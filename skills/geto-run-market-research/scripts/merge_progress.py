#!/usr/bin/env python3
"""Merge one task-owned block into progress.md under an exclusive file lock."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


REQUIRED = {"sectionName", "title", "status", "did", "artifacts", "decision", "gaps", "next"}


def render(payload: dict[str, Any]) -> str:
    missing = sorted(REQUIRED - set(payload))
    if missing:
        raise ValueError(f"missing progress fields: {', '.join(missing)}")
    section = str(payload["sectionName"])
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", section):
        raise ValueError("sectionName must use lowercase letters, digits, hyphen, or underscore")

    def lines(value: Any) -> str:
        values = value if isinstance(value, list) else [value]
        clean = [str(item).strip() for item in values if str(item).strip()]
        return "；".join(clean) if clean else "无"

    return "\n".join([
        f"<!-- task:{section}:start -->",
        f"### {payload['title']}",
        f"- status: {payload['status']}",
        f"- did: {lines(payload['did'])}",
        f"- artifacts: {lines(payload['artifacts'])}",
        f"- decision: {lines(payload['decision'])}",
        f"- gaps: {lines(payload['gaps'])}",
        f"- next: {lines(payload['next'])}",
        f"<!-- task:{section}:end -->",
    ])


def atomic_write(path: Path, text: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def merge(progress: Path, payload: dict[str, Any]) -> None:
    progress.parent.mkdir(parents=True, exist_ok=True)
    lock_path = progress.with_name(f".{progress.name}.lock")
    block = render(payload)
    section = re.escape(str(payload["sectionName"]))
    pattern = re.compile(rf"<!-- task:{section}:start -->.*?<!-- task:{section}:end -->", re.DOTALL)
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        current = progress.read_text(encoding="utf-8") if progress.exists() else "# GETO 市场调研进度\n"
        updated = pattern.sub(block, current) if pattern.search(current) else current.rstrip() + "\n\n" + block + "\n"
        atomic_write(progress, updated)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("progress_md")
    parser.add_argument("payload_json")
    args = parser.parse_args()
    progress = Path(args.progress_md).expanduser().resolve()
    payload = json.loads(Path(args.payload_json).expanduser().read_text(encoding="utf-8"))
    merge(progress, payload)
    print(json.dumps({"progress": str(progress), "sectionName": payload["sectionName"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
