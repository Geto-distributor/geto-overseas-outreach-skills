#!/usr/bin/env python3
"""Initialize a country ResearchBundle and optionally one company workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_bundle import empty_company


ALLOWED_MODULES = {
    "Info", "Financial", "ProductsAndServices", "Projects", "NewsAndSocialMedia",
    "CustomsTransactions", "LawsuitsAndCompliance", "Inquiries", "RisksAndAssessment",
    "Additional",
}


def progress_template(country: str) -> str:
    return f"""# {country} GETO 市场调研进度

## 范围
- 国家：{country}
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
    parser.add_argument("--country-root", required=True)
    parser.add_argument("--company-name")
    parser.add_argument("--country", default="")
    parser.add_argument("--module", action="append", default=[])
    args = parser.parse_args()

    country_root = Path(args.country_root).expanduser().resolve()
    country_root.mkdir(parents=True, exist_ok=True)
    (country_root / "companies").mkdir(exist_ok=True)
    progress = country_root / "progress.md"
    if not progress.exists():
        progress.write_text(progress_template(args.country or country_root.name), encoding="utf-8")

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
                json.dumps(empty_company(args.company_name, args.country), ensure_ascii=False, indent=2) + "\n",
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
