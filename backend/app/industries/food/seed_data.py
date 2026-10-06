"""
食品加工行业包 — 种子数据

包含：
1. 标准工序模板（原料验收/预处理/加工/包装/入库）
2. 质检模板（HACCP/微生物/感官/理化/出厂）
3. 缺陷代码（异物/污染/变质/包装/重量）
4. 行业字典（食品类别/包装形式/储藏方式/过敏原）
"""

from typing import Any


# ============================================================
# 1. 标准工序模板
# ============================================================
FOOD_PROCESSES = [
    # ------ 原料阶段 ------
    {"code": "FOOD_RAW_INSP", "name": "原料验收", "workshop": "原料仓", "std_minutes": 15},
    {"code": "FOOD_RAW_STORE", "name": "原料入库", "workshop": "原料仓", "std_minutes": 10},
    {"code": "FOOD_RAW_THRAW", "name": "解冻/回温", "workshop": "预处理车间", "std_minutes": 480},
    # ------ 预处理 ------
    {"code": "FOOD_WASH", "name": "清洗", "workshop": "预处理车间", "std_minutes": 20},
    {"code": "FOOD_PEEL", "name": "去皮/去壳", "workshop": "预处理车间", "std_minutes": 30},
    {"code": "FOOD_CUT", "name": "切割/分切", "workshop": "预处理车间", "std_minutes": 20},
    {"code": "FOOD_BLANCH", "name": "漂烫/焯水", "workshop": "预处理车间", "std_minutes": 10},
    {"code": "FOOD_MARINATE", "name": "腌制/调味", "workshop": "预处理车间", "std_minutes": 60},
    # ------ 加工 ------
    {"code": "FOOD_MIX", "name": "配料混合", "workshop": "加工车间", "std_minutes": 15},
    {"code": "FOOD_GRIND", "name": "粉碎/研磨", "workshop": "加工车间", "std_minutes": 20},
    {"code": "FOOD_COOK", "name": "蒸煮", "workshop": "加工车间", "std_minutes": 60},
    {"code": "FOOD_FRYPAN", "name": "炒制/煎制", "workshop": "加工车间", "std_minutes": 15},
    {"code": "FOOD_FRY", "name": "油炸", "workshop": "加工车间", "std_minutes": 10},
    {"code": "FOOD_BAKE", "name": "烘焙", "workshop": "烘焙车间", "std_minutes": 45},
    {"code": "FOOD_GRILL", "name": "烧烤/熏制", "workshop": "加工车间", "std_minutes": 30},
    {"code": "FOOD_STERILIZE", "name": "高温灭菌", "workshop": "杀菌车间", "std_minutes": 30},
    {"code": "FOOD_PASTEURIZE", "name": "巴氏杀菌", "workshop": "杀菌车间", "std_minutes": 30},
    {"code": "FOOD_COLD_CHAIN", "name": "速冻/冷藏", "workshop": "冷链车间", "std_minutes": 240},
    {"code": "FOOD_FERMENT", "name": "发酵", "workshop": "发酵车间", "std_minutes": 1440},
    {"code": "FOOD_DRY", "name": "干燥/脱水", "workshop": "干燥车间", "std_minutes": 360},
    {"code": "FOOD_EXTRACT", "name": "萃取/浓缩", "workshop": "加工车间", "std_minutes": 120},
    # ------ 包装 ------
    {"code": "FOOD_METAL_DETECT", "name": "金属检测", "workshop": "包装车间", "std_minutes": 1},
    {"code": "FOOD_XRAY", "name": "X光检测", "workshop": "包装车间", "std_minutes": 1},
    {"code": "FOOD_WEIGH", "name": "称重", "workshop": "包装车间", "std_minutes": 1},
    {"code": "FOOD_PACK_PRIMARY", "name": "内包装", "workshop": "包装车间", "std_minutes": 2},
    {"code": "FOOD_PACK_SECONDARY", "name": "外包装", "workshop": "包装车间", "std_minutes": 2},
    {"code": "FOOD_LABEL", "name": "贴标/喷码", "workshop": "包装车间", "std_minutes": 1},
    {"code": "FOOD_CARTON", "name": "装箱", "workshop": "包装车间", "std_minutes": 3},
    # ------ 检验 ------
    {"code": "FOOD_IPQC", "name": "过程巡检", "workshop": "品控部", "std_minutes": 5},
    {"code": "FOOD_MICRO_TEST", "name": "微生物检验", "workshop": "化验室", "std_minutes": 120},
    {"code": "FOOD_OQC", "name": "出厂检验", "workshop": "品控部", "std_minutes": 15},
    {"code": "FOOD_STORAGE", "name": "成品入库", "workshop": "成品仓", "std_minutes": 10},
]


# ============================================================
# 2. 质检模板
# ============================================================
FOOD_INSPECTION_TEMPLATES = [
    {
        "code": "FOOD_RAW_INSP",
        "name": "原料验收检验",
        "description": "原料入库前的感官/包装/温度/索证检验",
        "items": [
            {"seq": 1, "item_name": "外包装完整性", "item_type": "pass_fail", "standard_value": "无破损/泄漏/污染", "is_required": True},
            {"seq": 2, "item_name": "标签标识", "item_type": "pass_fail", "standard_value": "品名/规格/批号/日期齐全", "is_required": True},
            {"seq": 3, "item_name": "索证索票", "item_type": "pass_fail", "standard_value": "检验报告/检疫证明齐全", "is_required": True},
            {"seq": 4, "item_name": "温度(冷链)", "item_type": "measure", "standard_value": "", "upper_limit": "4", "lower_limit": "-2", "unit": "℃", "is_required": True},
            {"seq": 5, "item_name": "感官检验", "item_type": "pass_fail", "standard_value": "色泽/气味/形态正常", "is_required": True},
            {"seq": 6, "item_name": "水分含量", "item_type": "measure", "standard_value": "", "upper_limit": "15", "lower_limit": "0", "unit": "%", "is_required": False},
        ],
    },
    {
        "code": "FOOD_IPQC",
        "name": "HACCP过程检验",
        "description": "关键控制点CCP监控（温度/时间/pH/金属/重量）",
        "items": [
            {"seq": 1, "item_name": "杀菌温度", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "121", "unit": "℃", "is_required": True},
            {"seq": 2, "item_name": "杀菌时间", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "15", "unit": "min", "is_required": True},
            {"seq": 3, "item_name": "金属检测", "item_type": "pass_fail", "standard_value": "Fe≥1.5mm Non-Fe≥2.0mm SS≥2.5mm", "is_required": True},
            {"seq": 4, "item_name": "包装密封性", "item_type": "pass_fail", "standard_value": "无漏气/泄漏", "is_required": True},
            {"seq": 5, "item_name": "净含量偏差", "item_type": "measure", "standard_value": "", "upper_limit": "1", "lower_limit": "-1", "unit": "%", "is_required": True},
            {"seq": 6, "item_name": "车间环境温度", "item_type": "measure", "standard_value": "", "upper_limit": "25", "lower_limit": "0", "unit": "℃", "is_required": False},
            {"seq": 7, "item_name": "车间洁净度", "item_type": "pass_fail", "standard_value": "无可见异物/积水", "is_required": True},
        ],
    },
    {
        "code": "FOOD_MICRO_TEST",
        "name": "微生物检验",
        "description": "菌落总数/大肠菌群/致病菌检验",
        "items": [
            {"seq": 1, "item_name": "菌落总数", "item_type": "measure", "standard_value": "", "upper_limit": "10000", "lower_limit": "0", "unit": "CFU/g", "is_required": True},
            {"seq": 2, "item_name": "大肠菌群", "item_type": "measure", "standard_value": "", "upper_limit": "10", "lower_limit": "0", "unit": "MPN/g", "is_required": True},
            {"seq": 3, "item_name": "沙门氏菌", "item_type": "pass_fail", "standard_value": "不得检出", "is_required": True},
            {"seq": 4, "item_name": "金黄色葡萄球菌", "item_type": "pass_fail", "standard_value": "不得检出", "is_required": True},
            {"seq": 5, "item_name": "霉菌酵母菌", "item_type": "measure", "standard_value": "", "upper_limit": "100", "lower_limit": "0", "unit": "CFU/g", "is_required": False},
        ],
    },
    {
        "code": "FOOD_SENSE_TEST",
        "name": "感官检验",
        "description": "色泽/气味/滋味/形态/杂质评价",
        "items": [
            {"seq": 1, "item_name": "色泽", "item_type": "pass_fail", "standard_value": "与标准样一致", "is_required": True},
            {"seq": 2, "item_name": "气味", "item_type": "pass_fail", "standard_value": "无异味/哈败味", "is_required": True},
            {"seq": 3, "item_name": "滋味", "item_type": "pass_fail", "standard_value": "与标准样一致", "is_required": True},
            {"seq": 4, "item_name": "组织形态", "item_type": "pass_fail", "standard_value": "均匀/完整", "is_required": True},
            {"seq": 5, "item_name": "杂质", "item_type": "pass_fail", "standard_value": "无可见异物", "is_required": True},
        ],
    },
    {
        "code": "FOOD_OQC",
        "name": "成品出厂检验",
        "description": "成品批次放行前的综合检验",
        "items": [
            {"seq": 1, "item_name": "批次检验报告", "item_type": "pass_fail", "standard_value": "齐全有效", "is_required": True},
            {"seq": 2, "item_name": "感官检验", "item_type": "pass_fail", "standard_value": "全部合格", "is_required": True},
            {"seq": 3, "item_name": "净含量", "item_type": "measure", "standard_value": "", "upper_limit": "1", "lower_limit": "-1", "unit": "%", "is_required": True},
            {"seq": 4, "item_name": "包装标识", "item_type": "pass_fail", "standard_value": "SC/生产日期/批号/保质期齐全", "is_required": True},
            {"seq": 5, "item_name": "微生物", "item_type": "pass_fail", "standard_value": "符合标准", "is_required": True},
            {"seq": 6, "item_name": "添加剂使用", "item_type": "pass_fail", "standard_value": "符合GB2760", "is_required": True},
            {"seq": 7, "item_name": "过敏原标注", "item_type": "pass_fail", "standard_value": "如有则标注", "is_required": True},
        ],
    },
]


# ============================================================
# 3. 缺陷代码
# ============================================================
FOOD_DEFECT_CODES = [
    # ------ 异物污染类 ------
    {"code": "F001", "name": "金属异物", "severity": "critical", "description": "检测出金属异物"},
    {"code": "F002", "name": "毛发", "severity": "critical", "description": "检测出毛发"},
    {"code": "F003", "name": "塑料碎片", "severity": "critical", "description": "检测出塑料/包装碎片"},
    {"code": "F004", "name": "虫/鼠害", "severity": "critical", "description": "发现虫体/鼠迹"},
    {"code": "F005", "name": "其他异物", "severity": "major", "description": "其他可见异物"},
    # ------ 微生物类 ------
    {"code": "F011", "name": "菌落超标", "severity": "critical", "description": "菌落总数超出限值"},
    {"code": "F012", "name": "大肠菌群超标", "severity": "critical", "description": "大肠菌群超出限值"},
    {"code": "F013", "name": "致病菌检出", "severity": "critical", "description": "检出沙门氏菌/金葡菌等"},
    {"code": "F014", "name": "霉菌超标", "severity": "major", "description": "霉菌酵母菌超标"},
    # ------ 变质类 ------
    {"code": "F021", "name": "酸败/哈败", "severity": "critical", "description": "油脂氧化哈败"},
    {"code": "F022", "name": "霉变", "severity": "critical", "description": "发生霉变"},
    {"code": "F023", "name": "发酵异常", "severity": "major", "description": "非预期发酵/胀袋"},
    {"code": "F024", "name": "变色", "severity": "major", "description": "颜色异常变化"},
    {"code": "F025", "name": "异味", "severity": "major", "description": "出现异味"},
    {"code": "F026", "name": "结块/沉淀", "severity": "minor", "description": "异常结块或沉淀"},
    # ------ 包装类 ------
    {"code": "F031", "name": "包装破损", "severity": "critical", "description": "包装破损泄漏"},
    {"code": "F032", "name": "密封不良", "severity": "critical", "description": "封口不严/漏气"},
    {"code": "F033", "name": "胀袋/鼓罐", "severity": "critical", "description": "包装膨胀"},
    {"code": "F034", "name": "标签错误", "severity": "major", "description": "标签信息错误"},
    {"code": "F035", "name": "生产日期错", "severity": "critical", "description": "生产日期喷码错误"},
    {"code": "F036", "name": "批次号错", "severity": "major", "description": "批次号错误或缺失"},
    # ------ 重量类 ------
    {"code": "F041", "name": "净含量不足", "severity": "major", "description": "低于标示净含量"},
    {"code": "F042", "name": "净含量超标", "severity": "minor", "description": "高于标示过多"},
    # ------ 添加剂/合规 ------
    {"code": "F051", "name": "添加剂超标", "severity": "critical", "description": "食品添加剂使用超标"},
    {"code": "F052", "name": "添加剂超范围", "severity": "critical", "description": "使用了未批准添加剂"},
    {"code": "F053", "name": "过敏原未标注", "severity": "major", "description": "含过敏原但未标注"},
    {"code": "F054", "name": "SC证过期", "severity": "critical", "description": "生产许可证过期"},
]


# ============================================================
# 4. 行业字典
# ============================================================
FOOD_DICTIONARIES = [
    {
        "type_code": "food_category",
        "type_name": "食品类别",
        "items": [
            {"label": "肉制品", "value": "MEAT", "sort": 1},
            {"label": "水产品", "value": "SEAFOOD", "sort": 2},
            {"label": "禽制品", "value": "POULTRY", "sort": 3},
            {"label": "乳制品", "value": "DAIRY", "sort": 4},
            {"label": "蛋制品", "value": "EGG", "sort": 5},
            {"label": "果蔬制品", "value": "FRUIT_VEG", "sort": 10},
            {"label": "粮食制品", "value": "GRAIN", "sort": 11},
            {"label": "食用油", "value": "OIL", "sort": 12},
            {"label": "调味品", "value": "SEASONING", "sort": 13},
            {"label": "饮料", "value": "BEVERAGE", "sort": 14},
            {"label": "酒类", "value": "ALCOHOL", "sort": 15},
            {"label": "烘焙食品", "value": "BAKERY", "sort": 20},
            {"label": "糖果巧克力", "value": "CONFECTIONERY", "sort": 21},
            {"label": "冷冻食品", "value": "FROZEN", "sort": 22},
            {"label": "方便食品", "value": "INSTANT", "sort": 23},
            {"label": "保健食品", "value": "HEALTH", "sort": 30},
        ],
    },
    {
        "type_code": "food_package_type",
        "type_name": "包装形式",
        "items": [
            {"label": "真空包装", "value": "VACUUM", "sort": 1},
            {"label": "气调包装(MAP)", "value": "MAP", "sort": 2},
            {"label": "热收缩包装", "value": "SHRINK", "sort": 3},
            {"label": "罐装", "value": "CAN", "sort": 10},
            {"label": "玻璃瓶", "value": "GLASS_BOTTLE", "sort": 11},
            {"label": "塑料瓶", "value": "PLASTIC_BOTTLE", "sort": 12},
            {"label": "利乐包", "value": "TETRA_PAK", "sort": 13},
            {"label": "自立袋", "value": "STAND_POUCH", "sort": 14},
            {"label": "三边封袋", "value": "THREE_SIDE", "sort": 15},
            {"label": "盒装", "value": "BOX", "sort": 20},
            {"label": "袋装", "value": "BAG", "sort": 21},
            {"label": "托盘+膜", "value": "TRAY_FILM", "sort": 22},
            {"label": "散装", "value": "BULK", "sort": 30},
        ],
    },
    {
        "type_code": "food_storage_type",
        "type_name": "储藏方式",
        "items": [
            {"label": "常温", "value": "AMBIENT", "sort": 1},
            {"label": "阴凉(≤20℃)", "value": "COOL", "sort": 2},
            {"label": "冷藏(0-10℃)", "value": "CHILLED", "sort": 3},
            {"label": "冷冻(≤-18℃)", "value": "FROZEN", "sort": 4},
            {"label": "深冷(≤-25℃)", "value": "DEEP_FROZEN", "sort": 5},
            {"label": "恒温", "value": "CONST_TEMP", "sort": 6},
        ],
    },
    {
        "type_code": "food_allergen",
        "type_name": "过敏原",
        "items": [
            {"label": "含麸质谷物", "value": "GLUTEN", "sort": 1},
            {"label": "甲壳类动物", "value": "CRUSTACEAN", "sort": 2},
            {"label": "鱼类", "value": "FISH", "sort": 3},
            {"label": "蛋类", "value": "EGG", "sort": 4},
            {"label": "花生", "value": "PEANUT", "sort": 5},
            {"label": "大豆", "value": "SOYBEAN", "sort": 6},
            {"label": "乳及乳制品", "value": "MILK", "sort": 7},
            {"label": "坚果", "value": "NUTS", "sort": 8},
            {"label": "芹菜", "value": "CELERY", "sort": 9},
            {"label": "芥末", "value": "MUSTARD", "sort": 10},
            {"label": "芝麻", "value": "SESAME", "sort": 11},
            {"label": "二氧化硫/亚硫酸盐", "value": "SULFITE", "sort": 12},
            {"label": "羽扇豆", "value": "LUPIN", "sort": 13},
            {"label": "软体动物", "value": "MOLLUSC", "sort": 14},
        ],
    },
    {
        "type_code": "food_additive_type",
        "type_name": "食品添加剂类型",
        "items": [
            {"label": "防腐剂", "value": "PRESERVATIVE", "sort": 1},
            {"label": "抗氧化剂", "value": "ANTIOXIDANT", "sort": 2},
            {"label": "着色剂", "value": "COLORANT", "sort": 3},
            {"label": "甜味剂", "value": "SWEETENER", "sort": 4},
            {"label": "增味剂", "value": "FLAVOR_ENHANCER", "sort": 5},
            {"label": "乳化剂", "value": "EMULSIFIER", "sort": 6},
            {"label": "增稠剂", "value": "THICKENER", "sort": 7},
            {"label": "膨松剂", "value": "LEAVENING", "sort": 8},
            {"label": "凝固剂", "value": "COAGULANT", "sort": 9},
            {"label": "水分保持剂", "value": "HUMECTANT", "sort": 10},
            {"label": "酸度调节剂", "value": "PH_REGULATOR", "sort": 11},
            {"label": "酶制剂", "value": "ENZYME", "sort": 12},
        ],
    },
    {
        "type_code": "food_certification",
        "type_name": "认证证书",
        "items": [
            {"label": "SC生产许可", "value": "SC", "sort": 1},
            {"label": "ISO 22000", "value": "ISO22000", "sort": 2},
            {"label": "HACCP", "value": "HACCP", "sort": 3},
            {"label": "BRC", "value": "BRC", "sort": 4},
            {"label": "IFS", "value": "IFS", "sort": 5},
            {"label": "FSSC 22000", "value": "FSSC22000", "sort": 6},
            {"label": "清真(Halal)", "value": "HALAL", "sort": 10},
            {"label": "犹太(Kosher)", "value": "KOSHER", "sort": 11},
            {"label": "有机", "value": "ORGANIC", "sort": 12},
            {"label": "绿色食品", "value": "GREEN_FOOD", "sort": 13},
            {"label": "无公害", "value": "POLLUTION_FREE", "sort": 14},
        ],
    },
]


def get_all_seed_data() -> dict[str, Any]:
    return {
        "processes": FOOD_PROCESSES,
        "inspection_templates": FOOD_INSPECTION_TEMPLATES,
        "defect_codes": FOOD_DEFECT_CODES,
        "dictionaries": FOOD_DICTIONARIES,
    }