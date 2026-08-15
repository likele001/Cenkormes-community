"""
汽车零部件行业包 — 主实现

特性：
- IATF 16949质量体系
- PPAP生产件批准（5级）
- APQP先期产品质量策划
- FMEA失效模式分析（DFMEA/PFMEA）
- MSA测量系统分析（GR&R）
- SPC统计过程控制（Xbar-R/I-MR/P/C等）
- 关键特性/安全件追溯
- 防错防呆（Poka-Yoke）
- 8D问题解决报告
- 客户审核（VDA6.3/BIQS/Q1/Formel Q）
- 多OEM客户体系适配
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.industries.auto_parts.seed_data import get_all_seed_data
from app.industries.base import IndustryPack, IndustryPackMeta


class AutoPartsIndustryPack(IndustryPack):
    """汽车零部件行业包"""

    def meta(self) -> IndustryPackMeta:
        return IndustryPackMeta(
            code="auto_parts",
            name="汽车零部件",
            name_en="Auto Parts",
            description=(
                "适用于汽车零部件、配件厂等制造企业。"
                "支持IATF 16949体系下的PPAP、APQP、FMEA、MSA、SPC、"
                "关键件追溯、防错、8D报告、客户审核。"
            ),
            version="1.0.0",
            author="LightMES",
            icon="car",
            features=[
                "IATF 16949质量体系",
                "PPAP生产件批准（5级）",
                "APQP先期产品质量策划",
                "DFMEA/PFMEA失效分析",
                "MSA测量系统分析（GR&R）",
                "SPC统计过程控制（Xbar-R/I-MR等）",
                "关键件/安全件全追溯",
                "防错防呆（Poka-Yoke）",
                "8D问题解决报告",
                "客户审核（VDA6.3/BIQS/Q1）",
                "多OEM客户体系适配",
            ],
            dependencies=["production", "quality", "equipment"],
        )

    def default_settings(self) -> dict[str, Any]:
        return {
            # 通用
            "production.report.default_mode": "unit",
            "quality.aql.default_level": "1.0",
            "quality.inspection.sampling_rule": "IATF",
            # 汽车零部件特有
            "industry.auto.iatf_required": True,
            "industry.auto.ppap_default_level": "L3",
            "industry.auto.apqp_required": True,
            "industry.auto.fmea_required": True,
            "industry.auto.msa_required": True,
            "industry.auto.spc_required": True,
            "industry.auto.spc_min_cpk": 1.33,
            "industry.auto.critical_char_trace_required": True,
            "industry.auto.poka_yoke_required": True,
            "industry.auto.8d_response_hours": 24,
            "industry.auto.customer_audit_required": True,
            "industry.auto.change_management_required": True,
        }

    def seed_data(self, db: Session, tenant_id: int) -> dict[str, Any]:
        """
        初始化汽车零部件行业种子数据
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
                        industry_code="auto_parts",
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
                    industry_code="auto_parts",
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
                        industry_code="auto_parts",
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
                    industry_code="auto_parts",
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
        """租户启用汽车零部件行业包时，写入默认设置"""
        from app.crud.tenant_setting import upsert_setting

        for key, value in self.default_settings().items():
            upsert_setting(db, tenant_id, key, value)