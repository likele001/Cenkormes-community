"""
汽车零部件行业包 — 种子数据

包含：
1. 标准工序模板（IATF 16949 体系下的汽车零部件典型工艺）
2. 质检模板（来料/IPQC/出厂/客户审核）
3. 缺陷代码（外观/尺寸/功能/装配/材质）
4. 行业字典（零件类型/客户体系/认证/SPC控制图类型）
"""

from typing import Any


# ============================================================
# 1. 标准工序模板
# ============================================================
AUTO_PARTS_PROCESSES = [
    # ------ 准备阶段 ------
    {"code": "AUTO_PPAP", "name": "PPAP生产件批准", "workshop": "技术质量部", "std_minutes": 14400},
    {"code": "AUTO_APQP", "name": "APQP先期策划", "workshop": "项目部", "std_minutes": 43200},
    {"code": "AUTO_FMEA", "name": "FMEA分析", "workshop": "技术质量部", "std_minutes": 2880},
    {"code": "AUTO_MSA", "name": "MSA测量系统分析", "workshop": "技术质量部", "std_minutes": 480},
    # ------ 原材料 ------
    {"code": "AUTO_RAW_INSP", "name": "来料检验", "workshop": "来料检验室", "std_minutes": 20},
    {"code": "AUTO_RAW_STORE", "name": "原材料入库", "workshop": "原材料仓", "std_minutes": 10},
    # ------ 机加工 ------
    {"code": "AUTO_CNC", "name": "CNC加工", "workshop": "机加工车间", "std_minutes": 30},
    {"code": "AUTO_LATHE", "name": "车削加工", "workshop": "机加工车间", "std_minutes": 20},
    {"code": "AUTO_MILLING", "name": "铣削加工", "workshop": "机加工车间", "std_minutes": 25},
    {"code": "AUTO_GRINDING", "name": "磨削加工", "workshop": "机加工车间", "std_minutes": 15},
    {"code": "AUTO_DEBURR", "name": "去毛刺", "workshop": "后加工车间", "std_minutes": 5},
    # ------ 表面处理 ------
    {"code": "AUTO_HEAT_TREAT", "name": "热处理", "workshop": "热处理车间", "std_minutes": 180},
    {"code": "AUTO_PLATING", "name": "电镀", "workshop": "表面处理车间", "std_minutes": 60},
    {"code": "AUTO_PAINTING", "name": "喷涂", "workshop": "涂装车间", "std_minutes": 30},
    {"code": "AUTO_PHOSPHATING", "name": "磷化", "workshop": "表面处理车间", "std_minutes": 30},
    {"code": "AUTO_BLACKEN", "name": "发黑/氧化", "workshop": "表面处理车间", "std_minutes": 45},
    # ------ 装配 ------
    {"code": "AUTO_SUB_ASSEMBLY", "name": "分总成装配", "workshop": "装配车间", "std_minutes": 20},
    {"code": "AUTO_FINAL_ASSEMBLY", "name": "总成装配", "workshop": "装配车间", "std_minutes": 30},
    {"code": "AUTO_PRESS_FIT", "name": "压装", "workshop": "装配车间", "std_minutes": 10},
    {"code": "AUTO_RIVETING", "name": "铆接", "workshop": "装配车间", "std_minutes": 8},
    {"code": "AUTO_WELDING_SPOT", "name": "点焊", "workshop": "焊接车间", "std_minutes": 5},
    {"code": "AUTO_WELDING_ROBOT", "name": "机器人焊接", "workshop": "焊接车间", "std_minutes": 15},
    {"code": "AUTO_BRAZING", "name": "钎焊", "workshop": "焊接车间", "std_minutes": 20},
    # ------ 检验 ------
    {"code": "AUTO_FAI", "name": "首件检验(FAI)", "workshop": "技术质量部", "std_minutes": 30},
    {"code": "AUTO_IPQC", "name": "过程巡检(IPQC)", "workshop": "技术质量部", "std_minutes": 15},
    {"code": "AUTO_SPC", "name": "SPC统计过程控制", "workshop": "技术质量部", "std_minutes": 20},
    {"code": "AUTO_OQC", "name": "出厂检验(OQC)", "workshop": "技术质量部", "std_minutes": 20},
    {"code": "AUTO_AUDIT", "name": "过程审核(VDA6.3)", "workshop": "技术质量部", "std_minutes": 240},
    # ------ 防错 ------
    {"code": "AUTO_POKA_YOKE", "name": "防错验证", "workshop": "技术质量部", "std_minutes": 10},
    {"code": "AUTO_8D_REPORT", "name": "8D报告处理", "workshop": "技术质量部", "std_minutes": 480},
    # ------ 包装与发货 ------
    {"code": "AUTO_TRACE_LABEL", "name": "追溯标签", "workshop": "包装车间", "std_minutes": 2},
    {"code": "AUTO_PACK", "name": "包装", "workshop": "包装车间", "std_minutes": 10},
    {"code": "AUTO_SHIP", "name": "发货", "workshop": "物流部", "std_minutes": 30},
]


# ============================================================
# 2. 质检模板
# ============================================================
AUTO_PARTS_INSPECTION_TEMPLATES = [
    {
        "code": "AUTO_FAI",
        "name": "首件检验FAI报告",
        "description": "PPAP/小批量/工艺变更后的首件全尺寸+功能+材料检验",
        "items": [
            {"seq": 1, "item_name": "尺寸报告", "item_type": "pass_fail", "standard_value": "全尺寸100%合格", "is_required": True},
            {"seq": 2, "item_name": "材料报告", "item_type": "pass_fail", "standard_value": "材质证明齐全", "is_required": True},
            {"seq": 3, "item_name": "外观报告", "item_type": "pass_fail", "standard_value": "无缺陷", "is_required": True},
            {"seq": 4, "item_name": "性能测试", "item_type": "pass_fail", "standard_value": "符合技术规范", "is_required": True},
            {"seq": 5, "item_name": "金相检验", "item_type": "pass_fail", "standard_value": "符合图纸要求", "is_required": False},
            {"seq": 6, "item_name": "硬度", "item_type": "measure", "standard_value": "", "upper_limit": "62", "lower_limit": "55", "unit": "HRC", "is_required": False},
            {"seq": 7, "item_name": "粗糙度", "item_type": "measure", "standard_value": "", "upper_limit": "0.8", "lower_limit": "0", "unit": "μm", "is_required": False},
        ],
    },
    {
        "code": "AUTO_IPQC",
        "name": "过程巡检IPQC",
        "description": "生产过程中的尺寸/外观/SPC监控",
        "items": [
            {"seq": 1, "item_name": "关键尺寸", "item_type": "measure", "standard_value": "见控制计划", "is_required": True},
            {"seq": 2, "item_name": "外观缺陷", "item_type": "pass_fail", "standard_value": "无裂纹/锈蚀/变形", "is_required": True},
            {"seq": 3, "item_name": "SPC数据采集", "item_type": "pass_fail", "standard_value": "Cpk≥1.33", "is_required": True},
            {"seq": 4, "item_name": "设备参数", "item_type": "pass_fail", "standard_value": "符合工艺规范", "is_required": True},
            {"seq": 5, "item_name": "刀具/模具状态", "item_type": "pass_fail", "standard_value": "在寿命内", "is_required": True},
            {"seq": 6, "item_name": "首末件对比", "item_type": "pass_fail", "standard_value": "尺寸一致", "is_required": True},
        ],
    },
    {
        "code": "AUTO_RAW_INSP",
        "name": "来料检验",
        "description": "原材料/外购件入库检验",
        "items": [
            {"seq": 1, "item_name": "材质证明", "item_type": "pass_fail", "standard_value": "合格证/质保书齐全", "is_required": True},
            {"seq": 2, "item_name": "外观检验", "item_type": "pass_fail", "standard_value": "无缺陷/损伤/锈蚀", "is_required": True},
            {"seq": 3, "item_name": "关键尺寸", "item_type": "measure", "standard_value": "符合图纸", "is_required": True},
            {"seq": 4, "item_name": "批次一致性", "item_type": "pass_fail", "standard_value": "批次号一致", "is_required": True},
            {"seq": 5, "item_name": "包装防护", "item_type": "pass_fail", "standard_value": "防护到位", "is_required": True},
            {"seq": 6, "item_name": "化学成分", "item_type": "pass_fail", "standard_value": "符合牌号要求", "is_required": False},
        ],
    },
    {
        "code": "AUTO_OQC",
        "name": "出厂检验",
        "description": "成品批次放行前的综合检验",
        "items": [
            {"seq": 1, "item_name": "全尺寸检验", "item_type": "pass_fail", "standard_value": "符合图纸", "is_required": True},
            {"seq": 2, "item_name": "外观100%", "item_type": "pass_fail", "standard_value": "无缺陷", "is_required": True},
            {"seq": 3, "item_name": "性能测试", "item_type": "pass_fail", "standard_value": "全部合格", "is_required": True},
            {"seq": 4, "item_name": "扭矩验证", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "N·m", "is_required": False},
            {"seq": 5, "item_name": "气密/水密", "item_type": "pass_fail", "standard_value": "无泄漏", "is_required": False},
            {"seq": 6, "item_name": "追溯标签", "item_type": "pass_fail", "standard_value": "齐全可读", "is_required": True},
            {"seq": 7, "item_name": "包装防护", "item_type": "pass_fail", "standard_value": "符合客户要求", "is_required": True},
        ],
    },
    {
        "code": "AUTO_SPC_MONITOR",
        "name": "SPC监控记录",
        "description": "关键特性的统计过程控制数据记录",
        "items": [
            {"seq": 1, "item_name": "样本量", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "5", "unit": "件", "is_required": True},
            {"seq": 2, "item_name": "子组频率", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "1", "unit": "次/h", "is_required": True},
            {"seq": 3, "item_name": "均值Xbar", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 4, "item_name": "极差R", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "", "unit": "mm", "is_required": True},
            {"seq": 5, "item_name": "Cpk值", "item_type": "measure", "standard_value": "", "upper_limit": "", "lower_limit": "1.33", "unit": "", "is_required": True},
            {"seq": 6, "item_name": "控制图判异", "item_type": "pass_fail", "standard_value": "无8种判异准则", "is_required": True},
        ],
    },
    {
        "code": "AUTO_CUSTOMER_AUDIT",
        "name": "客户审核",
        "description": "OEM客户审核（IATF/VDA/Q1等）",
        "items": [
            {"seq": 1, "item_name": "质量体系", "item_type": "pass_fail", "standard_value": "IATF 16949有效", "is_required": True},
            {"seq": 2, "item_name": "过程能力", "item_type": "pass_fail", "standard_value": "Cpk/Ppk达标", "is_required": True},
            {"seq": 3, "item_name": "PPAP资料", "item_type": "pass_fail", "standard_value": "完整有效", "is_required": True},
            {"seq": 4, "item_name": "变更管理", "item_type": "pass_fail", "standard_value": "客户批准", "is_required": True},
            {"seq": 5, "item_name": "问题整改", "item_type": "pass_fail", "standard_value": "8D闭环", "is_required": True},
            {"seq": 6, "item_name": "交付绩效", "item_type": "pass_fail", "standard_value": "OTD≥98%", "is_required": False},
        ],
    },
]


# ============================================================
# 3. 缺陷代码
# ============================================================
AUTO_PARTS_DEFECT_CODES = [
    # ------ 尺寸类 ------
    {"code": "A001", "name": "尺寸超差", "severity": "critical", "description": "关键/重要尺寸超出公差"},
    {"code": "A002", "name": "形位公差超差", "severity": "major", "description": "圆度/平行度/垂直度等超差"},
    {"code": "A003", "name": "粗糙度不足", "severity": "major", "description": "表面粗糙度未达要求"},
    {"code": "A004", "name": "锥度/鼓形", "severity": "major", "description": "圆柱度不合格"},
    # ------ 外观类 ------
    {"code": "A011", "name": "裂纹", "severity": "critical", "description": "表面/内部裂纹"},
    {"code": "A012", "name": "划伤/碰伤", "severity": "major", "description": "表面机械损伤"},
    {"code": "A013", "name": "锈蚀/氧化", "severity": "major", "description": "表面发生锈蚀或异常氧化"},
    {"code": "A014", "name": "凹坑", "severity": "major", "description": "表面凹陷"},
    {"code": "A015", "name": "毛刺/飞边", "severity": "minor", "description": "机加工/冲压残留"},
    {"code": "A016", "name": "色差", "severity": "minor", "description": "表面颜色不一致"},
    # ------ 装配类 ------
    {"code": "A021", "name": "装配干涉", "severity": "critical", "description": "装配时零件干涉"},
    {"code": "A022", "name": "过盈/间隙不当", "severity": "critical", "description": "配合尺寸不符"},
    {"code": "A023", "name": "错装/漏装", "severity": "critical", "description": "零件错装或漏装"},
    {"code": "A024", "name": "螺栓扭矩异常", "severity": "critical", "description": "紧固扭矩超标"},
    {"code": "A025", "name": "焊接缺陷", "severity": "critical", "description": "焊缝气孔/裂纹/未焊透"},
    # ------ 材质/性能 ------
    {"code": "A031", "name": "材质不符", "severity": "critical", "description": "材料牌号与图纸不符"},
    {"code": "A032", "name": "硬度异常", "severity": "major", "description": "热处理硬度异常"},
    {"code": "A033", "name": "渗层/镀层不足", "severity": "major", "description": "表面处理层厚度不足"},
    {"code": "A034", "name": "性能测试不合格", "severity": "critical", "description": "强度/疲劳/密封等测试失败"},
    # ------ 标识追溯 ------
    {"code": "A041", "name": "追溯标识缺失", "severity": "critical", "description": "批次/序列号无法追溯"},
    {"code": "A042", "name": "标识错误", "severity": "major", "description": "零件号/批次号打错"},
    {"code": "A043", "name": "批次混料", "severity": "critical", "description": "不同批次混料"},
    # ------ 包装类 ------
    {"code": "A051", "name": "包装破损", "severity": "major", "description": "运输包装破损"},
    {"code": "A052", "name": "防护不当", "severity": "minor", "description": "防锈/防震防护不到位"},
    {"code": "A053", "name": "装箱数量错", "severity": "major", "description": "装箱数量与箱唛不符"},
]


# ============================================================
# 4. 行业字典
# ============================================================
AUTO_PARTS_DICTIONARIES = [
    {
        "type_code": "auto_part_type",
        "type_name": "汽车零部件类型",
        "items": [
            {"label": "发动机零部件", "value": "ENGINE", "sort": 1},
            {"label": "变速箱零部件", "value": "TRANSMISSION", "sort": 2},
            {"label": "底盘零部件", "value": "CHASSIS", "sort": 3},
            {"label": "车身零部件", "value": "BODY", "sort": 4},
            {"label": "制动系统", "value": "BRAKE", "sort": 10},
            {"label": "转向系统", "value": "STEERING", "sort": 11},
            {"label": "悬挂系统", "value": "SUSPENSION", "sort": 12},
            {"label": "电气系统", "value": "ELECTRICAL", "sort": 20},
            {"label": "内饰件", "value": "INTERIOR", "sort": 30},
            {"label": "外饰件", "value": "EXTERIOR", "sort": 31},
            {"label": "紧固件", "value": "FASTENER", "sort": 40},
            {"label": "密封件", "value": "SEAL", "sort": 41},
            {"label": "管路件", "value": "PIPE", "sort": 42},
            {"label": "新能源专用件", "value": "NEV", "sort": 50},
            {"label": "智能驾驶件", "value": "ADAS", "sort": 51},
        ],
    },
    {
        "type_code": "auto_customer_oem",
        "type_name": "主机厂客户",
        "items": [
            {"label": "一汽集团", "value": "FAW", "sort": 1},
            {"label": "上汽集团", "value": "SAIC", "sort": 2},
            {"label": "东风汽车", "value": "DFM", "sort": 3},
            {"label": "长安汽车", "value": "CHANGAN", "sort": 4},
            {"label": "广汽集团", "value": "GAC", "sort": 5},
            {"label": "北汽集团", "value": "BAIC", "sort": 6},
            {"label": "吉利汽车", "value": "GEELY", "sort": 7},
            {"label": "比亚迪", "value": "BYD", "sort": 8},
            {"label": "长城汽车", "value": "GWM", "sort": 9},
            {"label": "奇瑞汽车", "value": "CHERY", "sort": 10},
            {"label": "特斯拉", "value": "TESLA", "sort": 20},
            {"label": "大众", "value": "VW", "sort": 21},
            {"label": "丰田", "value": "TOYOTA", "sort": 22},
            {"label": "通用", "value": "GM", "sort": 23},
            {"label": "福特", "value": "FORD", "sort": 24},
            {"label": "宝马", "value": "BMW", "sort": 25},
            {"label": "奔驰", "value": "BENZ", "sort": 26},
            {"label": "奥迪", "value": "AUDI", "sort": 27},
        ],
    },
    {
        "type_code": "auto_certification",
        "type_name": "认证体系",
        "items": [
            {"label": "IATF 16949", "value": "IATF16949", "sort": 1},
            {"label": "ISO 9001", "value": "ISO9001", "sort": 2},
            {"label": "ISO 14001", "value": "ISO14001", "sort": 3},
            {"label": "VDA 6.3", "value": "VDA63", "sort": 10},
            {"label": "VDA 6.5", "value": "VDA65", "sort": 11},
            {"label": "BIQS(通用)", "value": "BIQS", "sort": 12},
            {"label": "Q1(福特)", "value": "Q1", "sort": 13},
            {"label": "Formel Q(大众)", "value": "FORMEL_Q", "sort": 14},
            {"label": "MMOG/LE", "value": "MMOG", "sort": 15},
            {"label": "CSR", "value": "CSR", "sort": 16},
        ],
    },
    {
        "type_code": "auto_spc_chart",
        "type_name": "SPC控制图类型",
        "items": [
            {"label": "Xbar-R(均值极差)", "value": "XBAR_R", "sort": 1},
            {"label": "Xbar-S(均值标准差)", "value": "XBAR_S", "sort": 2},
            {"label": "I-MR(单值移动极差)", "value": "I_MR", "sort": 3},
            {"label": "P图(不合格品率)", "value": "P_CHART", "sort": 4},
            {"label": "NP图(不合格品数)", "value": "NP_CHART", "sort": 5},
            {"label": "C图(缺陷数)", "value": "C_CHART", "sort": 6},
            {"label": "U图(单位缺陷数)", "value": "U_CHART", "sort": 7},
            {"label": "EWMA(指数加权)", "value": "EWMA", "sort": 10},
        ],
    },
    {
        "type_code": "auto_ppap_level",
        "type_name": "PPAP提交等级",
        "items": [
            {"label": "Level 1 - 仅PSW", "value": "L1", "sort": 1},
            {"label": "Level 2 - PSW+有限项目", "value": "L2", "sort": 2},
            {"label": "Level 3 - PSW+客户指定项目", "value": "L3", "sort": 3, "is_default": True},
            {"label": "Level 4 - PSW+客户定义要求", "value": "L4", "sort": 4},
            {"label": "Level 5 - 全部项目+样本", "value": "L5", "sort": 5},
        ],
    },
]


def get_all_seed_data() -> dict[str, Any]:
    return {
        "processes": AUTO_PARTS_PROCESSES,
        "inspection_templates": AUTO_PARTS_INSPECTION_TEMPLATES,
        "defect_codes": AUTO_PARTS_DEFECT_CODES,
        "dictionaries": AUTO_PARTS_DICTIONARIES,
    }