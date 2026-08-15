"""
服装/纺织行业包 — 主实现

继承 IndustryPack 基类，实现种子数据初始化逻辑。
特性：
- 工票计件（按件/按工序计价）
- 尺码色号矩阵管理
- 裁剪排料与裁片管理
- 缝制工序流转（多机台、多工人）
- 中查/终检（AQL抽检）
- 外发加工管理（印染/水洗/绣花）
- 整烫包装出货
- 计件工资自动核算
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.industries.base import IndustryPack, IndustryPackMeta
from app.industries.garment.seed_data import get_all_seed_data


class GarmentIndustryPack(IndustryPack):
    """服装/纺织行业包"""

    def meta(self) -> IndustryPackMeta:
        return IndustryPackMeta(
            code="garment",
            name="服装纺织",
            name_en="Garment & Textile",
            description=(
                "适用于服装厂、纺织厂等劳动密集型制造企业。"
                "支持工票计件、尺码色号矩阵、裁剪排料、缝制工序流转、"
                "AQL抽检、外发加工、计件工资核算。"
            ),
            version="1.0.0",
            author="LightMES",
            icon="scissors",
            features=[
                "工票计件（按件/按工序）",
                "尺码×色号矩阵管理",
                "裁剪排料与裁片管理",
                "多机台缝制工序流转",
                "中查/终检（AQL抽检）",
                "外发加工管理（印染/水洗/绣花）",
                "整烫包装出货",
                "计件工资自动核算",
                "款号/订单全程追溯",
            ],
            dependencies=["production", "quality", "equipment"],
        )

    def default_settings(self) -> dict[str, Any]:
        return {
            # 通用
            "production.report.default_mode": "piece",
            "quality.aql.default_level": "2.5",
            "quality.inspection.sampling_rule": "AQL",
            # 服装行业特有
            "industry.garment.piece_rate_enabled": True,
            "industry.garment.size_color_matrix": True,
            "industry.garment.cutting_layout_enabled": True,
            "industry.garment.mid_inspection_required": True,
            "industry.garment.final_inspection_aql": "2.5",
            "industry.garment.outsource_managed": True,
            "industry.garment.washing_record_required": False,
            "industry.garment.ironing_required": True,
            "industry.garment.payroll_by_piece": True,
            "industry.garment.sewing_efficiency_target": 85,
        }

    def seed_data(self, db: Session, tenant_id: int) -> dict[str, Any]:
        """
        初始化服装/纺织行业种子数据
        幂等：已存在的数据会跳过
        """
        from sqlalchemy import select

        from app.models.process import Process
        from app.models.quality import DefectCode, InspectionTemplate, InspectionTemplateItem
        from app.models.dictionary import DictItem, DictType

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
                        industry_code="garment",
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
                    industry_code="garment",
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
                        industry_code="garment",
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
                    industry_code="garment",
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
        """租户启用服装行业包时，写入默认设置"""
        from app.crud.tenant_setting import upsert_setting

        for key, value in self.default_settings().items():
            upsert_setting(db, tenant_id, key, value)