"""
注塑行业包 — 种子数据

包含：
1. 标准工序模板（烘料/注塑/取件/去水口/检验/包装...）
2. 质检模板（首件/巡检/终检）
3. 缺陷代码（注塑常见缺陷）
4. 行业字典（材料类型、模具类型、注塑机类型）
"""

from typing import Any


# ============================================================
# 1. 标准工序模板
# ============================================================
INJECTION_MOLDING_PROCESSES = [
    {"code": "DRY", "name": "烘料", "workshop": "注塑车间", "std_minutes": 30},
    {"code": "SETUP", "name": "上模/换模", "workshop": "注塑车间", "std_minutes": 45},
    {"code": "WARMUP", "name": "预热调机", "workshop": "注塑车间", "std_minutes": 20},
    {"code": "FAI", "name": "首件确认", "workshop": "注塑车间", "std_minutes": 10},
    {"code": "INJECT", "name": "注塑成型", "workshop": "注塑车间", "std_minutes": 3},
    {"code": "EJECT", "name": "取件/机械手取件", "workshop": "注塑车间", "std_minutes": 1},
    {"code": "GATE_TRIM", "name": "去水口/去毛边", "workshop": "后加工车间", "std_minutes": 2},
    {"code": "DEFLASH", "name": "去披锋", "workshop": "后加工车间", "std_minutes": 2},
    {"code": "SURFACE", "name": "表面处理/抛光", "workshop": "后加工车间", "std_minutes": 5},
    {"code": "PRINT", "name": "丝印/移印", "workshop": "后加工车间", "std_minutes": 8},
    {"code": "ULTRASONIC", "name": "超声波焊接", "workshop": "后加工车间", "std_minutes": 6},
    {"code": "HEAT_STAKE", "name": "热熔", "workshop": "后加工车间", "std_minutes": 4},
    {"code": "ASSEMBLY", "name": "装配/组装", "workshop": "装配车间", "std_minutes": 10},
    {"code": "IPQC", "name": "过程巡检", "workshop": "注塑车间", "std_minutes": 5},
    {"code": "OQC", "name": "出货检验", "workshop": "质检车间", "std_minutes": 8},
    {"code": "PACK", "name": "包装", "workshop": "包装车间", "std_minutes": 3},
    {"code": "REWORK", "name": "返工", "workshop": "返工区", "std_minutes": 15},
]


# ============================================================
# 2. 质检模板
# ============================================================
INJECTION_MOLDING_INSPECTION_TEMPLATES = [
    {
        "code": "FAI_IM",
        "name": "首件检验-注塑",
        "description": "每批次/每模首件全尺寸及外观检验",
        "items": [
            {"seq": 1, "item_name": "外观", "item_type": "pass_fail", "is_required": True},
            {"seq": 2, "item_name": "关键尺寸", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 3, "item_name": "重量", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "g", "is_required": True},
            {"seq": 4, "item_name": "色差", "item_type": "pass_fail", "is_required": True},
            {"seq": 5, "item_name": "缩水/变形", "item_type": "pass_fail", "is_required": True},
            {"seq": 6, "item_name": "熔接线", "item_type": "pass_fail", "is_required": False},
            {"seq": 7, "item_name": "气泡/银丝", "item_type": "pass_fail", "is_required": False},
        ],
    },
    {
        "code": "IPQC_IM",
        "name": "巡检-注塑",
        "description": "生产过程中定时抽检",
        "items": [
            {"seq": 1, "item_name": "外观抽检", "item_type": "pass_fail", "is_required": True},
            {"seq": 2, "item_name": "关键尺寸", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 3, "item_name": "重量", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "g", "is_required": True},
            {"seq": 4, "item_name": "色差", "item_type": "pass_fail", "is_required": True},
        ],
    },
    {
        "code": "OQC_IM",
        "name": "出货检验-注塑",
        "description": "入库/出货前终检",
        "items": [
            {"seq": 1, "item_name": "外观全检", "item_type": "pass_fail", "is_required": True},
            {"seq": 2, "item_name": "尺寸抽检", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 3, "item_name": "数量核对", "item_type": "pass_fail", "is_required": True},
            {"seq": 4, "item_name": "包装/标签", "item_type": "pass_fail", "is_required": True},
        ],
    },
]


# ============================================================
# 3. 缺陷代码
# ============================================================
INJECTION_MOLDING_DEFECT_CODES = [
    # 外观缺陷
    {"code": "IM001", "name": "缩水", "severity": "major", "description": "表面凹陷，冷却收缩不均"},
    {"code": "IM002", "name": "飞边/披锋", "severity": "minor", "description": "分型面处溢料"},
    {"code": "IM003", "name": "气泡", "severity": "major", "description": "内部或表面气泡"},
    {"code": "IM004", "name": "银丝", "severity": "major", "description": "表面银白色条纹，水分或气体"},
    {"code": "IM005", "name": "熔接线", "severity": "minor", "description": "两股料流汇合处痕迹"},
    {"code": "IM006", "name": "流痕", "severity": "minor", "description": "表面波纹状痕迹"},
    {"code": "IM007", "name": "烧焦", "severity": "major", "description": "局部过热碳化发黑"},
    {"code": "IM008", "name": "色差", "severity": "minor", "description": "颜色与样板不一致"},
    {"code": "IM009", "name": "光泽不均", "severity": "minor", "description": "表面光泽度不一致"},
    {"code": "IM010", "name": "黑点/杂质", "severity": "major", "description": "表面或内部有黑色异物"},
    # 尺寸缺陷
    {"code": "IM020", "name": "尺寸超差", "severity": "critical", "description": "关键尺寸超出公差"},
    {"code": "IM021", "name": "变形", "severity": "critical", "description": "翘曲、扭曲"},
    {"code": "IM022", "name": "重量偏差", "severity": "major", "description": "单件重量超出范围"},
    # 结构缺陷
    {"code": "IM030", "name": "缺料/短射", "severity": "critical", "description": "未注满，缺肉"},
    {"code": "IM031", "name": "粘模", "severity": "major", "description": "产品粘在前模或后模"},
    {"code": "IM032", "name": "顶白", "severity": "minor", "description": "顶针处发白"},
    {"code": "IM033", "name": "拉伤", "severity": "minor", "description": "脱模时拉伤表面"},
    {"code": "IM034", "name": "断差", "severity": "minor", "description": "分型面处高低不平"},
    # 操作缺陷
    {"code": "IM040", "name": "混料", "severity": "critical", "description": "不同材料/颜色混用"},
    {"code": "IM041", "name": "漏工序", "severity": "critical", "description": "缺少后加工工序"},
    {"code": "IM042", "name": "参数异常", "severity": "major", "description": "温度/压力/速度超出工艺范围"},
]


# ============================================================
# 4. 行业字典
# ============================================================
INJECTION_MOLDING_DICTIONARIES = [
    {
        "type_code": "material_type_injection",
        "type_name": "注塑材料类型",
        "items": [
            {"label": "ABS", "value": "abs", "sort": 1},
            {"label": "PP", "value": "pp", "sort": 2},
            {"label": "PE", "value": "pe", "sort": 3},
            {"label": "PS", "value": "ps", "sort": 4},
            {"label": "PVC", "value": "pvc", "sort": 5},
            {"label": "PA(尼龙)", "value": "pa", "sort": 6},
            {"label": "PC", "value": "pc", "sort": 7},
            {"label": "PMMA", "value": "pmma", "sort": 8},
            {"label": "POM", "value": "pom", "sort": 9},
            {"label": "PBT", "value": "pbt", "sort": 10},
            {"label": "TPE/TPR", "value": "tpe", "sort": 11},
            {"label": "PET", "value": "pet", "sort": 12},
            {"label": "PPS", "value": "pps", "sort": 13},
            {"label": "LCP", "value": "lcp", "sort": 14},
            {"label": "玻纤增强", "value": "gf_reinforced", "sort": 15},
        ],
    },
    {
        "type_code": "mold_type",
        "type_name": "模具类型",
        "items": [
            {"label": "两板模", "value": "two_plate", "sort": 1},
            {"label": "三板模", "value": "three_plate", "sort": 2},
            {"label": "热流道模", "value": "hot_runner", "sort": 3},
            {"label": "冷流道模", "value": "cold_runner", "sort": 4},
            {"label": "叠层模", "value": "stack_mold", "sort": 5},
            {"label": "双色模", "value": "two_color", "sort": 6},
            {"label": "包胶模", "value": "overmold", "sort": 7},
            {"label": "气辅模", "value": "gas_assist", "sort": 8},
        ],
    },
    {
        "type_code": "machine_type_injection",
        "type_name": "注塑机类型",
        "items": [
            {"label": "卧式注塑机", "value": "horizontal", "sort": 1},
            {"label": "立式注塑机", "value": "vertical", "sort": 2},
            {"label": "全电动注塑机", "value": "all_electric", "sort": 3},
            {"label": "油电混合注塑机", "value": "hybrid", "sort": 4},
            {"label": "双色注塑机", "value": "two_color_machine", "sort": 5},
            {"label": "液态硅胶注塑机", "value": "lsr", "sort": 6},
        ],
    },
    {
        "type_code": "gate_type",
        "type_name": "浇口类型",
        "items": [
            {"label": "侧浇口", "value": "edge_gate", "sort": 1},
            {"label": "点浇口", "value": "pin_gate", "sort": 2},
            {"label": "潜伏式浇口", "value": "submarine_gate", "sort": 3},
            {"label": "扇形浇口", "value": "fan_gate", "sort": 4},
            {"label": "薄膜浇口", "value": "film_gate", "sort": 5},
            {"label": "环形浇口", "value": "ring_gate", "sort": 6},
            {"label": "热流道针阀", "value": "valve_gate", "sort": 7},
        ],
    },
    {
        "type_code": "surface_finish",
        "type_name": "表面处理",
        "items": [
            {"label": "抛光", "value": "polishing", "sort": 1},
            {"label": "晒纹", "value": "texturing", "sort": 2},
            {"label": "电镀", "value": "plating", "sort": 3},
            {"label": "喷涂", "value": "painting", "sort": 4},
            {"label": "丝印", "value": "silk_screen", "sort": 5},
            {"label": "移印", "value": "pad_printing", "sort": 6},
            {"label": "镭雕", "value": "laser_engraving", "sort": 7},
            {"label": "烫金", "value": "hot_stamping", "sort": 8},
        ],
    },
]


def get_all_seed_data() -> dict[str, Any]:
    return {
        "processes": INJECTION_MOLDING_PROCESSES,
        "inspection_templates": INJECTION_MOLDING_INSPECTION_TEMPLATES,
        "defect_codes": INJECTION_MOLDING_DEFECT_CODES,
        "dictionaries": INJECTION_MOLDING_DICTIONARIES,
    }
