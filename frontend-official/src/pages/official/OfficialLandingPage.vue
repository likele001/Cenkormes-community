<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useHead } from '@unhead/vue'
import { usePageSeo } from '@/composables/useSeo'
import { useSiteConfig } from '@/composables/useSiteConfig'
import { saasPlans } from '@/data/official-content'

const h5Url = 'https://h5.mes.cenkor.cn'
const communityUrl = 'https://github.com/likele001/Cenkormes-community'
const trialUrl = 'https://admin.mes.cenkor.cn/register/'
const { contact, fetchContact } = useSiteConfig()
const salesWechat = computed(() => contact.value.wechat || '')
const salesPhone = computed(() => contact.value.phone || '')
const salesEmail = computed(() => contact.value.email || '')
const showWechatPanel = ref(false)
const copied = ref(false)

onMounted(() => {
  fetchContact()
})

const heroHighlights = [
  { label: '扫码报工', desc: '手机扫码录入产量，照片留痕' },
  { label: '自动算薪', desc: '审核通过自动计件工资' },
  { label: 'AI 智能报工', desc: '照片计数、缺陷分类、语音输入' },
  { label: '模具管理', desc: '模具档案、保养计划、工序绑定' },
  { label: 'CRM 客户', desc: '客户档案、商机、公海、跟进' },
  { label: '仓储库存', desc: '出入库、盘点、安全库存预警' },
  { label: '外协加工', desc: '外协订单、报工与对账管理' },
  { label: 'SPC 质量', desc: '工序能力分析、控制图监控' },
]

const painPoints = [
  { title: '微信群报工，月底全靠回忆', desc: '产量、合格、不良、照片散在不同群和聊天记录里，月底想回看一条都翻半天，员工和班组长经常对不上数。' },
  { title: 'Excel 算计件工资，加班对到崩溃', desc: '一个工人一个月几十张单子，工序、单价、补贴、扣款全靠手算，算错一次就是一次扯皮，员工不信任、老板背锅。' },
  { title: '订单进度不透明，老板天天追问', desc: '客户来电话问交期，只能挨个打电话问车间组长，订单卡在哪一道工序、还差多少件、谁在做，全靠人脑记。' },
  { title: '出了质量问题，根本查不到根', desc: '客户投诉一批货，想知道是哪个工人、哪台机、哪批料做的，翻不到记录，只能集体担责或者下次注意。' },
  { title: '客户资料散在销售手机里', desc: '客户名单、跟进记录、报价历史都在销售微信或脑子里，人一走客户就断，公海客户没人跟也发现不了。' },
  { title: '想上系统又被报价吓退', desc: '随便问一家就是十几万、几十万，实施半年起步，小厂用不起，大功能也用不上，最后回到 Excel 和微信群。' },
]

const advantageGroups = [
  {
    group: '生产管理', color: '#2563eb',
    items: [
      { title: '扫码报工', desc: '一码一任务，手机扫码录入合格/不良数量，拍照留痕，提交后显示预估工资。' },
      { title: '两级审核', desc: '班组长初审 + 质检终审，驳回必须填原因，重报有记录可追溯。' },
      { title: '甘特排产', desc: '甘特图拖拽排产，智能派工到人，齐套检查提示缺料，任务码批量打印推送。' },
      { title: '生产看板', desc: '车间大屏实时滚动产量、良率和异常，订单全生命周期追踪。' },
      { title: '质量溯源', desc: '一物一码，扫成品反查物料批次、操作人、设备、时间和质检记录。' },
      { title: '客户下单', desc: '客户 H5 自助浏览型号、选数量交期、下单，进度自己查。' },
      { title: '模具管理', desc: '模具档案、保养计划、保养执行记录、工序绑定，模具寿命预警。' },
      { title: '质检模板', desc: '自定义质检项目，支持合格/不合格/测量/文本四种类型，模板复用。' },
      { title: '缺陷代码', desc: '缺陷分类与严重程度管理，报工/质检时快速标记缺陷原因。' },
      { title: '审批流程', desc: '自定义多级审核步骤，配置审核人角色，订单/报工/工资灵活适配。' },
      { title: '排班管理', desc: '班次规则定义、员工排班日历、自动统计工时与考勤。' },
      { title: '外协管理', desc: '外协订单分发、外协报工录入、外协对账与结算。' },
      { title: 'SPC 质量图表', desc: 'Xbar-R 控制图、工序能力 CPK 分析，实时监控质量稳定性。' },
    ],
  },
  {
    group: 'AI 智能中心', color: '#7c3aed',
    items: [
      { title: '工厂助手', desc: '基于生产数据的 AI 问答，问产量、问进度、问异常，直接给答案。' },
      { title: '数据预警', desc: '产能负荷异常、良率下滑、交期临近自动预警，不用人盯数据。' },
      { title: '智能分析', desc: 'AI 自动分析产量趋势、工序瓶颈、人员效率，给出改进建议。' },
      { title: '操作指引', desc: '系统内置智能帮助，新员工遇到问题直接问 AI，不靠老员工带。' },
      { title: 'AI 照片计数', desc: '报工上传照片后 AI 自动识别产品数量，免去手动清点输入。' },
      { title: 'AI 缺陷分类', desc: '上传不良品照片，AI 自动识别缺陷类型，辅助质检决策。' },
      { title: '语音报工', desc: '语音输入产量数据，系统语音播报确认结果，双手不离开工件。' },
      { title: 'AI 员工中心', desc: 'AI 虚拟员工辅助管理，自动分配任务、跟踪执行、异常上报。' },
    ],
  },
  {
    group: '经营与协同', color: '#0891b2',
    items: [
      { title: '计件工资', desc: '型号 × 工序工价，审核通过自动入工资，补贴扣款单独项，月底一键生成工资条。' },
      { title: '时薪管理', desc: '按时计薪、加班倍率设置、工时统计，适合非计件岗位。' },
      { title: 'CRM 客户管理', desc: '客户档案、联系人、销售机会、公海池、客户标签、售后跟进，商机转订单。' },
      { title: '人事管理', desc: '组织架构、员工档案、技能标签、GPS 考勤打卡（可选地理围栏）。' },
      { title: '仓储库存', desc: '仓库管理、出入库、退货、库存流水、安全库存预警，和采购、订单联动。' },
      { title: '采购管理', desc: '采购单、入库、退货、供应商管理、采购对账。' },
      { title: '出货管理', desc: '出库单管理、发货跟踪、客户签收确认，与订单自动关联。' },
      { title: '财务管理', desc: '客户对账单、收支流水、成本毛利分析，数据从订单和报工自动汇总。' },
      { title: '设备管理', desc: '设备档案、日常点检、保养计划与保养记录，维护日期自动联动。' },
      { title: '数据报表', desc: '产量/良率/工序排行/日报趋势，ECharts 图表，老板移动端随时看。' },
    ],
  },
]

const compareRows = [
  ['月底算工资', '加班对账 1-3 天，错算扯皮', '审核通过自动算，几分钟出表'],
  ['老板看进度', '打电话问车间', '手机随时看订单和工序'],
  ['员工报工', '微信群发数字，没凭证', '扫码 + 完工照片，留痕可查'],
  ['质量追溯', '出问题翻不到记录', '扫成品码反查整链'],
  ['客户管理', '名单在销售微信里', 'CRM 统一管理，公海回收'],
  ['库存进出', '月底盘才知道差了', '出入库实时，库存预警'],
  ['模具保养', '坏了才知道该保养了', '到期提醒，保养记录可查'],
  ['外协管理', '电话微信来回确认', '系统下单、报工、对账一体'],
  ['AI 分析', '靠人盯报表', 'AI 自动预警、分析、建议'],
  ['上线周期', '半年起步，预算十几万', '几天到两周，按需部署'],
]

const whySourceCode = [
  { saas: '数据在别人服务器，心里不踏实', source: '源码部署在自己服务器，数据不出厂' },
  { saas: '按月扣费，用久了比买源码贵', source: '年费 ¥2800 起，成本可控' },
  { saas: '停服了数据就没了', source: '源码在手，永久可用' },
  { saas: '功能改不了，等厂商排期', source: '有源码可以自己改或找人改' },
  { saas: '工厂数据外泄风险', source: '私有部署，自己管控安全' },
  { saas: '绑定一家服务商，换不了', source: '源码交付，自由迁移' },
]

const deliverables = [
  { deliver: '完整源码（前端 + 后端）', extra: '服务器购买和配置' },
  { deliver: '一年内版本更新', extra: '域名和 SSL 证书' },
  { deliver: 'GitHub 私有仓库权限', extra: '系统安装和部署' },
  { deliver: '基础部署文档', extra: '数据导入和培训' },
  { deliver: '微信技术支持群', extra: '定制开发' },
]

const featureCompare = [
  { name: '扫码报工', community: true, pro: true },
  { name: '派工管理', community: true, pro: true },
  { name: '报工审核', community: true, pro: true },
  { name: '工单列表', community: true, pro: true },
  { name: '计件工资', community: false, pro: true },
  { name: '工资条签名', community: false, pro: true },
  { name: 'CRM 客户管理', community: false, pro: true },
  { name: '模具管理', community: false, pro: true },
  { name: '质检模板', community: false, pro: true },
  { name: '缺陷代码', community: false, pro: true },
  { name: '审批流程', community: false, pro: true },
  { name: '排班管理', community: false, pro: true },
  { name: '外协管理', community: false, pro: true },
  { name: 'SPC 质量图表', community: false, pro: true },
  { name: '时薪管理', community: false, pro: true },
  { name: '出货管理', community: false, pro: true },
  { name: 'AI 工厂助手', community: false, pro: true },
  { name: 'AI 数据预警', community: false, pro: true },
  { name: 'AI 照片计数', community: false, pro: true },
  { name: 'AI 缺陷分类', community: false, pro: true },
  { name: '语音报工', community: false, pro: true },
  { name: 'AI 员工中心', community: false, pro: true },
  { name: '仓储库存', community: false, pro: true },
  { name: '采购管理', community: false, pro: true },
  { name: '财务管理', community: false, pro: true },
  { name: '设备管理', community: false, pro: true },
  { name: '甘特排产', community: false, pro: true },
  { name: '客户自助下单', community: false, pro: true },
  { name: '数据报表', community: false, pro: true },
  { name: '微信小程序', community: false, pro: true },
  { name: '用户数', community: '≤5', pro: '不限' },
  { name: 'SKU 数', community: '≤20', pro: '不限' },
  { name: '工序数', community: '≤10', pro: '不限' },
]

const closingSteps = [
  { title: '创建订单', desc: '后台建单或客户 H5 自助下单，系统自动按工艺分解出工单和任务。' },
  { title: '排产派工', desc: '甘特图排产，按员工技能和负荷智能派工，每个任务生成唯一二维码。' },
  { title: '扫码报工', desc: '员工手机扫任务码，填合格 / 不良数量，拍照留证据，提交即看到预估工资。' },
  { title: '审核算薪', desc: '班组长初审、质检终审，通过即计入工资，月底一键导工资条，员工手机签字。' },
]

const allModules = [
  '产品管理', 'SKU 型号', '工序工价', '订单管理', '生产计划', '甘特排产',
  '派工管理', '扫码报工', '两级审核', '生产看板', '质量溯源', '客户下单',
  '模具管理', '模具保养', '工序绑定', '质检模板', '缺陷代码', '审批流程',
  '排班管理', '外协管理', 'SPC 质量图表',
  '计件工资', '时薪管理', '工资条签名',
  'CRM 客户', '销售机会', '公海池', '客户标签',
  '人事管理', '考勤打卡', '技能标签',
  '仓储库存', '出入库', '安全库存', '出货管理',
  '采购管理', '供应商管理', '对账单',
  '财务管理', '收支流水', '成本毛利',
  '设备管理', '点检保养',
  'AI 工厂助手', 'AI 数据预警', 'AI 智能分析',
  'AI 照片计数', 'AI 缺陷分类', '语音报工', 'AI 员工中心',
  '微信小程序', '数据报表',
]

const industries = ['五金加工', '钣金加工', '注塑加工', '服装加工', '家具定制', '电子装配', '包装印刷', '机械零件加工', '金属制品', '食品加工']

const trustCases = [
  { tag: '五金加工 · 35 人', quote: '以前月底算工资要 2 天，现在 10 分钟出表。', author: '东莞某精密五金厂 王厂长' },
  { tag: '注塑加工 · 80 人', quote: '扫码报工工人 5 分钟学会，车间主任说早知道就早上了。', author: '苏州某注塑厂 李总' },
  { tag: '电子装配 · 50 人', quote: '客户要追溯码，上了之后客户说比大厂还规范。', author: '深圳某电子装配厂 张经理' },
]

const galleryTabs = [
  { id: 'manufacturing', label: '生产管理' },
  { id: 'sales', label: '销售 CRM' },
  { id: 'finance', label: '财务库存' },
]
const galleryActive = ref('manufacturing')
const galleryImages: Record<string, Array<{ src: string; label: string }>> = {
  manufacturing: [
    { src: '/screenshots/gallery/01-首页.png', label: '管理后台首页' },
    { src: '/screenshots/gallery/03-大屏显示.png', label: '车间数据大屏' },
    { src: '/screenshots/gallery/45-生产排程-工单.png', label: '生产排程 · 工单' },
    { src: '/screenshots/gallery/54-报工管理.png', label: '扫码报工管理' },
    { src: '/screenshots/gallery/55-工资核算.png', label: '计件工资核算' },
    { src: '/screenshots/gallery/35-工序工价.png', label: '工序工价配置' },
    { src: '/screenshots/gallery/57-溯源查询.png', label: '质量溯源查询' },
    { src: '/screenshots/gallery/27-产品管理.png', label: '产品基础库' },
  ],
  sales: [
    { src: '/screenshots/gallery/44-客户订单.png', label: '客户订单管理' },
    { src: '/screenshots/gallery/38-销售漏斗.png', label: '销售漏斗分析' },
  ],
  finance: [
    { src: '/screenshots/gallery/58-库存管理.png', label: '仓储库存管理' },
    { src: '/screenshots/gallery/60-设备管理.png', label: '设备点检保养' },
  ],
}

const plans = [
  { name: 'Community 社区版', price: '免费', suffix: '开源', desc: '扫码报工、派工、审核，适合小团队先跑通核心流程。', features: ['扫码报工 + H5 派工', '班组长初审', '基础订单和工单', '5 人 / 20 SKU / 10 工序限制', 'GitHub 公开仓库，自行下载部署'], cta: '免费下载', href: communityUrl },
  { name: 'Pro 商业版', price: '¥2800', suffix: '/ 年', desc: '全功能源码，无限制，一年更新。生产、CRM、AI、模具、外协、仓储、财务全覆盖。', features: ['全部 46+ 个功能模块', '无限用户 / SKU / 工序', '一年内版本更新', 'GitHub 私有仓库权限', '源码交付，私有部署'], highlight: true, cta: '获取 Pro 报价', href: null },
  { name: 'Pro + 标准实施', price: '¥3800', suffix: '/ 年', desc: '源码 + 远程部署 + 数据导入 + 培训，确保工厂真正用起来。', features: ['包含 Pro 全部内容', '远程安装部署', '基础数据导入', '管理员 / 班组长培训', '试运行陪跑'], cta: '预约实施', href: null },
]

const rollout = [
  { step: 1, title: '聊清楚流程', desc: '了解你的产品、工序、工价规则，确认上线范围。' },
  { step: 2, title: '配置基础数据', desc: '产品 / SKU / 工序 / 工价 / 人员 / 权限一次性配齐。' },
  { step: 3, title: '导入历史数据', desc: '订单、客户、库存、工资基础数据可批量导入。' },
  { step: 4, title: '培训三类角色', desc: '管理员、班组长、一线员工分别培训，半小时学会。' },
  { step: 5, title: '一个车间试跑', desc: '先选一条产线或一个车间跑一周，发现问题立即调。' },
  { step: 6, title: '正式上线扩展', desc: '试跑没问题再扩到全厂，可分批接入业务模块。' },
]

const faqs = [
  { q: '社区版和 Pro 版有什么区别？', a: '社区版免费开源，包含扫码报工、派工、审核核心流程，但有 5 人 / 20 SKU / 10 工序限制，不含工资、CRM、AI、仓储、财务等模块。Pro 版全功能无限制，源码交付。' },
  { q: '源码怎么交付？', a: '购买 Pro 后开通 GitHub 私有仓库权限，源码直接克隆。一年内免费更新，到期可续费。' },
  { q: '部署谁来做？', a: '源码交付不包含部署，需要自己有服务器或找运维。Pro + 实施版包含远程部署和培训，另外也可以单独购买部署服务。' },
  { q: '数据放在你们服务器还是我们自己的？', a: '源码部署在你自己的服务器上，数据完全在工厂内部。我们不托管任何客户数据。' },
  { q: 'AI 功能需要额外付费吗？', a: 'AI 工厂助手、数据预警、智能分析是 Pro 版内置功能，不需要额外付费。需要接入外部大模型的按配置接入。' },
  { q: '能不能先免费试一下再决定？', a: '可以。社区版免费开源，5 人以内可跑通扫码报工和审核流程。也可以在线试用体验系统。觉得合适再购买 Pro 商业版源码。' },
  { q: 'Pro 版相比之前新增了哪些模块？', a: '最近新增了模具管理（档案/保养/工序绑定）、质检模板（自定义质检项目）、缺陷代码（分类与严重程度）、审批流程（自定义审核步骤）、排班管理、时薪管理、外协管理、出货管理、SPC 质量图表、微信小程序，以及 AI 照片计数、AI 缺陷分类、语音报工、AI 员工中心等智能报工能力。Pro 版已覆盖 46+ 个功能模块。' },
  { q: '后续要加功能或者改流程怎么办？', a: '有源码可以自己改或找人改。我们也提供定制开发服务，按人天报价（¥1500-3000/人天）。' },
  { q: '我们工厂员工不会用智能手机怎么办？', a: '只要会扫码、会拍照就够了，扫码报工是用大字加图标设计的。第一天发任务二维码贴在工位上，老员工带 5 分钟就会。' },
  { q: '小工厂用什么MES系统好？', a: '小工厂（5-200人）选MES系统最看重三点：上线快（几天而不是半年）、价格低（不是十几万）、数据自己控制。辰科MES专为中小加工厂设计，源码交付年费￥2800起，扫码报工、计件工资、订单跟踪、CRM、AI助手全覆盖，私有部署数据不出厂。' },
  { q: 'MES系统一般多少钱？', a: '市场上MES系统价格差距很大。传统厂商报价通常在十几万到几十万，实施周期半年起步。SaaS类产品按月/按年扣费，用久了比买源码贵。辰科MES走源码交付路线，Pro版￥2800/年全功能源码，Pro+实施￥3800/年含部署培训，成本可控。' },
  { q: 'MES和ERP有什么区别？', a: 'ERP管的是企业经营层面（财务、采购、销售、库存），MES管的是车间执行层面（报工、排产、质检、设备）。小工厂通常先上MES解决车间报工和工资问题，辰科MES也内置了CRM、财务、仓储等轻量ERP功能，小厂一套就够用。' },
  { q: '工厂还在用微信群报工怎么办？', a: '微信群报工的核心问题是数据散落、无法追溯、月底对账难。辰科MES的扫码报工和微信群一样简单（扫码、填数字、拍照），但数据自动汇总到系统，审核通过自动算工资，月底不用再对账。员工 5 分钟就能学会。' },
  { q: '源码交付的MES和SaaS MES哪个好？', a: '源码交付的优势：数据在自己服务器、一次买断长期使用、可以自己修改功能、不依赖单一厂商。SaaS的优势：不用管服务器、开箱即用。小工厂数据敏感，建议源码交付，辰科MES Pro版￥2800/年就能拿到全部源码。' },
  { q: '上线一套MES系统要多久？', a: '传统厂商MES实施周期通常 3-6 个月。辰科MES因为是轻量化设计，从沟通到正式上线通常 1-2 周。流程是：聊清楚流程 → 配置基础数据 → 导入历史数据 → 培训三类角色 → 一个车间试跑 → 正式上线。' },
]

const wechatText = computed(() => salesWechat.value || '微信号待填写')

function toggleWechatPanel() {
  showWechatPanel.value = !showWechatPanel.value
  copied.value = false
}

async function copyWechat() {
  if (!salesWechat.value) return
  await navigator.clipboard.writeText(salesWechat.value)
  copied.value = true
}

usePageSeo({
  title: '辰科MES · 中小加工厂生产管理系统 | 源码交付私有部署',
  description: '专为中小加工厂打造的轻量化MES系统。扫码报工、计件工资自动算、CRM客户管理、AI工厂助手、仓储库存、质量溯源。源码部署在自己服务器，数据不出厂。免费社区版开源下载。',
  keywords: 'MES系统,生产管理系统,扫码报工,计件工资,加工厂管理软件,私有部署,源码交付',
})

const jsonLdSoftwareApp = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: '辰科MES', alternateName: 'Cenkor MES',
  description: '面向中小加工厂的轻量化生产管理系统。扫码报工、计件工资自动核算、订单跟踪、CRM客户管理、AI工厂助手、质量溯源。源码交付，年费￥2800起，私有部署数据不出厂。',
  applicationCategory: 'BusinessApplication', applicationSubCategory: 'Manufacturing Execution System (MES)',
  operatingSystem: 'Linux, Windows',
  url: 'https://mes.cenkor.cn', codeRepository: 'https://github.com/likele001/Cenkormes-community',
  downloadUrl: 'https://github.com/likele001/Cenkormes-community', installUrl: 'https://admin.mes.cenkor.cn/register/',
  screenshot: 'https://mes.cenkor.cn/screenshots/dashboard.png', softwareVersion: '2025.06',
  featureList: '扫码报工, 计件工资, 甘特排产, 生产看板, 质量溯源, CRM客户管理, AI工厂助手, 模具管理, 外协管理, 仓储库存, 采购管理, 财务管理, 设备管理, SPC质量图表, 微信小程序',
  author: { '@type': 'Organization', name: '辰科科技', alternateName: 'Cenkor', url: 'https://cenkor.cn', email: 'contact@cenkor.cn' },
  publisher: { '@type': 'Organization', name: '辰科科技', url: 'https://cenkor.cn' },
  offers: [
    { '@type': 'Offer', price: '0', priceCurrency: 'CNY', description: '社区版 - 免费开源，扫码报工核心流程' },
    { '@type': 'Offer', price: '2800', priceCurrency: 'CNY', priceValidUntil: '2027-12-31', description: 'Pro 商业版 - 46+模块源码，年费制' },
    { '@type': 'Offer', price: '3800', priceCurrency: 'CNY', priceValidUntil: '2027-12-31', description: 'Pro + 标准实施 - 含部署培训' },
  ],
  aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', ratingCount: '36', bestRating: '5' },
}

const jsonLdOrg = {
  '@context': 'https://schema.org', '@type': 'Organization',
  name: '辰科科技', alternateName: 'Cenkor', url: 'https://cenkor.cn', email: 'contact@cenkor.cn',
  description: '辰科科技专注企业级软件与AI智能化解决方案，产品覆盖企业后台、AI智能化、智能制造三大方向。旗舰产品辰科MES面向中小加工厂，源码交付私有部署。',
  sameAs: ['https://github.com/likele001/Cenkormes-community', 'https://mes.cenkor.cn'],
}

const jsonLdHowTo = {
  '@context': 'https://schema.org', '@type': 'HowTo',
  name: '中小加工厂如何上线辰科MES生产管理系统',
  description: '从零开始，6步上线辰科MES到你的工厂车间。', totalTime: 'P2W',
  step: [
    { '@type': 'HowToStep', name: '聊清楚流程', text: '了解你的产品、工序、工价规则，确认上线范围。' },
    { '@type': 'HowToStep', name: '配置基础数据', text: '产品/SKU/工序/工价/人员/权限一次性配齐。' },
    { '@type': 'HowToStep', name: '导入历史数据', text: '订单、客户、库存、工资基础数据可批量导入。' },
    { '@type': 'HowToStep', name: '培训三类角色', text: '管理员、班组长、一线员工分别培训，半小时学会。' },
    { '@type': 'HowToStep', name: '一个车间试跑', text: '先选一条产线或一个车间跑一周，发现问题立即调。' },
    { '@type': 'HowToStep', name: '正式上线扩展', text: '试跑没问题再扩到全厂，可分批接入业务模块。' },
  ],
}

const jsonLdFaq = {
  '@context': 'https://schema.org', '@type': 'FAQPage',
  mainEntity: faqs.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })),
}

useHead({
  script: [
    { type: 'application/ld+json', innerHTML: JSON.stringify(jsonLdSoftwareApp), key: 'software-app' },
    { type: 'application/ld+json', innerHTML: JSON.stringify(jsonLdOrg), key: 'organization' },
    { type: 'application/ld+json', innerHTML: JSON.stringify(jsonLdHowTo), key: 'howto' },
    { type: 'application/ld+json', innerHTML: JSON.stringify(jsonLdFaq), key: 'faq' },
  ],
})
</script>

<template>
  <div class="official-container sales-page">
    <header class="official-hero sales-hero">
      <div class="official-hero-grid">
        <div class="official-hero__content">
          <div class="official-badge sales-hero__badge"><span class="official-badge__dot" />源码交付 · 私有部署 · 数据不出厂</div>
          <h1 class="official-hero__title sales-hero__title">小工厂的生产管理系统<br>扫码报工 · 自动算薪 · 源码交付</h1>
          <p class="official-hero__desc sales-hero__desc">扫码报工、计件工资自动算、订单跟踪、CRM、仓储、AI 智能报工。源码部署在你自己的服务器，数据不出厂。年费 ¥2800 起，不买 SaaS 不按月扣。</p>
          <div class="official-hero__actions sales-hero__actions">
            <a class="official-btn official-btn--primary" :href="trialUrl" target="_blank" rel="noopener">免费试用体验</a>
            <button class="official-btn official-btn--ghost" type="button" @click="toggleWechatPanel">加微信看演示</button>
            <a class="official-btn official-btn--text" :href="communityUrl" target="_blank" rel="noopener">免费下载社区版 →</a>
          </div>
          <div v-if="showWechatPanel" class="sales-wechat-card" role="status">
            <span>微信号</span><strong>{{ wechatText }}</strong>
            <button class="sales-copy" type="button" :disabled="!salesWechat" @click="copyWechat">{{ copied ? '已复制' : '复制微信号' }}</button>
            <p>添加时备注「MES 演示」，方便我们安排你工厂的真实场景演示。</p>
            <p v-if="salesPhone" class="sales-wechat-card__alt">电话咨询：{{ salesPhone }}</p>
            <p v-if="salesEmail" class="sales-wechat-card__alt">邮箱联系：{{ salesEmail }}</p>
          </div>
        </div>
        <div class="official-showcase sales-showcase">
          <div class="official-showcase__dash">
            <div class="sales-hero-browser">
              <div class="sales-hero-browser__bar">
                <span class="sales-hero-browser__dots" aria-hidden="true"><i></i><i></i><i></i></span>
                <span class="sales-hero-browser__url">admin.mes.cenkor.cn</span>
              </div>
              <img src="/screenshots/dashboard.png" alt="辰科MES 管理后台看板" class="sales-hero-screenshot" loading="eager" />
            </div>
          </div>
          <div class="official-showcase__float">
            <figure class="sales-hero-phone">
              <div class="sales-hero-phone__shell">
                <div class="sales-hero-phone__notch" aria-hidden="true"></div>
                <img src="/screenshots/phone-scan.png" alt="H5 扫码报工" class="sales-hero-phone__screen" loading="eager" />
              </div>
              <figcaption>员工扫码报工</figcaption>
            </figure>
            <figure class="sales-hero-phone">
              <div class="sales-hero-phone__shell">
                <div class="sales-hero-phone__notch" aria-hidden="true"></div>
                <img src="/screenshots/phone-salary.png" alt="H5 电子工资条" class="sales-hero-phone__screen" loading="eager" />
              </div>
              <figcaption>电子工资条签名</figcaption>
            </figure>
          </div>
        </div>
      </div>
      <div class="sales-hero-highlights">
        <div v-for="h in heroHighlights" :key="h.label" class="sales-hero-highlight">
          <h3>{{ h.label }}</h3><p>{{ h.desc }}</p>
        </div>
      </div>
    </header>

    <section id="cenkormes" class="official-section official-section--bordered sales-cenkormes" aria-labelledby="cenkormes-heading">
      <div class="sales-split-head">
        <p class="sales-eyebrow">辰科科技 · 另一套生产管理系统</p>
        <h2 id="cenkormes-heading" class="official-section__title">CenkorMES · 标准版生产管理系统</h2>
        <p class="official-section__desc">与辰科MES同属辰科科技，面向需要更完整企业级功能的工厂。独立部署、独立账号体系，覆盖从接单到算薪的全流程。</p>
      </div>
      <div class="sales-advantage-grid">
        <article class="sales-advantage">
          <span class="sales-advantage__tag" style="background:#2563eb14;color:#2563eb">生产</span>
          <h3>完整生产闭环</h3><p>接单、排产、派工、扫码报工、两级审核、算薪、车间看板，全流程数字化。</p>
        </article>
        <article class="sales-advantage">
          <span class="sales-advantage__tag" style="background:#7c3aed14;color:#7c3aed">AI</span>
          <h3>AI 智能中心</h3><p>工厂助手问答、数据预警、智能分析、照片计数、缺陷分类、语音报工，日常可用。</p>
        </article>
        <article class="sales-advantage">
          <span class="sales-advantage__tag" style="background:#0891b214;color:#0891b2">经营</span>
          <h3>经营与协同</h3><p>计件/时薪工资、CRM 客户管理、人事考勤、仓储库存、采购、出货、财务报表一体汇总。</p>
        </article>
        <article class="sales-advantage">
          <span class="sales-advantage__tag" style="background:#dc262614;color:#dc2626">质量</span>
          <h3>质量与溯源</h3><p>质检模板、缺陷代码、SPC 控制图、一物一码反查物料批次与操作人，问题可追溯。</p>
        </article>
        <article class="sales-advantage">
          <span class="sales-advantage__tag" style="background:#16a34a14;color:#16a34a">外协</span>
          <h3>外协与设备</h3><p>外协订单分发、报工对账结算；设备档案、点检与保养计划联动，到期自动提醒。</p>
        </article>
        <article class="sales-advantage">
          <span class="sales-advantage__tag" style="background:#ea580c14;color:#ea580c">部署</span>
          <h3>私有化部署</h3><p>源码部署在你自己的服务器，数据不出厂；同时提供 H5 与微信小程序双端入口。</p>
        </article>
      </div>
      <div class="sales-hero__actions" style="justify-content:center;margin-top:28px">
        <a class="official-btn official-btn--primary" href="https://ck.mes.cenkor.cn" target="_blank" rel="noopener">进入 CenkorMES 系统</a>
        <a class="official-btn official-btn--ghost" href="https://ck.mes.cenkor.cn" target="_blank" rel="noopener">查看演示</a>
      </div>
    </section>

    <section class="official-section sales-pain" aria-labelledby="pain-heading">
      <div class="sales-split-head">
        <p class="sales-eyebrow">老板的真实日常</p>
        <h2 id="pain-heading" class="official-section__title">每一条都让人头大，是不是你正在经历的？</h2>
        <p class="official-section__desc">这些不是危言耸听，是几乎每家小加工厂每天都在重复的事。</p>
      </div>
      <div class="sales-pain-list">
        <article v-for="(point, idx) in painPoints" :key="point.title" class="sales-pain-item">
          <span class="sales-pain-item__num">{{ String(idx + 1).padStart(2, '0') }}</span>
          <h3>{{ point.title }}</h3><p>{{ point.desc }}</p>
        </article>
      </div>
    </section>

    <section class="official-section official-section--bordered" aria-labelledby="close-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">四步闭环</p>
        <h2 id="close-heading" class="official-section__title">从接单到算薪，跑通整个车间</h2>
        <p class="official-section__desc">先选一个车间或一条产线试起来，跑通后再扩展到全厂。</p>
      </div>
      <div class="sales-flow-grid">
        <article v-for="(step, index) in closingSteps" :key="step.title" class="sales-flow-step">
          <div class="sales-flow-step__num">{{ index + 1 }}</div>
          <h3>{{ step.title }}</h3><p>{{ step.desc }}</p>
        </article>
      </div>
    </section>

    <template v-for="group in advantageGroups" :key="group.group">
      <section class="official-section official-section--bordered sales-advantages" :aria-labelledby="`adv-${group.group}`">
        <div class="sales-split-head">
          <p class="sales-eyebrow" :style="{ background: group.color + '14', color: group.color }">{{ group.group }}</p>
          <h2 :id="`adv-${group.group}`" class="official-section__title">{{ group.group === '生产管理' ? '车间高频动作，全部数字化' : group.group === 'AI 智能中心' ? 'AI 不是噱头，是每天都在用的能力' : '不只管生产，经营数据一个系统汇总' }}</h2>
          <p class="official-section__desc">{{ group.group === '生产管理' ? '从订单到报工、从排产到溯源，把散在微信群和 Excel 里的事搬到系统里。' : group.group === 'AI 智能中心' ? '基于你工厂的真实数据做分析、预警和建议，不是通用聊天机器人。' : 'CRM、人事、工资、仓储、采购、财务、设备、报表，数据从订单和报工自动汇总。' }}</p>
        </div>
        <div class="sales-advantage-grid">
          <article v-for="item in group.items" :key="item.title" class="sales-advantage">
            <span class="sales-advantage__tag" :style="{ background: group.color + '14', color: group.color }">{{ group.group }}</span>
            <h3>{{ item.title }}</h3><p>{{ item.desc }}</p>
          </article>
        </div>
      </section>
    </template>

    <section class="official-section official-section--bordered" aria-labelledby="compare-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">用之前 vs 用之后</p>
        <h2 id="compare-heading" class="official-section__title">同一件事，工厂会发生什么变化</h2>
      </div>
      <div class="sales-compare-table">
        <div class="sales-compare-row sales-compare-row--head" role="row">
          <div role="cell">日常场景</div><div role="cell">现在的做法</div><div role="cell">辰科MES 上线后</div>
        </div>
        <div v-for="row in compareRows" :key="row[0]" class="sales-compare-row" role="row">
          <div role="cell" class="sales-compare-row__title">{{ row[0] }}</div>
          <div role="cell" class="sales-compare-row__before">{{ row[1] }}</div>
          <div role="cell" class="sales-compare-row__after">{{ row[2] }}</div>
        </div>
      </div>
    </section>

    <section class="official-section official-section--bordered sales-gallery" aria-labelledby="gallery-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">真实界面</p>
        <h2 id="gallery-heading" class="official-section__title">看看系统长什么样</h2>
        <p class="official-section__desc">不是设计稿，是 辰科MES 真实运行界面截图。</p>
      </div>
      <div class="sales-gallery-tabs" role="tablist">
        <button v-for="tab in galleryTabs" :key="tab.id" role="tab"
          :class="['sales-gallery-tab', { 'sales-gallery-tab--active': galleryActive === tab.id }]"
          :aria-selected="galleryActive === tab.id"
          @click="galleryActive = tab.id">{{ tab.label }}</button>
      </div>
      <div class="sales-gallery-grid" role="tabpanel">
        <figure v-for="img in galleryImages[galleryActive]" :key="img.src" class="sales-gallery-item">
          <img :src="img.src" :alt="img.label" loading="lazy" />
          <figcaption>{{ img.label }}</figcaption>
        </figure>
      </div>
    </section>

    <section class="official-section official-section--bordered sales-source-code" aria-labelledby="source-heading">
      <div class="sales-split-head">
        <p class="sales-eyebrow">为什么买源码</p>
        <h2 id="source-heading" class="official-section__title">买源码，不买 SaaS</h2>
        <p class="official-section__desc">工厂数据敏感，按月扣费不划算，买源码部署在自己服务器才踏实。</p>
      </div>
      <div class="sales-source-grid">
        <article v-for="(item, idx) in whySourceCode" :key="idx" class="sales-source-row">
          <div class="sales-source-row__saas"><span>SaaS</span><p>{{ item.saas }}</p></div>
          <div class="sales-source-row__arrow" aria-hidden="true">→</div>
          <div class="sales-source-row__source"><span>买源码</span><p>{{ item.source }}</p></div>
        </article>
      </div>
    </section>

    <section class="official-section official-section--bordered" aria-labelledby="pricing-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">价格透明</p>
        <h2 id="pricing-heading" class="official-section__title">三个版本，按需选择</h2>
        <p class="official-section__desc">社区版免费试水，Pro 版买源码，实施版帮你部署上线。</p>
      </div>
      <div class="sales-plan-grid">
        <article v-for="plan in plans" :key="plan.name" class="sales-plan" :class="{ 'sales-plan--highlight': plan.highlight }">
          <span v-if="plan.highlight" class="sales-plan__badge">推荐</span>
          <h3>{{ plan.name }}</h3>
          <div class="sales-plan__price"><strong>{{ plan.price }}</strong><em v-if="plan.suffix">{{ plan.suffix }}</em></div>
          <p class="sales-plan__desc">{{ plan.desc }}</p>
          <ul><li v-for="f in plan.features" :key="f">{{ f }}</li></ul>
          <a v-if="plan.href" class="official-btn" :class="plan.highlight ? 'official-btn--primary' : 'official-btn--ghost'" :href="plan.href" target="_blank" rel="noopener">{{ plan.cta }}</a>
          <button v-else class="official-btn" :class="plan.highlight ? 'official-btn--primary' : 'official-btn--ghost'" type="button" @click="toggleWechatPanel()">{{ plan.cta }}</button>
        </article>
      </div>
      <p class="sales-pricing-note">源码交付 · 部署在自己服务器 · 数据不出厂</p>
    </section>

    <section class="sales-plan-section" id="saas-pricing" aria-labelledby="saas-pricing-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">灵活套餐，按需选型</p>
        <h2 id="saas-pricing-heading" class="official-section__title">选择最匹配你工厂规模的版本</h2>
        <p class="official-section__desc">从免费社区版到企业级 SaaS，再到源码买断。所有付费套餐均含 1 个行业包起步，按用量和交付方式自由选择。</p>
      </div>
      <div class="sales-plan-grid sales-plan-grid--3">
        <article
          v-for="plan in saasPlans"
          :key="plan.id"
          class="sales-plan"
          :class="{ 'sales-plan--free': plan.free, 'sales-plan--highlight': plan.highlight }"
        >
          <span v-if="plan.badge" class="sales-plan__badge">{{ plan.badge }}</span>
          <h3 class="sales-plan__name">{{ plan.name }}</h3>
          <p class="sales-plan__price">
            <strong>{{ plan.price }}</strong><span>{{ plan.priceSuffix }}</span>
          </p>
          <ul class="sales-plan__features">
            <li v-for="f in plan.features" :key="f">{{ f }}</li>
          </ul>
          <a class="official-btn" :class="plan.highlight ? 'official-btn--primary' : 'official-btn--ghost'" :href="plan.ctaHref" target="_blank" rel="noopener">{{ plan.cta }}</a>
          <p v-if="plan.note" class="sales-plan__note">{{ plan.note }}</p>
        </article>
      </div>
    </section>

    <section class="official-section official-section--bordered" aria-labelledby="deliver-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">交付说明</p>
        <h2 id="deliver-heading" class="official-section__title">我们交付什么，不交付什么</h2>
        <p class="official-section__desc">买的是源码和更新，部署运维按需付费。Pro + 实施版包含部署和培训。</p>
      </div>
      <div class="sales-deliver-table">
        <div class="sales-deliver-row sales-deliver-row--head" role="row">
          <div role="cell">包含交付</div><div role="cell">另外付费</div>
        </div>
        <div v-for="row in deliverables" :key="row.deliver" class="sales-deliver-row" role="row">
          <div role="cell">✓ {{ row.deliver }}</div>
          <div role="cell">✗ {{ row.extra }}</div>
        </div>
      </div>
    </section>

    <section class="official-section official-section--bordered" aria-labelledby="feature-compare-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">Community vs Pro</p>
        <h2 id="feature-compare-heading" class="official-section__title">社区版够试用，Pro 版才是完整经营系统</h2>
      </div>
      <div class="sales-feature-compare-table">
        <div class="sales-fc-row sales-fc-row--head" role="row">
          <div role="cell">功能</div><div role="cell">Community</div><div role="cell">Pro</div>
        </div>
        <div v-for="row in featureCompare" :key="row.name" class="sales-fc-row" role="row">
          <div role="cell" class="sales-fc-row__name">{{ row.name }}</div>
          <div role="cell" class="sales-fc-row__community"><template v-if="typeof row.community === 'boolean'">{{ row.community ? '✓' : '✗' }}</template><template v-else>{{ row.community }}</template></div>
          <div role="cell" class="sales-fc-row__pro"><template v-if="typeof row.pro === 'boolean'">{{ row.pro ? '✓' : '✗' }}</template><template v-else>{{ row.pro }}</template></div>
        </div>
      </div>
    </section>

    <section class="official-section official-section--bordered sales-industries" aria-labelledby="industry-heading">
      <div class="sales-split-head">
        <p class="sales-eyebrow">适用行业</p>
        <h2 id="industry-heading" class="official-section__title">有工序、有派工、有计件，就适合用</h2>
        <p class="official-section__desc">尤其适合订单多、工序多、人员流动大、月底工资核算压力大的加工型企业。</p>
      </div>
      <div class="sales-industry-grid"><span v-for="item in industries" :key="item">{{ item }}</span></div>
    </section>

    <section class="official-section official-section--bordered" aria-labelledby="modules-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">功能清单</p>
        <h2 id="modules-heading" class="official-section__title">Pro 版覆盖加工厂全流程</h2>
        <p class="official-section__desc">以下是 辰科MES Pro 已有的功能模块，持续迭代更新中。</p>
      </div>
      <div class="sales-module-grid"><span v-for="mod in allModules" :key="mod">{{ mod }}</span></div>
    </section>

    <section class="official-section official-section--bordered sales-rollout" aria-labelledby="rollout-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">上线流程</p>
        <h2 id="rollout-heading" class="official-section__title">不折腾，按你厂里的流程走</h2>
        <p class="official-section__desc">从沟通到正式上线，每一步都有交付物。</p>
      </div>
      <ol class="sales-rollout-list">
        <li v-for="r in rollout" :key="r.step">
          <span class="sales-rollout-list__num">{{ String(r.step).padStart(2, '0') }}</span>
          <h4>{{ r.title }}</h4><p>{{ r.desc }}</p>
        </li>
      </ol>
    </section>

    <section class="official-section official-section--bordered sales-trust" aria-labelledby="trust-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">他们已经在用</p>
        <h2 id="trust-heading" class="official-section__title">已经有工厂在用 辰科MES 管车间了</h2>
        <p class="official-section__desc">不是 PPT 案例，是真实在用——你也可以。</p>
      </div>
      <div class="sales-trust-grid">
        <article v-for="tc in trustCases" :key="tc.tag" class="sales-trust-card">
          <span class="sales-trust-card__tag">{{ tc.tag }}</span>
          <blockquote>{{ tc.quote }}</blockquote>
          <p class="sales-trust-card__author">—— {{ tc.author }}</p>
        </article>
      </div>
    </section>

    <section class="official-section official-section--bordered sales-faq" aria-labelledby="faq-heading">
      <div class="official-section__head">
        <p class="sales-eyebrow">老板常问</p>
        <h2 id="faq-heading" class="official-section__title">买之前，你大概会问这些</h2>
      </div>
      <div class="sales-faq-list">
        <details v-for="item in faqs" :key="item.q" class="sales-faq-item">
          <summary>{{ item.q }}</summary>
          <p>{{ item.a }}</p>
        </details>
      </div>
    </section>

    <aside class="official-cta sales-final-cta">
      <p class="sales-eyebrow sales-eyebrow--light">现在就动手</p>
      <p class="official-cta__title">先用起来，觉得好再买源码</p>
      <p class="official-cta__desc">在线试用免费，Pro 版源码 ¥2800/年，部署在自己服务器，数据不出厂。</p>
      <div class="sales-final-cta__actions">
        <a class="official-btn official-btn--primary" :href="trialUrl" target="_blank" rel="noopener">免费试用体验</a>
        <button class="official-btn official-btn--ghost" type="button" @click="toggleWechatPanel">加微信看演示</button>
      </div>
      <p class="sales-final-cta__note">源码交付 · 私有部署 · 年费 ¥2800 起</p>
    </aside>

    <div class="sales-float-contact">
      <button class="sales-float-contact__btn" type="button" @click="toggleWechatPanel">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
        加微信看演示
      </button>
      <a class="sales-float-contact__btn sales-float-contact__btn--primary" :href="trialUrl" target="_blank" rel="noopener">免费试用</a>
    </div>

    <footer class="official-footer"><p>辰科MES · 中小加工厂生产管理系统</p></footer>
  </div>
</template>
