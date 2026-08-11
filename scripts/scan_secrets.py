#!/usr/bin/env python3
"""Fail when repository files contain likely credentials or private artifacts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
SKIP_PARTS = {".git", "__pycache__", ".venv", "venv"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".pyc"}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".xlsx", ".xls", ".p12", ".pfx", ".pem", ".key"}
FORBIDDEN_NAMES = {".env", "cookies.json", "credentials.json", "secrets.json"}
PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github-token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "tradewind-key": re.compile(r"tw_[A-Za-z0-9_-]{16,}"),
    "omnix-key": re.compile(r"omx_(?:test|live)_[A-Za-z0-9_-]{16,}"),
    "slack-token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{16,}"),
    "google-api-key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "authorization-bearer": re.compile(r"Authorization\s*[:=]\s*[\"']?Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE),
}


def main() -> int:
    findings: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.resolve() == SELF or SKIP_PARTS.intersection(path.parts):
            continue
        relative = path.relative_to(ROOT)
        lower_name = path.name.lower()
        if lower_name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"forbidden artifact: {relative}")
            continue
        if path.suffix.lower() in BINARY_SUFFIXES or path.stat().st_size > 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"unexpected binary file: {relative}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(f"{label}: {relative}:{line_number}")
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1
    print("Credential and private-artifact scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
