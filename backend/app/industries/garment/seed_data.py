"""
服装/纺织行业包 — 种子数据

包含：
1. 标准工序模板（订单评审/备料/裁剪/缝制/整烫/包装...）
2. 质检模板（面料来料/裁片/半成品/成衣出厂）
3. 缺陷代码（缝制/尺寸/外观/印花绣花/辅料/包装）
4. 行业字典（尺码/色号/面料类型/部位/外发工序）
"""

from typing import Any


# ============================================================
# 1. 标准工序模板
# ============================================================
GARMENT_PROCESSES = [
    # ------ 准备阶段 ------
    {"code": "GARMENT_ORDER_REVIEW", "name": "订单评审", "workshop": "业务部", "std_minutes": 10},
    {"code": "GARMENT_MATERIAL_PREP", "name": "备料", "workshop": "备料组", "std_minutes": 5},
    {"code": "GARMENT_LAYOUT", "name": "排料", "workshop": "裁剪车间", "std_minutes": 30},
    {"code": "GARMENT_CUT", "name": "裁剪", "workshop": "裁剪车间", "std_minutes": 10},
    # ------ 印绣花阶段 ------
    {"code": "GARMENT_PRINT", "name": "印花", "workshop": "印花车间", "std_minutes": 1},
    {"code": "GARMENT_EMBROIDERY", "name": "绣花", "workshop": "绣花车间", "std_minutes": 3},
    # ------ 缝制阶段 ------
    {"code": "GARMENT_SEW_FRONT", "name": "车缝-前身", "workshop": "缝制车间", "std_minutes": 4},
    {"code": "GARMENT_SEW_BACK", "name": "车缝-后身", "workshop": "缝制车间", "std_minutes": 3},
    {"code": "GARMENT_SEW_SLEEVE", "name": "车缝-袖子", "workshop": "缝制车间", "std_minutes": 3},
    {"code": "GARMENT_SEW_COLLAR", "name": "车缝-领口", "workshop": "缝制车间", "std_minutes": 2},
    {"code": "GARMENT_SEW_POCKET", "name": "车缝-口袋", "workshop": "缝制车间", "std_minutes": 2},
    {"code": "GARMENT_SEW_JOINT", "name": "拼缝合身", "workshop": "缝制车间", "std_minutes": 6},
    {"code": "GARMENT_OVERLOCK", "name": "锁边/包缝", "workshop": "缝制车间", "std_minutes": 1},
    {"code": "GARMENT_BUTTON", "name": "钉扣/打枣", "workshop": "缝制车间", "std_minutes": 1},
    # ------ 后整理 ------
    {"code": "GARMENT_IRONING", "name": "整烫", "workshop": "整烫车间", "std_minutes": 2},
    {"code": "GARMENT_QC_MID", "name": "中查", "workshop": "质检部", "std_minutes": 1},
    {"code": "GARMENT_QC_FINAL", "name": "成衣检验", "workshop": "质检部", "std_minutes": 2},
    {"code": "GARMENT_FOLD", "name": "折叠", "workshop": "包装车间", "std_minutes": 1},
    # ------ 包装 ------
    {"code": "GARMENT_PACK_INNER", "name": "单件包装", "workshop": "包装车间", "std_minutes": 1},
    {"code": "GARMENT_PACK_OUTER", "name": "装箱", "workshop": "包装车间", "std_minutes": 2},
    # ------ 外包 ------
    {"code": "GARMENT_OUTSOURCE", "name": "外包工序", "workshop": "外发组", "std_minutes": 0},
]


# ============================================================
# 2. 质检模板
# ============================================================
GARMENT_INSPECTION_TEMPLATES = [
    {
        "code": "GARMENT_FABRIC_INSP",
        "name": "面料来料检验",
        "description": "面料入库前的颜色/克重/幅宽/疵点/缩水率检验",
        "items": [
            {"seq": 1, "item_name": "颜色", "item_type": "pass_fail", "standard_value": "与确认样一致", "is_required": True},
            {"seq": 2, "item_name": "克重", "item_type": "measure", "standard_value": "", "upper_limit": "5", "lower_limit": "-5", "unit": "%", "is_required": True},
            {"seq": 3, "item_name": "幅宽", "item_type": "measure", "standard_value": "", "upper_limit": "2", "lower_limit": "-2", "unit": "cm", "is_required": True},
            {"seq": 4, "item_name": "疵点", "item_type": "pass_fail", "standard_value": "无破洞/明显疵点", "is_required": True},
            {"seq": 5, "item_name": "缩水率", "item_type": "measure", "standard_value": "", "upper_limit": "3", "lower_limit": "0", "unit": "%", "is_required": False},
        ],
    },
    {
        "code": "GARMENT_CUT_INSP",
        "name": "裁片检验",
        "description": "裁剪后的裁片尺寸/丝缕/数量/标记检验",
        "items": [
            {"seq": 1, "item_name": "裁片尺寸", "item_type": "measure", "standard_value": "", "upper_limit": "0.5", "lower_limit": "-0.5", "unit": "cm", "is_required": True},
            {"seq": 2, "item_name": "丝缕方向", "item_type": "pass_fail", "standard_value": "与纸样一致", "is_required": True},
            {"seq": 3, "item_name": "数量", "item_type": "pass_fail", "standard_value": "与排料单一致", "is_required": True},
            {"seq": 4, "item_name": "裁片标记", "item_type": "pass_fail", "standard_value": "钻眼/粉印清晰", "is_required": True},
        ],
    },
    {
        "code": "GARMENT_SEMI_INSP",
        "name": "半成品检验",
        "description": "缝制过程中的线迹/线头/尺寸/对称性抽检",
        "items": [
            {"seq": 1, "item_name": "缝制线迹", "item_type": "pass_fail", "standard_value": "无跳针/断线", "is_required": True},
            {"seq": 2, "item_name": "线头", "item_type": "pass_fail", "standard_value": "无线头外露", "is_required": True},
            {"seq": 3, "item_name": "尺寸", "item_type": "measure", "standard_value": "", "upper_limit": "1", "lower_limit": "-1", "unit": "cm", "is_required": True},
            {"seq": 4, "item_name": "对称性", "item_type": "pass_fail", "standard_value": "左右对称", "is_required": True},
        ],
    },
    {
        "code": "GARMENT_FINAL_INSP",
        "name": "成衣出厂检验",
        "description": "成衣出厂前的外观/尺寸/做工/辅料/吊牌检验",
        "items": [
            {"seq": 1, "item_name": "外观", "item_type": "pass_fail", "standard_value": "无污渍/破损", "is_required": True},
            {"seq": 2, "item_name": "尺寸", "item_type": "measure", "standard_value": "", "upper_limit": "1.5", "lower_limit": "-1.5", "unit": "cm", "is_required": True},
            {"seq": 3, "item_name": "做工", "item_type": "pass_fail", "standard_value": "缝制牢固/无线头", "is_required": True},
            {"seq": 4, "item_name": "辅料", "item_type": "pass_fail", "standard_value": "纽扣/拉链齐全", "is_required": True},
            {"seq": 5, "item_name": "色牢度", "item_type": "measure", "standard_value": "干摩4级/湿摩3级", "is_required": False},
            {"seq": 6, "item_name": "整烫", "item_type": "pass_fail", "standard_value": "平整无褶皱", "is_required": True},
            {"seq": 7, "item_name": "吊牌/唛头", "item_type": "pass_fail", "standard_value": "正确/清晰", "is_required": True},
        ],
    },
]


# ============================================================
# 3. 缺陷代码
# ============================================================
GARMENT_DEFECT_CODES = [
    # ------ 缝制类 ------
    {"code": "G001", "name": "跳针", "severity": "minor", "description": "缝纫线迹跳过针距"},
    {"code": "G002", "name": "断线", "severity": "critical", "description": "缝线断裂"},
    {"code": "G003", "name": "线头外露", "severity": "minor", "description": "未修剪干净的线头"},
    {"code": "G004", "name": "针距不均", "severity": "minor", "description": "针距疏密不均"},
    {"code": "G005", "name": "缝线皱缩", "severity": "major", "description": "缝线处面料皱缩"},
    {"code": "G006", "name": "缝制方向错", "severity": "critical", "description": "缝纫方向与工艺单相反"},
    # ------ 尺寸类 ------
    {"code": "G011", "name": "尺寸偏大", "severity": "major", "description": "成衣尺寸超出允差"},
    {"code": "G012", "name": "尺寸偏小", "severity": "major", "description": "成衣尺寸低于允差"},
    {"code": "G013", "name": "左右不对称", "severity": "major", "description": "左右片尺寸差异过大"},
    {"code": "G014", "name": "丝缕歪斜", "severity": "major", "description": "裁片丝缕方向与样板不一致"},
    # ------ 外观类 ------
    {"code": "G021", "name": "污渍", "severity": "major", "description": "油渍/水渍/墨渍等"},
    {"code": "G022", "name": "色差", "severity": "critical", "description": "与确认样色差超出允差"},
    {"code": "G023", "name": "破洞", "severity": "critical", "description": "面料破损"},
    {"code": "G024", "name": "色花", "severity": "major", "description": "染色不匀"},
    {"code": "G025", "name": "起球", "severity": "minor", "description": "面料表面起毛球"},
    # ------ 印花绣花类 ------
    {"code": "G031", "name": "印花错位", "severity": "critical", "description": "印花位置偏移"},
    {"code": "G032", "name": "印花模糊", "severity": "major", "description": "印花图案不清晰"},
    {"code": "G033", "name": "绣花跳线", "severity": "minor", "description": "绣花针迹跳线"},
    {"code": "G034", "name": "印花色差", "severity": "major", "description": "印花颜色与确认样不一致"},
    # ------ 辅料类 ------
    {"code": "G041", "name": "纽扣缺失", "severity": "critical", "description": "纽扣未钉或脱落"},
    {"code": "G042", "name": "拉链损坏", "severity": "critical", "description": "拉链卡死/缺齿"},
    {"code": "G043", "name": "吊牌错误", "severity": "major", "description": "吊牌信息错误/缺失"},
    {"code": "G044", "name": "配件缺失", "severity": "major", "description": "缺失应附配件"},
    # ------ 包装类 ------
    {"code": "G051", "name": "折叠不规范", "severity": "minor", "description": "折叠方式不符合包装要求"},
    {"code": "G052", "name": "装箱数量错", "severity": "critical", "description": "装箱数量与箱唛不符"},
    {"code": "G053", "name": "箱唛错误", "severity": "major", "description": "箱唛信息错误"},
]


# ============================================================
# 4. 行业字典
# ============================================================
GARMENT_DICTIONARIES = [
    {
        "type_code": "garment_size_code",
        "type_name": "服装尺码",
        "items": [
            {"label": "XS", "value": "XS", "sort": 1},
            {"label": "S", "value": "S", "sort": 2},
            {"label": "M", "value": "M", "sort": 3},
            {"label": "L", "value": "L", "sort": 4},
            {"label": "XL", "value": "XL", "sort": 5},
            {"label": "XXL", "value": "XXL", "sort": 6},
            {"label": "XXXL", "value": "XXXL", "sort": 7},
            {"label": "28码", "value": "28", "sort": 10},
            {"label": "29码", "value": "29", "sort": 11},
            {"label": "30码", "value": "30", "sort": 12},
            {"label": "31码", "value": "31", "sort": 13},
            {"label": "32码", "value": "32", "sort": 14},
            {"label": "33码", "value": "33", "sort": 15},
            {"label": "34码", "value": "34", "sort": 16},
            {"label": "35码", "value": "35", "sort": 17},
            {"label": "36码", "value": "36", "sort": 18},
            {"label": "38码", "value": "38", "sort": 19},
            {"label": "40码", "value": "40", "sort": 20},
            {"label": "42码", "value": "42", "sort": 21},
            {"label": "44码", "value": "44", "sort": 22},
            {"label": "90cm", "value": "90", "sort": 30},
            {"label": "100cm", "value": "100", "sort": 31},
            {"label": "110cm", "value": "110", "sort": 32},
            {"label": "120cm", "value": "120", "sort": 33},
            {"label": "130cm", "value": "130", "sort": 34},
            {"label": "140cm", "value": "140", "sort": 35},
            {"label": "150cm", "value": "150", "sort": 36},
            {"label": "160cm", "value": "160", "sort": 37},
            {"label": "均码", "value": "FREE", "sort": 99},
        ],
    },
    {
        "type_code": "garment_color_code",
        "type_name": "颜色色号",
        "items": [
            {"label": "黑色", "value": "BLACK", "sort": 1},
            {"label": "白色", "value": "WHITE", "sort": 2},
            {"label": "灰色", "value": "GRAY", "sort": 3},
            {"label": "红色", "value": "RED", "sort": 10},
            {"label": "蓝色", "value": "BLUE", "sort": 11},
            {"label": "藏青", "value": "NAVY", "sort": 12},
            {"label": "绿色", "value": "GREEN", "sort": 13},
            {"label": "黄色", "value": "YELLOW", "sort": 14},
            {"label": "粉色", "value": "PINK", "sort": 15},
            {"label": "米色", "value": "BEIGE", "sort": 16},
            {"label": "卡其", "value": "KHAKI", "sort": 17},
            {"label": "驼色", "value": "CAMEL", "sort": 18},
            {"label": "混色", "value": "MIXED", "sort": 99},
        ],
    },
    {
        "type_code": "garment_fabric_type",
        "type_name": "面料类型",
        "items": [
            {"label": "纯棉", "value": "COTTON", "sort": 1},
            {"label": "涤纶", "value": "POLYESTER", "sort": 2},
            {"label": "涤棉", "value": "CVC", "sort": 3},
            {"label": "涤棉混纺", "value": "TC", "sort": 4},
            {"label": "羊毛", "value": "WOOL", "sort": 10},
            {"label": "羊绒", "value": "CASHMERE", "sort": 11},
            {"label": "真丝", "value": "SILK", "sort": 12},
            {"label": "亚麻", "value": "LINEN", "sort": 13},
            {"label": "牛仔布", "value": "DENIM", "sort": 20},
            {"label": "针织布", "value": "KNIT", "sort": 21},
            {"label": "梭织布", "value": "WOVEN", "sort": 22},
            {"label": "抓绒", "value": "FLEECE", "sort": 30},
            {"label": "灯芯绒", "value": "CORDUROY", "sort": 31},
            {"label": "天鹅绒", "value": "VELVET", "sort": 32},
            {"label": "皮革", "value": "LEATHER", "sort": 40},
            {"label": "PU皮", "value": "PU", "sort": 41},
            {"label": "羽绒", "value": "DOWN", "sort": 50},
        ],
    },
    {
        "type_code": "garment_part",
        "type_name": "服装部位",
        "items": [
            {"label": "前身", "value": "FRONT_BODY", "sort": 1},
            {"label": "后身", "value": "BACK_BODY", "sort": 2},
            {"label": "袖子", "value": "SLEEVE", "sort": 3},
            {"label": "领子", "value": "COLLAR", "sort": 4},
            {"label": "口袋", "value": "POCKET", "sort": 5},
            {"label": "袖口", "value": "CUFF", "sort": 6},
            {"label": "下摆", "value": "HEM", "sort": 7},
            {"label": "门襟", "value": "PLACKET", "sort": 8},
            {"label": "腰头", "value": "WAISTBAND", "sort": 9},
            {"label": "育克/过肩", "value": "YOKE", "sort": 10},
            {"label": "里布", "value": "LINING", "sort": 20},
            {"label": "衬布", "value": "INTERLINING", "sort": 21},
        ],
    },
    {
        "type_code": "garment_outsource_type",
        "type_name": "外发工序类型",
        "items": [
            {"label": "水洗", "value": "WASHING", "sort": 1},
            {"label": "染色", "value": "DYEING", "sort": 2},
            {"label": "印花", "value": "PRINTING", "sort": 3},
            {"label": "绣花", "value": "EMBROIDERY", "sort": 4},
            {"label": "涂层", "value": "COATING", "sort": 5},
            {"label": "贴合", "value": "BONDING", "sort": 6},
            {"label": "防水处理", "value": "WATERPROOF", "sort": 7},
            {"label": "抗菌处理", "value": "ANTIBACTERIAL", "sort": 8},
            {"label": "整烫定型", "value": "IRONING", "sort": 20},
            {"label": "特种车缝", "value": "SPECIAL_SEW", "sort": 21},
        ],
    },
]


def get_all_seed_data() -> dict[str, Any]:
    return {
        "processes": GARMENT_PROCESSES,
        "inspection_templates": GARMENT_INSPECTION_TEMPLATES,
        "defect_codes": GARMENT_DEFECT_CODES,
        "dictionaries": GARMENT_DICTIONARIES,
    }