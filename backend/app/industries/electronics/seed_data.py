"""
电子组装行业包 — 种子数据

包含：
1. 标准工序模板（SMT贴片/回流焊/插件/波峰焊/测试/组装...）
2. 质检模板（首件/巡检/ICT/FCT/老化测试）
3. 缺陷代码（电子组装常见缺陷）
4. 行业字典（PCB类型、元件封装、焊接方式）
"""

from typing import Any


# ============================================================
# 1. 标准工序模板
# ============================================================
ELECTRONICS_PROCESSES = [
    {"code": "SOLDER_PASTE", "name": "锡膏印刷", "workshop": "SMT车间", "std_minutes": 5},
    {"code": "SPI", "name": "SPI锡膏检测", "workshop": "SMT车间", "std_minutes": 3},
    {"code": "SMT_PLACE", "name": "SMT贴片", "workshop": "SMT车间", "std_minutes": 2},
    {"code": "REFLOW", "name": "回流焊", "workshop": "SMT车间", "std_minutes": 8},
    {"code": "AOI_SMT", "name": "AOI检测（SMT后）", "workshop": "SMT车间", "std_minutes": 3},
    {"code": "DIP_INSERT", "name": "插件", "workshop": "DIP车间", "std_minutes": 4},
    {"code": "WAVE_SOLDER", "name": "波峰焊", "workshop": "DIP车间", "std_minutes": 10},
    {"code": "AOI_DIP", "name": "AOI检测（DIP后）", "workshop": "DIP车间", "std_minutes": 3},
    {"code": "REWORK_SMT", "name": "SMT返修", "workshop": "返修区", "std_minutes": 15},
    {"code": "REWORK_DIP", "name": "DIP返修", "workshop": "返修区", "std_minutes": 12},
    {"code": "ICT", "name": "ICT在线测试", "workshop": "测试车间", "std_minutes": 5},
    {"code": "FCT", "name": "FCT功能测试", "workshop": "测试车间", "std_minutes": 8},
    {"code": "BURN_IN", "name": "老化测试", "workshop": "测试车间", "std_minutes": 120},
    {"code": "PROGRAM", "name": "程序烧录", "workshop": "测试车间", "std_minutes": 3},
    {"code": "CALIBRATE", "name": "校准", "workshop": "测试车间", "std_minutes": 6},
    {"code": "COATING", "name": "三防涂覆", "workshop": "组装车间", "std_minutes": 10},
    {"code": "ASSEMBLY", "name": "组装", "workshop": "组装车间", "std_minutes": 12},
    {"code": "SCREW", "name": "锁螺丝", "workshop": "组装车间", "std_minutes": 3},
    {"code": "LABEL", "name": "贴标签/条码", "workshop": "组装车间", "std_minutes": 2},
    {"code": "PACK", "name": "包装", "workshop": "包装车间", "std_minutes": 3},
    {"code": "OQC", "name": "出货检验", "workshop": "质检车间", "std_minutes": 8},
]


# ============================================================
# 2. 质检模板
# ============================================================
ELECTRONICS_INSPECTION_TEMPLATES = [
    {
        "code": "FAI_SMT",
        "name": "首件检验-SMT",
        "description": "每批次SMT首件全检",
        "items": [
            {"seq": 1, "item_name": "元件方向", "item_type": "pass_fail", "is_required": True},
            {"seq": 2, "item_name": "元件位置偏移", "item_type": "measure", "standard_value": "", "upper_limit": "0.1", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 3, "item_name": "锡膏量", "item_type": "pass_fail", "is_required": True},
            {"seq": 4, "item_name": "极性元件方向", "item_type": "pass_fail", "is_required": True},
            {"seq": 5, "item_name": "BGA焊接", "item_type": "pass_fail", "is_required": True},
            {"seq": 6, "item_name": "锡珠", "item_type": "pass_fail", "is_required": True},
        ],
    },
    {
        "code": "IPQC_SMT",
        "name": "巡检-SMT",
        "description": "SMT产线定时抽检",
        "items": [
            {"seq": 1, "item_name": "元件偏移", "item_type": "pass_fail", "is_required": True},
            {"seq": 2, "item_name": "虚焊/连锡", "item_type": "pass_fail", "is_required": True},
            {"seq": 3, "item_name": "锡珠", "item_type": "pass_fail", "is_required": True},
            {"seq": 4, "item_name": "极性反向", "item_type": "pass_fail", "is_required": True},
        ],
    },
    {
        "code": "FCT_CHECK",
        "name": "功能测试检验",
        "description": "FCT测试后抽检",
        "items": [
            {"seq": 1, "item_name": "功能测试通过率", "item_type": "measure", "standard_value": "100%", "upper_limit": "", "lower_limit": "", "unit": "%", "is_required": True},
            {"seq": 2, "item_name": "外观", "item_type": "pass_fail", "is_required": True},
            {"seq": 3, "item_name": "标签/条码", "item_type": "pass_fail", "is_required": True},
        ],
    },
    {
        "code": "OQC_ELEC",
        "name": "出货检验-电子",
        "description": "入库/出货前终检",
        "items": [
            {"seq": 1, "item_name": "外观全检", "item_type": "pass_fail", "is_required": True},
            {"seq": 2, "item_name": "功能抽检", "item_type": "pass_fail", "is_required": True},
            {"seq": 3, "item_name": "SN码/IMEI核对", "item_type": "pass_fail", "is_required": True},
            {"seq": 4, "item_name": "包装/附件", "item_type": "pass_fail", "is_required": True},
            {"seq": 5, "item_name": "ESD防护", "item_type": "pass_fail", "is_required": True},
        ],
    },
]


# ============================================================
# 3. 缺陷代码
# ============================================================
ELECTRONICS_DEFECT_CODES = [
    # SMT缺陷
    {"code": "E001", "name": "元件偏移", "severity": "major", "description": "贴片位置超出允许偏差"},
    {"code": "E002", "name": "元件立碑", "severity": "critical", "description": "元件一端翘起"},
    {"code": "E003", "name": "元件翻转", "severity": "critical", "description": "元件180度翻转"},
    {"code": "E004", "name": "极性反向", "severity": "critical", "description": "极性元件方向装反"},
    {"code": "E005", "name": "漏件", "severity": "critical", "description": "应贴元件未贴"},
    {"code": "E006", "name": "错件", "severity": "critical", "description": "贴了错误的元件"},
    {"code": "E007", "name": "多件", "severity": "critical", "description": "同一位置贴了多个元件"},
    {"code": "E008", "name": "锡珠", "severity": "major", "description": "焊点周围有锡珠"},
    {"code": "E009", "name": "连锡/桥接", "severity": "critical", "description": "相邻焊点短路"},
    {"code": "E010", "name": "虚焊", "severity": "critical", "description": "焊点未完全润湿"},
    {"code": "E011", "name": "少锡", "severity": "major", "description": "焊锡量不足"},
    {"code": "E012", "name": "多锡", "severity": "minor", "description": "焊锡量过多"},
    {"code": "E013", "name": "锡裂", "severity": "major", "description": "焊点裂纹"},
    # BGA/QFN缺陷
    {"code": "E020", "name": "BGA空洞", "severity": "major", "description": "BGA焊球内部空洞超标"},
    {"code": "E021", "name": "BGA偏移", "severity": "critical", "description": "BGA整体偏移"},
    {"code": "E022", "name": "QFN接地焊盘虚焊", "severity": "critical", "description": "底部接地焊盘未焊好"},
    # DIP缺陷
    {"code": "E030", "name": "插件不到位", "severity": "major", "description": "元件未插到底"},
    {"code": "E031", "name": "插件歪斜", "severity": "minor", "description": "元件倾斜"},
    {"code": "E032", "name": "剪脚不良", "severity": "minor", "description": "引脚长度不符合要求"},
    {"code": "E033", "name": "波峰焊连锡", "severity": "critical", "description": "波峰焊后相邻引脚短路"},
    {"code": "E034", "name": "波峰焊拉尖", "severity": "minor", "description": "焊点有尖刺"},
    # 测试缺陷
    {"code": "E040", "name": "功能不良", "severity": "critical", "description": "FCT测试不通过"},
    {"code": "E041", "name": "ICT开路", "severity": "critical", "description": "ICT测试发现开路"},
    {"code": "E042", "name": "ICT短路", "severity": "critical", "description": "ICT测试发现短路"},
    {"code": "E043", "name": "参数漂移", "severity": "major", "description": "测试参数超出规格"},
    # 外观缺陷
    {"code": "E050", "name": "PCB划伤", "severity": "minor", "description": "PCB表面划伤"},
    {"code": "E051", "name": "元件破损", "severity": "major", "description": "元件本体损坏"},
    {"code": "E052", "name": "标签错误", "severity": "critical", "description": "条码/SN码错误"},
    {"code": "E053", "name": "ESD损伤", "severity": "critical", "description": "静电放电损伤"},
]


# ============================================================
# 4. 行业字典
# ============================================================
ELECTRONICS_DICTIONARIES = [
    {
        "type_code": "pcb_type",
        "type_name": "PCB类型",
        "items": [
            {"label": "单面板", "value": "single_side", "sort": 1},
            {"label": "双面板", "value": "double_side", "sort": 2},
            {"label": "四层板", "value": "4_layer", "sort": 3},
            {"label": "六层板", "value": "6_layer", "sort": 4},
            {"label": "八层板", "value": "8_layer", "sort": 5},
            {"label": "HDI板", "value": "hdi", "sort": 6},
            {"label": "柔性板(FPC)", "value": "fpc", "sort": 7},
            {"label": "刚柔结合板", "value": "rigid_flex", "sort": 8},
        ],
    },
    {
        "type_code": "component_package",
        "type_name": "元件封装类型",
        "items": [
            {"label": "SOP", "value": "sop", "sort": 1},
            {"label": "QFP", "value": "qfp", "sort": 2},
            {"label": "QFN", "value": "qfn", "sort": 3},
            {"label": "BGA", "value": "bga", "sort": 4},
            {"label": "CSP", "value": "csp", "sort": 5},
            {"label": "0402", "value": "0402", "sort": 6},
            {"label": "0603", "value": "0603", "sort": 7},
            {"label": "0805", "value": "0805", "sort": 8},
            {"label": "1206", "value": "1206", "sort": 9},
            {"label": "SOT-23", "value": "sot23", "sort": 10},
            {"label": "SOT-89", "value": "sot89", "sort": 11},
            {"label": "TO-252", "value": "to252", "sort": 12},
        ],
    },
    {
        "type_code": "solder_type",
        "type_name": "焊接方式",
        "items": [
            {"label": "回流焊", "value": "reflow", "sort": 1},
            {"label": "波峰焊", "value": "wave", "sort": 2},
            {"label": "选择性波峰焊", "value": "selective_wave", "sort": 3},
            {"label": "手工焊", "value": "hand_solder", "sort": 4},
            {"label": "激光焊", "value": "laser_solder", "sort": 5},
            {"label": "压接", "value": "press_fit", "sort": 6},
        ],
    },
    {
        "type_code": "test_type",
        "type_name": "测试类型",
        "items": [
            {"label": "ICT", "value": "ict", "sort": 1},
            {"label": "FCT", "value": "fct", "sort": 2},
            {"label": "AOI", "value": "aoi", "sort": 3},
            {"label": "X-RAY", "value": "xray", "sort": 4},
            {"label": "老化测试", "value": "burn_in", "sort": 5},
            {"label": "ESD测试", "value": "esd_test", "sort": 6},
            {"label": "EMC测试", "value": "emc", "sort": 7},
        ],
    },
    {
        "type_code": "product_type_elec",
        "type_name": "电子产品类型",
        "items": [
            {"label": "消费电子", "value": "consumer", "sort": 1},
            {"label": "工业控制", "value": "industrial", "sort": 2},
            {"label": "汽车电子", "value": "automotive", "sort": 3},
            {"label": "医疗电子", "value": "medical", "sort": 4},
            {"label": "通信设备", "value": "communication", "sort": 5},
            {"label": "安防监控", "value": "security", "sort": 6},
            {"label": "智能家居", "value": "smart_home", "sort": 7},
            {"label": "新能源", "value": "new_energy", "sort": 8},
        ],
    },
]


def get_all_seed_data() -> dict[str, Any]:
    return {
        "processes": ELECTRONICS_PROCESSES,
        "inspection_templates": ELECTRONICS_INSPECTION_TEMPLATES,
        "defect_codes": ELECTRONICS_DEFECT_CODES,
        "dictionaries": ELECTRONICS_DICTIONARIES,
    }
