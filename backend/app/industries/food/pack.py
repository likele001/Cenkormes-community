"""
食品加工行业包 — 主实现

特性：
- 批次管理 + 双向追溯（前向/后向）
- 保质期/效期管理 + 先进先出
- HACCP关键控制点(CCP)监控
- 冷链温度监控
- 配方管理（BOM精确到原料）
- 称重计量 + 净含量控制
- 微生物/感官/理化检验
- 食品添加剂合规校验
- 过敏原标注
- 多认证体系（SC/HACCP/ISO22000/BRC/有机等）
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.industries.base import IndustryPack, IndustryPackMeta
from app.industries.food.seed_data import get_all_seed_data


class FoodIndustryPack(IndustryPack):
    """食品加工行业包"""

    def meta(self) -> IndustryPackMeta:
        return IndustryPackMeta(
            code="food",
            name="食品加工",
            name_en="Food Processing",
            description=(
                "适用于食品厂、饮料厂、烘焙厂、冷冻食品厂等食品制造企业。"
                "支持批次双向追溯、HACCP关键控制点、冷链监控、配方管理、"
                "微生物检验、过敏原标注、合规校验。"
            ),
            version="1.0.0",
            author="LightMES",
            icon="apple",
            features=[
                "批次双向追溯（前向/后向）",
                "保质期/效期管理（FIFO/FEFO）",
                "HACCP关键控制点(CCP)监控",
                "冷链温度记录与超限报警",
                "配方管理（BOM精确到原料）",
                "称重计量 + 净含量控制",
                "微生物/感官/理化检验",
                "食品添加剂合规校验（GB2760）",
                "过敏原标注管理",
                "SC/HACCP/ISO22000/BRC多认证",
            ],
            dependencies=["production", "quality", "equipment"],
        )

    def default_settings(self) -> dict[str, Any]:
        return {
            # 通用
            "production.report.default_mode": "batch",
            "quality.aql.default_level": "1.5",
            "quality.inspection.sampling_rule": "GB",
            # 食品行业特有
            "industry.food.batch_trace_required": True,
            "industry.food.shelf_life_required": True,
            "industry.food.fifo_mode": "FEFO",  # 先到期先出
            "industry.food.haccp_enabled": True,
            "industry.food.cold_chain_monitor": True,
            "industry.food.metal_detection_required": True,
            "industry.food.xray_required": False,
            "industry.food.allergen_label_required": True,
            "industry.food.net_weight_tolerance": 1.0,  # %
            "industry.food.micro_test_required": True,
            "industry.food.additive_compliance": "GB2760",
            "industry.food.sc_required": True,
        }

    def seed_data(self, db: Session, tenant_id: int) -> dict[str, Any]:
        """
        初始化食品加工行业种子数据
        幂等：已存在的数据会跳过
        """
        from sqlalchemy import select

        from app.models.dictionary import DictItem, DictType
        from app.models.process import Process
        from app.models.quality import DefectCode, InspectionTemplate, InspectionTemplateItem

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
                        industry_code="food",
                        code=p["code"],
                        name=p["name"],
                        workshop=p.get("workshop", ""),
                        std_minutes=p.get("std_minutes", 0),
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
                    industry_code="food",
                    code=t["code"],
                    name=t["name"],
                    description=t.get("description", ""),
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
                            item_type=item.get("item_type", "pass_fail"),
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
                        industry_code="food",
                        code=d["code"],
                        name=d["name"],
                        severity=d["severity"],
                        description=d.get("description", ""),
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
                    industry_code="food",
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
        """租户启用食品行业包时，写入默认设置"""
        from app.crud.tenant_setting import upsert_setting

        for key, value in self.default_settings().items():
            upsert_setting(db, tenant_id, key, value)