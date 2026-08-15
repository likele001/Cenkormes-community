"""
机加工行业包 — 主实现

继承 IndustryPack 基类，实现种子数据初始化逻辑。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.industries.base import IndustryPack, IndustryPackMeta
from app.industries.machining.seed_data import get_all_seed_data


class MachiningIndustryPack(IndustryPack):
    """机加工行业包"""

    def meta(self) -> IndustryPackMeta:
        return IndustryPackMeta(
            code="machining",
            name="机加工",
            name_en="Machining",
            description="适用于车铣磨钻等金属切削加工企业，支持工序流转、首件检验、刀具管理、设备联网",
            version="1.0.0",
            author="LightMES",
            icon="wrench",
            features=[
                "逐件报工与追溯",
                "首件/巡检/终检三级质检",
                "工序计件工资",
                "设备状态监控",
                "CNC程序管理",
                "刀具寿命管理",
                "SPC统计过程控制",
            ],
            dependencies=["production", "quality", "equipment"],
        )

    def default_settings(self) -> dict[str, Any]:
        return {
            "production.report.default_mode": "unit",
            "industry.machining.tool_management": True,
            "industry.machining.fai_required": True,
            "industry.machining.ipqc_interval": 30,
            "industry.machining.spc_enabled": False,
        }

    def seed_data(self, db: Session, tenant_id: int) -> dict[str, Any]:
        """
        初始化机加工行业种子数据
        幂等：已存在的数据会跳过
        """
        from app.models.process import Process
        from app.models.quality import InspectionTemplate, InspectionTemplateItem, DefectCode
        from app.models.dictionary import DictType, DictItem
        from sqlalchemy import select

        data = get_all_seed_data()
        result: dict[str, Any] = {
            "processes": 0,
            "inspection_templates": 0,
            "defect_codes": 0,
            "dictionaries": 0,
        }

        # 1. 工序模板
        for p in data["processes"]:
            exists = db.execute(
                select(Process).where(
                    Process.tenant_id == tenant_id,
                    Process.code == p["code"],
                )
            ).scalar_one_or_none()
            if not exists:
                db.add(
                    Process(
                        tenant_id=tenant_id,
                        industry_code="machining",
                        code=p["code"],
                        name=p["name"],
                        workshop=p["workshop"],
                        std_minutes=p["std_minutes"],
                        is_active=True,
                    )
                )
                result["processes"] += 1

        db.flush()

        # 2. 质检模板
        for t in data["inspection_templates"]:
            exists = db.execute(
                select(InspectionTemplate).where(
                    InspectionTemplate.tenant_id == tenant_id,
                    InspectionTemplate.code == t["code"],
                )
            ).scalar_one_or_none()
            if not exists:
                tpl = InspectionTemplate(
                    tenant_id=tenant_id,
                    industry_code="machining",
                    code=t["code"],
                    name=t["name"],
                    description=t["description"],
                    is_active=True,
                )
                db.add(tpl)
                db.flush()
                for item in t["items"]:
                    db.add(
                        InspectionTemplateItem(
                            template_id=tpl.id,
                            seq=item["seq"],
                            item_name=item["item_name"],
                            item_type=item["item_type"],
                            standard_value=item.get("standard_value", ""),
                            upper_limit=item.get("upper_limit", ""),
                            lower_limit=item.get("lower_limit", ""),
                            unit=item.get("unit", ""),
                            is_required=item.get("is_required", False),
                            remark=item.get("remark", ""),
                        )
                    )
                result["inspection_templates"] += 1

        db.flush()

        # 3. 缺陷代码
        for d in data["defect_codes"]:
            exists = db.execute(
                select(DefectCode).where(
                    DefectCode.tenant_id == tenant_id,
                    DefectCode.code == d["code"],
                )
            ).scalar_one_or_none()
            if not exists:
                db.add(
                    DefectCode(
                        tenant_id=tenant_id,
                        industry_code="machining",
                        code=d["code"],
                        name=d["name"],
                        severity=d["severity"],
                        description=d["description"],
                        is_active=True,
                    )
                )
                result["defect_codes"] += 1

        db.flush()

        # 4. 行业字典
        for dic in data["dictionaries"]:
            dt = db.execute(
                select(DictType).where(
                    DictType.tenant_id == tenant_id,
                    DictType.code == dic["type_code"],
                )
            ).scalar_one_or_none()
            if not dt:
                dt = DictType(
                    tenant_id=tenant_id,
                    industry_code="machining",
                    code=dic["type_code"],
                    name=dic["type_name"],
                    is_active=True,
                )
                db.add(dt)
                db.flush()
            for item in dic["items"]:
                exists = db.execute(
                    select(DictItem).where(
                        DictItem.dict_type_id == dt.id,
                        DictItem.value == item["value"],
                    )
                ).scalar_one_or_none()
                if not exists:
                    db.add(
                        DictItem(
                            dict_type_id=dt.id,
                            label=item["label"],
                            value=item["value"],
                            sort_order=item["sort"],
                            is_active=True,
                        )
                    )
                    result["dictionaries"] += 1

        db.commit()
        return result

    def on_enable(self, db: Session, tenant_id: int) -> None:
        """租户启动机加工行业包时，写入默认设置"""
        from app.crud.tenant_setting import upsert_setting

        for key, value in self.default_settings().items():
            upsert_setting(db, tenant_id, key, value)
