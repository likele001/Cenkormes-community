"""
机加工行业包 — 种子数据

包含：
1. 标准工序模板（车/铣/磨/钻/线切割/电火花/热处理...）
2. 质检模板（尺寸检验、外观检验、首件检验）
3. 缺陷代码（机加工常见缺陷）
4. 行业字典（加工类型、设备类型、刀具类型）
"""

from typing import Any


# ============================================================
# 1. 标准工序模板
# ============================================================
MACHINING_PROCESSES = [
    {"code": "TURN", "name": "车削", "workshop": "机加工车间", "std_minutes": 10},
    {"code": "MILL", "name": "铣削", "workshop": "机加工车间", "std_minutes": 12},
    {"code": "DRILL", "name": "钻孔", "workshop": "机加工车间", "std_minutes": 5},
    {"code": "GRIND", "name": "磨削", "workshop": "磨削车间", "std_minutes": 15},
    {"code": "BORING", "name": "镗孔", "workshop": "机加工车间", "std_minutes": 12},
    {"code": "TAPPING", "name": "攻丝", "workshop": "机加工车间", "std_minutes": 4},
    {"code": "REAMING", "name": "铰孔", "workshop": "机加工车间", "std_minutes": 6},
    {"code": "BROACHING", "name": "拉削", "workshop": "机加工车间", "std_minutes": 8},
    {"code": "WIRE_EDM", "name": "线切割", "workshop": "特种加工车间", "std_minutes": 30},
    {"code": "SINK_EDM", "name": "电火花", "workshop": "特种加工车间", "std_minutes": 25},
    {"code": "HEAT_TREAT", "name": "热处理", "workshop": "热处理车间", "std_minutes": 60},
    {"code": "ANODIZE", "name": "阳极氧化", "workshop": "表面处理车间", "std_minutes": 45},
    {"code": "PLATING", "name": "电镀", "workshop": "表面处理车间", "std_minutes": 40},
    {"code": "PAINTING", "name": "喷涂", "workshop": "表面处理车间", "std_minutes": 20},
    {"code": "DEBURR", "name": "去毛刺", "workshop": "机加工车间", "std_minutes": 3},
    {"code": "CLEAN", "name": "清洗", "workshop": "清洗车间", "std_minutes": 5},
    {"code": "ASSY", "name": "装配", "workshop": "装配车间", "std_minutes": 15},
    {"code": "PACK", "name": "包装", "workshop": "包装车间", "std_minutes": 5},
    {"code": "INSPECT", "name": "终检", "workshop": "质检车间", "std_minutes": 8},
]


# ============================================================
# 2. 质检模板
# ============================================================
MACHINING_INSPECTION_TEMPLATES = [
    {
        "code": "FAI",
        "name": "首件检验",
        "description": "每批次首件全尺寸检验",
        "items": [
            {"seq": 1, "item_name": "外观", "item_type": "pass_fail", "is_required": True},
            {"seq": 2, "item_name": "关键尺寸", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 3, "item_name": "螺纹通规", "item_type": "pass_fail", "is_required": True},
            {"seq": 4, "item_name": "螺纹止规", "item_type": "pass_fail", "is_required": True},
            {"seq": 5, "item_name": "表面粗糙度", "item_type": "measure", "standard_value": "Ra3.2", "upper_limit": "Ra6.3", "lower_limit": "", "unit": "μm", "is_required": False},
            {"seq": 6, "item_name": "毛刺检查", "item_type": "pass_fail", "is_required": True},
        ],
    },
    {
        "code": "IPQC_DIM",
        "name": "巡检-尺寸",
        "description": "生产过程中定时抽检尺寸",
        "items": [
            {"seq": 1, "item_name": "关键尺寸", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 2, "item_name": "外观", "item_type": "pass_fail", "is_required": True},
        ],
    },
    {
        "code": "FQC_FINAL",
        "name": "终检",
        "description": "入库前终检",
        "items": [
            {"seq": 1, "item_name": "外观全检", "item_type": "pass_fail", "is_required": True},
            {"seq": 2, "item_name": "关键尺寸抽检", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 3, "item_name": "数量核对", "item_type": "pass_fail", "is_required": True},
            {"seq": 4, "item_name": "包装检查", "item_type": "pass_fail", "is_required": True},
        ],
    },
]


# ============================================================
# 3. 缺陷代码
# ============================================================
MACHINING_DEFECT_CODES = [
    # 外观缺陷
    {"code": "D001", "name": "表面划伤", "severity": "major", "description": "加工表面可见划痕"},
    {"code": "D002", "name": "表面碰伤", "severity": "major", "description": "搬运/装夹导致的碰伤"},
    {"code": "D003", "name": "锈蚀", "severity": "major", "description": "表面生锈"},
    {"code": "D004", "name": "毛刺未除", "severity": "minor", "description": "边缘毛刺未清理干净"},
    # 尺寸缺陷
    {"code": "D010", "name": "尺寸超差", "severity": "critical", "description": "关键尺寸超出公差范围"},
    {"code": "D011", "name": "孔径偏大", "severity": "major", "description": "钻孔/镗孔直径超出上限"},
    {"code": "D012", "name": "孔径偏小", "severity": "major", "description": "钻孔/镗孔直径低于下限"},
    {"code": "D013", "name": "螺纹不良", "severity": "critical", "description": "螺纹乱牙/滑牙/不通"},
    {"code": "D014", "name": "同轴度超差", "severity": "major", "description": "同轴度超出公差"},
    {"code": "D015", "name": "平面度超差", "severity": "major", "description": "平面度超出公差"},
    {"code": "D016", "name": "垂直度超差", "severity": "major", "description": "垂直度超出公差"},
    # 加工缺陷
    {"code": "D020", "name": "粗糙度不合格", "severity": "minor", "description": "表面粗糙度超出标准"},
    {"code": "D021", "name": "振纹", "severity": "minor", "description": "加工振动导致的表面波纹"},
    {"code": "D022", "name": "刀痕", "severity": "minor", "description": "进刀痕迹明显"},
    {"code": "D023", "name": "烧伤", "severity": "major", "description": "切削热导致的表面烧伤"},
    {"code": "D024", "name": "变形", "severity": "critical", "description": "加工/热处理导致的工件变形"},
    # 程序/操作缺陷
    {"code": "D030", "name": "漏工序", "severity": "critical", "description": "缺少某道工序"},
    {"code": "D031", "name": "程序错误", "severity": "critical", "description": "CNC程序错误导致加工异常"},
    {"code": "D032", "name": "装夹错误", "severity": "critical", "description": "装夹方式不当导致加工错误"},
]


# ============================================================
# 4. 行业字典
# ============================================================
MACHINING_DICTIONARIES = [
    {
        "type_code": "machining_type",
        "type_name": "加工类型",
        "items": [
            {"label": "车削", "value": "turning", "sort": 1},
            {"label": "铣削", "value": "milling", "sort": 2},
            {"label": "磨削", "value": "grinding", "sort": 3},
            {"label": "钻孔", "value": "drilling", "sort": 4},
            {"label": "镗孔", "value": "boring", "sort": 5},
            {"label": "线切割", "value": "wire_edm", "sort": 6},
            {"label": "电火花", "value": "sink_edm", "sort": 7},
            {"label": "热处理", "value": "heat_treat", "sort": 8},
            {"label": "表面处理", "value": "surface_treat", "sort": 9},
        ],
    },
    {
        "type_code": "equipment_type_machining",
        "type_name": "机加工设备类型",
        "items": [
            {"label": "数控车床", "value": "cnc_lathe", "sort": 1},
            {"label": "普通车床", "value": "manual_lathe", "sort": 2},
            {"label": "加工中心", "value": " machining_center", "sort": 3},
            {"label": "数控铣床", "value": "cnc_mill", "sort": 4},
            {"label": "普通铣床", "value": "manual_mill", "sort": 5},
            {"label": "外圆磨床", "value": "cylindrical_grinder", "sort": 6},
            {"label": "内圆磨床", "value": "internal_grinder", "sort": 7},
            {"label": "平面磨床", "value": "surface_grinder", "sort": 8},
            {"label": "钻床", "value": "drill_press", "sort": 9},
            {"label": "镗床", "value": "boring_machine", "sort": 10},
            {"label": "线切割机", "value": "wire_edm", "sort": 11},
            {"label": "电火花机", "value": "sink_edm", "sort": 12},
            {"label": "加工中心(五轴)", "value": "5axis_mc", "sort": 13},
        ],
    },
    {
        "type_code": "tool_type",
        "type_name": "刀具类型",
        "items": [
            {"label": "车刀", "value": "turning_tool", "sort": 1},
            {"label": "铣刀", "value": "milling_cutter", "sort": 2},
            {"label": "钻头", "value": "drill_bit", "sort": 3},
            {"label": "丝锥", "value": "tap", "sort": 4},
            {"label": "铰刀", "value": "reamer", "sort": 5},
            {"label": "砂轮", "value": "grinding_wheel", "sort": 6},
            {"label": "锯片", "value": "saw_blade", "sort": 7},
        ],
    },
    {
        "type_code": "material_type_machining",
        "type_name": "加工材料类型",
        "items": [
            {"label": "碳钢", "value": "carbon_steel", "sort": 1},
            {"label": "合金钢", "value": "alloy_steel", "sort": 2},
            {"label": "不锈钢", "value": "stainless_steel", "sort": 3},
            {"label": "铝合金", "value": "aluminum", "sort": 4},
            {"label": "铜合金", "value": "copper", "sort": 5},
            {"label": "铸铁", "value": "cast_iron", "sort": 6},
            {"label": "钛合金", "value": "titanium", "sort": 7},
            {"label": "工程塑料", "value": "plastic", "sort": 8},
        ],
    },
]


def get_all_seed_data() -> dict[str, Any]:
    return {
        "processes": MACHINING_PROCESSES,
        "inspection_templates": MACHINING_INSPECTION_TEMPLATES,
        "defect_codes": MACHINING_DEFECT_CODES,
        "dictionaries": MACHINING_DICTIONARIES,
    }
