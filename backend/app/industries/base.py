"""
行业插件包框架 — 基类与注册表

设计理念：
- 每个 IndustryPack 是一个自包含的模块，包含：元数据、数据模型扩展、种子数据、API 路由
- 核心平台不改，行业包通过注册表动态加载
- 租户通过 tenant.industry_code 选择行业，系统自动加载对应 Pack
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session


@dataclass
class IndustryPackMeta:
    """行业包元数据"""

    code: str  # 行业代码，如 "machining"
    name: str  # 中文名，如 "机加工"
    name_en: str  # 英文名
    description: str  # 行业描述
    version: str = "1.0.0"
    author: str = "LightMES"
    icon: str = ""  # 图标标识
    # 行业特性标签
    features: list[str] = field(default_factory=list)
    # 依赖的核心模块
    dependencies: list[str] = field(default_factory=list)


class IndustryPack(ABC):
    """行业包基类，所有行业插件必须继承"""

    @abstractmethod
    def meta(self) -> IndustryPackMeta:
        """返回行业包元数据"""
        ...

    @abstractmethod
    def seed_data(self, db: Session, tenant_id: int) -> dict[str, Any]:
        """
        初始化行业种子数据（工序模板、质检模板、缺陷代码、字典等）
        在租户选择行业时调用，幂等执行。
        返回: {"processes": N, "templates": N, "defect_codes": N, ...}
        """
        ...

    @abstractmethod
    def default_settings(self) -> dict[str, Any]:
        """
        返回行业默认的租户设置（key-value）
        如: {"production.report.default_mode": "unit", "industry.machining.tool_management": True}
        """
        ...

    def extra_models(self) -> list[type]:
        """行业包扩展的 ORM 模型类列表（用于自动建表）"""
        return []

    def extra_routes(self):
        """行业包扩展的 APIRouter（可为空）"""
        return None

    def on_enable(self, db: Session, tenant_id: int) -> None:
        """租户启用此行业包时的钩子（可选）"""
        pass

    def on_disable(self, db: Session, tenant_id: int) -> None:
        """租户禁用此行业包时的钩子（可选）"""
        pass


class IndustryRegistry:
    """行业包注册表 — 单例"""

    _instance: IndustryRegistry | None = None
    _packs: dict[str, IndustryPack] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, pack: IndustryPack) -> None:
        meta = pack.meta()
        self._packs[meta.code] = pack

    def get(self, code: str) -> IndustryPack | None:
        return self._packs.get(code)

    def list_all(self) -> list[IndustryPackMeta]:
        return [pack.meta() for pack in self._packs.values()]

    def is_registered(self, code: str) -> bool:
        return code in self._packs


# 全局注册表实例
registry = IndustryRegistry()


def auto_discover_packs() -> None:
    """
    自动发现并注册所有行业包。
    在应用启动时调用一次。
    """
    try:
        # 机加工（核心示范行业包）
        from app.industries.machining.pack import MachiningIndustryPack

        registry.register(MachiningIndustryPack())
    except ImportError:
        pass

    # 注塑行业包
    try:
        from app.industries.injection_molding.pack import InjectionMoldingIndustryPack

        registry.register(InjectionMoldingIndustryPack())
    except ImportError:
        pass

    # 电子组装行业包
    try:
        from app.industries.electronics.pack import ElectronicsIndustryPack

        registry.register(ElectronicsIndustryPack())
    except ImportError:
        pass

    # 服装/纺织行业包
    try:
        from app.industries.garment.pack import GarmentIndustryPack

        registry.register(GarmentIndustryPack())
    except ImportError:
        pass

    # 食品加工行业包
    try:
        from app.industries.food.pack import FoodIndustryPack

        registry.register(FoodIndustryPack())
    except ImportError:
        pass

    # 汽车零部件行业包
    try:
        from app.industries.auto_parts.pack import AutoPartsIndustryPack

        registry.register(AutoPartsIndustryPack())
    except ImportError:
        pass

    # 后续行业包按需添加...
