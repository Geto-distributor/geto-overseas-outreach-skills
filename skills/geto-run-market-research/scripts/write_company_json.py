#!/usr/bin/env python3
"""Validate and atomically replace one company.json."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from research_bundle import format_result, load_json, validate_company


def atomic_write(destination: Path, value: object) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_json")
    parser.add_argument("destination")
    args = parser.parse_args()
    source = Path(args.source_json).expanduser().resolve()
    destination = Path(args.destination).expanduser().resolve()
    value = load_json(source)
    errors, warnings, infos = validate_company(value)
    result = {"source": str(source), "destination": str(destination), **format_result(errors, warnings, infos)}
    if errors:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    atomic_write(destination, value)
    result["written"] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
