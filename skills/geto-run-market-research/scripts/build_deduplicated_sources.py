#!/usr/bin/env python3
"""Build Sources/sources.md from embedded Evidence in company.json."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from research_bundle import all_evidence, canonical_url, load_json


def build(company_json: Path) -> Path:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for evidence in all_evidence(load_json(company_json)):
        url = canonical_url(str(evidence.get("sourceUrl") or ""))
        locator = str(evidence.get("locator") or "").strip()
        grouped[(url, locator)].append(evidence)

    lines = ["# Sources", "", "由 company.json 内嵌 Evidence 派生；company.json 是权威结构化来源。", ""]
    for number, ((url, locator), items) in enumerate(sorted(grouped.items()), 1):
        first = items[0]
        title = str(first.get("sourceTitle") or url or "Customer document")
        lines.append(f"## {number}. {title}")
        lines.append("")
        if url:
            lines.append(f"- URL: {url}")
        if locator:
            lines.append(f"- Locator: {locator}")
        publishers = sorted({str(item.get("publisher") or "") for item in items if item.get("publisher")})
        relations = sorted({str(item.get("relation") or "") for item in items if item.get("relation")})
        retrieved = sorted({str(item.get("retrievedOn") or "") for item in items if item.get("retrievedOn")})
        if publishers:
            lines.append(f"- Publisher: {', '.join(publishers)}")
        if relations:
            lines.append(f"- Relations: {', '.join(relations)}")
        if retrieved:
            lines.append(f"- Retrieved: {', '.join(retrieved)}")
        lines.append(f"- Evidence occurrences: {len(items)}")
        lines.append("")

    output = company_json.parent / "Sources" / "sources.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("company_json")
    args = parser.parse_args()
    output = build(Path(args.company_json).expanduser().resolve())
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
