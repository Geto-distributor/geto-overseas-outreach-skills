#!/usr/bin/env python3
"""Initialize a country ResearchBundle and optionally one company workspace."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from research_bundle import empty_company


ALLOWED_MODULES = {
    "Info", "Financial", "ProductsAndServices", "Projects", "NewsAndSocialMedia",
    "CustomsTransactions", "LawsuitsAndCompliance", "Inquiries", "RisksAndAssessment",
    "Additional",
}


def progress_template(country: str, country_code: str) -> str:
    return f"""# {country} GETO 市场调研进度

## 范围
- 国家：{country}
- 国家代码：{country_code}
- 产品：待填写
- 语言：待填写
- 截止日：待填写
- 结果范围：待填写

## 检查点
| 阶段 | 状态 | 成果路径 | 缺口 | 下一步 |
| --- | --- | --- | --- | --- |
| intake | pending |  |  |  |
| discovery | pending |  |  |  |
| arbitration | pending |  |  |  |
| diligence | pending |  |  |  |
| decision | pending |  |  |  |
| validation | pending |  |  |  |
| optional_upload | pending |  |  |  |
| complete | pending |  |  |  |

## 任务
| 任务 | 状态 | 做了什么 | 成果路径 | 接受/拒绝理由 | 缺口 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- |

## 公司仲裁
| 公司 | lead | competitor | 目录 | 理由/冲突 |
| --- | --- | --- | --- | --- |

## 上传
- uploadStatus: not_requested
- detailRoute:
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    location = parser.add_mutually_exclusive_group(required=True)
    location.add_argument("--workspace-root")
    location.add_argument("--country-root", help=argparse.SUPPRESS)
    parser.add_argument("--country-code")
    parser.add_argument("--country-name")
    parser.add_argument("--company-name")
    parser.add_argument("--module", action="append", default=[])
    args = parser.parse_args()

    if args.workspace_root:
        country_code = str(args.country_code or "").upper()
        country_name = str(args.country_name or "").strip()
        if not re.fullmatch(r"[A-Z]{2}", country_code):
            raise SystemExit("country-code must be ISO 3166-1 alpha-2")
        slug = re.sub(r"[^A-Za-z0-9]+", "-", country_name).strip("-")
        if not slug:
            raise SystemExit("country-name must contain a stable Latin display name")
        country_root = Path(args.workspace_root).expanduser().resolve() / f"{country_code}-{slug}"
    else:
        country_root = Path(args.country_root).expanduser().resolve()
        match = re.fullmatch(r"([A-Z]{2})-(.+)", country_root.name)
        if not match:
            raise SystemExit("country-root directory must use <ISO2>-<English-Display-Name>")
        country_code = args.country_code or match.group(1)
        country_name = args.country_name or match.group(2).replace("-", " ")
    country_root.mkdir(parents=True, exist_ok=True)
    (country_root / "companies").mkdir(exist_ok=True)
    progress = country_root / "progress.md"
    if not progress.exists():
        progress.write_text(progress_template(country_name, country_code), encoding="utf-8")

    created = [str(progress), str(country_root / "companies")]
    if args.company_name:
        if Path(args.company_name).name != args.company_name or args.company_name in {".", ".."}:
            raise SystemExit("company-name must be a natural directory name without path separators")
        invalid = sorted(set(args.module) - ALLOWED_MODULES)
        if invalid:
            raise SystemExit(f"unsupported module directories: {invalid}")
        company_dir = country_root / "companies" / args.company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        company_json = company_dir / "company.json"
        if not company_json.exists():
            company_json.write_text(
                json.dumps(empty_company(args.company_name, country_name, country_code), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        report = company_dir / "report.md"
        if not report.exists():
            report.write_text(f"# {args.company_name} 背调报告\n\n待补充。\n", encoding="utf-8")
        for module in args.module:
            (company_dir / module).mkdir(exist_ok=True)
        created.extend((str(company_json), str(report)))

    print(json.dumps({"countryRoot": str(country_root), "artifacts": created}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
