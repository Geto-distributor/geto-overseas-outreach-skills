#!/usr/bin/env python3
"""Route one inquiry into full, identity-gap, provider-gap, or partial-intake diligence."""

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
        if value.get("strongIdentityMatch") is True and not _text(value.get("matchedEntity")):
            errors.append(f"{label}.matchedEntity is required for a strong identity match")
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


def _normalized_entity(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", _text(value).casefold())


def _research_anchors(value: dict[str, Any]) -> list[str]:
    anchors: list[str] = []
    if len(_text(value.get("companyName"))) >= 2:
        anchors.append("companyName")
    for field in ("contactName", "website", "phone", "projectName"):
        if _text(value.get(field)):
            anchors.append(field)
    email = _text(value.get("email"))
    if EMAIL_RE.fullmatch(email):
        anchors.append("emailDomain")
    requirement = value.get("requirement")
    if _has_requirement(requirement):
        anchors.append("requirement")
    for label in ("webSearch", "tradewind"):
        observation = value.get(label)
        if not isinstance(observation, dict):
            continue
        if _text(observation.get("matchedEntity")):
            anchors.append(f"{label}.matchedEntity")
        if isinstance(observation.get("evidence"), list) and observation.get("evidence"):
            anchors.append(f"{label}.evidence")
    return sorted(set(anchors))


def validate_intake(value: Any) -> dict[str, Any]:
    errors: list[str] = []
    missing: list[str] = []
    actions: list[str] = []
    if not isinstance(value, dict):
        return {
            "gateStatus": "blocked_no_research_anchor",
            "errors": ["intake manifest must be an object"],
            "missingFields": [], "nextActions": ["Provide one inquiry intake manifest."],
            "researchAllowed": False,
        }

    if len(_text(value.get("companyName"))) < 2:
        missing.append("companyName")
    if not _has_requirement(value.get("requirement")):
        missing.append("requirement")
    if not EMAIL_RE.fullmatch(_text(value.get("email"))):
        missing.append("email")
    errors.extend(_valid_observation(value.get("webSearch"), WEB_STATUSES, "webSearch"))
    errors.extend(_valid_observation(value.get("tradewind"), TRADEWIND_STATUSES, "tradewind"))

    anchors = _research_anchors(value)
    if missing:
        actions.append("继续现有锚点调研，并向客户补齐公司名、需求和可回复邮箱中的缺失项。")
    web = value.get("webSearch") if isinstance(value.get("webSearch"), dict) else {}
    trade = value.get("tradewind") if isinstance(value.get("tradewind"), dict) else {}
    web_status = web.get("status")
    trade_status = trade.get("status")
    if web_status in {"no_result", "not_queried", "failed"} or (
        web_status == "found" and web.get("strongIdentityMatch") is not True
    ):
        actions.append("继续查登记、官网、域名历史、电话、地址、人员、项目和社媒，并补充法定名、注册号或项目文件。")
    if trade_status in {"no_result", "not_queried"} or (
        trade_status == "found" and trade.get("strongIdentityMatch") is not True
    ):
        actions.append("保留 TradeWind 查询边界，改查精确域名、法定名、展示名和历史别名，并逐条仲裁宽匹配候选。")
    if trade_status in {"not_configured", "upstream_unavailable", "failed"}:
        actions.append("在恢复 TradeWind 的同时继续 Web、登记、项目、社媒、地图目录和其他可用 Provider；工具故障不能记为主体不存在。")

    web_strong = web_status == "found" and web.get("strongIdentityMatch") is True
    trade_strong = trade_status == "found" and trade.get("strongIdentityMatch") is True
    same_entity = (
        web_strong and trade_strong
        and _normalized_entity(web.get("matchedEntity"))
        and _normalized_entity(web.get("matchedEntity")) == _normalized_entity(trade.get("matchedEntity"))
    )
    provider_gap = (
        web_status in {"not_queried", "failed"}
        or trade_status in {"not_queried", "failed", "not_configured", "upstream_unavailable"}
    )

    if not anchors:
        status = "blocked_no_research_anchor"
        research_mode = "awaiting_research_anchor"
    elif missing:
        status = "diligence_with_partial_intake"
        research_mode = "open_research_and_intake_recovery"
    elif provider_gap:
        status = "diligence_with_provider_gaps"
        research_mode = "open_research_with_alternative_sources"
    elif not same_entity:
        status = "diligence_with_identity_gaps"
        research_mode = "identity_resolution_and_full_diligence"
    else:
        status = "ready_for_diligence"
        research_mode = "full_diligence"
    return {
        "gateStatus": status,
        "companyName": _text(value.get("companyName")),
        "inquiryRef": _text(value.get("inquiryRef")),
        "missingFields": missing,
        "errors": sorted(set(errors)),
        "nextActions": sorted(set(actions)),
        "researchAllowed": status != "blocked_no_research_anchor",
        "researchMode": research_mode,
        "researchAnchors": anchors,
        "scoringPolicy": (
            "not_available_without_research_anchor"
            if status == "blocked_no_research_anchor"
            else "evidence_only_with_identity_gaps_and_hard_blocks"
        ),
        "discovery": {
            "webSearch": web_status,
            "tradewind": trade_status,
            "webStrongIdentityMatch": web.get("strongIdentityMatch") is True,
            "tradewindStrongIdentityMatch": trade.get("strongIdentityMatch") is True,
            "sameStrongMatchedEntity": bool(same_entity),
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
        result = {
            "gateStatus": "blocked_no_research_anchor", "errors": [str(error)],
            "missingFields": [], "nextActions": [], "researchAllowed": False,
        }
    else:
        result = validate_intake(value)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result.get("researchAllowed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
