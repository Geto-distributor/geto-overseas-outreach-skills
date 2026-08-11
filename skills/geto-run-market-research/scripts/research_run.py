#!/usr/bin/env python3
"""Create and validate local GETO research-run checkpoints.

This utility stores orchestration state only. It never stores API keys and never
calls Provider or OmniX APIs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


STAGES = ("intake", "resolve", "discovery", "evidence", "decision", "submission")
STAGE_STATUSES = {"pending", "in_progress", "completed", "blocked", "skipped"}
PROVIDER_STATUSES = {
    "available",
    "skill_unavailable",
    "not_configured",
    "unauthenticated",
    "forbidden",
    "rate_limited",
    "provider_session_expired",
    "upstream_unavailable",
    "partial",
    "failed",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("research-run state must be a JSON object")
    return value


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def validate(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for required in ("researchRunKey", "marketCode", "scopeCode", "asOf", "executionMode", "resultMode"):
        if not value.get(required):
            errors.append(f"missing {required}")
    if value.get("executionMode") not in {"quick", "adversarial"}:
        errors.append("executionMode must be quick or adversarial")
    if value.get("resultMode") not in {"full", "sample"}:
        errors.append("resultMode must be full or sample")
    if value.get("resultMode") == "sample" and not value.get("sampleBoundary"):
        errors.append("sample result requires sampleBoundary")
    checkpoints = value.get("checkpoints")
    if not isinstance(checkpoints, dict):
        errors.append("checkpoints must be an object")
    else:
        unknown = set(checkpoints) - set(STAGES)
        if unknown:
            errors.append(f"unknown checkpoint stages: {sorted(unknown)}")
        for stage in STAGES:
            item = checkpoints.get(stage)
            if not isinstance(item, dict):
                errors.append(f"missing checkpoint {stage}")
            elif item.get("status") not in STAGE_STATUSES:
                errors.append(f"invalid status for checkpoint {stage}")
    providers = value.get("providerStatuses", {})
    if not isinstance(providers, dict):
        errors.append("providerStatuses must be an object")
    else:
        for provider, status in providers.items():
            if status not in PROVIDER_STATUSES:
                errors.append(f"invalid provider status for {provider}: {status}")
    serialized = json.dumps(value, ensure_ascii=False).lower()
    for marker in ("tw_", "omx_test_", "omx_live_", "authorization: bearer"):
        if marker in serialized:
            errors.append(f"state appears to contain a credential marker: {marker}")
    return errors


def command_init(args: argparse.Namespace) -> int:
    as_of = args.as_of or date.today().isoformat()
    token = args.run_token or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    state = {
        "researchRunKey": f"{args.market.lower()}:{args.scope}:{as_of}:{token}",
        "marketCode": args.market.upper(),
        "scopeCode": args.scope,
        "asOf": as_of,
        "executionMode": args.mode,
        "resultMode": args.result_mode,
        "sampleBoundary": args.sample_boundary,
        "publicationStatus": "private_draft",
        "deliveryStatus": "pending",
        "providerStatuses": {},
        "checkpoints": {
            stage: {
                "status": "in_progress" if stage == "intake" else "pending",
                "startedOn": now() if stage == "intake" else None,
                "completedOn": None,
                "inputs": [],
                "outputs": [],
                "gapCodes": [],
            }
            for stage in STAGES
        },
        "createdOn": now(),
        "modifiedOn": now(),
    }
    errors = validate(state)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    atomic_write(Path(args.output), state)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    state = read_json(Path(args.path))
    errors = validate(state)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    print("OK")
    return 0


def command_summary(args: argparse.Namespace) -> int:
    state = read_json(Path(args.path))
    errors = validate(state)
    summary = {
        "researchRunKey": state.get("researchRunKey"),
        "deliveryStatus": state.get("deliveryStatus"),
        "providerStatuses": state.get("providerStatuses", {}),
        "checkpoints": {k: v.get("status") for k, v in state.get("checkpoints", {}).items()},
        "valid": not errors,
        "errors": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


def command_checkpoint(args: argparse.Namespace) -> int:
    path = Path(args.path)
    state = read_json(path)
    item = state.get("checkpoints", {}).get(args.stage)
    if not isinstance(item, dict):
        raise ValueError(f"unknown checkpoint: {args.stage}")
    item["status"] = args.status
    if args.status == "in_progress" and not item.get("startedOn"):
        item["startedOn"] = now()
    if args.status in {"completed", "skipped"}:
        item["startedOn"] = item.get("startedOn") or now()
        item["completedOn"] = now()
    if args.gap_code:
        item["gapCodes"] = list(dict.fromkeys([*item.get("gapCodes", []), *args.gap_code]))
    state["modifiedOn"] = now()
    errors = validate(state)
    if errors:
        raise ValueError("; ".join(errors))
    atomic_write(path, state)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def command_provider(args: argparse.Namespace) -> int:
    path = Path(args.path)
    state = read_json(path)
    state.setdefault("providerStatuses", {})[args.provider] = args.status
    state["modifiedOn"] = now()
    errors = validate(state)
    if errors:
        raise ValueError("; ".join(errors))
    atomic_write(path, state)
    print(json.dumps(state["providerStatuses"], ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a research-run checkpoint file")
    init.add_argument("--output", required=True)
    init.add_argument("--market", required=True)
    init.add_argument("--scope", required=True)
    init.add_argument("--mode", choices=("quick", "adversarial"), default="quick")
    init.add_argument("--result-mode", choices=("full", "sample"), default="full")
    init.add_argument("--sample-boundary")
    init.add_argument("--as-of")
    init.add_argument("--run-token")
    init.set_defaults(func=command_init)
    check = sub.add_parser("validate", help="validate a research-run checkpoint file")
    check.add_argument("path")
    check.set_defaults(func=command_validate)
    summary = sub.add_parser("summary", help="print a compact checkpoint summary")
    summary.add_argument("path")
    summary.set_defaults(func=command_summary)
    checkpoint = sub.add_parser("checkpoint", help="update one checkpoint status")
    checkpoint.add_argument("path")
    checkpoint.add_argument("stage", choices=STAGES)
    checkpoint.add_argument("status", choices=sorted(STAGE_STATUSES))
    checkpoint.add_argument("--gap-code", action="append")
    checkpoint.set_defaults(func=command_checkpoint)
    provider = sub.add_parser("provider", help="record one Provider capability status")
    provider.add_argument("path")
    provider.add_argument("provider")
    provider.add_argument("status", choices=sorted(PROVIDER_STATUSES))
    provider.set_defaults(func=command_provider)
    return root


if __name__ == "__main__":
    try:
        arguments = parser().parse_args()
        raise SystemExit(arguments.func(arguments))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
