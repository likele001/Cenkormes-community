"""
电子组装行业包 — 主实现

继承 IndustryPack 基类，实现种子数据初始化逻辑。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.industries.base import IndustryPack, IndustryPackMeta
from app.industries.electronics.seed_data import get_all_seed_data


class ElectronicsIndustryPack(IndustryPack):
    """电子组装行业包"""

    def meta(self) -> IndustryPackMeta:
        return IndustryPackMeta(
            code="electronics",
            name="电子组装",
            name_en="Electronics Assembly",
            description="适用于SMT贴片、DIP插件、测试组装等电子制造企业，支持SN追溯、防呆、ESD管控",
            version="1.0.0",
            author="LightMES",
            icon="cpu",
            features=[
                "SN码/IMEI全追溯",
                "SMT首件/巡检/AOI三级质检",
                "ICT/FCT测试管理",
                "BOM精确到颗",
                "防呆防错（极性/方向/位置）",
                "ESD防静电管控",
                "老化测试管理",
                "直通率(FPY)统计",
            ],
            dependencies=["production", "quality", "equipment"],
        )

    def default_settings(self) -> dict[str, Any]:
        return {
            "production.report.default_mode": "unit",
            "industry.electronics.sn_trace": True,
            "industry.electronics.bom_precision": "component",
            "industry.electronics.fai_required": True,
            "industry.electronics.aoi_required": True,
            "industry.electronics.esd_control": True,
            "industry.electronics.fpy_target": 98.5,
        }

    def seed_data(self, db: Session, tenant_id: int) -> dict[str, Any]:
        """
        初始化电子组装行业种子数据
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
                        industry_code="electronics",
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
                    industry_code="electronics",
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
                        industry_code="electronics",
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
                    industry_code="electronics",
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
        """租户启动电子组装行业包时，写入默认设置"""
        from app.crud.tenant_setting import upsert_setting

        for key, value in self.default_settings().items():
            upsert_setting(db, tenant_id, key, value)
