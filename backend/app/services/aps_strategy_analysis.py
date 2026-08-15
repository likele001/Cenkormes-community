"""APS 策略分析（规则 + 可选 LLM）"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.planning_optimizer import optimize_plan_schedule
from app.services.production_forecast import build_plan_forecast


def analyze_aps_strategies(db: Session, tenant_id: int, plan_id: int, user_id: int = 0) -> dict:
    forecast = build_plan_forecast(db, tenant_id, plan_id)
    optimizer = optimize_plan_schedule(db, tenant_id, plan_id)

    strategies = []

    s1 = {
        "key": "due_first",
        "title": "优先交期（OR-Tools 倒排）",
        "score": 85 if forecast.get("due_risk") != "red" else 55,
        "pros": ["贴近订单交期", "适合急单"],
        "cons": ["可能均衡性一般"],
    }
    if optimizer.get("ok"):
        s1["suggest_start"] = optimizer.get("suggest_start_date")
        s1["suggest_end"] = optimizer.get("suggest_end_date")
        s1["solver"] = optimizer.get("solver")
    strategies.append(s1)

    s2 = {
        "key": "balance_load",
        "title": "均衡负荷派工",
        "score": 80,
        "pros": ["员工负荷更均匀", "适合计件厂"],
        "cons": ["交期可能略松"],
    }
    strategies.append(s2)

    s3 = {
        "key": "allow_shortage",
        "title": "允许缺料先下发",
        "score": 40 if forecast.get("shortage_count", 0) > 0 else 20,
        "pros": ["先占产能、先派工"],
        "cons": ["缺料停工风险"],
        "enabled": forecast.get("shortage_count", 0) > 0,
    }
    strategies.append(s3)

    recommended = max(strategies, key=lambda x: x["score"])["key"]

    llm_summary = None
    if user_id:
        try:
            from app.services.ai.client import chat_completion

            llm_summary, _, _ = chat_completion(
                db,
                tenant_id=tenant_id,
                messages=[
                    {
                        "role": "user",
                        "content": f"对比以下排产策略并推荐一种，200字内：{strategies}；预测：{forecast}",
                    }
                ],
                max_tokens=400,
            )
        except Exception:
            llm_summary = None

    return {
        "plan_id": plan_id,
        "forecast": forecast,
        "optimizer": optimizer,
        "strategies": strategies,
        "recommended": recommended,
        "llm_summary": llm_summary,
    }
