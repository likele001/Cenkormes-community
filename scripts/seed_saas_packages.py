# -*- coding: utf-8 -*-
"""预置 LightMes 套餐种子数据 - SaaS + 源码交付"""

import json
import sys
sys.path.insert(0, '/www/wwwroot/lightmes/backend')

from decimal import Decimal
from app.core.db import SessionLocal
from app.models.saas_package import SaasPackage

# 按 sort_order 排列
SEED_PACKAGES = [
    # ======== SaaS 云服务 ========
    {
        "code": "saas-starter",
        "name": "Starter 创业版（SaaS）",
        "price_yuan": Decimal("998"),
        "duration_days": 365,
        "max_users": 15,
        "features_json": json.dumps([
            "基础生产管理", "扫码报工", "审核管理",
            "产品/型号管理(≤200)", "工序管理", "工艺路线",
            "工单/任务管理", "派工管理",
            "计件工资管理", "客户H5自助下单",
            "邀请加入", "考勤记录", "本地存储(3图/报工)"
        ], ensure_ascii=False),
        "description": "SaaS云服务 · 适合小型加工厂，含1个行业包(机加工)，15用户",
        "tier": "starter",
        "delivery_mode": "saas",
        "max_industries": 1,
        "allowed_industry_codes": json.dumps(["machining"], ensure_ascii=False),
        "sort_order": 10,
        "is_active": True,
    },
    {
        "code": "saas-pro",
        "name": "Pro 专业版（SaaS）",
        "price_yuan": Decimal("2800"),
        "duration_days": 365,
        "max_users": 100,
        "features_json": json.dumps([
            "全部 Starter 功能",
            "3个行业包可切换", "CRM客户管理", "商机/销售漏斗",
            "公海池", "客户对账单", "收支流水", "成本毛利",
            "生产计划/甘特图", "排班管理", "MRP运算",
            "外协管理", "报价单", "SPC质量分析",
            "采购管理", "库存/仓库管理", "供应商管理",
            "物料/BOM管理", "设备管理", "模具管理",
            "飞书/企微/钉钉推送", "审批流", "打印模板",
            "云存储(多图+视频)", "工厂助手(AI问答)"
        ], ensure_ascii=False),
        "description": "SaaS云服务 · 46+全功能模块，3个行业包可切换，完整生产+经营+CRM+财务",
        "tier": "pro",
        "delivery_mode": "saas",
        "max_industries": 3,
        "allowed_industry_codes": json.dumps(
            ["machining", "injection_molding", "electronics", "garment"],
            ensure_ascii=False
        ),
        "sort_order": 20,
        "is_active": True,
    },
    {
        "code": "saas-enterprise",
        "name": "Enterprise 企业版（SaaS）",
        "price_yuan": Decimal("5800"),
        "duration_days": 365,
        "max_users": 0,
        "features_json": json.dumps([
            "全部 Pro 功能", "无限用户", "全部6个行业包",
            "AI员工(Agent)", "生产自动化", "定时任务",
            "微信小程序(员工端+客户端)",
            "私有化部署", "自定义域名", "优先技术支持"
        ], ensure_ascii=False),
        "description": "SaaS云服务 · 全行业包无限制，AI+自动化全功能，优先技术支持",
        "tier": "enterprise",
        "delivery_mode": "saas",
        "max_industries": -1,
        "allowed_industry_codes": None,
        "sort_order": 30,
        "is_active": True,
    },
    # ======== 源码交付 ========
    {
        "code": "source-pro",
        "name": "Pro 源码版",
        "price_yuan": Decimal("3999"),
        "duration_days": 365,
        "max_users": 0,
        "features_json": json.dumps([
            "全部 46+ 个功能模块", "无限用户/SKU/工序",
            "3个行业包可切换", "CRM + 财务 + 仓储",
            "飞书/企微/钉钉集成", "AI 工厂助手",
            "云存储(多图+视频)", "GitHub 私有仓库权限",
            "一年内版本更新", "源码交付，私有部署"
        ], ensure_ascii=False),
        "description": "源码交付 · 全功能源码，GitHub私有仓库，自己部署，一年更新",
        "tier": "pro",
        "delivery_mode": "source",
        "max_industries": 3,
        "allowed_industry_codes": json.dumps(
            ["machining", "injection_molding", "electronics", "garment"],
            ensure_ascii=False
        ),
        "sort_order": 40,
        "is_active": True,
    },
    {
        "code": "source-enterprise",
        "name": "Enterprise 企业交付",
        "price_yuan": Decimal("0"),
        "duration_days": 365,
        "max_users": 0,
        "features_json": json.dumps([
            "全部 Pro 源码功能", "全部6个行业包",
            "AI员工(Agent) + 生产自动化",
            "微信小程序（员工+客户端）",
            "私有化部署 + 自定义域名",
            "现场实施部署 + 培训",
            "定制开发支持"
        ], ensure_ascii=False),
        "description": "源码交付 · 全功能+全部行业包+实施部署+培训，价格请咨询",
        "tier": "enterprise",
        "delivery_mode": "source",
        "max_industries": -1,
        "allowed_industry_codes": None,
        "sort_order": 50,
        "is_active": True,
    },
]

def seed():
    db = SessionLocal()
    existing = {p.code for p in db.query(SaasPackage).all()}
    created = 0
    for item in SEED_PACKAGES:
        if item["code"] in existing:
            print(f'  跳过: {item["code"]}')
            continue
        pkg = SaasPackage(**item)
        db.add(pkg)
        db.flush()
        created += 1
        mode = "SaaS" if item["delivery_mode"] == "saas" else "源码"
        print(f'  创建: [{pkg.code}] {pkg.name} ({mode}) - ¥{float(pkg.price_yuan):.0f}')
    db.commit()
    db.close()
    print(f'\n完成: 新增 {created} 个，共 {len(existing) + created} 个')

if __name__ == "__main__":
    seed()
