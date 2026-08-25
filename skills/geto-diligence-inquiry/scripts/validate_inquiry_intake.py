#!/usr/bin/env python3
"""Validate the minimum inputs and independent identity discovery for one inquiry."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
WEB_STATUSES = {"found", "no_result", "not_queried", "failed"}
TRADEWIND_STATUSES = {
    "found", "no_result", "not_configured", "upstream_unavailable", "failed", "not_queried",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _has_requirement(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if not isinstance(value, dict):
        return False
    keys = ("requestedProduct", "technicalRequirements", "projectScenario", "useCase", "projectName")
    return any(_has_requirement(value.get(key)) for key in keys)


def _valid_observation(value: Any, allowed_statuses: set[str], label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{label} must be an object"]
    status = value.get("status")
    if status not in allowed_statuses:
        errors.append(f"{label}.status has an invalid value")
    if status == "found":
        if value.get("strongIdentityMatch") is not True:
            errors.append(f"{label}.strongIdentityMatch must be true when status=found")
        if not _text(value.get("matchedEntity")):
            errors.append(f"{label}.matchedEntity is required when status=found")
        if not isinstance(value.get("evidence"), list) or not value.get("evidence"):
            errors.append(f"{label}.evidence must contain at least one observation")
        else:
            for index, item in enumerate(value["evidence"]):
                if not isinstance(item, dict):
                    errors.append(f"{label}.evidence[{index}] must be an object")
                    continue
                for field in ("sourceTitle", "sourceType", "retrievedOn"):
                    if not _text(item.get(field)):
                        errors.append(f"{label}.evidence[{index}].{field} is required")
    return errors


def validate_intake(value: Any) -> dict[str, Any]:
    errors: list[str] = []
    missing: list[str] = []
    actions: list[str] = []
    if not isinstance(value, dict):
        return {
            "gateStatus": "blocked_missing_intake",
            "errors": ["intake manifest must be an object"],
            "missingFields": [], "nextActions": ["Provide one inquiry intake manifest."],
        }

    if len(_text(value.get("companyName"))) < 2:
        missing.append("companyName")
    if not _has_requirement(value.get("requirement")):
        missing.append("requirement")
    if not EMAIL_RE.fullmatch(_text(value.get("email"))):
        missing.append("email")
    errors.extend(_valid_observation(value.get("webSearch"), WEB_STATUSES, "webSearch"))
    errors.extend(_valid_observation(value.get("tradewind"), TRADEWIND_STATUSES, "tradewind"))

    if missing:
        actions.append("补齐公司名、至少一项可描述的产品/技术/项目需求和可回复邮箱。")
    web = value.get("webSearch") if isinstance(value.get("webSearch"), dict) else {}
    trade = value.get("tradewind") if isinstance(value.get("tradewind"), dict) else {}
    web_status = web.get("status")
    trade_status = trade.get("status")
    if web_status in {"no_result", "not_queried", "failed"} or (
        web_status == "found" and web.get("strongIdentityMatch") is not True
    ):
        actions.append("补充法定名、官网域名、注册号或项目文件，并完成 Web 主体核验。")
    if trade_status in {"no_result", "not_queried"} or (
        trade_status == "found" and trade.get("strongIdentityMatch") is not True
    ):
        actions.append("使用 TradeWind 精确公司查询重试，并核对 queryCountry 与 observedCountry。")
    if trade_status in {"not_configured", "upstream_unavailable", "failed"}:
        actions.append("先配置或恢复 TradeWind 查询能力；工具故障不能记为主体不存在。")

    if missing:
        status = "blocked_missing_intake"
    elif web_status in {"not_queried", "failed"} or trade_status in {"not_queried", "failed", "not_configured", "upstream_unavailable"}:
        status = "blocked_provider"
    elif web_status != "found" or trade_status != "found" or not web.get("strongIdentityMatch") or not trade.get("strongIdentityMatch"):
        status = "blocked_identity_discovery"
    else:
        status = "ready_for_diligence"
    return {
        "gateStatus": status,
        "companyName": _text(value.get("companyName")),
        "inquiryRef": _text(value.get("inquiryRef")),
        "missingFields": missing,
        "errors": sorted(set(errors)),
        "nextActions": sorted(set(actions)),
        "discovery": {
            "webSearch": web_status,
            "tradewind": trade_status,
            "webStrongIdentityMatch": web.get("strongIdentityMatch") is True,
            "tradewindStrongIdentityMatch": trade.get("strongIdentityMatch") is True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intake_json")
    parser.add_argument("--output")
    args = parser.parse_args()
    path = Path(args.intake_json).expanduser().resolve()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        result = {"gateStatus": "blocked_missing_intake", "errors": [str(error)], "missingFields": [], "nextActions": []}
    else:
        result = validate_intake(value)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result.get("gateStatus") == "ready_for_diligence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
