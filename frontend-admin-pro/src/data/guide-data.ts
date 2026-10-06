export interface GuideSection {
  id: string
  title: string
  icon?: string
  content?: string
  children?: GuideSection[]
}

const guideData: GuideSection[] = [
  {
    id: 'part1',
    title: '第一篇：管理员PC端操作指南',
    icon: 'Setting',
    children: [
      {
        id: 'ch1',
        title: '第一章 系统初始化配置',
        icon: 'Tools',
        children: [
          {
            id: 'ch1-1',
            title: '1.1 用户管理',
            content: `<h3>用户管理</h3>
<p><strong>使用者</strong>：系统管理员 / 超级管理员</p>
<p><strong>操作路径</strong>：系统 → 用户管理</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建用户」按钮</li>
<li>填写基本信息：用户名（必填，建议格式如 <code>employee_001</code>）、密码、姓名、部门、手机号、邮箱</li>
<li>选择角色（必填，可多选）</li>
<li>点击「保存」</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>用户名全局唯一，一旦创建不可更改</li>
<li>一个用户可绑定多个角色，系统合并权限</li>
<li>员工离职时建议禁用而非删除，保留操作日志</li>
<li>首次登录强制修改密码</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>编辑</strong>：点击用户行 → 修改 → 保存</li>
<li><strong>禁用</strong>：点击用户行 → 禁用（禁用后无法登录）</li>
<li><strong>重置密码</strong>：点击用户行 → 重置密码 → 发送临时密码</li>
</ul>`
          },
          {
            id: 'ch1-2',
            title: '1.2 角色管理',
            content: `<h3>角色管理</h3>
<p><strong>使用者</strong>：系统管理员 / 超级管理员</p>
<p><strong>操作路径</strong>：系统 → 角色管理</p>
<h4>内置角色</h4>
<table>
<tr><th>角色</th><th>说明</th></tr>
<tr><td>超级管理员</td><td>全部权限</td></tr>
<tr><td>厂长</td><td>生产/财务/报表管理</td></tr>
<tr><td>生产计划员</td><td>订单/排产/派工</td></tr>
<tr><td>班组长</td><td>派工审核/报工审核</td></tr>
<tr><td>操作员工</td><td>报工/查看任务</td></tr>
<tr><td>客户</td><td>下单/查看进度</td></tr>
<tr><td>财务</td><td>工资/对账/报表</td></tr>
</table>
<h4>核心权限点</h4>
<table>
<tr><th>权限点</th><th>说明</th></tr>
<tr><td>dashboard.view</td><td>仪表盘查看</td></tr>
<tr><td>user.manage</td><td>用户管理</td></tr>
<tr><td>product.manage</td><td>产品管理</td></tr>
<tr><td>order.manage</td><td>订单管理</td></tr>
<tr><td>plan.manage</td><td>生产计划</td></tr>
<tr><td>report.audit</td><td>报工审核</td></tr>
<tr><td>salary.manage</td><td>工资管理</td></tr>
<tr><td>trace.query</td><td>溯源查询</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>最小权限原则：只分配必要的权限</li>
<li>权限更新后，当前用户需重新登录才能生效</li>
<li>内置角色建议不要修改，可创建新角色</li>
</ul>`
          },
          {
            id: 'ch1-3',
            title: '1.3 部门管理',
            content: `<h3>部门管理</h3>
<p><strong>使用者</strong>：系统管理员 / HR</p>
<p><strong>操作路径</strong>：系统 → 部门管理</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建部门」</li>
<li>填写：部门名称（必填，如"冲压车间"）、负责人、描述</li>
<li>点击「保存」</li>
<li>可设置上级部门建立层级关系</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>部门名称建议不超过20个字</li>
<li>负责人一般是该部门的班组长或主管</li>
<li>启用了数据权限控制时，用户只能查看本部门数据</li>
<li>删除部门前确认该部门没有员工</li>
</ul>`
          },
          {
            id: 'ch1-4',
            title: '1.4 字典管理',
            content: `<h3>字典管理</h3>
<p><strong>使用者</strong>：系统管理员 / 主数据管理员</p>
<p><strong>操作路径</strong>：系统 → 字典管理</p>
<h4>系统预置字典</h4>
<ul>
<li><strong>单位</strong>：个、米、吨等</li>
<li><strong>颜色</strong>：红、蓝、黄等（可设十六进制色值）</li>
<li><strong>工序分类</strong>：机加、热处理等</li>
<li><strong>订单状态</strong>：草稿、已确认等</li>
</ul>
<h4>操作步骤</h4>
<ol>
<li>选择字典分类 → 点击「+ 新建」</li>
<li>输入字典值代码（唯一，保存后不可改）、文本、排序值</li>
<li>点击「保存」</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>字典值代码一旦保存不能修改</li>
<li>删除前检查是否已被数据引用</li>
<li>不要删除系统预置的关键字典</li>
</ul>`
          },
          {
            id: 'ch1-5',
            title: '1.5 行业包管理',
            content: `<h3>行业包管理</h3>
<p><strong>使用者</strong>：系统管理员 / 超级管理员</p>
<p><strong>操作路径</strong>：系统 → 行业包管理</p>
<h4>什么是行业包</h4>
<p>行业包是 LightMES 为不同制造行业预置的「开箱即用」模板。激活后系统自动导入该行业的标准工序、质检模板、缺陷代码和字典数据，省去手动创建的时间。</p>
<h4>支持的行业</h4>
<table>
<tr><th>行业</th><th>核心特性</th></tr>
<tr><td>机加工</td><td>车/铣/钻/磨/热处理，首件/巡检/出厂检验</td></tr>
<tr><td>注塑</td><td>模具管理、工艺参数、首件/巡检/出货检验</td></tr>
<tr><td>电子组装</td><td>SMT/DIP/AOI/ICT/FCT，ESD防护、BOM追溯</td></tr>
<tr><td>服装纺织</td><td>工票计件、尺码色号矩阵、AQL抽检、外发加工</td></tr>
<tr><td>食品加工</td><td>批次追溯、HACCP/CCP、冷链监控、过敏原管理</td></tr>
<tr><td>汽车零部件</td><td>IATF 16949、PPAP、SPC、关键件追溯、8D报告</td></tr>
</table>
<h4>操作步骤</h4>
<ol>
<li>进入「系统 → 行业包管理」</li>
<li>浏览可用行业包，查看特性说明</li>
<li>点击「激活」按钮，确认激活</li>
<li>系统自动初始化该行业的工序、质检模板、缺陷代码和字典</li>
<li>在工序管理/质检模板/缺陷代码页面，可通过行业筛选查看对应数据</li>
</ol>
<h4>多行业支持</h4>
<p>一个租户可同时激活多个行业包。例如：既做机加工又做注塑的工厂，可以同时激活「机加工」和「注塑」两个行业包，数据按行业分类存储，互不干扰。</p>
<h4>注意事项</h4>
<ul>
<li>行业包激活是<strong>追加</strong>操作，不会删除已有数据</li>
<li>种子数据是<strong>幂等</strong>的，重复激活不会重复插入</li>
<li>取消激活仅移除行业标识，不会删除已导入的数据</li>
<li>行业包可随时「重新初始化」补充缺失数据</li>
</ul>`
          },
{
            id: 'ch1-6',
            title: '1.6 数据权限（ABAC）配置',
            content: `<h3>数据权限（ABAC）配置</h3>
<p><strong>使用者</strong>：系统管理员 / 超级管理员</p>
<p><strong>操作路径</strong>：系统 → 数据权限（数据范围 / 策略规则 / 用户/角色绑定）</p>
<p>「角色权限」决定<strong>能否进入某个功能</strong>，「数据权限」决定<strong>进入后能看到哪些数据</strong>，两者叠加生效：先过权限这道门，再用数据权限把可视范围收窄到具体数据。</p>
<p>数据权限分两级：</p>
<ul>
<li><strong>行级（数据范围）</strong>：能看哪些数据行。例如财务只看本部门订单、车间主任只看本车间报工、销售只看自己名下的客户/订单。</li>
<li><strong>列级（字段脱敏）</strong>：手机号、身份证、薪资等敏感字段按角色脱敏，防止越权看到明文。</li>
</ul>
<h4>第一步：维护数据范围（数据权限 · 数据范围）</h4>
<p>数据范围是可复用的「看数据的口径」。</p>
<ol>
<li>点击「新增」</li>
<li>填写<strong>范围码</strong>（唯一编码，建议用大写英文，如 LEAD_ONLY）</li>
<li>填写<strong>名称</strong>（如 仅本部门负责人）</li>
<li>选择<strong>类型</strong>：ALL（全部） / DEPT_SUBTREE（本部门及下级） / DEPT（本部门） / WORKSHOP（本车间） / SELF（本人） / CUSTOM_EXPR（自定义表达式）</li>
<li>若选了「自定义表达式」，填写 SQL 表达式，如 {department_id} IN (SELECT ...)</li>
</ol>
<h4>第二步：配置策略规则（数据权限 · 策略规则）</h4>
<p>为「某资源 × 某角色」配置行级范围和列级脱敏，这是数据权限的核心页。</p>
<ol>
<li>点击「新增」，填写<strong>资源</strong>：如 orders（订单）、customers（客户）、suppliers（供应商）、salary_slips（工资条）、work_orders（工单）等</li>
<li>选择<strong>角色码</strong>：支持通配 <strong>@all</strong> 或 <strong>*</strong>（对所有角色生效，作为默认）；也可选具体角色如 sales / finance / employee</li>
<li>选择<strong>行级范围</strong>（可留空表示不限制行）</li>
<li>设置<strong>优先级</strong>（数值小优先）与<strong>启用</strong>开关</li>
<li>针对单独列做脱敏：在列表该行点「列脱敏」按钮，用 JSON 配置，如 {"phone":"LAST4","email":"FULL"}</li>
</ol>
<h4>第三步：绑定主体（数据权限 · 用户/角色绑定）</h4>
<p>把某个<strong>用户</strong>或<strong>角色</strong>绑定到某个资源的数据范围。按实际需要可选配；若不绑定，则按策略规则的行级范围解析。</p>
<ol>
<li>点击「新增绑定」</li>
<li>选择<strong>主体类型</strong>：用户 或 角色</li>
<li>选择具体<strong>用户/角色</strong></li>
<li>填写<strong>资源</strong>（如 orders）</li>
<li>选择<strong>数据范围</strong>（引用第一步建的范围码）</li>
</ol>
<h4>四种脱敏方式</h4>
<table>
<tr><th>掩码</th><th>说明</th><th>示例（13800138000）</th></tr>
<tr><td>NULL</td><td>置空</td><td>（空值）</td></tr>
<tr><td>FULL</td><td>整体掩码</td><td>***********</td></tr>
<tr><td>LAST4</td><td>仅保留后4位</td><td>*******8000</td></tr>
<tr><td>HASH</td><td>哈希摘要，便于比对不可还原</td><td>6124d580</td></tr>
</table>
<h4>最佳实践建议</h4>
<ul>
<li>先为关键资源配一条 <strong>@all</strong> 通配规则作为兜底，再用具体角色放开或加强个别字段</li>
<li>具体角色的配置<strong>优先级高于</strong>通配 @all / *</li>
<li>超级管理员（superadmin）不受数据权限限制，始终可看全部</li>
<li>数据权限仅在角色权限<strong>之内</strong>再做约束，不会超出已授权的菜单</li>
<li>脱敏对导出/打印同样生效</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch2',
        title: '第二章 主数据管理',
        icon: 'Box',
        children: [
          {
            id: 'ch2-1',
            title: '2.1 产品管理',
            content: `<h3>产品管理</h3>
<p><strong>使用者</strong>：主数据管理员 / 生产部</p>
<p><strong>操作路径</strong>：主数据 → 产品</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建产品」</li>
<li>填写：产品编码（必填唯一）、产品名称、分类、单位、描述、主图</li>
<li>点击「保存」</li>
<li>支持 Excel 批量导入：下载模板 → 填充数据 → 上传</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>产品编码全局唯一，建议建立编码规范（如 P + 3位数字）</li>
<li>一个产品可对应多个型号（SKU），如不同颜色/规格</li>
<li>产品建立后在型号中关联</li>
<li>删除产品前确认没有关联的订单或型号</li>
</ul>`
          },
          {
            id: 'ch2-2',
            title: '2.2 产品型号（SKU）管理',
            content: `<h3>产品型号（SKU）管理</h3>
<p><strong>使用者</strong>：主数据管理员</p>
<p><strong>操作路径</strong>：主数据 → 产品型号</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建型号」</li>
<li>选择关联的<strong>产品</strong>（必填）</li>
<li>填写型号编码（唯一），如 <code>P001-RED</code></li>
<li>设置扩展属性：<ul>
<li><strong>颜色</strong>：从色卡选择或自定义</li>
<li><strong>材料</strong>：材质说明、用料标准</li>
<li><strong>规格</strong>：尺寸、重量、厚度等自定义字段</li>
<li><strong>备注</strong>：特殊说明</li>
<li><strong>多角度图片</strong>：正面/侧面/细节图</li>
</ul></li>
<li>点击「保存」</li>
</ol>
<h4>批量导入</h4>
<p>支持 Excel 批量导入，下载模板后按格式填充数据，上传即可批量创建型号。</p>
<h4>注意事项</h4>
<ul>
<li>型号编码全局唯一</li>
<li>一个产品可以有多个型号，但一个型号只能属于一个产品</li>
<li>型号可以启用/停用，停用的型号不可用于新订单</li>
</ul>`
          },
          {
            id: 'ch2-3',
            title: '2.3 工序管理',
            content: `<h3>工序管理</h3>
<p><strong>使用者</strong>：主数据管理员 / 生产部</p>
<p><strong>操作路径</strong>：主数据 → 工序</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建工序」</li>
<li>填写：工序编码（如 OP-010）、工序名称（如"下料""冲压""焊接"）、所属车间、标准工时、责任人</li>
<li>点击「保存」</li>
</ol>
<h4>命名示例</h4>
<table>
<tr><th>编码</th><th>名称</th><th>车间</th><th>标准工时</th></tr>
<tr><td>OP-010</td><td>下料</td><td>下料车间</td><td>0.5h/件</td></tr>
<tr><td>OP-020</td><td>冲压</td><td>冲压车间</td><td>0.3h/件</td></tr>
<tr><td>OP-030</td><td>焊接</td><td>焊接车间</td><td>0.8h/件</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>工序编码建议有规律，便于排序和识别</li>
<li>标准工时用于产能估算和排产参考</li>
<li>修改工序后，已有订单按原工序执行</li>
</ul>`
          },
          {
            id: 'ch2-4',
            title: '2.4 工艺路线管理',
            content: `<h3>工艺路线管理</h3>
<p><strong>使用者</strong>：主数据管理员 / 生产部</p>
<p><strong>操作路径</strong>：主数据 → 工艺路线</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建工艺路线」</li>
<li>选择产品（必填）</li>
<li>输入路线名称（如"标准工艺路线"）</li>
<li>逐条添加工序步骤，可拖拽调整顺序</li>
<li>设置默认路线（一个产品只能有一个默认路线）</li>
<li>点击「保存」</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>一个产品可设置多条工艺路线（如"标准路线"和"加急路线"）</li>
<li>订单确认时选择使用哪条工艺路线</li>
<li>工序顺序通过拖拽调整，非常直观</li>
<li>工艺路线变更不影响已确认的订单</li>
</ul>`
          },
          {
            id: 'ch2-5',
            title: '2.5 物料管理',
            content: `<h3>物料管理</h3>
<p><strong>使用者</strong>：主数据管理员 / 采购</p>
<p><strong>操作路径</strong>：主数据 → 物料</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建物料」</li>
<li>填写：物料编码、物料名称、规格型号、单位、默认供应商、最低库存预警</li>
<li>点击「保存」</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>物料编码全局唯一</li>
<li>设置最低库存预警，库存低于阈值时系统提示</li>
<li>物料用于 BOM 和采购管理</li>
</ul>`
          },
          {
            id: 'ch2-6',
            title: '2.6 BOM（物料清单）管理',
            content: `<h3>BOM（物料清单）管理</h3>
<p><strong>使用者</strong>：主数据管理员 / 生产部</p>
<p><strong>操作路径</strong>：主数据 → BOM</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建 BOM」</li>
<li>选择产品（必填）</li>
<li>逐条添加物料：选择物料、输入用量、设定损耗率</li>
<li>设置版本号，BOM 支持版本管理</li>
<li>点击「保存」</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>BOM 用于物料需求计算和成本核算</li>
<li>损耗率影响实际物料采购量</li>
<li>BOM 变更后，新订单使用新版本，旧订单用旧版本</li>
<li>建议建立 BOM 审核流程</li>
</ul>`
          },
          {
            id: 'ch2-7',
            title: '2.7 供应商管理',
            content: `<h3>供应商管理</h3>
<p><strong>使用者</strong>：采购 / 主数据管理员</p>
<p><strong>操作路径</strong>：主数据 → 供应商</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建供应商」</li>
<li>填写：供应商编码、名称、联系人、联系方式、地址、供应商等级</li>
<li>点击「保存」</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>供应商编码建议有规律，便于管理</li>
<li>供应商关联到采购订单</li>
<li>定期评估供应商绩效（交期准时率、质量合格率）</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch3',
        title: '第三章 工价设置',
        icon: 'Money',
        children: [
          {
            id: 'ch3-1',
            title: '3.1 工序工价设置',
            content: `<h3>工序工价设置</h3>
<p><strong>使用者</strong>：财务 / 主数据管理员</p>
<p><strong>操作路径</strong>：主数据 → 工序工价</p>
<p>工价是 辰科MES 的核心计费逻辑，按「产品型号 × 工序」设定计件单价（元/件）。</p>
<h4>设置方法一：逐个型号设置</h4>
<ol>
<li>进入产品型号详情页</li>
<li>点击「工价设置」Tab</li>
<li>为每个工序输入单价，如：下料 ¥0.5/件、冲压 ¥0.8/件、焊接 ¥1.2/件</li>
<li>点击「保存」</li>
</ol>
<h4>设置方法二：批量设置</h4>
<ol>
<li>在工序工价页面，选择产品型号</li>
<li>点击「批量设置」</li>
<li>输入各工序的统一单价</li>
<li>一键应用到所有选中型号</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>工价精度到 2 位小数</li>
<li><strong>历史追溯</strong>：工价变更后，旧订单按旧价，新订单按新价</li>
<li>工价直接影响工资计算，务必准确</li>
<li>定期的工价审计有助于控制成本</li>
</ul>
<h4>示例</h4>
<table>
<tr><th>产品型号</th><th>工序</th><th>单价（元/件）</th></tr>
<tr><td>离心泵-标准型</td><td>下料</td><td>0.50</td></tr>
<tr><td>离心泵-标准型</td><td>冲压</td><td>0.80</td></tr>
<tr><td>离心泵-标准型</td><td>焊接</td><td>1.20</td></tr>
<tr><td>离心泵-标准型</td><td>组装</td><td>0.60</td></tr>
<tr><td>离心泵-标准型</td><td>质检</td><td>0.30</td></tr>
</table>`
          },
        ]
      },
      {
        id: 'ch4',
        title: '第四章 订单与生产',
        icon: 'List',
        children: [
          {
            id: 'ch4-1',
            title: '4.1 订单管理',
            content: `<h3>订单管理</h3>
<p><strong>使用者</strong>：生产计划员 / 销售</p>
<p><strong>操作路径</strong>：生产 → 订单管理</p>
<h4>手工创建订单</h4>
<ol>
<li>点击「+ 新建订单」</li>
<li>选择<strong>客户</strong>（必填）</li>
<li>选择<strong>产品型号</strong>（必填），支持多行</li>
<li>输入<strong>数量</strong>（必填）</li>
<li>设定<strong>交期</strong>（必填）</li>
<li>填写备注信息（可选）</li>
<li>点击「保存」</li>
</ol>
<h4>订单状态流转</h4>
<table>
<tr><th>状态</th><th>说明</th></tr>
<tr><td>草稿</td><td>刚创建，可修改</td></tr>
<tr><td>已确认</td><td>确认后自动分解为工单，不可修改</td></tr>
<tr><td>生产中</td><td>至少一个工单开始生产</td></tr>
<tr><td>已完成</td><td>所有工单生产完成</td></tr>
<tr><td>已发货</td><td>产品已出库</td></tr>
<tr><td>已取消</td><td>订单取消</td></tr>
</table>
<h4>批量导入</h4>
<p>点击「导入订单」→ 下载 Excel 模板 → 按格式填写 → 上传 → 系统自动校验并创建。</p>
<h4>注意事项</h4>
<ul>
<li>已确认的订单不能直接修改，需取消后重建</li>
<li>订单确认后自动分解为工单</li>
<li>订单交期影响排产优先级</li>
</ul>`
          },
          {
            id: 'ch4-2',
            title: '4.2 工单查看',
            content: `<h3>工单查看</h3>
<p><strong>使用者</strong>：生产计划员 / 班组长</p>
<p><strong>操作路径</strong>：生产 → 工单管理</p>
<h4>工单说明</h4>
<p>订单确认后，系统按工艺路线自动分解为工单。每个工单对应一个订单的一个工序。</p>
<h4>工单管理</h4>
<ul>
<li><strong>筛选</strong>：按订单号、产品型号、工序、状态筛选</li>
<li><strong>状态查看</strong>：待生产、生产中、已完成</li>
<li><strong>进度查看</strong>：每个工单的完成数量和比例</li>
<li><strong>操作</strong>：可暂停/恢复工单</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>工单是排产和派工的最小单位</li>
<li>工单完成后才能进行下一道工序</li>
<li>可在工单详情中查看报工记录和审核状态</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch5',
        title: '第五章 派工与执行',
        icon: 'User',
        children: [
          {
            id: 'ch5-1',
            title: '5.1 生产计划',
            content: `<h3>生产计划</h3>
<p><strong>使用者</strong>：生产计划员</p>
<p><strong>操作路径</strong>：生产 → 生产计划</p>
<h4>操作步骤</h4>
<ol>
<li>进入「生产计划」页面，查看所有待排产工单</li>
<li><strong>手动排产</strong>：选择工单 → 分配设备和产线 → 设定开始时间</li>
<li><strong>甘特图</strong>：可视化展示工单分布，支持拖拽平移调整起止日期</li>
<li><strong>物料齐套检查</strong>：排产前自动计算物料需求，提示缺料</li>
<li>点击「发布计划」</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>排产时考虑设备负荷和人员可用性</li>
<li>物料不足时系统会提示不齐套，不建议强行排产</li>
<li>甘特图拖拽调整非常直观，适合快速调整排产</li>
<li>排产冲突时系统会高亮提示</li>
</ul>`
          },
          {
            id: 'ch5-2',
            title: '5.2 任务派工',
            content: `<h3>任务派工</h3>
<p><strong>使用者</strong>：生产主管 / 班组长</p>
<p><strong>操作路径</strong>：生产 → 任务派工</p>
<h4>操作步骤</h4>
<ol>
<li>进入「任务派工」页面，选择要派工的工单</li>
<li>系统<strong>智能推荐</strong>合适员工（根据技能标签和当前负荷）</li>
<li>选择员工，输入派工数量</li>
<li>点击「派工」，系统自动生成任务</li>
<li><strong>二维码标签</strong>：每个任务生成唯一二维码，可打印粘贴在工件上</li>
<li>系统自动<strong>推送通知</strong>到员工手机端</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>派工时考虑员工的技能标签，确保能力匹配</li>
<li>合理分配负荷，避免部分员工过忙、部分闲置</li>
<li>二维码标签是扫码报工的关键入口</li>
<li>可批量派工：一次选择多个员工和数量</li>
</ul>`
          },
          {
            id: 'ch5-3',
            title: '5.3 员工技能管理',
            content: `<h3>员工技能管理</h3>
<p><strong>使用者</strong>：HR / 班组长</p>
<p><strong>操作路径</strong>：系统 → 技能管理</p>
<h4>操作步骤</h4>
<ol>
<li>进入「技能管理」页面</li>
<li>点击「+ 新建技能标签」，如：氩弧焊、冲压操作、质检</li>
<li>进入员工档案，为员工分配技能</li>
<li>技能等级可选：初级、中级、高级</li>
</ol>
<h4>派工中的应用</h4>
<p>排产派工时，系统会根据技能标签智能推荐合适的员工，提高派工效率和准确性。</p>`
          },
        ]
      },
      {
        id: 'ch6',
        title: '第六章 报工与审核',
        icon: 'Edit',
        children: [
          {
            id: 'ch6-1',
            title: '6.1 报工（员工端）',
            content: `<h3>报工（员工端 - 手机/H5）</h3>
<p><strong>使用者</strong>：操作员工</p>
<p><strong>操作路径</strong>：手机端 → 扫码报工 或 页面报工</p>
<h4>扫码报工流程</h4>
<ol>
<li>打开手机端，点击「扫码报工」</li>
<li>扫描任务二维码，系统自动识别任务</li>
<li>输入<strong>合格数</strong>和<strong>不良数</strong></li>
<li>上传完工照片或短视频（1-5张照片，视频最长30秒）</li>
<li>填写备注（如问题说明）</li>
<li>点击「提交」，立即显示预估工资</li>
</ol>
<h4>页面报工流程</h4>
<ol>
<li>在手机端点击「报工」，进入报工页面</li>
<li>手工选择任务（或搜索任务编号）</li>
<li>输入合格数/不良数 + 上传证据 + 提交</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>合格数 + 不良数 ≤ 派工总数</li>
<li>多媒体证据越清晰，审核通过越快</li>
<li>提交后不可修改，如需修改联系班组长驳回</li>
<li>报工数据影响工资，务必真实准确</li>
</ul>`
          },
          {
            id: 'ch6-2',
            title: '6.2 报工审核',
            content: `<h3>报工审核（班组长/QC 后台）</h3>
<p><strong>使用者</strong>：班组长 / QC 质检员</p>
<p><strong>操作路径</strong>：生产 → 报工审核 / 报工单位</p>
<h4>多级审核流程</h4>
<ol>
<li><strong>班组长初审</strong>：<ul>
<li>查看报工照片/视频</li>
<li>核实合格数和不良数是否合理</li>
<li>通过→进入 QC 终审</li>
<li>驳回→填写原因，员工重新报工</li>
</ul></li>
<li><strong>QC 终审</strong>：<ul>
<li>从质检角度审核产品质量</li>
<li>通过→报工生效，自动计入工资</li>
<li>驳回→填写质检原因，返回员工</li>
</ul></li>
</ol>
<h4>批量审核</h4>
<p>支持批量选择报工记录 → 批量通过/驳回，提高审核效率。</p>
<h4>注意事项</h4>
<ul>
<li>审核时仔细查看员工上传的照片/视频</li>
<li>驳回时务必填写明确的原因</li>
<li>审核通过后报工数据即进入工资计算</li>
<li>定期审核避免积压影响工资计算</li>
</ul>
<h4>QC 审核中可关联质检模板与缺陷代码</h4>
<p>新版 QC 终审支持<strong>按质检模板逐项打勾</strong>，并对不合格项<strong>关联缺陷代码</strong>，自动落库到 <code>inspection_records</code>。详见 <a>6.3 质量管理</a>。</p>`
          },
          {
            id: 'ch6-3',
            title: '6.3 质量管理（质检模板 / 缺陷代码 / 检测记录）',
            content: `<h3>质量管理</h3>
<p>辰科MES 提供「<strong>质检模板 → 检测记录 → 缺陷分析</strong>」的完整质量管理闭环：先配置好模板（哪些工序要查什么），QC 审核报工时按模板逐项打勾，结果自动汇总到缺陷分析报表里。</p>
<h4>角色与权限</h4>
<ul>
<li><code>report.audit</code> 权限：可管理质检模板、缺陷代码、查看检测记录</li>
<li>QC 终审岗：审核报工时填写检测记录</li>
<li>质量分析（厂长/经理）：查看缺陷分析报表</li>
</ul>
<h4>1. 质检模板（Inspection Template）</h4>
<p><strong>路径</strong>：主数据 → 质检模板</p>
<p>模板是「某个工序 / 某类产品要做哪些检查项」的清单。</p>
<p>字段说明：</p>
<ul>
<li><strong>编码 / 名称</strong>：如 <code>WELD-STD-01</code>「标准焊接检查」</li>
<li><strong>关联工序</strong>（可选）：限定本模板只在该工序审核时出现</li>
<li><strong>关联产品</strong>（可选）：限定只对该产品生效</li>
<li><strong>是否启用</strong>：停用后审核页不再出现</li>
</ul>
<p>模板下有多个<strong>检查明细项</strong>，每项 3 种类型：</p>
<ul>
<li><code>pass_fail</code> 合格/不合格：最常用（焊点是否饱满、尺寸是否合规）</li>
<li><code>measure</code> 测量值：填实测数值（厚度 1.2mm、长度 50mm），需配 <code>standard_value</code> / <code>upper_limit</code> / <code>lower_limit</code> / <code>unit</code>，系统自动判定 pass/fail</li>
<li><code>text</code> 文本描述：开放文字（外观描述、备注）</li>
</ul>
<p>明细项可设置 <code>is_required</code> 必填，QC 不填该项不能通过审核。</p>
<h4>2. 缺陷代码（Defect Code）</h4>
<p><strong>路径</strong>：主数据 → 缺陷代码</p>
<p>把工厂常出现的质量问题<strong>标准化成代码</strong>，便于统计与趋势分析。</p>
<p>字段：</p>
<ul>
<li><strong>编码 / 名称</strong>：如 <code>D-001</code>「焊点虚焊」、<code>D-002</code>「尺寸超差」</li>
<li><strong>严重度</strong>：
  <ul>
    <li><code>critical</code> 致命：影响安全的缺陷，必须返工/报废</li>
    <li><code>major</code> 主要：影响功能但可让步接收</li>
    <li><code>minor</code> 次要：轻微外观缺陷，不影响使用</li>
  </ul>
</li>
<li><strong>是否启用</strong>：旧缺陷下线后停用</li>
</ul>
<h4>3. 检测记录（Inspection Record）</h4>
<p><strong>录入路径</strong>：报工审核 → QC 终审时</p>
<p>QC 进入审核页 → 系统自动加载该工序/产品对应的<strong>生效模板</strong> → 逐项打勾 / 填值：</p>
<ul>
<li><code>pass_fail</code> 项：选「合格 / 不合格 / 不适用」</li>
<li><code>measure</code> 项：填实测值，超上下限自动标红</li>
<li>不合格项必填<strong>缺陷代码</strong> + 备注</li>
</ul>
<p>审核提交后写入 <code>inspection_records</code> 表，与 <code>report_unit_audits</code> 关联。</p>
<h4>4. 缺陷分析报表</h4>
<p><strong>路径</strong>：报表 → 缺陷分析</p>
<p>从 <code>inspection_records</code> 汇总：</p>
<ul>
<li><strong>缺陷码 TOP 10</strong>：出现频率最高的缺陷，便于针对性改善工艺</li>
<li><strong>缺陷严重度分布</strong>：critical / major / minor 占比，监控质量趋势</li>
<li><strong>按工序 / 产品 / 时间段</strong>筛选</li>
<li><strong>缺陷-员工关联</strong>：分析某员工的高频缺陷，定位培训需求</li>
</ul>
<h4>典型流程</h4>
<ol>
<li>质量主管在「主数据 → 质检模板」配置模板（如「焊接检查」），挂 5~10 个检查项</li>
<li>在「主数据 → 缺陷代码」维护 10~30 个缺陷码（含 critical/major/minor）</li>
<li>QC 审核报工时，系统自动加载模板，QC 逐项打勾 + 标缺陷</li>
<li>月底看缺陷分析报表，对 top 缺陷做工艺改善或员工培训</li>
</ol>
<h4>与报工审核的关联</h4>
<p>QC 终审不通过时，可以同时：</p>
<ul>
<li>把报工<strong>驳回</strong>（员工重新报工）</li>
<li>把对应<strong>缺陷码</strong>绑定到 <code>inspection_records</code>（用于缺陷分析）</li>
</ul>
<p>这样驳回原因有数据支撑，后续能追到「哪个工序 / 哪个员工 / 哪类缺陷最多」。</p>`
          },
          {
            id: 'ch6-4',
            title: '6.4 按件报工（逐件扫码）',
            content: `<h3>按件报工</h3>
<p><strong>使用者</strong>：操作员工 / 班组长</p>
<p><strong>适用场景</strong>：高单价加工、单件计件、每件都需要独立追溯（成品码 / 件次）的工序。</p>
<p>与「批量报工」不同，按件报工<strong>逐件扫码或逐件录入</strong>，每一件都是一条独立记录，可绑定成品码进行精准溯源。</p>
<h4>两种报工模式</h4>
<table>
<tr><th>模式</th><th>方式</th><th>适用</th></tr>
<tr><td>批量报工</td><td>一次扫码录入合格 / 不良数量</td><td>大批量、低单价、按数量计件</td></tr>
<tr><td>逐件报工（件次+成品码）</td><td>每件独立扫码，记录件次与成品码</td><td>高单价、单件计件、需逐件追溯</td></tr>
</table>
<h4>切换报工模式</h4>
<p><strong>操作路径</strong>：系统 → 系统设置 → 报工模式</p>
<p>当前租户可设置<strong>默认报工模式</strong>为「批量」或「逐件报工」；员工端按当前模式下发的入口报工。</p>
<h4>逐件报工操作步骤</h4>
<ol>
<li>员工在移动端进入「报工」入口（扫码 / 页面）</li>
<li>系统按报工模式下发任务，逐件模式显示待报工明细</li>
<li>扫成品码 / 录入件次，系统校验条码合法性（防重复）</li>
<li>记录合格 / 不良，逐件生成可追溯记录</li>
<li>提交后生成<strong>成品码 → 物料 / 人员 / 时间</strong> 溯源关系</li>
<li>班组长 / QC 审核通过后计入计件工资</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>件次与成品码需唯一，重复扫码会提示冲突</li>
<li>逐件记录便于后续<strong>质量问题反查</strong>（定位到具体某件）</li>
<li>工资计算同样按"审核通过的报工"口径</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch7',
        title: '第七章 工资结算',
        icon: 'Money',
        children: [
          {
            id: 'ch7-1',
            title: '7.1 工资自动计算',
            content: `<h3>工资自动计算</h3>
<p><strong>使用者</strong>：财务 / 班组长</p>
<p><strong>操作路径</strong>：生产 → 工资管理</p>
<h4>计算逻辑</h4>
<p><strong>公式</strong>：<br>
<code>计件工资 = Σ(审核通过的报工合格数 × 工序工价)</code><br>
<code>月总工资 = 计件工资 + 补贴 - 扣款</code></p>
<h4>操作步骤</h4>
<ol>
<li>进入「工资管理」，选择月份</li>
<li>系统自动汇总所有审核通过的报工记录</li>
<li>查看员工工资明细：<ul>
<li>姓名、部门、工序数量、合格数、单价、金额</li>
<li>补贴项：全勤奖、岗位津贴等</li>
<li>扣款项：迟到扣款、罚款等</li>
</ul></li>
<li>确认无误后，点击「确认工资」</li>
<li>支持导出 Excel 工资表</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>工资计算严格基于"审核通过的报工"</li>
<li>未审核的报工不计入工资</li>
<li>财务确认前可以手动调整补贴/扣款</li>
<li>工资确认后生成电子工资条</li>
</ul>`
          },
          {
            id: 'ch7-2',
            title: '7.2 电子工资条',
            content: `<h3>电子工资条</h3>
<p><strong>使用者</strong>：财务（生成）/ 员工（查看）</p>
<p><strong>操作路径</strong>：生产 → 工资条管理</p>
<h4>操作步骤</h4>
<ol>
<li>财务确认工资后，点击「生成工资条」</li>
<li>系统为每个员工生成电子工资条</li>
<li>员工在手机端查看工资条明细</li>
<li>员工可进行<strong>电子签名确认</strong></li>
<li>如员工有异议，可拒绝签名并提交问题</li>
</ol>
<h4>工资条内容</h4>
<ul>
<li>员工信息：姓名、部门、工号</li>
<li>计件工资：各工序报工明细</li>
<li>补贴明细：全勤奖、岗位津贴等</li>
<li>扣款明细：迟到、罚款等</li>
<li>实发金额</li>
<li>电子签名区</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>员工签名后视为确认工资，不可再修改</li>
<li>异议处理流程：员工提出 → 财务复核 → 调整→重新生成</li>
<li>支持 PDF 下载和打印</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch8',
        title: '第八章 进度监控',
        icon: 'Monitor',
        children: [
          {
            id: 'ch8-1',
            title: '8.1 首页仪表盘',
            content: `<h3>首页仪表盘</h3>
<p><strong>使用者</strong>：所有管理员</p>
<p><strong>操作路径</strong>：首页</p>
<h4>关键数据概览</h4>
<ul>
<li><strong>今日产值</strong>：当天完成的订单产值</li>
<li><strong>订单达成率</strong>：本月已完成 / 本月目标</li>
<li><strong>不良率</strong>：当日不良品占比</li>
<li><strong>待办事项</strong>：待审核报工、待派工任务</li>
</ul>
<h4>实时生产趋势图</h4>
<ul>
<li>产量趋势折线图（近7天/30天）</li>
<li>良率趋势图</li>
<li>订单达成率饼图</li>
</ul>
<h4>紧急提醒</h4>
<ul>
<li>交期即将逾期的订单（红色高亮）</li>
<li>异常报警：高不良率、未报工、设备故障</li>
</ul>`
          },
          {
            id: 'ch8-2',
            title: '8.2 进度看板',
            content: `<h3>进度看板</h3>
<p><strong>使用者</strong>：班组长 / 工厂主管</p>
<p><strong>操作路径</strong>：仪表盘 → 进度看板</p>
<h4>显示内容</h4>
<ul>
<li>所有订单的实时进度</li>
<li>各工序完成比例</li>
<li>交期倒计时</li>
<li>异常提醒（延迟、物料缺货）</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>看板数据自动更新，无需手动刷新</li>
<li>快逾期的订单高亮显示</li>
<li>客户也可登录查看自己订单的进度</li>
</ul>`
          },
          {
            id: 'ch8-3',
            title: '8.3 车间大屏',
            content: `<h3>车间大屏</h3>
<p><strong>使用者</strong>：班组长 / 工厂主管</p>
<p><strong>操作路径</strong>：仪表盘 → 车间大屏</p>
<h4>显示内容</h4>
<ul>
<li><strong>实时产量</strong>：各工序当日目标 vs 实际</li>
<li><strong>良率/不良率</strong></li>
<li><strong>异常报警</strong>：不良率过高、未报工、物料不足</li>
<li><strong>交期倒计时</strong>：绿色(正常) / 黄色(当日) / 红色(逾期)</li>
<li><strong>员工排名</strong>：日完成数量排行、良率排行</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>大屏应投放在车间显眼位置</li>
<li>数据每1-2分钟自动刷新</li>
<li>具有激励作用，员工可看到自己的排名</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch9',
        title: '第九章 AI 员工管理',
        icon: 'MagicStick',
        children: [
          {
            id: 'ch9-1',
            title: '9.1 创建与配置 AI 员工',
            content: `<h3>创建与配置 AI 员工</h3>
<p><strong>价值</strong>：AI 员工是工厂智能助手，可自动回答员工关于订单进度、生产计划、任务完成情况、设备状态、库存等问题，减少管理人员的重复沟通成本。</p>
<p><strong>使用者</strong>：系统管理员</p>
<p><strong>操作路径</strong>：系统 → AI 员工</p>
<h4>创建 AI 员工</h4>
<ol>
<li>点击「<strong>新建 AI 员工</strong>」按钮</li>
<li>填写以下信息：<ul>
<li><strong>名称</strong>：AI 员工的显示名称，如"生产调度助手"</li>
<li><strong>头像 URL</strong>：可选，AI 员工头像图片链接</li>
<li><strong>角色描述</strong>：简短说明 AI 员工的职责，如"负责查询生产进度和订单状态"</li>
<li><strong>系统 Prompt</strong>：核心提示词，定义 AI 的身份、行为准则和回答风格（详见下方说明）</li>
<li><strong>欢迎消息</strong>：用户首次打开对话时显示的问候语</li>
</ul></li>
<li>点击「保存」</li>
</ol>
<h4>系统 Prompt 编写指南</h4>
<p>系统 Prompt 是 AI 员工的核心配置，建议包含以下要素：</p>
<table>
<tr><th>要素</th><th>说明</th><th>示例</th></tr>
<tr><td>身份定义</td><td>告诉 AI 它是什么角色</td><td>你是一个专业的 MES 生产调度助手</td></tr>
<tr><td>能力范围</td><td>它能用哪些工具查什么</td><td>你可以查询订单状态、生产计划、任务进度</td></tr>
<tr><td>回答要求</td><td>回答风格和格式</td><td>用表格或列表呈现结果，回答简洁</td></tr>
<tr><td>边界约束</td><td>不能做什么</td><td>只回答生产相关问题，无关问题请引导回正题</td></tr>
</table>
<h4>配置渠道</h4>
<p>在「绑定渠道」中勾选 AI 员工可用的对话渠道：</p>
<ul>
<li><strong>H5</strong>：员工在手机 H5 端「AI 员工」入口对话</li>
<li><strong>飞书 / 企微 / 钉钉</strong>：员工在 IM 中直接给机器人发消息（需先配置好对应渠道的消息推送）</li>
</ul>
<h4>配置工具</h4>
<p>在「可用工具」中勾选 AI 员工可以调用的 MES 数据查询工具：</p>
<table>
<tr><th>工具</th><th>功能</th></tr>
<tr><td>query_order_status</td><td>查询订单生产进度和状态</td></tr>
<tr><td>query_production_plan</td><td>查询生产计划详情</td></tr>
<tr><td>query_task_progress</td><td>查询生产任务完成进度</td></tr>
<tr><td>query_equipment_status</td><td>查询设备运行状态和保养记录</td></tr>
<tr><td>query_stock</td><td>查询仓库库存信息</td></tr>
<tr><td>search_knowledge</td><td>搜索知识库文档</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>AI 员工需要平台已配置 AI 网关和默认模型才能正常工作</li>
<li>网关覆盖留空则使用平台默认模型，填写模型 code 可指定特定模型</li>
<li>创建后记得在操作列点击「启用」使 AI 员工上线</li>
</ul>`
          },
          {
            id: 'ch9-2',
            title: '9.2 管理 AI 员工',
            content: `<h3>管理 AI 员工</h3>
<p><strong>操作路径</strong>：系统 → AI 员工</p>
<h4>编辑</h4>
<p>点击 AI 员工行的「编辑」按钮，可修改名称、角色描述、系统 Prompt、渠道、工具等所有配置。</p>
<h4>启用 / 暂停</h4>
<ul>
<li><strong>启用</strong>：AI 员工上线，员工可在各渠道发起对话</li>
<li><strong>暂停</strong>：AI 员工下线，对话接口返回"该 AI 员工已暂停"</li>
</ul>
<h4>删除</h4>
<p>点击「删除」按钮，确认后删除该 AI 员工。注意：删除会同时清除所有相关对话记录和操作日志。</p>
<h4>查看统计数据</h4>
<p>每个 AI 员工自动统计以下数据：</p>
<ul>
<li>总对话数、总消息数</li>
<li>总 Token 消耗</li>
<li>今日对话数、今日消息数</li>
<li>工具调用次数</li>
</ul>
<h4>查看对话记录</h4>
<p>可查看每个 AI 员工的所有历史对话和消息内容，用于审计和分析使用情况。</p>
<h4>查看操作日志</h4>
<p>记录 AI 员工的每次工具调用、错误、回复等操作，便于排查问题。</p>`
          },
          {
            id: 'ch9-3',
            title: '9.3 AI 网关配置',
            content: `<h3>AI 网关配置</h3>
<p><strong>操作路径</strong>：平台总控 → AI 模型</p>
<p>AI 员工需要调用大语言模型，因此必须先配置 AI 网关和模型。</p>
<h4>配置步骤</h4>
<ol>
<li>登录平台总控后台（<code>/platform</code>）</li>
<li>进入「AI 模型」页面</li>
<li>确保顶部「启用 AI」开关已打开</li>
<li>点击「新增网关」，填写：<ul>
<li><strong>编码</strong>：唯一标识，如 <code>deepseek</code></li>
<li><strong>名称</strong>：显示名称，如 <code>DeepSeek</code></li>
<li><strong>Base URL</strong>：API 地址，如 <code>https://api.deepseek.com</code></li>
<li><strong>API Key</strong>：API 密钥</li>
</ul></li>
<li>在网关下「新增模型」，填写：<ul>
<li><strong>编码</strong>：如 <code>deepseek-chat</code></li>
<li><strong>显示名</strong>：如 <code>DeepSeek Chat</code></li>
<li><strong>Model ID</strong>：模型标识，如 <code>deepseek-chat</code></li>
<li>勾选「全局默认」</li>
</ul></li>
<li>点击「测试」按钮验证连接是否正常</li>
</ol>
<h4>支持的模型</h4>
<p>支持所有 OpenAI 兼容的 API：</p>
<ul>
<li>DeepSeek</li>
<li>通义千问（阿里云）</li>
<li>Azure OpenAI</li>
<li>OpenAI</li>
<li>本地部署的 Ollama / vLLM 等</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>必须有一个模型设为「全局默认」，AI 员工才能工作</li>
<li>如果 AI 员工对话返回空或报错，先检查 AI 网关测试是否通过</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch10',
        title: '第十章 财务管理',
        icon: 'Coin',
        children: [
          {
            id: 'ch10-1',
            title: '10.1 客户对账单',
            content: `<h3>客户对账单</h3>
<p><strong>使用者</strong>：财务 / 销售客服</p>
<p><strong>操作路径</strong>：财务 → 客户对账单</p>
<h4>操作步骤</h4>
<ol>
<li>点击「+ 新建对账单」</li>
<li>选择客户和对账周期（如2026年5月）</li>
<li>系统自动列出该周期内所有订单及金额</li>
<li>核实订单数量和金额</li>
<li>确认无误后，对账单发送给客户</li>
<li>客户确认后，结束对账</li>
<li>支持导出 PDF 或 Excel</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>定期对账（月底或季度末），不要积压</li>
<li>确保订单状态准确（已交付/已结款）</li>
<li>保留对账记录以备查证</li>
</ul>`
          },
          {
            id: 'ch10-2',
            title: '10.2 收支流水',
            content: `<h3>收支流水</h3>
<p><strong>使用者</strong>：财务 / 会计</p>
<p><strong>操作路径</strong>：财务 → 收支流水</p>
<h4>主要功能</h4>
<ul>
<li>查看所有收支记录（应收/应付/实收/实付）</li>
<li>按时间、类型、客户/供应商筛选</li>
<li>手动新增收支记录</li>
<li>与银行流水对账</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>订单应收和采购应付自动生成</li>
<li>定期对账银行流水，确保账实相符</li>
</ul>`
          },
          {
            id: 'ch10-3',
            title: '10.3 成本毛利分析',
            content: `<h3>成本毛利分析</h3>
<p><strong>使用者</strong>：财务 / 运营主管</p>
<p><strong>操作路径</strong>：财务 → 成本毛利</p>
<h4>主要分析维度</h4>
<ul>
<li>订单总收入、生产成本（工资+物料）</li>
<li>毛利率、单笔订单毛利</li>
<li>毛利趋势图、成本占比图</li>
<li>产品毛利对比</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>成本计算基于工价和 BOM，必须准确</li>
<li>定期分析毛利，识别低毛利产品</li>
<li>用毛利分析指导定价策略</li>
</ul>`
          },
          {
            id: 'ch10-4',
            title: '10.4 财务总账（凭证 / 试算平衡 / 资产负债表）',
            content: `<h3>财务总账</h3>
<p><strong>使用者</strong>：财务</p>
<p><strong>操作路径</strong>：财务 → 总账</p>
<p>系统提供基础的<strong>记账凭证 → 试算平衡 → 资产负债表</strong>总账能力，与业务数据（销售 / 采购 / 收款 / 付款）联动生成会计分录。</p>
<h4>1. 记账凭证</h4>
<ul>
<li>按借贷分录录入：凭证日期、摘要、科目、借方金额、贷方金额</li>
<li>凭证号自动编排，支持多行分录（一借多贷 / 多借一贷）</li>
<li>保存时校验：借贷合计必须相等，否则无法过账</li>
</ul>
<h4>2. 试算平衡</h4>
<p>按会计期间汇总所有已过账凭证，输出各科目的<strong>期初 / 借方发生 / 贷方发生 / 期末余额</strong>，校验借贷平衡。</p>
<ul>
<li>支持按期间筛选试算表</li>
<li>不平衡提示定位差异分录</li>
</ul>
<h4>3. 资产负债表</h4>
<p>基于总账科目余额生成<strong>资产负债表</strong>：资产 / 负债 / 所有者权益，校验「资产 = 负债 + 所有者权益」恒等。</p>
<h4>注意事项</h4>
<ul>
<li>总账依赖规范的科目与凭证录入；业务单据自动生成的分录以业务配置为准</li>
<li>建议按会计期间结账后再出报表，避免期中数据波动</li>
</ul>`
          },
          {
            id: 'ch10-5',
            title: '10.5 固定资产（资产卡片 / 折旧 / 盘点）',
            content: `<h3>固定资产管理</h3>
<p><strong>使用者</strong>：财务 / 资产管理员</p>
<p><strong>操作路径</strong>：财务 → 固定资产</p>
<p>管理企业固定资产的生命周期：<strong>资产卡片 → 入账 → 按月折旧 → 定期盘点 → 报废 / 处置</strong>。</p>
<h4>1. 资产卡片</h4>
<ul>
<li>登记资产：名称、类别、购置日期、原值、预计残值、预计使用月数、责任人 / 部门</li>
<li>支持附件（购置发票 / 照片）</li>
<li>自动生成资产编码，全局唯一</li>
</ul>
<h4>2. 折旧</h4>
<ul>
<li>默认直线法（原值 - 残值）/ 使用月数，按月计提</li>
<li>已计提月数、累计折旧、账面净值自动更新</li>
<li>折旧期满自动停止计提</li>
</ul>
<h4>3. 盘点与处置</h4>
<ul>
<li>发起盘点：账面数量 vs 实地盘点，记录盘盈 / 盘亏</li>
<li>报废 / 处置：登记处置日期、方式（报废 / 出售 / 捐赠）、处置金额</li>
<li>处置后资产从在用转为已处置，停止折旧</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>折旧计入与总账联动，转成固定资产凭证</li>
<li>盘点差异需财务复核后方可调账</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch11',
        title: '第十一章 溯源与报表',
        icon: 'DataBoard',
        children: [
          {
            id: 'ch11-1',
            title: '11.1 溯源查询',
            content: `<h3>溯源查询</h3>
<p><strong>使用者</strong>：质管 / 客户服务 / 工程</p>
<p><strong>操作路径</strong>：生产 → 溯源查询</p>
<h4>操作步骤</h4>
<ol>
<li>输入或扫描成品二维码/条码</li>
<li>系统反查全生命周期信息：<ul>
<li><strong>订单信息</strong>：订单号、客户、交期</li>
<li><strong>工单信息</strong>：工单号、产品型号、数量</li>
<li><strong>工序追踪</strong>：各工序操作员工、时间、数量、照片/视频</li>
<li><strong>质检记录</strong>：QC 审核意见、不良率</li>
<li><strong>物料批次</strong>：使用物料来源和批次号</li>
<li><strong>设备记录</strong>：使用设备和工序参数</li>
</ul></li>
<li>生成 PDF 溯源报告</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>溯源信息完整性很重要，确保所有工序有记录</li>
<li>报工时必须上传照片/视频，否则无法溯源</li>
<li>用于：质量问题追责、客户投诉、产品召回</li>
</ul>`
          },
          {
            id: 'ch11-2',
            title: '11.2 生产报表',
            content: `<h3>生产报表</h3>
<p><strong>使用者</strong>：厂长 / 生产经理 / 财务</p>
<p><strong>操作路径</strong>：报表 → 生产报表</p>
<h4>指标类型</h4>
<ul>
<li><strong>产量</strong>：目标产量、实际完成量、达成率</li>
<li><strong>质量</strong>：合格率、不良率、重点工序不良率</li>
<li><strong>工时</strong>：总工时、有效工时、工时利用率、人均产出</li>
<li><strong>工序分析</strong>：各工序产出量、不良数、瓶颈识别</li>
<li><strong>员工排名</strong>：按产量、良率、工资排名</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>报表基于报工数据，报工准确性影响报表准确性</li>
<li>异常数据需调查（如产量突增/骤减）</li>
<li>用报表数据指导改进（消除瓶颈、提高良率）</li>
</ul>`
          },
          {
            id: 'ch11-3',
            title: '11.3 经营报表',
            content: `<h3>经营报表</h3>
<p><strong>使用者</strong>：厂长 / 财务 / 运营</p>
<p><strong>操作路径</strong>：报表 → 经营报表</p>
<h4>指标类型</h4>
<ul>
<li><strong>销售</strong>：订单总数、总金额、平均金额、完成率</li>
<li><strong>客户</strong>：客户总数、活跃客户数、贡献度排名</li>
<li><strong>成本毛利</strong>：总收入、总成本、毛利、毛利率</li>
<li><strong>趋势</strong>：月销售额趋势、客户增长趋势</li>
</ul>`
          },
          {
            id: 'ch11-4',
            title: '11.4 采购统计',
            content: `<h3>采购统计</h3>
<p><strong>使用者</strong>：采购 / 财务 / 运营</p>
<p><strong>操作路径</strong>：报表 → 采购统计</p>
<h4>指标类型</h4>
<ul>
<li>采购总金额，按供应商/物料类别排名</li>
<li>供应商评价：交期准时率、质量合格率</li>
<li>物料库存：积压预警、缺货预警、周转率</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch12',
        title: '第十二章 设备与保养',
        icon: 'Tools',
        children: [
          {
            id: 'ch12-1',
            title: '12.1 设备档案',
            content: `<h3>设备档案</h3>
<p><strong>使用者</strong>：设备管理员 / 生产主管</p>
<p><strong>操作路径</strong>：生产 → 设备管理</p>
<h4>操作步骤</h4>
<ol>
<li>点击「新增设备」</li>
<li>填写设备名称（必填）、型号、所属车间</li>
<li>编码可留空，系统自动生成</li>
<li>保存后可在列表查看上次/下次维护日期</li>
</ol>
<p>设备状态：<strong>正常</strong>、<strong>维修中</strong>、<strong>已退役</strong></p>`
          },
          {
            id: 'ch12-2',
            title: '12.2 日常点检',
            content: `<h3>日常点检</h3>
<p><strong>使用者</strong>：班组长 / 设备员</p>
<p><strong>操作路径</strong>：设备管理 → 列表「点检」</p>
<h4>操作步骤</h4>
<ol>
<li>在设备行点击「点检」</li>
<li>系统默认登记「日检 / 合格」</li>
<li>异常设备应改为「维修中」状态</li>
</ol>
<p>点检数据供 AI 设备健康分析参考。</p>`
          },
          {
            id: 'ch12-3',
            title: '12.3 保养计划',
            content: `<h3>保养计划（预防性维护）</h3>
<p><strong>使用者</strong>：设备管理员</p>
<p><strong>操作路径</strong>：设备管理 →「保养」→ 保养计划</p>
<h4>操作步骤</h4>
<ol>
<li>点击设备行的「保养」，打开保养管理抽屉</li>
<li>点击「新增计划」</li>
<li>配置：计划类型（日检/周检/月检）、周期(天)、下次日期、负责人、检查项</li>
<li>保存计划</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>同一设备可配置多条计划（如周检+月检）</li>
<li>周期天数用于登记保养后自动推算下次维护日期</li>
</ul>`
          },
          {
            id: 'ch12-4',
            title: '12.4 登记保养记录',
            content: `<h3>登记保养记录</h3>
<p><strong>使用者</strong>：设备员 / 班组长</p>
<p><strong>操作路径</strong>：保养抽屉 → 执行/登记保养</p>
<h4>操作步骤</h4>
<ol>
<li><strong>从计划执行</strong>：点击计划行的「执行」→ 选择结果（合格/不合格/部分完成）→ 填写说明 → 提交</li>
<li><strong>直接登记</strong>：点击「登记保养」→ 可选关联计划 → 填写结果与说明 → 提交</li>
<li>提交后上次维护更新为当天，下次维护自动顺延</li>
</ol>`
          },
        ]
      },
      {
        id: 'ch13',
        title: '第十三章 智能中心与 IM 推送',
        icon: 'ChatLineRound',
        children: [
          {
            id: 'ch13-1',
            title: '13.1 飞书消息推送',
            content: `<h3>飞书消息推送</h3>
<p>辰科MES 通过飞书自建应用把派工、报工审核、工资、预警等事件推送到飞书群或个人。<strong>必须先在飞书开放平台创建企业自建应用</strong>，详见 <a href="https://admin.mes.cenkor.cn" target="_blank">《飞书消息推送部署指南》</a>（docs/飞书消息推送部署指南.md）。</p>
<h4>配置入口</h4>
<p>侧边栏 → <strong>系统管理 → 飞书消息推送</strong>（需 <code>setting.manage</code> 权限）。</p>
<h4>三步开启</h4>
<ol>
<li><strong>填入 App ID / App Secret</strong>：从飞书开放平台 → 应用 → 凭证获取；<code>Encrypt Key</code> / <code>Verification Token</code> 在「事件订阅」页获取。</li>
<li><strong>设置事件回调</strong>：在「飞书消息推送」页面保存后会显示事件回调 URL（<code>{域名}/api/feishu/events</code>），粘贴到飞书开放平台 → 事件订阅 → 请求地址 URL，飞书会发起 <code>url_verification</code> 验证。</li>
<li><strong>配置群组 chat_id</strong>：点「拉取机器人所在群」自动列出机器人已加入的群；选三个固定群（<strong>生产群 / 管理群 / 全厂群</strong>），<code>chat_id</code> 必须以 <code>oc_</code> 开头，<em>不是</em>机器人 webhook URL。</li>
</ol>
<h4>员工飞书账号绑定（推到个人）</h4>
<ul>
<li><strong>方案 A · OAuth（推荐）</strong>：员工在 H5 个人中心点「绑定我的飞书」跳转飞书授权，回调后系统自动存 <code>open_id</code>。</li>
<li><strong>方案 B · 管理员后台批量匹配</strong>：Admin → 飞书消息推送 → 「按手机号批量匹配」，员工手机号与飞书账号一致时一键批量绑定。</li>
<li><strong>方案 C · 个人手动</strong>：Admin → 「人员绑定」用邮箱 / 手机号逐个匹配（适用于手机号不一致的少数员工）。</li>
</ul>
<h4>推送规则</h4>
<p>事件码 → 推送目标 → 通道。系统默认规则可按需调整，典型事件：</p>
<ul>
<li><code>dispatch.assigned</code> 派工 → 推给被派员工（飞书 + 站内）</li>
<li><code>report.submitted</code> 报工提交 → 推给部门负责人 + 车间负责人（飞书 + 站内）</li>
<li><code>report.leader_approved</code> / <code>report.qc_approved</code> 审核通过 → 推给员工</li>
<li><code>report.rejected</code> 驳回 → 推给员工</li>
<li><code>salary.slip_remind</code> / <code>salary.slip_reset</code> 工资条 → 推给员工</li>
<li><code>alert</code> 预警 → 按 <code>level</code>（info/warning/danger/critical）逐级升级到部门管理 / 老板 / 全厂群</li>
<li><code>brief.daily</code> 每日简报 → 推给老板 + 管理群 + 全厂群（每天 20:00 自动跑，需开启 <code>briefing.daily_enabled</code>）</li>
</ul>
<h4>静默时段</h4>
<p>配置 <code>quiet_hours</code>（默认 22:00–07:00）后，该时段事件会落库为 <code>deferred</code> 状态，<strong>Celery Beat 每 5 分钟</strong>触发 <code>feishu.flush_deferred</code> 任务到点发送。</p>
<h4>故障排查</h4>
<ul>
<li>「完全收不到」：检查 Celery worker + beat 是否在跑（<code>ps aux | grep celery -A app.celery_app</code>）。</li>
<li>「deferred 一直不发」：Beat 没起来或调度没加载，<code>grep feishu /tmp/lightmes-celery/beat.log</code> 应能看到 <code>feishu-flush-deferred</code> 每 5 分钟。</li>
<li>「open_id 与 App 不匹配」：更换了飞书 App ID 但员工 <code>open_id</code> 没重绑 → 走「按手机号批量匹配」一键恢复。</li>
<li>日志查 <code>/tmp/lightmes-celery/worker.log</code>，失败任务会有 <code>error</code> 字段。</li>
</ul>`
          },
          {
            id: 'ch13-2',
            title: '13.2 钉钉消息推送',
            content: `<h3>钉钉消息推送</h3>
<p>钉钉通道支持两种推送方式：</p>
<ul>
<li><strong>群机器人 Webhook</strong>（推荐）：最简，群里加个机器人即可收消息；支持 ActionCard 卡片（含按钮），无需企业自建应用。</li>
<li><strong>工作通知（企业自建应用）</strong>：需在钉钉开放平台建应用、配置 <code>AgentId</code>，可向指定员工单发；可发卡片含审核按钮（报工审核场景）。</li>
</ul>
<h4>配置入口</h4>
<p>侧边栏 → <strong>系统管理 → 钉钉消息推送</strong>（需 <code>setting.manage</code> 权限）。</p>
<h4>群机器人配置</h4>
<ol>
<li>在钉钉群里「群设置 → 智能群助手 → 添加机器人 → 自定义」获取 <strong>Webhook URL</strong>；如启用「加签」会得到 <strong>Secret</strong>，两者都要填到 辰科MES。</li>
<li>辰科MES → 钉钉消息推送 → 选群（生产群 / 管理群 / 全厂群）→ 填 webhook + secret → 保存。</li>
<li>点「测试推送」验证。</li>
</ol>
<h4>工作通知配置</h4>
<ol>
<li>钉钉开放平台 → 应用开发 → 创建「企业内部应用」→ 拿到 <code>AppKey</code> / <code>AppSecret</code> / <code>AgentId</code>。</li>
<li>应用权限开通「<strong>机器人发送消息</strong>」「<strong>工作通知</strong>」「<strong>免登</strong>」。</li>
<li>辰科MES → 钉钉消息推送 → 顶部填 AppKey / AppSecret / AgentId → 保存。</li>
</ol>
<h4>员工钉钉账号绑定</h4>
<p>工作通知通道依赖 <code>dingtalk_userid</code>，三种方式：</p>
<ul>
<li><strong>OAuth 绑定</strong>：员工在 H5 个人中心 → 「绑定钉钉」走授权。</li>
<li><strong>手机号匹配</strong>：Admin → 钉钉推送 → 「按手机号批量匹配」。</li>
<li><strong>手动</strong>：Admin → 人员绑定 → 输入钉钉 userid。</li>
</ul>
<h4>卡片含审核按钮</h4>
<p>报工提交后推给审核人，钉钉卡片含「初审通过 / 驳回」按钮，点按钮直接审批（不打开网页）。需在钉钉推送页开启 <code>card_actions_enabled</code>，并在「安全设置」配置回调 URL <code>{域名}/api/dingtalk/card_action</code>。</p>
<h4>推送规则与静默时段</h4>
<p>事件码 → 目标 → 通道结构与飞书一致；静默时段配置 <code>quiet_hours</code>，<strong>Beat 每 5 分钟</strong>触发 <code>dingtalk.flush_deferred</code>。</p>
<h4>故障排查</h4>
<ul>
<li>「完全收不到」：Celery worker/beat 未跑；或总开关未启用。</li>
<li>「ActionCard 报错 400002」：ActionCard 字段名错（已修复为 <code>markdown</code>），<code>grep 'dingtalk webhook failed' /tmp/lightmes-celery/worker.log</code> 看实际发出去的 payload。</li>
<li>「工作通知 task_id 返回但收不到」：钉钉「机器人单聊」需在钉钉里主动给应用发一条消息激活。</li>
</ul>`
          },
          {
            id: 'ch13-3',
            title: '13.3 企业微信消息推送',
            content: `<h3>企业微信消息推送</h3>
<p>企微通道以<strong>群机器人 Webhook</strong>为主，把派工、报工审核、工资、预警推到企微群。无需企业自建应用，几分钟就能配好。</p>
<h4>配置入口</h4>
<p>侧边栏 → <strong>系统管理 → 企微消息推送</strong>（需 <code>setting.manage</code> 权限）。</p>
<h4>三步开启</h4>
<ol>
<li>企微群里「群设置 → 群机器人 → 添加」拿到 <strong>Webhook URL</strong>。</li>
<li>辰科MES → 企微推送 → 选群（生产群 / 管理群 / 全厂群）→ 填 webhook → 保存。</li>
<li>点「测试推送」验证。</li>
</ol>
<h4>员工企微账号绑定</h4>
<p>企微通道默认只推群。如需推个人，需在「企业微信推送」页配置企业自建应用 <code>CorpID</code> + 应用 <code>AgentId</code> + <code>Secret</code>，并让员工在 H5 完成 OAuth 绑定。详细见 <a href="https://admin.mes.cenkor.cn" target="_blank">docs/飞书消息推送部署指南.md</a>（IM 通道通用部分）。</p>
<h4>故障排查</h4>
<ul>
<li>「完全收不到」：<code>grep wecom /tmp/lightmes-celery/worker.log</code>，看任务是否被消费；<code>wecom.flush_deferred</code> beat 调度是否注册。</li>
<li>「Webhook 返回 40069」：频率超限，企业微信群机器人限制 20 条/分钟。</li>
</ul>`
          },
          {
            id: 'ch13-4',
            title: '13.4 统一消息中心',
            content: `<h3>统一消息中心</h3>
<p>统一管理飞书 / 企微 / 钉钉多通道推送。<strong>三个通道的群组、规则、日志</strong>在一页面对照维护，避免飞书配一遍企微又配一遍。</p>
<h4>配置入口</h4>
<p>侧边栏 → <strong>系统管理 → 统一消息中心</strong>（需 <code>setting.manage</code> 权限）。</p>
<h4>系统指定 3 个群</h4>
<p>无论用哪个 IM 通道，都建议维护这三群：</p>
<ul>
<li><strong>生产群</strong>：车间班组长、生产主管（收派工、报工提醒、异常报警）。</li>
<li><strong>管理群</strong>：厂长 / 经理 / 业务（收订单、工资异常、每天 20:00 工厂日报）。</li>
<li><strong>全厂群</strong>：老板 / 管理层（收 critical 级别预警、工厂日报）。</li>
</ul>
<p>每个群可在三个通道里各设一个 webhook / chat_id，<strong>可同时启用</strong>，消息会同步发到三个通道。</p>
<h4>推送规则</h4>
<p>事件码 → 目标 → 通道。三通道默认规则一致，可独立微调；修改后需分别点保存。</p>
<h4>推送日志</h4>
<p>页面底部表格显示最近 <code>feishu_push_logs</code> / <code>wecom_push_logs</code> / <code>dingtalk_push_logs</code>，含状态（pending / deferred / success / failed）、错误信息、飞书 message_id / 钉钉 task_id。可按状态、目标筛选。</p>
<h4>绑定状态</h4>
<p>页面右侧显示员工 IM 绑定情况：</p>
<ul>
<li><code>feishu_open_id</code> 已绑 / 未绑</li>
<li><code>wecom_userid</code> 已绑 / 未绑</li>
<li><code>dingtalk_userid</code> 已绑 / 未绑</li>
</ul>
<p>未绑员工收不到个人通知，会回退到站内通知（铃铛）。</p>`
          },
          {
            id: 'ch12-5',
            title: '12.5 AI 助手（智能对话）',
            content: `<h3>AI 助手（智能对话）</h3>
<p>辰科MES 内置 AI 助手，按角色提供问答与操作建议。需要先在 <code>.env</code> 配置 <code>AI_BASE_URL</code> / <code>AI_API_KEY</code>，并开启 <code>AI_ENABLED=true</code>。详见 <a href="https://admin.mes.cenkor.cn" target="_blank">docs/AI集成说明.md</a>。</p>
<h4>入口</h4>
<p>侧边栏 → <strong>智能中心 → AI 助手</strong>（需 <code>ai.use</code> 权限）。</p>
<h4>典型用法</h4>
<ul>
<li><strong>老板/管理层</strong>：「本月订单达成率」「毛利最高的产品」「昨天异常报警有哪些」「帮我写个催货话术」。</li>
<li><strong>生产主管</strong>：「某订单当前在哪个工序」「这个工序积压了多少待报工任务」「帮我排个 30 号前能交的计划」。</li>
<li><strong>班组长</strong>：「今天的待审报工」「最近一次驳回原因最多的缺陷码是什么」。</li>
<li><strong>员工</strong>：H5 端也能用，「我本月预估工资」「我的任务里最紧急的是哪个」。</li>
</ul>
<h4>上下文（context_id）</h4>
<p>多次对话会自动带上 <code>context_id</code>，AI 能记得前文（如「那上一单呢？」「把这个订单的工价也对比下」）。同一会话最长保留 30 轮，超过会触发摘要压缩。</p>
<h4>智能中心其他模块</h4>
<ul>
<li><strong>首页 AI 数据预警</strong>：Celery 每天 8/12/16/20 点扫描指标，超阈值推飞书/企微/钉钉群。</li>
<li><strong>工厂日报（每日简报）</strong>：每天 20:00 自动生成，汇总当日产值、达成率、不良率、订单进度；推老板 + 管理群 + 全厂群。</li>
<li><strong>排产 AI 建议</strong>：生产计划保存时，<code>aiScheduleSuggest</code> 调用 OR-Tools + AI 给出交期/优先级建议。</li>
<li><strong>AI 交期分析</strong>：对当前计划跑一遍瓶颈分析，提示哪道工序会卡交期。</li>
</ul>`
          },
        ]
      },
      {
        id: 'ch14',
        title: '附录：常见问题与最佳实践',
        icon: 'QuestionFilled',
        children: [
          {
            id: 'ch14-1',
            title: '14.1 常见问题',
            content: `<h3>常见问题</h3>
<h4>Q1：订单确认后发现产品型号错了，怎么办？</h4>
<p>已确认的订单不能直接修改。操作：<strong>作废该订单 → 新建正确的订单</strong>，系统会记录作废原因和时间。</p>
<h4>Q2：报工提交后发现数字填错了，怎么办？</h4>
<p>已提交的报工不能自己修改。联系班组长「<strong>驳回</strong>」该报工，员工重新报工。</p>
<h4>Q3：工资计算似乎有误，怎么复查？</h4>
<p>进入「工资管理」，点击员工名称查看详细计算过程，每笔报工的数量和金额都有记录。如确实有误，通知财务调整。</p>
<h4>Q4：物料库存不足，排产能推进吗？</h4>
<p>排产前系统会提示「物料不齐套」。两种选择：<strong>A. 延期排产</strong>（等物料到货）或 <strong>B. 紧急采购</strong>（加急订货）。不建议在物料不足时排产。</p>
<h4>Q5：员工对工资有异议，怎么处理？</h4>
<p>在工资管理里查看明细，每笔报工的工序和金额都有记录。如有虚报，可查看报工照片/视频对质。确实算错的由财务调整。</p>
<h4>Q6：产品的工艺路线要改，已生成的订单受影响吗？</h4>
<p>已确认的订单按原工艺路线执行不受影响。只有新确认的订单才用新工艺路线。建议新旧同时维护一段时间再删除旧的。</p>
<h4>Q7：飞书推送"完全收不到"怎么查？</h4>
<p>三步定位：① <code>ps aux | grep 'celery -A app.celery_app worker'</code> 确认 worker 活着；② <code>grep feishu /tmp/lightmes-celery/worker.log</code> 看任务是否成功；③ 飞书推送页 → 推送日志，按时间查 error_msg 字段。</p>
<h4>Q8：换服务器后旧飞书 open_id 全部失效？</h4>
<p>更换了飞书 App ID 才会失效（飞书 open_id 按应用隔离）。换服务器但 App ID 不变则不受影响。失效时 Admin → 飞书推送 → 「按手机号批量匹配」一键恢复。</p>
<h4>Q9：Celery 任务一直 "pending" 不执行？</h4>
<p>看 Redis db 是否被同机其他项目占用（典型症状：和 bizcloud/dify 撞 db 0）。修改 <code>backend/.env</code> 的 <code>CELERY_BROKER_URL</code> 到独立 db（推荐 db 2），重启 worker。</p>
<h4>Q10：报工审核后没推飞书？</h4>
<p>检查三件事：① 飞书推送总开关是否启用；② 员工 <code>feishu_open_id</code> 是否已绑（未绑会回退到站内通知）；③ 事件码规则里 <code>channels</code> 是否包含 <code>feishu</code>。</p>`
          },
          {
            id: 'ch14-2',
            title: '14.2 最佳实践建议',
            content: `<h3>最佳实践建议</h3>
<h4>1. 数据准确性最重要</h4>
<ul>
<li>产品/型号/工价/BOM 一定要准确</li>
<li>报工数据关系到工资，员工很关注</li>
<li>定期审计数据，发现异常及时处理</li>
</ul>
<h4>2. 建立规范和标准</h4>
<ul>
<li>产品编码规范、订单号规范、字典值规范</li>
<li>便于数据查询和维护</li>
</ul>
<h4>3. 权限最小化原则</h4>
<ul>
<li>员工只能看自己的任务和工资</li>
<li>班组长能管理自己部门的工作</li>
<li>财务独立管理工资和对账</li>
</ul>
<h4>4. 定期备份和复盘</h4>
<ul>
<li>定期导出重要数据（工资表、订单表）</li>
<li>月度或季度复盘各项指标</li>
</ul>
<h4>5. 员工培训很关键</h4>
<ul>
<li>不同角色需要培训不同功能</li>
<li>班组长要理解报工审核的重要性</li>
<li>员工要知道如何正确报工</li>
</ul>
<h4>6. IM 推送运维必做</h4>
<ul>
<li>服务器迁移后必须改 <code>.env</code> 的 Redis db（避免和同机项目撞库）</li>
<li>飞书 / 钉钉 改了 App ID / AgentId 后必须重做员工 open_id 绑定</li>
<li>改完代码 / 上线新功能后必须重启 Celery（Beat 不会热加载调度表）</li>
</ul>`
          },
          {
            id: 'ch14-3',
            title: '14.3 部署与运维（开源版）',
            content: `<h3>部署与运维指南</h3>
<p>本文档面向开源用户，说明如何从零搭建 LightMes 并保持后台服务稳定运行。</p>

<h4>一、环境要求</h4>
<table>
<tr><th>组件</th><th>版本</th><th>说明</th></tr>
<tr><td>Linux</td><td>Debian/Ubuntu/CentOS</td><td>宝塔面板或纯命令行</td></tr>
<tr><td>Python</td><td>3.10+</td><td>后端运行环境</td></tr>
<tr><td>Node.js</td><td>18+</td><td>前端构建</td></tr>
<tr><td>MySQL</td><td>5.7+</td><td>数据库（需 utf8mb4）</td></tr>
<tr><td>Redis</td><td>6+</td><td>Celery 消息队列</td></tr>
</table>

<h4>二、后端部署</h4>
<ol>
<li>创建数据库：<code>CREATE DATABASE lightmes DEFAULT CHARACTER SET utf8mb4;</code></li>
<li>进入 <code>backend/</code> 目录，<code>cp .env.example .env</code> 修改数据库连接和 JWT 密钥</li>
<li>安装依赖并迁移：<code>pip install -r requirements.txt && alembic upgrade head</code></li>
<li>通过 uvicorn 启动：<code>uvicorn app.main:app --host 127.0.0.1 --port 8000</code></li>
<li>验证：<code>curl http://127.0.0.1:8000/api/health</code> 应返回 <code>{"code":200}</code></li>
</ol>

<h4>三、前端构建</h4>
<p>至少需要构建管理端和 H5 端：</p>
<pre><code>cd frontend-admin-pro && npm install && npm run build
cd frontend-h5 && npm install && npm run build</code></pre>
<p>产物分别在 <code>frontend-admin-pro/dist/</code> 和 <code>frontend-h5/dist/</code>，配置 Nginx 指向即可。</p>

<h4>四、Celery 后台任务（必配）</h4>
<p>消息推送、定时预警、工资导出等功能需要 Celery 来处理异步任务。<strong>不配则收不到飞书/钉钉/企微推送</strong>。</p>

<p><strong>推荐方式：systemd 系统服务（开机自启）</strong></p>
<pre><code>bash /www/wwwroot/lightmes/scripts/deploy-celery.sh</code></pre>
<p>脚本自动注册 Worker 和 Beat 为系统服务，服务器重启后自动运行。</p>

<p>查看状态：</p>
<pre><code>systemctl status lightmes-celery.service
systemctl status lightmes-beat.service</code></pre>

<p>备用方式（临时调试）：</p>
<pre><code>bash /www/wwwroot/lightmes/scripts/start-celery.sh
bash /www/wwwroot/lightmes/scripts/stop-celery.sh</code></pre>

<p>日志目录：<code>/tmp/lightmes-celery/</code></p>

<h4>五、换服务器 checklist</h4>
<ol>
<li>数据库导出导入，确认库名和密码一致</li>
<li>复制项目代码，配置 <code>backend/.env</code></li>
<li>安装依赖、执行 <code>alembic upgrade head</code></li>
<li>重新构建前端并部署到 Nginx</li>
<li><strong>重点：重新部署 Celery 服务</strong>：<code>bash scripts/deploy-celery.sh</code></li>
<li>检查 Redis：<code>.env</code> 中的 <code>REDIS_URL</code> 是否与同机其他项目冲突（推荐 db 2）</li>
<li>验证飞书/钉钉/企微推送是否正常</li>
</ol>

<h4>六、常见问题</h4>
<p><strong>Q：换服务器后收不到推送？</strong></p>
<p>99% 是 Celery 没启动。执行 <code>ps aux | grep celery</code> 看有没有 <code>lightmes_worker</code> 和 <code>DatabaseScheduler</code> 进程。没有则执行 <code>bash scripts/deploy-celery.sh</code> 重新部署。</p>
<p><strong>Q：Celery 任务一直 pending？</strong></p>
<p>Redis db 可能被同机其他项目占用。确保 <code>.env</code> 中 <code>REDIS_URL</code> 使用独立 db（推荐 <code>redis://127.0.0.1:6379/2</code>）。</p>`
          },
          {
            id: 'ch15',
            title: '第十五章 CRM 客户关系管理',
            icon: 'User',
            children: [
              {
                id: 'ch15-1',
                title: '15.1 CRM 是什么 & 解决什么问题',
                content: `<h3>CRM 客户关系管理</h3>
<p><strong>使用者</strong>：销售 / 销售经理 / 老板</p>
<p><strong>操作路径</strong>：顶部菜单 → 客户管理（CRM）</p>
<h4>一句话讲清楚</h4>
<p>CRM = 帮你<strong>管住每一个客户从「我听说过你」到「你已经付了钱」的整条路径</strong>，并在每个关键节点告诉你「该做什么了」。</p>
<h4>销售漏斗的五个阶段</h4>
<table>
<tr><th>阶段</th><th>在系统里叫</th><th>在系统里做什么</th></tr>
<tr><td>1. 线索</td><td><strong>线索池 (Leads)</strong></td><td>录入「谁可能买我东西」，分配给销售跟进</td></tr>
<tr><td>2. 商机</td><td><strong>商机 (Opportunities)</strong></td><td>把有意向的线索升级为商机，记录金额、预计成交日、阶段</td></tr>
<tr><td>3. 报价</td><td><strong>报价单 (Quotations)</strong></td><td>给客户发报价（产品、数量、单价、有效期）</td></tr>
<tr><td>4. 合同</td><td><strong>合同 (Contracts)</strong></td><td>客户接受了，签合同、设回款计划</td></tr>
<tr><td>5. 订单</td><td><strong>订单 (Orders)</strong></td><td>合同转成可生产订单，进入 MES 流程</td></tr>
</table>
<blockquote>新成员常见误区：CRM 不是「客户档案」。客户档案只是<strong>其中一个</strong>模块。CRM 是一条<strong>完整的销售流水线</strong>。</blockquote>
<h4>CRM 的 12 个子页面</h4>
<table>
<tr><th>菜单</th><th>做什么</th><th>谁用</th></tr>
<tr><td>客户档案</td><td>客户详细信息、健康度、订单历史</td><td>销售 / 老板</td></tr>
<tr><td>线索池</td><td>新客户来源记录、分配、跟进</td><td>销售</td></tr>
<tr><td>商机</td><td>在谈客户、金额、阶段、预计成交</td><td>销售 / 销售经理</td></tr>
<tr><td>商机看板</td><td>所有商机按阶段分列，拖拽改阶段</td><td>销售经理</td></tr>
<tr><td>商机统计</td><td>漏斗转化率、阶段金额、销售排行</td><td>老板</td></tr>
<tr><td>报价单</td><td>历史报价、有效/过期状态</td><td>销售</td></tr>
<tr><td>报价单创建</td><td>从商机一键转报价（自动带客户、产品）</td><td>销售</td></tr>
<tr><td>合同</td><td>历史合同、生效/到期状态</td><td>销售 / 财务</td></tr>
<tr><td>合同创建</td><td>从报价单转合同，可设回款计划</td><td>销售</td></tr>
<tr><td>销售目标</td><td>按月/季/年给销售设业绩目标</td><td>老板</td></tr>
<tr><td>公海池</td><td>长期未跟进的客户可被其他人领走</td><td>销售</td></tr>
<tr><td>营销活动</td><td>记录展会、广告、推广活动及 ROI</td><td>销售经理</td></tr>
<tr><td>赢单/输单原因</td><td>输了单必须填原因，用来改进</td><td>销售</td></tr>
<tr><td>客户标签</td><td>自定义客户分类标签（VIP、需发票、欠款等）</td><td>销售</td></tr>
<tr><td>导入导出</td><td>批量从 Excel 导入客户</td><td>销售</td></tr>
<tr><td>CRM 设置</td><td>配置赢单阶段、必填字段</td><td>管理员</td></tr>
</table>
<h4>与其他模块的联动</h4>
<ul>
<li>CRM 客户 → 销售订单（订单里选客户时只能选 CRM 客户）</li>
<li>CRM 商机 → 报价单 → 合同 → 订单（每一步都自动带上一阶段的数据）</li>
<li>CRM 客户健康度 → 老板看板的"客户风险"卡片</li>
<li>CRM 销售目标 → 老板看板的"销售达成率"</li>
</ul>`,
              },
              {
                id: 'ch15-2',
                title: '15.2 销售日常的一天：完整操作流程',
                content: `<h3>销售日常操作流程（实战版）</h3>
<p>这一节按<strong>销售一天的真实工作</strong>来讲，不是按菜单讲。</p>
<h4>上午 9:00：处理昨晚的公海客户</h4>
<ol>
<li>打开 <strong>CRM → 公海池</strong></li>
<li>看到「超过 7 天无跟进」的客户已被自动释放</li>
<li>挑出有价值的客户 → 点「领取」→ 客户自动进我的「我的客户」</li>
<li>系统自动给该客户的原负责人发通知：「客户 X 已被 Y 领取」</li>
</ol>
<h4>上午 9:30：录入今天的新线索</h4>
<ol>
<li>打开 <strong>CRM → 线索池 → + 新建线索</strong></li>
<li>填写：客户名、联系方式、来源（展会/转介绍/网络）、意向产品</li>
<li>点「分配给」→ 选择具体的销售同事</li>
<li>系统给该销售发通知：「你有一条新线索」</li>
</ol>
<h4>上午 10:00：跟进一个老客户的商机</h4>
<ol>
<li>打开 <strong>CRM → 商机</strong>，找到「在谈中」的商机</li>
<li>点商机名称 → 进入商机详情</li>
<li>看历史跟进记录（上次谁联系的、聊了什么）</li>
<li>点「记录跟进」→ 选跟进方式（电话/拜访/微信）→ 填内容 → 保存</li>
<li>如果客户有新的预算信息 → 改商机金额</li>
</ol>
<h4>上午 11:00：客户要报价了</h4>
<ol>
<li>在商机详情页点「转报价单」</li>
<li>系统自动把客户、产品、数量带过来</li>
<li>手动调整：单价、有效期、付款条件、备注</li>
<li>点「保存并发送」→ 客户邮箱/微信收到报价单 PDF</li>
<li>系统自动把商机阶段推进到「已报价」</li>
</ol>
<h4>下午 2:00：客户同意签合同</h4>
<ol>
<li>在报价单详情页点「转合同」</li>
<li>填写：合同编号、签订日期、生效日期、到期日期</li>
<li>设置「回款计划」：分几期、每期金额、每期日期</li>
<li>上传合同扫描件（拖到附件区）</li>
<li>点「提交审批」→ 走工作流 → 领导审批通过后合同生效</li>
</ol>
<h4>下午 3:00：合同转生产订单</h4>
<ol>
<li>合同审批通过后，点「转订单」</li>
<li>系统自动创建「销售订单」<strong>（这是从 CRM 跨到 MES 的入口）</strong></li>
<li>订单状态为「草稿」→ 销售复核金额、交期、备注</li>
<li>点「确认订单」→ 订单变为「已确认」</li>
<li>自动触发：<strong>生产计划 → 工单 → 派工</strong>，车间开始干活</li>
</ol>
<h4>下午 5:00：盘今天的销售业绩</h4>
<ol>
<li>打开 <strong>CRM → 商机看板</strong>（拖拽式看板，按阶段分列）</li>
<li>拖动商机卡片到不同阶段 → 自动记录阶段变化时间和操作人</li>
<li>打开 <strong>CRM → 商机统计</strong>，看：<ul>
<li>本月新增商机数</li>
<li>赢单率（赢 / 总数）</li>
<li>阶段漏斗图（每个阶段多少金额）</li>
<li>销售排行（按业绩）</li>
</ul></li>
</ol>
<h4>关键避坑</h4>
<blockquote>⚠️ <strong>不要跳过商机直接报价</strong>。没有商机记录的报价，是「无源之水」，后续统计不到赢率、看不到客户真实需求。</blockquote>
<blockquote>⚠️ <strong>输单必须填原因</strong>。在商机详情点「标记为输单」会强制弹窗让填原因，这是销售改进的核心数据。</blockquote>
<blockquote>⚠️ <strong>公海池 7 天未跟进自动释放</strong>，不可撤回。重要的客户建议在「客户档案」设「保护期」或者经常跟进。</blockquote>`,
              },
              {
                id: 'ch15-3',
                title: '15.3 客户健康度 & 公海池机制（重点）',
                content: `<h3>客户健康度与公海池机制</h3>
<h4>一、客户健康度是什么？</h4>
<p>系统对<strong>每个客户</strong>自动计算一个 0-100 的「健康分」，<strong>分数越低越危险</strong>。用来提醒老板：「这客户别丢了」。</p>
<h4>健康度怎么算？</h4>
<table>
<tr><th>因子</th><th>加分</th><th>减分</th></tr>
<tr><td>近 30 天有订单</td><td>+30</td><td></td></tr>
<tr><td>近 90 天有订单</td><td>+15</td><td></td></tr>
<tr><td>近 1 年有订单</td><td>+5</td><td></td></tr>
<tr><td>近 180 天无订单</td><td></td><td>-20</td></tr>
<tr><td>有欠款超期</td><td></td><td>-30</td></tr>
<tr><td>有投诉记录</td><td></td><td>-10/次</td></tr>
<tr><td>活跃沟通（电话/微信/拜访）</td><td>+5/次</td><td></td></tr>
</table>
<h4>健康度等级</h4>
<table>
<tr><th>分值</th><th>等级</th><th>含义</th><th>建议动作</th></tr>
<tr><td>80-100</td><td><strong>A 健康</strong></td><td>高价值活跃客户</td><td>保持服务，挖掘增购</td></tr>
<tr><td>60-79</td><td>B 良好</td><td>稳定客户</td><td>定期关怀</td></tr>
<tr><td>40-59</td><td>C 一般</td><td>需要唤醒</td><td>安排主动接触</td></tr>
<tr><td>20-39</td><td>D 风险</td><td>可能流失</td><td>销售经理介入</td></tr>
<tr><td>0-19</td><td>E 流失</td><td>已流失</td><td>分析流失原因</td></tr>
</table>
<h4>健康度自动更新时机</h4>
<ul>
<li>每天凌晨 3 点全量重算</li>
<li>客户新建订单时实时加分</li>
<li>客户被领取/释放时实时算</li>
</ul>
<h4>二、公海池机制详解</h4>
<p><strong>目的</strong>：防止销售「占着客户不跟进」造成资源浪费。</p>
<h4>什么客户会进公海？</h4>
<ol>
<li>领取后 <strong>7 天</strong>无任何跟进记录（电话/微信/拜访）</li>
<li>商机阶段 <strong>30 天</strong>未推进</li>
<li>客户被销售<strong>主动释放</strong></li>
<li>销售<strong>离职</strong>，名下所有客户自动进公海</li>
</ol>
<h4>保护机制</h4>
<table>
<tr><th>场景</th><th>是否进公海</th></tr>
<tr><td>刚领取，还没到 7 天</td><td>否</td></tr>
<tr><td>客户标记为「VIP」</td><td>否（VIP 永不进公海）</td></tr>
<tr><td>最近 3 天有跟进</td><td>否（重新计时）</td></tr>
<tr><td>客户已下过 10 单</td><td>否（高价值客户保护）</td></tr>
</table>
<h4>怎么防止客户被公海收走？</h4>
<ul>
<li><strong>设置 VIP 标签</strong>：客户档案 → 标签 → 加「VIP」</li>
<li><strong>勤跟进</strong>：哪怕只发个微信问候，<strong>3 天内必须有一次</strong>跟进记录</li>
<li><strong>设置保护期</strong>：客户档案 → 高级 → 保护期 30 天</li>
</ul>
<blockquote>⚠️ <strong>注意</strong>：保护期最长 90 天，到期后恢复普通规则。</blockquote>
<h4>从公海池领取客户</h4>
<ol>
<li>打开 CRM → 公海池</li>
<li>浏览客户列表（按「上次跟进时间」排序，最久未跟的在前）</li>
<li>看到合适的客户，点「领取」</li>
<li>系统检查：<ul>
<li>该客户当月领取上限（默认 20 个）</li>
<li>该客户是否在保护期</li>
</ul></li>
<li>领取成功 → 客户进入「我的客户」</li>
</ol>
<h4>查看「我的客户」</h4>
<p>顶部菜单「我的工作台」→「我的客户」。这里只显示你作为 owner 的客户，<strong>不等于</strong>你能看的所有客户（CRM 权限可配置看到全公司的客户）。</p>`,
              },
            ]
          },
          {
            id: 'ch16',
            title: '第十六章 工作流引擎（审批/会签/或签/多级）',
            icon: 'Setting',
            children: [
              {
                id: 'ch16-1',
                title: '16.1 工作流是什么 & 解决什么问题',
                content: `<h3>工作流引擎</h3>
<p><strong>使用者</strong>：管理员 / 流程设计者 / 各审批人</p>
<p><strong>操作路径</strong>：系统 → 审批流 / 工作流</p>
<h4>一句话讲清楚</h4>
<p>工作流 = 让「<strong>谁、什么时候、按什么规则、审批什么单据</strong>」这件事<strong>可视化、可配置、可追溯</strong>。不用每次审批都打电话问「该谁批」「批到哪一步了」。</p>
<h4>工作流 vs 普通审批的区别</h4>
<table>
<tr><th>普通审批（旧的）</th><th>工作流（新的）</th></tr>
<tr><td>写死在代码里</td><td>管理员可视化配置</td></tr>
<tr><td>顺序固定</td><td>支持条件分支、会签、或签、转交</td></tr>
<tr><td>只能一个人批</td><td>支持多人/多角色</td></tr>
<tr><td>改流程要开发</td><td>改流程配置即可，不用发版</td></tr>
<tr><td>历史记录只在单据上</td><td>独立轨迹页，可看全流程</td></tr>
</table>
<h4>工作流能处理的场景</h4>
<ul>
<li><strong>请假</strong>：员工 → 班组长 → 部门经理 → HR（按金额/天数条件分支）</li>
<li><strong>报销</strong>：员工 → 直属领导 → 财务（按金额分支，5000 以下财务终审）</li>
<li><strong>订单确认</strong>：销售 → 销售经理 → 财务审核 → 老板（VIP 客户需老板）</li>
<li><strong>采购订单</strong>：采购员 → 采购经理 → 财务 → 总经理（按金额）</li>
<li><strong>物料领用</strong>：员工 → 班组长 → 仓库</li>
<li><strong>设备维修</strong>：员工报修 → 设备主管 → 维修工</li>
</ul>
<h4>核心概念速查</h4>
<table>
<tr><th>术语</th><th>含义</th><th>举例</th></tr>
<tr><td>流程 (Flow)</td><td>一个完整的审批规则定义</td><td>「采购订单审批流」</td></tr>
<tr><td>节点 (Node)</td><td>流程中的一个审批环节</td><td>「采购经理审批」节点</td></tr>
<tr><td>实例 (Instance)</td><td>一次具体的审批过程</td><td>PO-2026-001 的审批实例</td></tr>
<tr><td>任务 (Task)</td><td>实例中每个节点产生的待办</td><td>「请王经理审批 PO-001」</td></tr>
<tr><td>轨迹 (Trace)</td><td>实例的完整审批日志</td><td>谁在几点几分批了/驳了/转给了谁</td></tr>
</table>`,
              },
              {
                id: 'ch16-2',
                title: '16.2 三种签字方式：会签 / 或签 / 顺序签',
                content: `<h3>三种签字方式（核心概念）</h3>
<p>工作流引擎最强大的特性是支持<strong>三种签字方式</strong>。在配置流程节点时必须选一种：</p>
<h4>1. 顺序签（最常见）</h4>
<p><strong>一个一个按顺序来</strong>。A 批完 → B 批 → C 批。</p>
<blockquote>📌 适用：请假、报销、订单确认、采购单 —— 99% 的场景都是顺序签</blockquote>
<p><strong>示例：请假 3 天</strong></p>
<ol>
<li>班组长批</li>
<li>部门经理批</li>
<li>HR 备案</li>
</ol>
<p>如果班组长驳回 → 直接回到申请人，流程结束。</p>
<h4>2. 会签（所有人都得批）</h4>
<p><strong>本节点所有人都必须批</strong>，缺一不可。<strong>全部通过</strong>才进入下一节点。</p>
<blockquote>📌 适用：合同审批（法务 + 财务 + 业务三方都同意）</blockquote>
<p><strong>示例：金额超 50 万的合同</strong></p>
<ol>
<li>销售总监 批</li>
<li><strong>法务 + 财务 + 老板三人会签</strong>（三人必须全批）</li>
<li>HR 备案</li>
</ol>
<p>如果三人中任何一个驳回 → <strong>全节点视为驳回</strong>，回到申请人。</p>
<h4>3. 或签（任一批就行）</h4>
<p><strong>本节点任一人批即可</strong>通过，其他人自动跳过。</p>
<blockquote>📌 适用：上级不在时的代审批、采购询价（多个采购员之一回复即可）</blockquote>
<p><strong>示例：紧急采购询价</strong></p>
<ol>
<li>采购员 A <strong>或</strong> 采购员 B <strong>或</strong> 采购员 C（三人中任一批即通过）</li>
</ol>
<p>如果 A 批了，B 和 C 不会收到任务（已自动跳过）。</p>
<h4>三种签字方式对比</h4>
<table>
<tr><th>方式</th><th>规则</th><th>驳回</th><th>通过条件</th></tr>
<tr><td>顺序签</td><td>按节点顺序一个一个</td><td>回到上一节点或申请人</td><td>当前节点通过即进下一节点</td></tr>
<tr><td>会签</td><td>本节点所有人同时</td><td>任一驳回 → 全节点驳回</td><td>所有人通过才进下一节点</td></tr>
<tr><td>或签</td><td>本节点任一人</td><td>任一驳回 → 全节点驳回</td><td>任一通过即进下一节点</td></tr>
</table>
<h4>实战配置建议</h4>
<blockquote>💡 <strong>会签用在「必须多方同意」</strong>，比如合同。用来约束所有人必须看。</blockquote>
<blockquote>💡 <strong>或签用在「加速流程」</strong>，比如领导不在时让副手能批。</blockquote>
<blockquote>💡 <strong>顺序签是默认</strong>，90% 场景够用。</blockquote>`,
              },
              {
                id: 'ch16-3',
                title: '16.3 条件分支：按金额/天数/部门自动分流',
                content: `<h3>条件分支（让流程"聪明"起来）</h3>
<p>条件分支 = 根据单据的<strong>实际数据</strong>，自动决定<strong>走哪条路径</strong>。</p>
<h4>常见条件场景</h4>
<table>
<tr><th>单据</th><th>条件</th><th>分支结果</th></tr>
<tr><td>请假</td><td>天数 < 3</td><td>班组长批 → 结束</td></tr>
<tr><td>请假</td><td>天数 ≥ 3</td><td>班组长 → 部门经理 → HR</td></tr>
<tr><td>采购</td><td>金额 < 1 万</td><td>采购经理批</td></tr>
<tr><td>采购</td><td>1 万 ≤ 金额 < 10 万</td><td>采购经理 → 财务</td></tr>
<tr><td>采购</td><td>金额 ≥ 10 万</td><td>采购经理 → 财务 → 总经理</td></tr>
<tr><td>订单</td><td>客户等级 = VIP</td><td>销售 → 销售经理 → <strong>老板</strong></td></tr>
<tr><td>订单</td><td>客户等级 = 普通</td><td>销售 → 销售经理</td></tr>
</table>
<h4>条件表达式的写法</h4>
<p>在「节点配置 → 条件」里写表达式，类 Excel 公式：</p>
<pre><code># 金额相关
amount &gt;= 100000

# 文本相关
customer.level == 'VIP'

# 组合
amount &gt;= 10000 AND department == '生产部'

# 多选
product_type IN ('设备', '模具')</code></pre>
<h4>条件评估的时机</h4>
<p>条件在<strong>进入下一个节点时</strong>评估一次，<strong>不是</strong>流程开始时评估。所以单据金额可以中间修改，流程会自动重新分流。</p>
<h4>条件没匹配上怎么办？</h4>
<p>走「<strong>默认分支</strong>」。每条流程的最后一个分支必须设为「默认」，否则单据会卡在条件节点等人工处理。</p>`,
              },
              {
                id: 'ch16-4',
                title: '16.4 实战：从零配置一个请假流程',
                content: `<h3>从零配置一个请假流程（手把手）</h3>
<p>这一节完整演示「员工请假 1 天」这个最常见流程怎么配。</p>
<h4>Step 1：创建流程</h4>
<ol>
<li>系统 → 审批流 → + 新建流程</li>
<li>填写：<ul>
<li><strong>流程名称</strong>：员工请假</li>
<li><strong>业务类型 (biz_type)</strong>：leave（这个对应后端代码里的 type）</li>
<li><strong>说明</strong>：所有员工的请假申请都走这个流程</li>
</ul></li>
<li>点「保存」</li>
</ol>
<h4>Step 2：画流程图</h4>
<p>进入流程设计画布，你看到的是一张空白 BPMN 图。系统支持拖拽式设计，左侧栏有节点：</p>
<ul>
<li><strong>开始节点</strong>（必选，1 个）</li>
<li><strong>审批节点</strong>（每个审批人/角色一个）</li>
<li><strong>结束节点</strong>（必选，1 个）</li>
<li><strong>条件网关</strong>（用来做分支）</li>
</ul>
<h4>Step 3：拖出三个审批节点</h4>
<ol>
<li><strong>节点 1：直属上级审批</strong><ul>
<li>审批人：选「角色」→ 班组长</li>
<li>签字方式：顺序签</li>
<li>超时时间：48 小时（不批自动催办）</li>
</ul></li>
<li><strong>节点 2：HR 备案</strong><ul>
<li>审批人：选「角色」→ HR</li>
<li>签字方式：顺序签</li>
</ul></li>
</ol>
<h4>Step 4：保存并启用</h4>
<ol>
<li>点画布右上「保存」</li>
<li>点「发布」→ 选择「v1.0」→ 启用</li>
<li>启用后流程状态变绿色，可被业务单据调用</li>
</ol>
<h4>Step 5：员工发起请假</h4>
<ol>
<li>员工打开 H5 → 我的 → 请假</li>
<li>填写：开始日期、结束日期、事由</li>
<li>点「提交」</li>
<li>系统自动：<ul>
<li>找到 biz_type=leave 的最新启用流程</li>
<li>创建审批实例</li>
<li>给节点 1 的班组长发通知：「你有 1 条待办」</li>
</ul></li>
</ol>
<h4>Step 6：班组长审批</h4>
<ol>
<li>班组长收到通知（飞书/钉钉/系统）</li>
<li>打开 PC 端 → 工作流 → 待办</li>
<li>看到「员工张三请假 1 天」</li>
<li>选「同意」或「驳回」</li>
<li>填审批意见（可选）</li>
<li>点「提交」</li>
</ol>
<h4>Step 7：HR 收到审批任务</h4>
<p>班组长通过后，系统自动推进到节点 2。HR 收到通知，重复 Step 6。</p>
<h4>Step 8：流程结束</h4>
<p>HR 通过后，流程结束。系统自动：</p>
<ul>
<li>更新请假单状态为「已通过」</li>
<li>触发考勤系统</li>
<li>归档流程轨迹</li>
</ul>
<h4>查看流程轨迹</h4>
<ol>
<li>请假单详情页 → 流程 → 查看轨迹</li>
<li>看到完整时间线：<ul>
<li>10:00 张三 提交</li>
<li>10:05 王班组长 同意（耗时 5 分钟）</li>
<li>10:10 李 HR 同意（耗时 5 分钟）</li>
<li>10:10 流程结束</li>
</ul></li>
</ol>
<h4>关键避坑</h4>
<blockquote>⚠️ <strong>修改已发起的流程实例不会生效</strong>。改流程定义后，只对新发起的实例生效，老的实例按原流程跑完。</blockquote>
<blockquote>⚠️ <strong>审批人离职/转岗</strong>：流程自动找「角色下的其他成员」，不会卡住。</blockquote>
<blockquote>⚠️ <strong>驳回后申请人改了单据再提交</strong>：会生成<strong>新实例</strong>，老的实例归档但不删。</blockquote>`,
              },
              {
                id: 'ch16-5',
                title: '16.5 我的待办 & 流程状态查询',
                content: `<h3>我的待办与流程状态查询</h3>
<h4>一、待办从哪里看？</h4>
<p>每个有审批权限的人，登录后默认有 3 个入口：</p>
<ol>
<li><strong>顶部铃铛图标</strong>（红点显示未读数）→ 点开是待办列表</li>
<li><strong>侧边栏「工作流」</strong> → 我的待办（详细列表，可过滤）</li>
<li><strong>移动端 H5</strong> → 消息 → 待办（老板/经理手机审批）</li>
</ol>
<h4>二、待办列表的字段</h4>
<table>
<tr><th>字段</th><th>说明</th><th>示例</th></tr>
<tr><td>单据类型</td><td>这个待办是什么单据</td><td>采购订单 / 请假单 / 报价单</td></tr>
<tr><td>单据编号</td><td>点进去看详情</td><td>PO-2026-001</td></tr>
<tr><td>发起人</td><td>谁提的</td><td>张三</td></tr>
<tr><td>发起时间</td><td>什么时候提的</td><td>10 分钟前</td></tr>
<tr><td>当前节点</td><td>流程走到哪了</td><td>采购经理审批</td></tr>
<tr><td>剩余时间</td><td>距离超时还剩多久（红色=快超时）</td><td>23 小时</td></tr>
<tr><td>操作</td><td>同意 / 驳回 / 转交 / 加签</td><td></td></tr>
</table>
<h4>三、4 种审批动作</h4>
<table>
<tr><th>动作</th><th>效果</th><th>何时用</th></tr>
<tr><td><strong>同意</strong></td><td>本节点通过，进入下一节点；如果是最后一个节点，流程结束</td><td>默认操作</td></tr>
<tr><td><strong>驳回</strong></td><td>本节点驳回，整个流程回到申请人，结束</td><td>不同意</td></tr>
<tr><td><strong>转交</strong></td><td>把任务转给其他人，<strong>自己不再处理这个待办</strong></td><td>出差、生病、请假的代审批</td></tr>
<tr><td><strong>加签</strong></td><td>增加一个人审批（本节点通过条件变了）</td><td>需要专家会诊</td></tr>
</table>
<h4>四、转交 vs 加签的区别</h4>
<blockquote>💡 <strong>转交</strong>：是「我不管了，让别人管」。我自己从流程里退出。</blockquote>
<blockquote>💡 <strong>加签</strong>：是「光我批不够，还得加个人批」。流程变复杂了，但原始审批人还是要在。</blockquote>
<h4>五、超时机制</h4>
<p>每个节点可以配<strong>超时时间</strong>（如 48 小时）。超时后系统自动：</p>
<ol>
<li>给审批人发催办通知</li>
<li>给他的上级也发通知</li>
<li>在待办列表标红</li>
</ol>
<p>超时<strong>不会</strong>自动通过。必须有人手动处理。</p>
<h4>六、撤销流程</h4>
<p>申请人可以撤销自己发起的流程（仅当还没人批时）。</p>
<ol>
<li>单据详情 → 流程 → 撤销</li>
<li>填撤销原因</li>
<li>流程结束，状态变「已撤销」</li>
</ol>
<p>如果已经有人批了，<strong>不能撤销</strong>，只能驳回。</p>
<h4>七、查看历史流程</h4>
<ol>
<li>工作流 → 已办</li>
<li>显示：流程名、单据、状态（通过/驳回/撤销）、处理时间</li>
<li>点「轨迹」看完整时间线（谁批的、批了多久、有什么意见）</li>
</ol>`,
              },
            ]
          },
          {
            id: 'ch17',
            title: '第十七章 AI 助理（老板问答 / 工具调用 / 写操作确认）',
            icon: 'QuestionFilled',
            children: [
              {
                id: 'ch17-1',
                title: '17.1 AI 助理是什么 & 解决什么问题',
                content: `<h3>AI 助理（智能对话）</h3>
<p><strong>使用者</strong>：老板 / 管理层 / 销售 / 车间主任 / 一线员工</p>
<p><strong>操作路径</strong>：侧边栏 → 智能中心 → AI 助理</p>
<h4>一句话讲清楚</h4>
<p>AI 助理 = <strong>用自然语言问系统问题，让 AI 帮你查数据 / 做分析 / 执行操作</strong>。不用记菜单路径、不用学 SQL、不用打电话问人。</p>
<h4>它能做什么 / 不能做什么</h4>
<table>
<tr><th>✅ 能做</th><th>❌ 不能做</th></tr>
<tr><td>查数据（订单、客户、库存、报工）</td><td>100% 准确（AI 可能答错，看下面）</td></tr>
<tr><td>做汇总统计（"上周销售额多少"）</td><td>做复杂的财务核算</td></tr>
<tr><td>分析异常（"为什么这个订单要逾期"）</td><td>修改底层数据（需要二次确认）</td></tr>
<tr><td>写操作（建草稿订单、创建客户）</td><td>绕过权限（你看不到的，它也查不到）</td></tr>
<tr><td>给建议（"怎么排产更合理"）</td><td>100% 替代人做决策</td></tr>
</table>
<h4>跟其他 AI 模块的关系</h4>
<ul>
<li>AI 助理 = <strong>通用对话入口</strong>，什么都能问</li>
<li>数字孪生 = <strong>3D 可视化</strong>的车间状态</li>
<li>视觉质检 = <strong>拍照判断</strong>产品是否合格</li>
<li>RAG 知识库 = <strong>查文档</strong>（操作手册、规范）</li>
<li>设备健康预测 = <strong>预测设备故障</strong></li>
<li>因果推断 = <strong>分析良率问题</strong>的根本原因</li>
</ul>
<h4>为什么需要 AI 网关？</h4>
<p>不同任务适合不同 LLM：</p>
<table>
<tr><th>场景</th><th>推荐模型</th><th>原因</th></tr>
<tr><td>老板问答（数据查询）</td><td>DeepSeek V3</td><td>中文好、成本低、速度可</td></tr>
<tr><td>长文档分析</td><td>豆包 Pro</td><td>长上下文好</td></tr>
<tr><td>多模态（看图）</td><td>Qwen-VL</td><td>支持图片输入</td></tr>
<tr><td>复杂推理</td><td>DeepSeek R1</td><td>推理能力强</td></tr>
</table>
<p>系统通过 <strong>AI 网关</strong> 自动路由到合适的模型，<strong>不绑死任何一家</strong>。</p>`,
              },
              {
                id: 'ch17-2',
                title: '17.2 三种使用方式：全局浮窗 / 对话页 / 移动端',
                content: `<h3>三种使用方式</h3>
<h4>方式 1：全局浮窗（最常用）</h4>
<p>在<strong>任何页面</strong>，右下角都有 AI 浮窗按钮。点开就能问。</p>
<ol>
<li>点右下角 🤖 浮窗</li>
<li>弹出对话窗</li>
<li>输入问题（或语音输入）</li>
<li>AI 流式回答（打字机效果）</li>
<li>如果 AI 要执行工具，会弹「确认卡片」</li>
</ol>
<blockquote>💡 <strong>优势</strong>：不用离开当前页面，沉浸式问答。</blockquote>
<h4>方式 2：完整对话页（深度会话）</h4>
<p>侧边栏 → 智能中心 → AI 助理，进入完整对话页。</p>
<p><strong>适合场景</strong>：</p>
<ul>
<li>多轮对话（AI 记得前文）</li>
<li>需要看历史会话</li>
<li>复杂问题（带表格、图表的回复）</li>
</ul>
<h4>方式 3：移动端 H5 / 小程序</h4>
<p>老板在外出差也能用：</p>
<ul>
<li><strong>H5 端</strong>：员工/经理手机端入口</li>
<li><strong>小程序</strong>：老板看板右上角浮窗</li>
</ul>
<p><strong>典型场景</strong>：老板在机场候机 → 打开小程序 → 问"今天生产怎么样" → 看到 AI 总结的昨日产量/今日目标/异常订单 → 决策下一步动作。</p>
<h4>界面速览</h4>
<table>
<tr><th>区域</th><th>功能</th></tr>
<tr><td>输入框</td><td>打字、语音、附件</td></tr>
<tr><td>历史会话</td><td>左侧栏，所有历史对话</td></tr>
<tr><td>工具卡</td><td>AI 决定调用工具时显示</td></tr>
<tr><td>确认卡</td><td>写操作前显示，等你确认</td></tr>
<tr><td>上下文引用</td><td>AI 引用了哪条业务数据，点开能跳转</td></tr>
</table>
<h4>对话历史保留</h4>
<ul>
<li>每个用户的会话<strong>单独保存</strong>（按 user_id）</li>
<li>默认保留 <strong>30 轮</strong>，超过自动摘要压缩</li>
<li>想全部保留：去 <code>系统 → AI 助理 → 设置</code> 关掉摘要</li>
</ul>`,
              },
              {
                id: 'ch17-3',
                title: '17.3 工具调用机制：只读 vs 写操作',
                content: `<h3>工具调用机制（最核心的原理）</h3>
<p>这一节是 AI 助理的<strong>灵魂</strong>，理解了它就理解了整个系统。</p>
<h4>什么是"工具"？</h4>
<p>工具 = 系统提供的一个函数，AI 可以"决定"调用它来获取数据或执行操作。</p>
<p>每个工具 = <strong>一个 Python 函数</strong>，AI 通过 function calling 自动选择。</p>
<h4>两类工具的对比</h4>
<table>
<tr><th>特性</th><th>只读工具（is_readonly=True）</th><th>写操作工具（is_readonly=False）</th></tr>
<tr><td>举例</td><td>query_customers / query_orders</td><td>create_order / update_customer</td></tr>
<tr><td>执行时机</td><td>AI 自动执行，无需确认</td><td><strong>必须用户在前端确认</strong></td></tr>
<tr><td>数据修改</td><td>不改</td><td>改</td></tr>
<tr><td>权限校验</td><td>需要相应读权限</td><td>需要相应写权限</td></tr>
<tr><td>误操作风险</td><td>无（不会改数据）</td><td>有（必须二次确认拦截）</td></tr>
</table>
<h4>为什么写操作必须二次确认？</h4>
<blockquote>⚠️ <strong>LLM 会幻觉</strong>。它可能把"取消订单"听成"删除订单"，把"客户 A"听成"客户 B"。如果没有二次确认，错数据就直接写进数据库了。</blockquote>
<p>二次确认 = <strong>最后一道防线</strong>。AI 说"我想做 X"，用户看到"AI 想做 X"，明确点「确认」才执行。</p>
<h4>完整流程：AI 怎么执行一个写操作</h4>
<ol>
<li>用户：「帮张三建个订单，5 个 A 产品」</li>
<li>AI 分析：需要调用 <code>create_order</code></li>
<li>AI 生成参数：<code>{customer_name: "张三", items: [{product_name: "A", qty: 5}]}</code></li>
<li>AI 返回 <code>confirmation</code> 事件给前端，包含参数</li>
<li>前端展示确认卡：「AI 想为张三建订单，5 个 A 产品，<strong>确认？</strong>」</li>
<li>用户点「确认」→ 前端调 <code>POST /assistant/act</code> 真正执行</li>
<li>后端执行工具，<strong>强制按当前用户 tenant_id 过滤</strong>（安全）</li>
<li>返回结果给前端</li>
<li>AI 看到结果，组织自然语言回答</li>
</ol>
<h4>用户拒绝会怎样？</h4>
<p>用户点「拒绝」→ 工具不执行 → AI 收到「用户拒绝」反馈 → AI 调整方案或询问更多细节。</p>
<h4>当前已内置的工具（v1）</h4>
<table>
<tr><th>工具名</th><th>类型</th><th>能问什么</th></tr>
<tr><td><code>query_customers</code></td><td>只读</td><td>"有哪些客户""搜客户名为 XX 的"</td></tr>
<tr><td><code>query_orders</code></td><td>只读</td><td>"今天的订单""XX 客户的所有订单""待确认的订单"</td></tr>
<tr><td><code>query_production_overview</code></td><td>只读</td><td>"今天怎么样""业绩如何""有什么要关注的"</td></tr>
<tr><td><code>query_inventory</code></td><td>只读</td><td>"XX 物料有多少库存""A 产品还有货吗"</td></tr>
<tr><td><code>create_order</code></td><td>写操作</td><td>"帮 XX 客户建个订单""录个订单"</td></tr>
</table>
<h4>给业务人员的话</h4>
<blockquote>💡 <strong>如果 AI 答错了，不要慌</strong>。写操作有二次确认，你点「拒绝」就行。如果你看到 AI 频繁出错的场景，反馈给管理员，让他调整提示词。</blockquote>`,
              },
              {
                id: 'ch17-4',
                title: '17.4 实战：30 个真实使用场景',
                content: `<h3>30 个真实使用场景（按角色分类）</h3>
<h4>🏢 老板 / 管理层（最常问）</h4>
<ol>
<li>「今天销售额多少？」</li>
<li>「本周订单达成率多少？」</li>
<li>「本月毛利最高的产品是什么？」</li>
<li>「哪些订单要逾期了？」</li>
<li>「最近一周有几次异常报警？」</li>
<li>「本月新增了多少客户？」</li>
<li>「赢单率最高的销售是谁？」</li>
<li>「有哪些客户健康度掉到 D 级了？」</li>
<li>「今天车间有什么异常？」</li>
<li>「帮我写个催货话术」</li>
</ol>
<h4>📊 销售 / 销售经理</h4>
<ol start="11">
<li>「张三这个客户最近一次下单是什么时候？」</li>
<li>「帮我查 XX 客户的所有订单」</li>
<li>「这个月业绩前三的销售是谁？」</li>
<li>「哪些商机卡在报价阶段超过 7 天了？」</li>
<li>「帮 XX 客户建个订单，5 个 A 产品，下周五交」</li>
<li>「XX 客户的健康度怎么样？」</li>
<li>「上个月赢单率是多少？」</li>
</ol>
<h4>🏭 生产主管 / 车间主任</h4>
<ol start="18">
<li>「今天车间进度怎么样？」</li>
<li>「XX 订单当前在哪个工序？」</li>
<li>「这个工序积压了多少待报工任务？」</li>
<li>「帮我排个 30 号前能交的计划」</li>
<li>「今天的待审报工有几条？」</li>
<li>「最近一次驳回原因最多的缺陷码是什么？」</li>
<li>「XX 工单的实际工时 vs 标准工时对比」</li>
</ol>
<h4>👷 一线员工 / 班组长</h4>
<ol start="25">
<li>「我今天有几个任务？」</li>
<li>「我本月预估工资多少？」</li>
<li>「我的任务里最紧急的是哪个？」</li>
<li>「XX 工单需要哪些物料？」</li>
<li>「请 3 天假怎么走流程？」</li>
</ol>
<h4>💡 高级玩法</h4>
<ul>
<li>「<strong>对比</strong>本周和上周的销售额」→ AI 会自动调两次 query 工具</li>
<li>「<strong>总结</strong>本月所有异常的订单」→ AI 多次调用后汇总</li>
<li>「<strong>给个建议</strong>，A 客户要不要继续跟进」→ AI 查客户健康度+订单历史后给建议</li>
</ul>`,
              },
              {
                id: 'ch17-5',
                title: '17.5 提示词模板 & 自定义场景',
                content: `<h3>提示词模板 & 自定义场景</h3>
<h4>什么是提示词模板？</h4>
<p>提示词 = <strong>告诉 AI"你是谁、你该怎么回答"</strong>的指令。系统管理员可以编辑这些模板，<strong>让 AI 的回答更贴合你的业务</strong>。</p>
<h4>内置场景</h4>
<table>
<tr><th>场景代码</th><th>用途</th><th>使用入口</th></tr>
<tr><td>boss_qa</td><td>老板问答（通用）</td><td>AI 助理</td></tr>
<tr><td>plan_risk</td><td>生产计划风险评估</td><td>生产计划保存时</td></tr>
<tr><td>plan_schedule</td><td>智能排产建议</td><td>排产页</td></tr>
<tr><td>audit_batch_summary</td><td>批量报工汇总</td><td>报工审核页</td></tr>
<tr><td>report_vision_audit</td><td>报表视觉审计</td><td>报表中心</td></tr>
</table>
<h4>怎么编辑提示词（管理员）</h4>
<ol>
<li>系统 → AI 助理 → 提示词管理</li>
<li>选场景：boss_qa</li>
<li>编辑模板：<pre><code>你是 LightMES 智能助理，名字叫「辰小秘」。
回答要求：
- 用中文
- 回答尽量简洁，3 句话内
- 涉及数据时给出具体数字
- 不要编造数据，不确定时明说
你的职责：帮老板快速了解生产/订单/财务情况。</code></pre></li>
<li>点「保存」</li>
<li>所有用户立即生效</li>
</ol>
<h4>提示词最佳实践</h4>
<blockquote>💡 <strong>明确身份</strong>：「你是 XX 公司的财务助理」比单纯「你是助理」更聚焦</blockquote>
<blockquote>💡 <strong>明确输出格式</strong>：「用表格回答」「不超过 5 行」</blockquote>
<blockquote>💡 <strong>明确禁止</strong>：「不要编造数据」「不要给医疗建议」</blockquote>
<blockquote>💡 <strong>提供上下文</strong>：「当前租户是 XX 工厂，主营 XX 产品」</blockquote>
<h4>怎么添加自定义场景</h4>
<p>当前版本场景是<strong>代码层注册</strong>的，需要开发加。新业务场景提需求给研发排期。</p>
<h4>A/B 测试提示词</h4>
<p>每个场景可以保存<strong>多个版本的提示词</strong>，按用户/租户分流。例：</p>
<ul>
<li>VIP 客户 → 用「专业版」提示词（更详细）</li>
<li>普通客户 → 用「简洁版」提示词</li>
</ul>`,
              },
              {
                id: 'ch17-6',
                title: '17.6 安全机制 & 常见问题',
                content: `<h3>安全机制 & 常见问题</h3>
<h4>一、安全机制（4 道防线）</h4>
<h5>防线 1：多租户隔离</h5>
<p>AI 看到的工具<strong>全部强制</strong>按 <code>current_user.tenant_id</code> 过滤，<strong>无法跨租户读</strong>。</p>
<p>如果用户用 admin 账号登录，AI 只能问 admin 所在租户的数据。</p>
<h5>防线 2：权限码</h5>
<p>每个工具有 <code>require_permissions</code> 字段，用户没这个权限 → AI 调不了。</p>
<p>例：<code>create_order</code> 需要 <code>order.manage</code> 权限，普通员工没有，AI 不会展示这个工具给员工。</p>
<h5>防线 3：写操作二次确认</h5>
<p>所有 <code>is_readonly=False</code> 的工具，<strong>必须</strong>前端点「确认」才执行。</p>
<h5>防线 4：审计日志</h5>
<p>所有 AI 对话和工具调用<strong>全部留痕</strong>：</p>
<ul>
<li>谁问的</li>
<li>什么时候</li>
<li>问了什么</li>
<li>AI 调了哪些工具</li>
<li>返回了什么</li>
<li>写操作用户有没有确认</li>
</ul>
<p>审计日志保留 180 天，管理员可查。</p>
<h4>二、常见问题（FAQ）</h4>
<h5>Q1：AI 答错了怎么办？</h5>
<p><strong>答</strong>：</p>
<ol>
<li>点对话气泡上的「❌」图标 → 选「回答有误」</li>
<li>系统记录这条反馈给管理员</li>
<li>管理员会调整提示词或工具</li>
</ol>
<h5>Q2：AI 调错工具怎么办？</h5>
<p><strong>答</strong>：写操作有二次确认，你点「拒绝」就行。读操作已经查了但没改数据，下次再问一次。</p>
<h5>Q3：AI 说"找不到数据"但我知道有</h5>
<p><strong>答</strong>：</p>
<ul>
<li>可能权限不够：你看不到的，AI 也看不到</li>
<li>可能 tenant 不对：切到对应租户再问</li>
<li>可能数据没录：去对应业务模块检查</li>
</ul>
<h5>Q4：怎么让 AI 记住我的偏好？</h5>
<p><strong>答</strong>：当前版本不支持长期记忆（每次会话独立）。要长期偏好，让管理员在提示词里写死。</p>
<h5>Q5：AI 响应慢？</h5>
<p><strong>答</strong>：</p>
<ul>
<li>慢 = LLM 响应慢，检查网关配置</li>
<li>切更快的模型（DeepSeek 比 Qwen 快）</li>
<li>管理员可在「AI 网关」配置超时</li>
</ul>
<h5>Q6：能不能用语音？</h5>
<p><strong>答</strong>：</p>
<ul>
<li>浏览器自带 Web Speech API（Chrome 支持）</li>
<li>移动端 H5 调用系统麦克风</li>
<li>语音转文字后还是用文本工具链</li>
</ul>
<h5>Q7：AI 能不能给老板主动推送？</h5>
<p><strong>答</strong>：可以。系统有「<strong>AI 主动推荐</strong>」模块：</p>
<ul>
<li>每天早上 9 点给老板推一份「今日关注」</li>
<li>发现异常时主动推飞书/企微/钉钉</li>
<li>订单状态变化时主动通知</li>
</ul>
<p>配置路径：智能中心 → 主动推荐设置。</p>
<h4>三、什么时候不应该用 AI 助理？</h4>
<blockquote>⚠️ <strong>涉及法律/合规/钱的决策</strong>：AI 给建议，人做决定</blockquote>
<blockquote>⚠️ <strong>大量数据导出</strong>：去报表中心导出 Excel，比 AI 准</blockquote>
<blockquote>⚠️ <strong>复杂流程配置</strong>：去工作流设计器画图</blockquote>`,
              },
            ]
          },
          {
            id: 'ch18',
            title: '第十八章 生产管理（工单/排产/报工/派工）',
            icon: 'Tools',
            children: [
              {
                id: 'ch18-1',
                title: '18.1 销售订单 → 工单 → 派工 → 报工 → 入库 完整流程',
                content: `<h3>生产管理总览</h3>
<p><strong>使用者</strong>：生产计划员 / 车间主任 / 班组长 / 操作工</p>
<p><strong>操作路径</strong>：生产 → 订单管理 / 工单 / 派工 / 报工</p>
<h4>一句话讲清楚</h4>
<p>生产管理 = 把「<strong>客户要的东西</strong>」变成「<strong>车间做出来的东西</strong>」。它是一条流水线：销售订单 → 工单 → 工序任务 → 派工 → 报工 → 入库 → 通知销售发货。</p>
<h4>完整流程时间线</h4>
<ol>
<li><strong>09:00 销售确认订单</strong>（订单从「草稿」变「已确认」）</li>
<li><strong>09:05 系统自动拆工单</strong>（一个订单按产品/数量/产线拆成 N 个工单）</li>
<li><strong>09:10 生产计划员排产</strong>（手工或 AI 排产，给每个工单定开始/结束时间）</li>
<li><strong>09:30 班组长派工</strong>（把工序任务派给具体员工，扫码或系统分配）</li>
<li><strong>10:00 员工开始干活</strong>（H5 接任务 → 开始 → 完工 → 报工）</li>
<li><strong>17:00 班组长审核报工</strong>（核对数量/质量/工时）</li>
<li><strong>18:00 报工数据 → 工资</strong>（自动算件资/时资，员工 H5 查）</li>
<li><strong>工单完工 → 自动入库</strong>（按 SKU/数量/批次入仓库）</li>
<li><strong>仓库发货</strong>（仓库管理员在「发货单」模块扫描出库）</li>
<li><strong>通知销售</strong>（订单状态自动变「已发货」）</li>
</ol>
<h4>状态机速查（工单）</h4>
<table>
<tr><th>状态</th><th>说明</th><th>下一步</th></tr>
<tr><td>open（待开工）</td><td>刚生成，工序任务未开始</td><td>派工</td></tr>
<tr><td>in_progress（生产中）</td><td>至少一个工序开始</td><td>继续监控报工</td></tr>
<tr><td>finished（已完工）</td><td>所有工序完工，质检通过</td><td>入库</td></tr>
<tr><td>cancelled（已取消）</td><td>订单取消导致工单取消</td><td>归档</td></tr>
</table>
<h4>与其他模块的联动</h4>
<ul>
<li>订单确认 → 工单自动生成</li>
<li>工序派工 → H5 端员工收到任务</li>
<li>员工报工 → 自动算工资 + 触发入库</li>
<li>工单完工 → 通知销售发货</li>
<li>物料不足 → 触发 MRP 采购建议</li>
</ul>`,
              },
              {
                id: 'ch18-2',
                title: '18.2 工单管理：CRUD + 打印 + 拆分 + 合并',
                content: `<h3>工单管理</h3>
<p><strong>使用者</strong>：生产计划员 / 车间主任</p>
<p><strong>操作路径</strong>：生产 → 工单管理</p>
<h4>列表关键字段</h4>
<table>
<tr><th>字段</th><th>说明</th><th>示例</th></tr>
<tr><td>工单号</td><td>自动生成，扫描二维码可查详情</td><td>WO-2026-001</td></tr>
<tr><td>产品 / SKU</td><td>要生产的具体产品</td><td>M8 螺丝 / 304 不锈钢</td></tr>
<tr><td>数量</td><td>工单总数量</td><td>5000</td></tr>
<tr><td>已生产</td><td>报工累计合格数</td><td>3200</td></tr>
<tr><td>不良数</td><td>累计不良数</td><td>15</td></tr>
<tr><td>状态</td><td>open / in_progress / finished / cancelled</td><td>in_progress</td></tr>
<tr><td>计划开始 / 结束</td><td>排产定的计划时间</td><td>2026-09-10 09:00 / 09-12 17:00</td></tr>
<tr><td>实际开始 / 结束</td><td>车间实际开工/完工时间</td><td>2026-09-10 09:23 / 待定</td></tr>
</table>
<h4>新建工单（手工）</h4>
<ol>
<li>生产 → 工单管理 → 「+ 新建工单」</li>
<li>选订单（必填，自动带产品/数量）</li>
<li>选产线 / 车间</li>
<li>计划开始/结束时间</li>
<li>指定工艺路线（自动带工序列表）</li>
<li>保存</li>
</ol>
<h4>拆分工单</h4>
<p>场景：一个订单 10000 件，要分两条产线同时做。</p>
<ol>
<li>工单详情 → 「拆分工单」</li>
<li>输入每条产线数量（必须等于总数）</li>
<li>系统生成 N 个子工单，自动分派</li>
</ol>
<h4>合并工单</h4>
<p>场景：3 个订单都是同一个产品，可以合并生产省换型时间。</p>
<ol>
<li>列表勾选多个工单 → 「合并」</li>
<li>确认产品/数量/产线</li>
<li>生成一个合并工单，原工单标记「已合并」</li>
</ol>
<blockquote>⚠️ 合并后原工单不能再单独操作，所有报工走合并工单。</blockquote>
<h4>打印</h4>
<ul>
<li>工单标签（A4 / A6 多种模板）</li>
<li>工序流转卡（每个工序一张）</li>
<li>批量打印（勾选多条）</li>
</ul>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>工单生成后发现数量错了</strong>：不能直接改数量，必须先取消工单，重做订单</blockquote>
<blockquote>⚠️ <strong>工单已经开工但还想拆</strong>：不允许，已开工不能拆/合并</blockquote>`,
              },
              {
                id: 'ch18-3',
                title: '18.3 派工：手动 / 自动 / 扫码三种方式',
                content: `<h3>派工（任务分配）</h3>
<p><strong>使用者</strong>：班组长 / 车间主任</p>
<p><strong>操作路径</strong>：生产 → 派工管理 / 工单详情 → 派工</p>
<h4>派工的三种方式</h4>
<h5>方式 1：手动派工（最常用）</h5>
<ol>
<li>工单详情 → 「工序任务」tab</li>
<li>看到所有工序任务（按顺序排列）</li>
<li>点某个工序任务 → 「派工」</li>
<li>选员工（支持多选同工序）</li>
<li>设计划开始时间</li>
<li>保存</li>
<li>员工 H5 端立即收到任务通知</li>
</ol>
<h5>方式 2：自动派工（按员工技能）</h5>
<p>适合工序标准化、技能明确的场景。</p>
<ol>
<li>工序任务 → 「自动派工」</li>
<li>系统按「员工技能」自动匹配</li>
<li>支持规则：<ul>
<li>技能等级 ≥ X 级</li>
<li>当日已分配任务 < 8 小时</li>
<li>优先分配给历史效率最高的</li>
</ul></li>
<li>预览分配结果 → 确认</li>
</ol>
<h5>方式 3：扫码派工（车间现场）</h5>
<p>适合车间主任在工位上现场分配。</p>
<ol>
<li>班组长打开 H5 → 「扫码派工」</li>
<li>扫工单上的二维码</li>
<li>选择工序</li>
<li>选择员工（员工二维码或姓名）</li>
<li>确认</li>
</ol>
<h4>派工状态</h4>
<table>
<tr><th>状态</th><th>说明</th></tr>
<tr><td>待派工</td><td>工单已生成但工序任务还没分配</td></tr>
<tr><td>已派工</td><td>已分配员工，员工还没开始</td></tr>
<tr><td>进行中</td><td>员工已扫码开始</td></tr>
<tr><td>已完工</td><td>员工报工完成</td></tr>
<tr><td>已超期</td><td>超过计划结束时间还没完工（红色警示）</td></tr>
</table>
<h4>转单/改派</h4>
<p>员工请假/离职/换岗时：</p>
<ol>
<li>派工列表 → 找到该任务 → 「改派」</li>
<li>选新员工</li>
<li>系统自动通知新员工，老员工任务变「已转出」</li>
</ol>
<h4>批量派工</h4>
<p>勾选多个工单所有未派工序 → 一键派给同一组员工（如：所有机加工序派给「甲班」）。</p>`,
              },
              {
                id: 'ch18-4',
                title: '18.4 报工：批量/逐件/语音三种模式',
                content: `<h3>报工（员工端）</h3>
<p><strong>使用者</strong>：操作工 / 班组长</p>
<p><strong>操作路径</strong>：H5 → 我的任务 → 报工</p>
<h4>三种报工模式</h4>
<h5>1. 批量报工（最常用）</h5>
<p>适合大批量生产，扫一次工单报一批数量。</p>
<ol>
<li>H5 → 我的任务 → 选任务</li>
<li>点「开始」→ 计时器开始</li>
<li>干完活 → 点「完工」</li>
<li>录入：<ul>
<li>合格数</li>
<li>不良数（可选，选缺陷码）</li>
<li>用时（自动算）</li>
</ul></li>
<li>上传现场照片（1-9 张）</li>
<li>提交</li>
</ol>
<h5>2. 逐件报工（按件扫码）</h5>
<p>适合单件计件、高单价、需逐件追溯。</p>
<ol>
<li>选任务 → 开始</li>
<li>每完成一件 → 扫成品码 → 录入</li>
<li>系统自动累加件数</li>
<li>完工时确认</li>
</ol>
<blockquote>📌 <strong>逐件报工核心价值</strong>：每件带唯一码，可正向追溯（这批件给了哪个客户）+ 反向追溯（这批件用的哪批料、谁做的、哪台设备）</blockquote>
<h5>3. 语音报工（车间嘈杂）</h5>
<ol>
<li>点麦克风图标</li>
<li>说：「合格 50，不良 2」</li>
<li>系统自动解析数字（用标准读法："一→幺""二→两""七→拐"）</li>
<li>人工核对 → 确认</li>
</ol>
<h4>报工状态流转</h4>
<p>员工提交 → 班组长审核 → 通过（数据入账）/ 驳回（员工重报）</p>
<h4>报工数据自动算</h4>
<ul>
<li>件资：合格数 × 单价</li>
<li>时资：用时 × 时薪</li>
<li>工时：自动算入工单实际工时</li>
<li>成本：自动算入订单成本</li>
</ul>
<h4>AI 审核（高级）</h4>
<p>系统自动检查报工的 6 个维度：</p>
<ol>
<li>数量合理性（相比历史均值）</li>
<li>工时合理性（相比标准工时）</li>
<li>不良率（突然升高会标红）</li>
<li>时间（连续报工间隔太短会标黄）</li>
<li>照片（模糊/无照片标黄）</li>
<li>位置（不在车间范围内标红）</li>
</ol>
<p>高风险的会标「需重点审核」，低风险自动通过。</p>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>报工数 > 工单总数</strong>：超量报工会被系统拒绝</blockquote>
<blockquote>⚠️ <strong>报工后想改数</strong>：自己不能改，需要班组长驳回后才能重报</blockquote>
<blockquote>⚠️ <strong>完工时间漏了</strong>：员工必须先点「开始」才能报工，否则无工时</blockquote>`,
              },
            ]
          },
          {
            id: 'ch19',
            title: '第十九章 采购/仓库/物料',
            icon: 'Box',
            children: [
              {
                id: 'ch19-1',
                title: '19.1 MRP 物料需求计划：自动算采购建议',
                content: `<h3>MRP 物料需求计划</h3>
<p><strong>使用者</strong>：生产计划员 / 采购 / 老板</p>
<p><strong>操作路径</strong>：生产 → MRP 运算 / 采购建议</p>
<h4>MRP 是什么？</h4>
<p>MRP = Material Requirements Planning，<strong>物料需求计划</strong>。系统自动算：<strong>"为了完成 X 订单，需要采购 Y 物料多少"</strong>。</p>
<h4>输入与输出</h4>
<table>
<tr><th>输入</th><th>输出</th></tr>
<tr><td>未来 N 天的生产计划</td><td>每种物料的需求数量</td></tr>
<tr><td>现有库存</td><td>需要采购的数量</td></tr>
<tr><td>在途采购（已订未到）</td><td>建议下单日期</td></tr>
<tr><td>安全库存</td><td>建议供应商</td></tr>
<tr><td>BOM（物料清单）</td><td>优先级排序</td></tr>
</table>
<h4>运算步骤</h4>
<ol>
<li>生产 → MRP 运算 → 「+ 新建 MRP」</li>
<li>选运算范围：<ul>
<li>时间窗口（未来 7/15/30 天）</li>
<li>产品范围（全部 / 指定产品 / 指定订单）</li>
</ul></li>
<li>点「开始运算」→ 系统跑 5-30 秒</li>
<li>出结果：<ul>
<li>需求清单（每种物料）</li>
<li>缺料清单（库存 - 需求）</li>
<li>采购建议（按供应商分组）</li>
</ul></li>
<li>人工确认 → 一键转采购订单</li>
</ol>
<h4>采购建议的关键字段</h4>
<table>
<tr><th>字段</th><th>说明</th></tr>
<tr><td>物料</td><td>需要采购的物料</td></tr>
<tr><td>需求数量</td><td>总需求量（来自所有工单）</td></tr>
<tr><td>现有库存</td><td>当前可用库存</td></tr>
<tr><td>在途数量</td><td>已下采购单未到货</td></tr>
<tr><td>建议采购量</td><td>需求量 - 库存 - 在途 + 安全库存</td></tr>
<tr><td>建议供应商</td><td>按价格/交期/历史评分推荐</td></tr>
<tr><td>建议下单日</td><td>反推：到货日 = 需求日 - 采购周期</td></tr>
</ol>
<h4>三种处理方式</h4>
<ol>
<li><strong>一键转采购单</strong>：选「按建议供应商分组」自动生成 N 张采购单</li>
<li><strong>手工调整</strong>：合并不同物料到一张单 / 换供应商 / 改数量</li>
<li><strong>暂不处理</strong>：留待后续批次</li>
</ol>
<h4>运算时机</h4>
<ul>
<li>每天凌晨 2 点自动跑一次（可关）</li>
<li>订单确认时触发增量运算</li>
<li>库存变化时（领料/入库）触发增量</li>
</ul>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>MRP 结果数量不对</strong>：检查 BOM 是否准确，物料库存是否最新</blockquote>
<blockquote>⚠️ <strong>建议供应商没出现</strong>：该物料没建供应商关系，去物料档案补充</blockquote>`,
              },
              {
                id: 'ch19-2',
                title: '19.2 采购订单：CRUD + 收货 + 对账 + 付款',
                content: `<h3>采购订单全流程</h3>
<p><strong>使用者</strong>：采购员 / 采购经理 / 仓库 / 财务</p>
<p><strong>操作路径</strong>：采购 → 采购订单 / 收货 / 对账单</p>
<h4>完整流程</h4>
<ol>
<li><strong>采购员建采购单</strong>（基于 MRP 建议或手工）</li>
<li><strong>采购经理审核</strong>（走工作流，按金额分支）</li>
<li><strong>发送给供应商</strong>（系统自动发邮件/微信/短信）</li>
<li><strong>供应商送货</strong>（附送货单）</li>
<li><strong>仓库收货</strong>（扫码核对 → 自动生成入库单）</li>
<li><strong>对账</strong>（按月生成对账单，跟供应商核对）</li>
<li><strong>财务付款</strong>（基于对账单 + 发票）</li>
</ol>
<h4>采购单状态</h4>
<table>
<tr><th>状态</th><th>说明</th></tr>
<tr><td>draft（草稿）</td><td>采购员编辑中</td></tr>
<tr><td>pending（待审）</td><td>提交了，等领导审批</td></tr>
<tr><td>approved（已批准）</td><td>领导批了，可发给供应商</td></tr>
<tr><td>sent（已发送）</td><td>系统发了邮件/微信给供应商</td></tr>
<tr><td>partial（部分到货）</td><td>收了一部分，还有欠货</td></tr>
<tr><td>received（全部到货）</td><td>全部收完</td></tr>
<tr><td>cancelled（已取消）</td><td>撤销采购</td></tr>
</table>
<h4>收货（入库）</h4>
<ol>
<li>仓库管理员 → 采购 → 「收货」</li>
<li>选采购单（可一次收多张）</li>
<li>扫码核对物料（系统自动匹配 PO 行）</li>
<li>录入：实收数量、批次号（如需）、库位</li>
<li>点「确认入库」</li>
<li>自动生成「入库单」+ 库存增加</li>
</ol>
<h4>部分收货</h4>
<blockquote>💡 供应商分批送货，常见。系统自动计算"欠货数量" = 订单数 - 累计已收</blockquote>
<h4>对账流程</h4>
<ol>
<li>月底 → 财务 → 采购对账 → 「+ 新建对账单」</li>
<li>选供应商 + 月份</li>
<li>系统自动汇总：<ul>
<li>该月所有已收货的采购单</li>
<li>总金额（不含税 / 含税）</li>
<li>已付款金额</li>
<li>未付金额</li>
</ul></li>
<li>导出 Excel / PDF → 发给供应商核对</li>
<li>供应商签字确认 → 系统标记「已对账」</li>
</ol>
<h4>付款</h4>
<ol>
<li>财务 → 付款单 → 「+ 新建」</li>
<li>选对账单</li>
<li>录入：付款金额、付款方式（银行/现金/承兑）、付款日期</li>
<li>上传付款凭证（银行回单）</li>
<li>提交 → 财务总监审批</li>
<li>审批通过 → 自动记入「财务流水」</li>
</ol>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>收货时发现数量不对</strong>：可以「部分收货」+「不良品退回」</blockquote>
<blockquote>⚠️ <strong>对账单跟供应商对不上</strong>：可能对方有退货没录入，检查退货单</blockquote>`,
              },
              {
                id: 'ch19-3',
                title: '19.3 仓库管理：入库/领料/退料/库存',
                content: `<h3>仓库管理</h3>
<p><strong>使用者</strong>：仓库管理员 / 生产 / 财务</p>
<p><strong>操作路径</strong>：仓库 → 入库/领料/退料/库存</p>
<h4>四个核心单据</h4>
<table>
<tr><th>单据</th><th>何时用</th><th>库存变化</th></tr>
<tr><td>入库单（warehouse_entries）</td><td>采购收货 / 生产完工入库 / 退货入库</td><td>+</td></tr>
<tr><td>领料单（material_issues）</td><td>生产从仓库领物料</td><td>-</td></tr>
<tr><td>退料单（material_returns）</td><td>多余物料退回仓库</td><td>+</td></tr>
<tr><td>发货单（shipments）</td><td>产品发给客户</td><td>-</td></tr>
</table>
<h4>入库单类型</h4>
<table>
<tr><th>来源</th><th>自动/手工</th><th>说明</th></tr>
<tr><td>采购入库</td><td>自动（从采购单收货）</td><td>最常用</td></tr>
<tr><td>生产入库</td><td>自动（工单完工）</td><td>成品入成品库</td></tr>
<tr><td>退货入库</td><td>手工</td><td>客户退货</td></tr>
<tr><td>调拨入库</td><td>手工</td><td>从其他仓库调入</td></tr>
<tr><td>盘盈入库</td><td>手工</td><td>盘点时多出来的</td></tr>
</table>
<h4>领料流程（生产用）</h4>
<ol>
<li>生产 → 领料单 → 「+ 新建」</li>
<li>选工单（自动带需要物料清单）</li>
<li>系统按 BOM 自动算：<ul>
<li>需要多少</li>
<li>库存多少</li>
<li>建议领多少</li>
</ul></li>
<li>仓库管理员审核可领数量</li>
<li>发料 → 仓库扫码确认出库</li>
<li>生成领料单 → 物料从库存扣减</li>
</ol>
<h4>超领管理</h4>
<p>如果实际领用 > 应领数量 → 触发超领审批：</p>
<ol>
<li>员工填「超领原因」</li>
<li>班组长确认</li>
<li>车间主任审批（按超领比例分级）</li>
<li>审批通过才允许出库</li>
</ol>
<h4>退料</h4>
<p>生产完工后多余物料退回：</p>
<ol>
<li>生产 → 退料单 → 「+ 新建」</li>
<li>选原领料单（自动带物料）</li>
<li>录入：实际退回数、批次</li>
<li>仓库扫码验收</li>
<li>物料回到库存</li>
</ol>
<h4>库存查询</h4>
<p>仓库 → 库存 → 列表</p>
<table>
<tr><th>字段</th><th>说明</th></tr>
<tr><td>物料编号 / 名称</td><td>SKU / 产品</td></tr>
<tr><td>仓库</td><td>所在仓库</td></tr>
<tr><td>库位</td><td>具体货架/库位</td></tr>
<tr><td>在库数量</td><td>当前库存</td></tr>
<tr><td>可用数量</td><td>在库 - 已锁库</td></tr>
<tr><td>安全库存</td><td>低于此值会预警</td></tr>
<tr><td>最近入库/出库</td><td>最后一次操作</td></tr>
</table>
<h4>库存预警</h4>
<ul>
<li><strong>低于安全库存</strong>：标黄 + 推送给采购员</li>
<li><strong>低于 0</strong>：标红 + 锁住所有领料</li>
<li><strong>积压</strong>（>180 天没动）：标灰 + 推送财务</li>
</ul>
<h4>盘点</h4>
<ol>
<li>仓库 → 盘点 → 「+ 新建盘点」</li>
<li>选仓库 + 物料范围（可全盘或抽盘）</li>
<li>打印盘点表（物料+理论库存）</li>
<li>仓库人员现场数实物</li>
<li>录入实盘数</li>
<li>系统自动算：盘盈/盘亏</li>
<li>主管审批后调整库存</li>
</ol>`,
              },
            ]
          },
          {
            id: 'ch20',
            title: '第二十章 设备管理与预测性维护',
            icon: 'Setting',
            children: [
              {
                id: 'ch20-1',
                title: '20.1 设备档案：基础信息 / 参数 / 关联',
                content: `<h3>设备档案</h3>
<p><strong>使用者</strong>：设备管理员 / 车间主任</p>
<p><strong>操作路径</strong>：生产 → 设备管理 → 设备档案</p>
<h4>设备档案核心字段</h4>
<table>
<tr><th>字段</th><th>说明</th><th>示例</th></tr>
<tr><td>设备编号</td><td>唯一，扫码即显示</td><td>EQ-001</td></tr>
<tr><td>设备名称 / 类型</td><td>机加工中心 / 注塑机 / 冲床</td><td>CNC-VMC850</td></tr>
<tr><td>规格型号</td><td>厂家型号</td><td>VMC-850L</td></tr>
<tr><td>厂家</td><td>设备制造商</td><td>北京精雕</td></tr>
<tr><td>购入日期 / 价格</td><td>固定资产</td><td>2023-03-15 / 50 万</td></tr>
<tr><td>位置</td><td>车间 / 产线 / 工位</td><td>1 号车间 A3 工位</td></tr>
<tr><td>状态</td><td>正常 / 维保中 / 故障 / 停用</td><td>正常</td></tr>
<tr><td>责任人</td><td>日常管理</td><td>张三</td></tr>
<tr><td>二维码</td><td>贴设备上，扫码报修/查详情</td><td>系统自动生成</td></tr>
</table>
<h4>设备参数</h4>
<p>每种设备类型有不同的运行参数：</p>
<ul>
<li><strong>CNC 加工中心</strong>：主轴转速 / 进给速度 / 刀库容量 / 行程范围</li>
<li><strong>注塑机</strong>：锁模力 / 注射量 / 温区 / 模板尺寸</li>
<li><strong>冲床</strong>：公称力 / 行程次数 / 滑块行程</li>
<li><strong>激光切割机</strong>：激光功率 / 切割厚度 / 工作台尺寸</li>
</ul>
<h4>设备关联</h4>
<ul>
<li>关联工艺路线：哪些工序用这台设备</li>
<li>关联模具：哪些模具在这台设备上用</li>
<li>关联备件库：备件库存预警</li>
<li>关联维保计划：定期维保规则</li>
</ul>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>设备状态没及时更新</strong>：报修后状态没改成"故障"，其他人继续派工</blockquote>
<blockquote>⚠️ <strong>设备位置变了没改</strong>：调岗后位置没更新，找不到设备</blockquote>`,
              },
              {
                id: 'ch20-2',
                title: '20.2 设备健康预测：AI 提前预警故障',
                content: `<h3>设备健康预测（AI）</h3>
<p><strong>使用者</strong>：设备管理员 / 车间主任</p>
<p><strong>操作路径</strong>：生产 → 设备管理 → 设备健康</p>
<h4>AI 预测什么？</h4>
<p>系统基于设备运行数据（振动/温度/电流/产能）预测：</p>
<ol>
<li><strong>健康度评分（0-100）</strong>：类似客户健康度，分数越低越危险</li>
<li><strong>剩余寿命</strong>：预计还能正常运行多久</li>
<li><strong>故障预警</strong>：可能发生什么故障（如轴承磨损、电机过热）</li>
<li><strong>最佳维保时间</strong>：什么时候做维保性价比最高</li>
</ol>
<h4>健康度等级</h4>
<table>
<tr><th>分数</th><th>等级</th><th>含义</th><th>建议动作</th></tr>
<tr><td>80-100</td><td>🟢 A 健康</td><td>运行良好</td><td>正常巡检</td></tr>
<tr><td>60-79</td><td>🟡 B 良好</td><td>轻微异常</td><td>关注趋势</td></tr>
<tr><td>40-59</td><td>🟠 C 一般</td><td>需要关注</td><td>计划维保</td></tr>
<tr><td>20-39</td><td>🔴 D 风险</td><td>高风险</td><td>立即维保</td></tr>
<tr><td>0-19</td><td>⚫ E 危险</td><td>即将故障</td><td>停机检查</td></tr>
</table>
<h4>AI 怎么算的？</h4>
<p>系统采集设备运行数据，用机器学习模型分析：</p>
<ul>
<li><strong>振动传感器</strong>：频谱分析 → 判断轴承/齿轮磨损</li>
<li><strong>温度传感器</strong>：趋势分析 → 判断电机/液压异常</li>
<li><strong>电流传感器</strong>：波动分析 → 判断负载/卡阻</li>
<li><strong>运行参数</strong>：转速/压力/产能 → 综合判断</li>
</ul>
<h4>预测结果在哪看？</h4>
<ol>
<li>设备健康看板（PC 端）</li>
<li>移动端 H5 推送</li>
<li>智能中心 → 主动推荐</li>
</ol>
<h4>接到预警怎么办？</h4>
<ol>
<li>查设备详情（AI 给出可能原因）</li>
<li>派维修工检查</li>
<li>登记维保记录（见 20.3）</li>
<li>维保完成 → 系统重新评分</li>
</ol>
<h4>模型持续学习</h4>
<p>每次故障记录都会喂给模型，让预测越来越准。</p>
<blockquote>💡 模型至少需要 <strong>3 个月历史数据</strong>才能开始准确预测，新设备先人工巡检</blockquote>`,
              },
              {
                id: 'ch20-3',
                title: '20.3 维保：计划/点检/维修/SPC',
                content: `<h3>设备维保管理</h3>
<p><strong>使用者</strong>：设备管理员 / 维修工 / 班组长</p>
<p><strong>操作路径</strong>：生产 → 设备管理 → 维保</p>
<h4>四种维保类型</h4>
<table>
<tr><th>类型</th><th>频率</th><th>谁做</th><th>记录</th></tr>
<tr><td>日常点检</td><td>每班/每天</td><td>操作工</td><td>点检表</td></tr>
<tr><td>定期保养</td><td>按计划（日/周/月/季/年）</td><td>维修工</td><td>保养单</td></tr>
<tr><td>故障维修</td><td>非计划</td><td>维修工</td><td>维修单</td></tr>
<tr><td>寿命校正</td><td>更换关键件后</td><td>维修工</td><td>校正记录</td></tr>
</table>
<h4>日常点检（5-10 分钟）</h4>
<ol>
<li>班前/班后各 1 次</li>
<li>检查项：<ul>
<li>外观（漏油/异响/异响）</li>
<li>润滑（油位/油质）</li>
<li>紧固（螺丝/防护罩）</li>
<li>清洁（碎屑/灰尘）</li>
</ul></li>
<li>H5 端录入点检表（点选/拍照）</li>
<li>异常项自动标红 + 推送设备员</li>
</ol>
<h4>定期保养（按计划）</h4>
<ol>
<li>系统自动生成保养计划（基于设备档案）</li>
<li>提前 3 天推送给维修工</li>
<li>维修工按 SOP 执行</li>
<li>录入：<ul>
<li>保养内容（每项打勾）</li>
<li>更换备件（自动扣库存）</li>
<li>耗时 / 费用</li>
<li>上传现场照片</li>
</ul></li>
<li>设备员审核 → 完成</li>
</ol>
<h4>故障维修流程</h4>
<ol>
<li>员工发现故障 → H5 「扫码报修」</li>
<li>拍照片 + 描述故障</li>
<li>系统推送给设备员 + 班组长</li>
<li>设备员评估：<ul>
<li>紧急（停线）→ 立即派维修</li>
<li>一般 → 加入当日维修计划</li>
</ul></li>
<li>维修工到场 → 诊断 → 维修</li>
<li>登记：<ul>
<li>故障原因（选故障码）</li>
<li>维修方法</li>
<li>更换备件</li>
<li>停机时长</li>
</ul></li>
<li>测试运行 → 关闭维修单</li>
</ol>
<h4>SPC（统计过程控制）</h4>
<p>对关键设备的运行参数做统计监控：</p>
<ul>
<li>X-bar R 控制图（监控均值和变异）</li>
<li>异常点自动告警</li>
<li>看趋势预测设备劣化</li>
</ul>
<h4>OEE 综合效率</h4>
<p>设备综合效率 = 可用率 × 性能率 × 合格率</p>
<ul>
<li><strong>可用率</strong> = 实际运行时间 / 计划运行时间</li>
<li><strong>性能率</strong> = 实际产能 / 理论产能</li>
<li><strong>合格率</strong> = 合格数 / 总数</li>
</ul>
<p>OEE < 60% 设备需要重点改进。</p>`,
              },
            ]
          },
          {
            id: 'ch21',
            title: '第二十一章 质量管理与 SPC',
            icon: 'List',
            children: [
              {
                id: 'ch21-1',
                title: '21.1 质检模板 / 缺陷代码 / 检测记录',
                content: `<h3>质量管理基础</h3>
<p><strong>使用者</strong>：质检员 / 车间主任 / 客户</p>
<p><strong>操作路径</strong>：生产 → 质量管理</p>
<h4>三个基础数据</h4>
<h5>1. 质检模板</h5>
<p>定义"检什么"和"怎么检"。</p>
<table>
<tr><th>字段</th><th>说明</th></tr>
<tr><td>模板名</td><td>如「机加工首件检验」「外观全检」</td></tr>
<tr><td>适用产品</td><td>通用 / 某产品 / 某 SKU</td></tr>
<tr><td>检验项</td><td>多项（每项：名称/标准/单位/上限/下限）</td></tr>
<tr><td>抽样规则</td><td>全检 / 抽检比例 / AQL</td></tr>
</table>
<p>示例：机加工首件检验模板</p>
<ul>
<li>外径：标准 10.00 ± 0.05 mm</li>
<li>长度：标准 50.00 ± 0.10 mm</li>
<li>表面粗糙度：Ra ≤ 1.6</li>
<li>外观：无毛刺/无划伤</li>
</ul>
<h5>2. 缺陷代码</h5>
<p>定义"问题叫什么"。</p>
<table>
<tr><th>字段</th><th>说明</th></tr>
<tr><td>代码</td><td>如 D001</td></tr>
<tr><td>名称</td><td>如 尺寸超差</td></tr>
<tr><td>分类</td><td>外观 / 尺寸 / 性能 / 功能 / 装配</td></tr>
<tr><td>严重度</td><td>轻微 / 一般 / 严重 / 致命</td></tr>
</table>
<h5>3. 检测记录</h5>
<p>实际检验的记录。</p>
<h4>三种质检场景</h4>
<h5>1. 首件检验（开班必检）</h5>
<ol>
<li>员工 H5 加工第一个产品</li>
<li>点「首件报检」</li>
<li>选模板 + 录入检测数据</li>
<li>上传首件照片</li>
<li>提交 → 班组长审核</li>
<li>审核通过 → 继续生产；不通过 → 停机调机</li>
</ol>
<h5>2. 过程巡检（按规则）</h5>
<ol>
<li>按抽样规则自动提醒</li>
<li>质检员到现场</li>
<li>扫码工单 → 录入数据</li>
<li>超差项自动标红 + 推班组长</li>
</ol>
<h5>3. 完工全检（出厂前）</h5>
<ol>
<li>工单完工 → 触发全检</li>
<li>全检合格 → 入库</li>
<li>不合格 → 入不良品库 + 推车间主任</li>
</ol>
<h4>不良品处理</h4>
<ol>
<li>不良品扫码入「不良品库」</li>
<li>选处理方式：<ul>
<li>返工（重新加工）</li>
<li>报废</li>
<li>降级（让步接收）</li>
<li>退货给客户</li>
</ul></li>
<li>走相应流程</li>
</ol>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>检测数据没录就继续生产</strong>：导致不良流出，没人能追溯</blockquote>
<blockquote>⚠️ <strong>缺陷代码用得不规范</strong>：分析数据会失真，统一培训质检员</blockquote>`,
              },
              {
                id: 'ch21-2',
                title: '21.2 SPC 统计过程控制：Cpk/Ppk/控制图',
                content: `<h3>SPC 统计过程控制</h3>
<p><strong>使用者</strong>：质检主管 / 工艺工程师</p>
<p><strong>操作路径</strong>：生产 → SPC 统计</p>
<h4>SPC 是什么？</h4>
<p>用<strong>统计方法</strong>监控生产过程，<strong>提前发现</strong>过程异常，<strong>避免</strong>批量不良。</p>
<h4>两个核心指标</h4>
<h5>Cpk（过程能力指数）</h5>
<p>衡量"这个工序能不能稳定做出合格品"。</p>
<table>
<tr><th>Cpk</th><th>等级</th><th>含义</th></tr>
<tr><td>≥ 1.67</td><td>★★★★★</td><td>能力过剩（可放宽检验）</td></tr>
<tr><td>1.33-1.67</td><td>★★★★</td><td>能力充足（推荐目标）</td></tr>
<tr><td>1.00-1.33</td><td>★★★</td><td>能力勉强（需关注）</td></tr>
<tr><td>0.67-1.00</td><td>★★</td><td>能力不足（需改进）</td></tr>
<tr><td>< 0.67</td><td>★</td><td>能力严重不足（需大改）</td></tr>
</table>
<h5>Ppk（初始过程能力）</h5>
<p>小批量试产时的能力指数。Ppk ≥ Cpk 时过程稳定。</p>
<h4>三种控制图</h4>
<h5>1. X-bar R 图（均值-极差）</h5>
<p>适合：<strong>批量连续生产</strong>，如机加工、注塑。</p>
<ul>
<li>中心线（CL）= 平均值</li>
<li>上下控制限（UCL/LCL）= ±3σ</li>
<li>采样：每班抽 5 个，连续 25 组</li>
</ul>
<h5>2. X-MR 图（单值-移动极差）</h5>
<p>适合：<strong>小批量</strong>或<strong>单件生产</strong>。</p>
<h5>3. P 图（不良率）</h5>
<p>适合：<strong>大批量</strong>，看不良率趋势。</p>
<h4>异常判读规则（Western Electric Rules）</h4>
<p>出现以下情况之一判为异常：</p>
<ol>
<li>1 个点超出 ±3σ</li>
<li>连续 9 个点在中心线同一侧</li>
<li>连续 6 个点递增或递减</li>
<li>连续 2 个点超出 ±2σ（同侧）</li>
<li>连续 4 个点超出 ±1σ（同侧）</li>
</ol>
<h4>SPC 异常处理流程</h4>
<ol>
<li>SPC 系统自动告警（红色）</li>
<li>推送给工艺工程师 + 班组长</li>
<li>4M 分析（人/机/料/法）：<ul>
<li>人：操作工换了？</li>
<li>机：设备异常？刀具磨损？</li>
<li>料：物料批次变了？</li>
<li>法：工艺参数变了？</li>
</ul></li>
<li>找到根因 → 调整 → 重新监控</li>
</ol>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>误删异常点</strong>：异常点必须保留作为分析依据，不能删除</blockquote>
<blockquote>⚠️ <strong>控制图全红但 Cpk 还 1.5</strong>：控制图反映"现在"，Cpk 反映"过去"，要分别看</blockquote>`,
              },
              {
                id: 'ch21-3',
                title: '21.3 质量追溯：从客户反查到原料',
                content: `<h3>质量追溯</h3>
<p><strong>使用者</strong>：质检员 / 销售 / 客户</p>
<p><strong>操作路径</strong>：生产 → 质量追溯</p>
<h4>正向追溯：原料 → 成品 → 客户</h4>
<p>从原料出发，查用这批料做的所有产品/客户。</p>
<h4>反向追溯：客户 → 成品 → 工序 → 原料</h4>
<p>客户反馈质量问题时，3 步查到根因。</p>
<h4>实战：客户投诉 "产品 X 表面有划伤"</h4>
<ol>
<li>质量追溯 → 反向追溯</li>
<li>输入：产品码 / 批次号 / 客户名</li>
<li>系统展示完整链路：<ul>
<li>这批产品是哪天生产的（工单）</li>
<li>哪个工序做的（哪个员工/设备）</li>
<li>用的什么原料（批次）</li>
<li>质检结果（合格还是让步接收）</li>
<li>出厂日期 / 发货单</li>
</ul></li>
<li>定位根因：是某个工序员工操作不当？原料本身有划伤？</li>
</ol>
<h4>追溯的核心：唯一码</h4>
<p>每件/每批/每工序都要有唯一标识：</p>
<ul>
<li>原料批次号（供应商给）</li>
<li>工序流转卡（贴在工位）</li>
<li>成品码（每件或每箱）</li>
</ul>
<p>没有码 = 断链 = 追不到。</p>
<h4>追溯报告</h4>
<p>系统自动生成 PDF 追溯报告，含：</p>
<ul>
<li>产品照片</li>
<li>工序时间线</li>
<li>员工 / 设备 / 原料详情</li>
<li>质检数据</li>
</ul>
<p>可直接发给客户作为质量证明。</p>`,
              },
            ]
          },
          {
            id: 'ch22',
            title: '第二十二章 财务管理（对账/成本/毛利/总账）',
            icon: 'Money',
            children: [
              {
                id: 'ch22-1',
                title: '22.1 客户对账单：按月汇总应收应付',
                content: `<h3>客户对账单</h3>
<p><strong>使用者</strong>：财务 / 销售</p>
<p><strong>操作路径</strong>：财务 → 客户对账</p>
<h4>对账单是什么？</h4>
<p>月底 / 季末给客户发的账目汇总：</p>
<ul>
<li>这个月买了多少（订单/发货/金额）</li>
<li>已经付了多少（收款流水）</li>
<li>还欠多少（应收余额）</li>
</ul>
<h4>生成对账单</h4>
<ol>
<li>财务 → 客户对账 → 「+ 新建对账单」</li>
<li>选客户 + 月份</li>
<li>系统自动汇总：<ul>
<li>期内所有已发货订单（含税/不含税）</li>
<li>期内所有收款（红冲/调整）</li>
<li>期初余额 + 期末余额</li>
</ul></li>
<li>确认 → 提交审核</li>
<li>财务经理审批</li>
<li>生成 PDF（含电子签章）</li>
</ol>
<h4>对账单状态</h4>
<table>
<tr><th>状态</th><th>说明</th></tr>
<tr><td>草稿</td><td>财务编辑中</td></tr>
<tr><td>已审核</td><td>内部审完，可发客户</td></tr>
<tr><td>已发送</td><td>通过邮件/微信发给客户</td></tr>
<tr><td>客户确认</td><td>客户在线/邮件确认</td></tr>
<tr><td>异议</td><td>客户提出异议，重新核对</td></tr>
</table>
<h4>客户在线确认</h4>
<ol>
<li>对账单推送到客户 H5 / 小程序</li>
<li>客户查看明细（订单/收款/余额）</li>
<li>客户点「确认」或「异议」+ 填说明</li>
<li>系统记录确认时间，作为对账证据</li>
</ol>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>对账单金额和客户认知不一致</strong>：客户说没收到货但系统显示已发，检查发货单物流签收</blockquote>
<blockquote>⚠️ <strong>对账单漏了部分订单</strong>：可能是草稿订单没确认，确认后才计入对账</blockquote>`,
              },
              {
                id: 'ch22-2',
                title: '22.2 收支流水 / 应收应付汇总',
                content: `<h3>财务流水</h3>
<p><strong>使用者</strong>：财务 / 老板</p>
<p><strong>操作路径</strong>：财务 → 收支流水</p>
<h4>流水分类</h4>
<table>
<tr><th>方向</th><th>类别</th><th>来源</th></tr>
<tr><td>收入（in）</td><td>销售收款 / 预收款 / 其他收入</td><td>客户付款</td></tr>
<tr><td>支出（out）</td><td>采购付款 / 费用报销 / 工资发放 / 其他支出</td><td>对账单付款 / 报销 / 工资</td></tr>
</table>
<h4>录入流水</h4>
<ol>
<li>财务 → 收支流水 → 「+ 新建」</li>
<li>选方向（收/付）</li>
<li>选对方类型（客户/供应商/员工/其他）</li>
<li>选对方具体（关联客户档案/供应商档案）</li>
<li>录入：金额、日期、付款方式（银行/现金/承兑/微信/支付宝）、账户</li>
<li>上传凭证（银行回单 / 收据）</li>
<li>关联单据：<ul>
<li>收款 → 关联对账单</li>
<li>付款 → 关联采购对账单 / 报销单</li>
</ul></li>
<li>保存</li>
</ol>
<h4>自动产生的流水</h4>
<p>大部分流水<strong>不是手工录的</strong>，是系统自动产生的：</p>
<ul>
<li>订单确认 → 自动产生「应收」流水</li>
<li>客户付款 → 自动产生「实收」流水，冲抵应收</li>
<li>采购单审核 → 自动产生「应付」</li>
<li>对账单付款 → 自动产生「实付」，冲抵应付</li>
<li>工资发放 → 自动产生「工资支出」</li>
</ul>
<h4>应收应付汇总</h4>
<table>
<tr><th>表</th><th>字段</th><th>说明</th></tr>
<tr><td>客户应收汇总</td><td>客户、累计应收、累计实收、当前余额</td><td>每个客户欠多少</td></tr>
<tr><td>供应商应付汇总</td><td>供应商、累计应付、累计实付、当前余额</td><td>每个供应商欠多少</td></tr>
</table>
<h4>账龄分析</h4>
<p>把应收/应付按账龄分组：</p>
<ul>
<li>0-30 天：正常</li>
<li>31-60 天：关注</li>
<li>61-90 天：高风险</li>
<li>> 90 天：呆账风险</li>
</ul>
<p>老板和财务重点看 > 60 天的余额。</p>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>客户付款没冲抵对账单</strong>：造成客户余额不准，手工调整</blockquote>
<blockquote>⚠️ <strong>个人卡付款没法对账</strong>：建议公对公转账，保留凭证</blockquote>`,
              },
              {
                id: 'ch22-3',
                title: '22.3 成本毛利分析：算清楚一笔订单赚多少',
                content: `<h3>成本毛利分析</h3>
<p><strong>使用者</strong>：老板 / 财务</p>
<p><strong>操作路径</strong>：财务 → 成本毛利 / 老板看板</p>
<h4>订单的成本构成</h4>
<table>
<tr><th>成本项</th><th>来源</th><th>说明</th></tr>
<tr><td>物料成本</td><td>领料单 × 单价</td><td>直接材料</td></tr>
<tr><td>人工成本</td><td>报工工时 × 时薪</td><td>直接人工</td></tr>
<tr><td>制造费用</td><td>设备折旧 / 厂房租金 / 水电</td><td>按工时分摊</td></tr>
<tr><td>外协费用</td><td>外协加工单</td><td>委外加工</td></tr>
<tr><td>采购成本</td><td>物料采购</td><td>如果含税要换算成不含税</td></tr>
</table>
<h4>订单毛利 = 订单金额 - 订单总成本</h4>
<h4>毛利率 = 毛利 / 订单金额 × 100%</h4>
<h4>看哪些订单赚钱</h4>
<ol>
<li>财务 → 成本毛利</li>
<li>列表展示每个订单：<ul>
<li>订单金额</li>
<li>物料成本</li>
<li>人工成本</li>
<li>制造费用</li>
<li>总成本</li>
<li>毛利</li>
<li>毛利率</li>
</ul></li>
<li>可按客户/产品/月份过滤</li>
</ol>
<h4>哪些订单亏钱？</h4>
<p>常见亏钱原因：</p>
<ol>
<li><strong>报价太低</strong>：销售没考虑成本就报</li>
<li><strong>工时超标</strong>：效率低/换型多/不良多</li>
<li><strong>物料浪费</strong>：超领 / 不良</li>
<li><strong>客户压价</strong>：接单时图省事</li>
</ol>
<h4>提升毛利的 4 个杠杆</h4>
<ol>
<li><strong>提价</strong>：提价 5% 可显著拉高毛利</li>
<li><strong>降物料成本</strong>：找替代供应商、批量议价</li>
<li><strong>提效率</strong>：减少工时浪费</li>
<li><strong>降不良</strong>：不良品直接吃掉毛利</li>
</ol>
<h4>老板看板关键数据</h4>
<ul>
<li>本月销售额（订单 amount 求和）</li>
<li>本月成本（订单 cost_amount 求和）</li>
<li>本月毛利 = 销售额 - 成本</li>
<li>本月毛利率</li>
<li>环比 / 同比（和上月/去年同月比）</li>
</ul>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>订单没算完就统计毛利</strong>：订单进行中毛利不准，等所有工序完工再算</blockquote>
<blockquote>⚠️ <strong>制造费用没分摊</strong>：成本算得偏低，毛利虚高</blockquote>`,
              },
              {
                id: 'ch22-4',
                title: '22.4 财务总账 / 凭证 / 试算平衡',
                content: `<h3>财务总账</h3>
<p><strong>使用者</strong>：财务 / 会计</p>
<p><strong>操作路径</strong>：财务 → 总账 / 凭证</p>
<h4>核心概念</h4>
<table>
<tr><th>概念</th><th>说明</th></tr>
<tr><td>会计科目</td><td>资产的分类（现金/银行/应收/应付/收入/成本等）</td></tr>
<tr><td>凭证</td><td>每笔业务的会计记录（借方/贷方）</td></tr>
<tr><td>总账</td><td>按科目汇总的账本</td></tr>
<tr><td>明细账</td><td>按科目+对方+时间的明细</td></tr>
<tr><td>试算平衡</td><td>借方总和 = 贷方总和</td></tr>
</table>
<h4>会计科目（系统预置）</h4>
<table>
<tr><th>类别</th><th>常见科目</th></tr>
<tr><td>资产类</td><td>现金、银行存款、应收账款、存货、固定资产</td></tr>
<tr><td>负债类</td><td>应付账款、短期借款、长期借款</td></tr>
<tr><td>权益类</td><td>实收资本、留存收益</td></tr>
<tr><td>收入类</td><td>主营业务收入、其他业务收入</td></tr>
<tr><td>成本类</td><td>主营业务成本、营业外支出</td></tr>
</table>
<h4>自动凭证</h4>
<p>系统自动生成凭证，<strong>不需要财务手工录</strong>：</p>
<table>
<tr><th>业务事件</th><th>凭证</th></tr>
<tr><td>销售发货</td><td>借：应收账款  贷：主营业务收入 / 销项税</td></tr>
<tr><td>客户收款</td><td>借：银行存款  贷：应收账款</td></tr>
<tr><td>采购收货</td><td>借：存货 / 进项税  贷：应付账款</td></tr>
<tr><td>付款给供应商</td><td>借：应付账款  贷：银行存款</td></tr>
<tr><td>工资发放</td><td>借：应付工资  贷：银行存款</td></tr>
</table>
<h4>手工凭证</h4>
<p>系统无法自动产生的（比如费用报销、调整）：</p>
<ol>
<li>财务 → 凭证 → 「+ 新建」</li>
<li>选日期、摘要</li>
<li>录借贷分录（必须借贷平衡）</li>
<li>选科目（带搜索）</li>
<li>录金额、对方</li>
<li>上传附件（发票/单据）</li>
<li>提交</li>
</ol>
<h4>试算平衡检查</h4>
<ol>
<li>财务 → 总账 → 「试算平衡表」</li>
<li>选期间（如 2026-09）</li>
<li>系统展示：<ul>
<li>期初余额（借/贷）</li>
<li>本期发生额（借/贷）</li>
<li>期末余额（借/贷）</li>
</ul></li>
<li>如果借贷不平衡 → 必有错账</li>
</ol>
<h4>资产负债表</h4>
<p>展示企业某一天的财务状况：</p>
<ul>
<li>资产 = 负债 + 所有者权益</li>
<li>系统按"资产-负债=权益"自动生成</li>
</ul>
<h4>常见错误</h4>
<blockquote>⚠️ <strong>借贷不平</strong>：找最近的凭证检查金额</blockquote>
<blockquote>⚠️ <strong>科目用错</strong>：比如把"管理费用"录成"制造费用"，影响成本计算</blockquote>`,
              },
            ]
          }
        ]
      },
    ]
  },
  {
    id: 'part2',
    title: '第二篇：H5员工端使用指南',
    icon: 'User',
    children: [
      {
        id: 'emp-ch1',
        title: '第一章 登录与首页',
        icon: 'Key',
        children: [
          {
            id: 'emp-1-1',
            title: '1.1 登录与认证',
            content: `<h3>登录与身份认证</h3>
<p><strong>适用用户</strong>：工厂员工 / 操作工人</p>
<p><strong>访问方式</strong>：手机浏览器打开 H5 链接，或扫描工厂发放的二维码</p>
<h4>首次登录</h4>
<ol>
<li>在手机浏览器输入应用 URL，或扫描二维码</li>
<li>输入用户名（通常是工号）和密码</li>
<li>首次登录需修改初始密码</li>
<li>成功后自动跳转到首页</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>账户由 HR 分配，联系人力资源部获取</li>
<li>忘记密码：点击「忘记密码」→ 输入手机号 → 验证码 → 重置</li>
<li>15分钟无操作自动退出</li>
<li>工作完毕记得退出登录</li>
</ul>`
          },
          {
            id: 'emp-1-2',
            title: '1.2 首页仪表盘',
            content: `<h3>首页仪表盘</h3>
<h4>页面布局</h4>
<ul>
<li><strong>账户信息栏</strong>：显示姓名、部门、日期</li>
<li><strong>今日概览卡片</strong>：<ul>
<li>待报工：还未报工的任务数</li>
<li>已报工：已提交报工数</li>
<li>待审核：班组长待初审的报工数</li>
<li>今日工资：基于已审核报工的实时估算</li>
</ul></li>
<li><strong>快速操作按钮</strong>：我的任务、扫码报工、打卡</li>
<li><strong>待办提醒</strong>：新任务、驳回通知等</li>
<li><strong>本周产量趋势图</strong></li>
</ul>`
          },
        ]
      },
      {
        id: 'emp-ch2',
        title: '第二章 任务与报工',
        icon: 'Edit',
        children: [
          {
            id: 'emp-2-1',
            title: '2.1 我的任务',
            content: `<h3>我的任务</h3>
<p><strong>路径</strong>：首页「我的任务」或底部导航「任务」</p>
<h4>任务列表</h4>
<ul>
<li>显示派给自己的所有任务</li>
<li>每项任务卡片显示：任务编码、产品信息、工序名称、派工数量、进度、状态</li>
<li><strong>任务状态</strong>：待开始 / 生产中 / 已完成 / 已驳回</li>
<li>可按工序、状态筛选，按产品名/订单号搜索</li>
</ul>
<h4>任务操作</h4>
<ul>
<li>点击任务 → 查看任务详情</li>
<li>点击「扫码报工」→ 进入报工流程</li>
</ul>`
          },
          {
            id: 'emp-2-2',
            title: '2.2 扫码报工',
            content: `<h3>扫码报工</h3>
<p><strong>路径</strong>：首页「扫码报工」或底部导航「报工」</p>
<h4>完整报工流程</h4>
<ol>
<li><strong>扫码识别</strong>：扫描任务二维码，系统自动识别任务</li>
<li><strong>输入数量</strong>：输入合格数和不良数（合格+不良 ≤ 派工数）</li>
<li><strong>上传证据</strong>：<ul>
<li>照片：1-5张，JPG/PNG，每张 ≤ 5MB</li>
<li>视频：最长30秒，MP4 格式，≤ 10MB</li>
</ul></li>
<li><strong>填写备注</strong>：如有异常或特殊情况</li>
<li><strong>确认提交</strong>：提交后立即显示预估工资</li>
</ol>
<h4>预估工资计算</h4>
<p><code>预估工资 = 合格数 × 工序工价</code></p>
<p>注意：这是预估值，最终工资需要审核通过后才确认。</p>
<h4>注意事项</h4>
<ul>
<li>数据要真实准确，虚报影响工资和信誉</li>
<li>照片要清晰展示产品细节</li>
<li>如有问题一定在备注中说明</li>
<li>提交后不可修改，被驳回可重新报工</li>
</ul>`
          },
        ]
      },
      {
        id: 'emp-ch3',
        title: '第三章 工资与考勤',
        icon: 'Money',
        children: [
          {
            id: 'emp-3-1',
            title: '3.1 我的工资',
            content: `<h3>我的工资</h3>
<p><strong>路径</strong>：底部导航「我的」→「工资」</p>
<h4>月工资汇总</h4>
<ul>
<li>选择月份查看</li>
<li><strong>计件工资</strong>：基于审核通过的报工合格数 × 工序工价</li>
<li><strong>补贴</strong>：全勤奖、岗位津贴等</li>
<li><strong>扣款</strong>：迟到扣款、罚款等</li>
<li><strong>实发金额</strong>：计件工资 + 补贴 - 扣款</li>
</ul>
<h4>工序报工明细</h4>
<p>显示每笔报工的工序名称、合格数、单价和金额，完全透明可查。</p>`
          },
          {
            id: 'emp-3-2',
            title: '3.2 电子工资条',
            content: `<h3>电子工资条</h3>
<p><strong>路径</strong>：我的 → 工资条</p>
<h4>功能特点</h4>
<ul>
<li>三种查看模式：简洁版、详细版、PDF 下载</li>
<li>显示完整的工资明细和各项金额</li>
<li><strong>电子签名</strong>：确认工资后可签名确认</li>
<li>有异议可选择「拒绝签名」并提交问题</li>
<li>支持 PDF 下载和打印</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>签名后视为确认工资，不可再修改</li>
<li>有异议先和班组长沟通，再联系财务</li>
<li>在下月发薪前完成签名</li>
</ul>`
          },
          {
            id: 'emp-3-3',
            title: '3.3 考勤打卡',
            content: `<h3>考勤打卡</h3>
<p><strong>路径</strong>：首页「打卡」或底部导航「我的」→「考勤打卡」</p>
<h4>操作步骤</h4>
<ol>
<li><strong>签到</strong>：上班时点击「签到」按钮，系统记录签到时间</li>
<li><strong>签退</strong>：下班时点击「签退」按钮，显示工作时长</li>
</ol>
<h4>打卡记录</h4>
<p>显示最近打卡记录：日期、签到时间、签退时间、工作时长、状态（准时/迟到）。</p>
<h4>注意事项</h4>
<ul>
<li>准时打卡，避免迟到扣款</li>
<li>忘记打卡可申请补卡（需班组长审批）</li>
<li>迟到15分钟起扣款，累计迟到影响全勤奖</li>
<li>考勤数据用于加班费计算和绩效考核</li>
</ul>`
          },
        ]
      },
      {
        id: 'emp-ch4',
        title: '第四章 员工FAQ',
        icon: 'QuestionFilled',
        children: [
          {
            id: 'emp-4-1',
            title: '4.1 常见问题',
            content: `<h3>常见问题</h3>
<h4>Q1：怎样快速报工？</h4>
<p>推荐使用<strong>扫码报工</strong>：打开手机端 → 首页「扫码报工」→ 扫描二维码 → 输入合格数/不良数 → 提交，整个流程不超过30秒。</p>
<h4>Q2：报工被驳回了，怎么办？</h4>
<ol>
<li>查看驳回原因通知</li>
<li>进入「我的任务」找到被驳回的任务</li>
<li>根据反馈重新报工（可修正数据和照片）</li>
</ol>
<p>常见驳回原因：照片不清晰、数量异常、没有备注、没上传视频。</p>
<h4>Q3：报工多久能到账工资？</h4>
<ul>
<li>报工提交 → 预估工资：立即（秒级）</li>
<li>预估 → 最终工资（审核通过）：1-3天</li>
<li>月工资最终确认：月底或次月初</li>
</ul>
<h4>Q4：预估工资和最终工资为什么不一样？</h4>
<ul>
<li>报工被驳回：返工或废品不计工资</li>
<li>还在审核中的报工未计入</li>
<li>最终工资可能加入补贴或扣款</li>
</ul>
<h4>Q5：如何避免报工被驳回？</h4>
<ul>
<li>数字准确：不虚报</li>
<li>拍好照片：至少3张，清晰展示产品</li>
<li>写好备注：有问题一定说明</li>
<li>及时报工：当天完成当天报</li>
<li>不确定时先问班组长</li>
</ul>
<h4>Q6：员工端和客户端有什么区别？</h4>
<table>
<tr><th>功能</th><th>员工端</th><th>客户端</th></tr>
<tr><td>查看任务</td><td>✅</td><td>❌</td></tr>
<tr><td>扫码报工</td><td>✅</td><td>❌</td></tr>
<tr><td>查看工资</td><td>✅</td><td>❌</td></tr>
<tr><td>客户下单</td><td>❌</td><td>✅</td></tr>
<tr><td>查看订单进度</td><td>❌</td><td>✅</td></tr>
<tr><td>对账单</td><td>❌</td><td>✅</td></tr>
</table>
<h4>Q7：怎么绑定飞书 / 钉钉 / 企微 收个人通知？</h4>
<ol>
<li>「我的」→「账号设置」→ 找到「飞书 / 钉钉 / 企微绑定」</li>
<li>点「去绑定」会跳到对应 IM 授权页（需安装对应 App）</li>
<li>授权后回跳 辰科MES，自动存 <code>open_id</code> / <code>dingtalk_userid</code> / <code>wecom_userid</code></li>
<li>绑定后派工、报工审核、工资条会推送到对应 IM</li>
</ol>
<p><strong>注意</strong>：未绑定也能用站内通知（铃铛），但 IM 推送需要绑定才能收个人消息。</p>
<h4>Q8：收不到派工/工资推送通知？</h4>
<ul>
<li>先确认已绑定 IM（见 Q7）</li>
<li>检查手机 IM App 通知权限是否被关闭</li>
<li>在「我的 → 通知设置」里检查是否被静默</li>
<li>静默时段（默认 22:00–07:00）内的消息会延迟到点发送</li>
</ul>`
          },
        ]
      },
    ]
  },
  {
    id: 'part3',
    title: '第三篇：H5客户端使用指南',
    icon: 'ShoppingCart',
    children: [
      {
        id: 'cust-ch1',
        title: '第一章 登录与首页',
        icon: 'Key',
        children: [
          {
            id: 'cust-1-1',
            title: '1.1 登录与认证',
            content: `<h3>登录与认证</h3>
<p><strong>适用用户</strong>：客户 / 会员用户</p>
<p><strong>访问方式</strong>：手机浏览器打开 H5 链接，或扫描企业提供的二维码</p>
<h4>登录步骤</h4>
<ol>
<li>打开应用，进入登录页</li>
<li>输入用户名（手机号或账号）和密码</li>
<li>点击「登录」，系统验证身份</li>
<li>首次登录可能需要完善用户资料</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>账户由企业分配，联系销售或客服获取</li>
<li>忘记密码：点击「忘记密码」→ 输入手机号 → 验证码 → 重置</li>
<li>15分钟未操作自动退出</li>
<li>一个客户账户对应一个公司</li>
</ul>`
          },
          {
            id: 'cust-1-2',
            title: '1.2 首页与导航',
            content: `<h3>首页与导航</h3>
<h4>首页布局</h4>
<ul>
<li><strong>账户信息栏</strong>：用户名、公司名、余额</li>
<li><strong>快速菜单</strong>：我要下单、订单列表、订单追踪、对账单、消息中心、个人设置</li>
<li><strong>最近订单</strong>：最近订单卡片列表</li>
</ul>
<h4>底部导航</h4>
<table>
<tr><th>菜单</th><th>功能</th></tr>
<tr><td>首页</td><td>仪表盘、快速菜单</td></tr>
<tr><td>下单</td><td>产品浏览与下单</td></tr>
<tr><td>订单</td><td>订单列表与详情</td></tr>
<tr><td>追踪</td><td>订单进度查询</td></tr>
<tr><td>我的</td><td>个人中心、设置</td></tr>
</table>`
          },
        ]
      },
      {
        id: 'cust-ch2',
        title: '第二章 下单与订单',
        icon: 'List',
        children: [
          {
            id: 'cust-2-1',
            title: '2.1 客户下单',
            content: `<h3>客户下单</h3>
<p><strong>路径</strong>：底部导航「下单」或首页「我要下单」</p>
<h4>完整下单流程</h4>
<p><strong>第一步：浏览产品</strong></p>
<ol>
<li>进入下单页面，显示产品列表</li>
<li>可按分类过滤或搜索产品</li>
<li>点击产品查看详情</li>
</ol>
<p><strong>第二步：选择型号与规格</strong></p>
<ol>
<li>点击要购买的产品，进入型号选择页</li>
<li>显示该产品的所有可用型号（颜色、材料、规格、库存状态）</li>
<li>选择需要的型号</li>
</ol>
<p><strong>第三步：输入订单信息</strong></p>
<ol>
<li>输入订单数量（≥ 1件）</li>
<li>选择交期（建议至少7天后）</li>
<li>填写特殊要求备注</li>
<li>点击「提交订单」→ 确认信息 → 订单提交成功</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>确认型号和数量无误后再提交</li>
<li>建议提前7天下单，紧急订单请电话咨询</li>
<li>草稿状态的订单可修改，已确认后不可修改</li>
</ul>`
          },
          {
            id: 'cust-2-2',
            title: '2.2 订单管理',
            content: `<h3>订单管理</h3>
<p><strong>路径</strong>：底部导航「订单」</p>
<h4>订单列表</h4>
<ul>
<li>显示所有历史订单（卡片形式）</li>
<li>按状态、时间筛选，搜索订单号</li>
<li>每张卡片显示：订单号、产品、数量、金额、状态、交期</li>
</ul>
<h4>订单详情</h4>
<ul>
<li>基本信息：订单号、创建时间、状态</li>
<li>产品信息：名称、型号、数量、单价</li>
<li>进度信息：当前工序、完成比例、预计完成时间</li>
<li>操作：查看进度、联系客服、下载文档</li>
</ul>
<h4>订单状态</h4>
<p>草稿 → 已确认 → 生产中 → 已完成 → 已发货 → 已取消</p>`
          },
          {
            id: 'cust-2-3',
            title: '2.3 订单进度追踪',
            content: `<h3>订单进度追踪</h3>
<p><strong>路径</strong>：底部导航「追踪」或订单详情「查看进度」</p>
<h4>进度查看</h4>
<ul>
<li><strong>时间线视图</strong>：显示各工序的完成状态（已完成/进行中/待开始）</li>
<li><strong>工序详情</strong>：派工人数、完成数量、预计完成时间</li>
<li><strong>自动刷新</strong>：每2分钟更新一次，也可手动刷新</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>如显示「延迟」，说明可能无法按时交期，建议联系客服</li>
<li>生产完成时会自动推送通知</li>
<li>可在订单列表直接查看进度概要</li>
</ul>`
          },
        ]
      },
      {
        id: 'cust-ch3',
        title: '第三章 对账与消息',
        icon: 'Document',
        children: [
          {
            id: 'cust-3-1',
            title: '3.1 对账单查看',
            content: `<h3>对账单查看</h3>
<p><strong>路径</strong>：底部导航「我的」→「对账单」</p>
<h4>操作步骤</h4>
<ol>
<li>按月选择对账单</li>
<li>查看对账明细：各订单号、产品、金额、状态</li>
<li>核对总金额、已付金额、待付金额</li>
<li>支持操作：下载 PDF、申请发票、确认对账、提出异议</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>定期查看对账单，及时确认</li>
<li>如有不符，点击「提出异议」，财务3-5个工作日回复</li>
<li>已确认的对账单不可再修改</li>
</ul>`
          },
          {
            id: 'cust-3-2',
            title: '3.2 消息通知',
            content: `<h3>消息通知</h3>
<p><strong>路径</strong>：底部导航「我的」→「消息中心」</p>
<h4>消息类型</h4>
<ul>
<li>订单确认通知</li>
<li>生产开始通知</li>
<li>工序完成通知</li>
<li>生产完成通知</li>
<li>已发货通知</li>
<li>对账单通知</li>
<li>系统通知</li>
</ul>
<h4>消息管理</h4>
<ul>
<li>消息列表按时间倒序显示</li>
<li>已读/未读标记</li>
<li>可删除单条或清空所有消息</li>
<li>可配置推送开关、推送类型和不打扰时段</li>
</ul>`
          },
        ]
      },
      {
        id: 'cust-ch4',
        title: '第四章 客户FAQ',
        icon: 'QuestionFilled',
        children: [
          {
            id: 'cust-4-1',
            title: '4.1 常见问题',
            content: `<h3>常见问题</h3>
<h4>Q1：提交订单后可以修改吗？</h4>
<p><strong>草稿状态</strong>：可以修改，进入订单详情点击「编辑」修改数量或交期。<br>
<strong>已确认状态</strong>：不能修改，需作废原订单重新下单，或联系客服。</p>
<h4>Q2：如何知道订单是否按时完成？</h4>
<p>三种方式：1. 消息推送通知 2. 「订单追踪」实时查看 3. 订单列表显示预计完成时间</p>
<h4>Q3：进度显示「延迟」是什么意思？</h4>
<p>表示可能无法按时完成，原因可能是物料延迟、产能不足、质检不通过。建议立即联系客服了解情况。</p>
<h4>Q4：对账单金额与我的账目不符怎么办？</h4>
<ol>
<li>仔细核对每个订单号和金额</li>
<li>检查是否有已取消订单被包含</li>
<li>如仍不符，点击「提出异议」说明情况</li>
<li>财务会在3-5个工作日回复</li>
</ol>
<h4>Q5：如何联系工厂客服？</h4>
<ul>
<li>订单详情页点击「联系客服」</li>
<li>消息中心点击「询问工厂」</li>
<li>个人中心查看客服电话和微信</li>
</ul>
<h4>Q6：支持哪些浏览器？</h4>
<p>iPhone：Safari 或 Chrome；Android：Chrome、Firefox。推荐使用最新版 Chrome 或 Safari。</p>`
          },
        ]
      },
    ]
  },
  {
    id: 'part4',
    title: '第四篇：微信小程序管理端使用指南',
    icon: 'Cellphone',
    children: [
      {
        id: 'wx-ch1',
        title: '第一章 小程序管理端简介',
        icon: 'Cellphone',
        children: [
          {
            id: 'wx-1-1',
            title: '1.1 什么是管理端小程序',
            content: `<h3>微信小程序管理端</h3>
<p>辰科MES 提供一个<strong>微信小程序版"轻量管理端"</strong>，面向厂长 / 班组长 / 财务 / 业务，适合<strong>出差、外勤、车间走动</strong>等不方便打开 PC 的场景。功能定位：<strong>PC 端的手机伴侣</strong>，不是替代。</p>
<h4>入口</h4>
<p>微信 → 搜索「辰科MES」小程序（或扫码「管理端」入口）→ 选择「<strong>管理端</strong>」模式登录。</p>
<h4>登录方式</h4>
<ul>
<li>手机号 + 验证码（默认）</li>
<li>账号密码（PC 创建账号后可用）</li>
</ul>
<h4>适用角色</h4>
<table>
<tr><th>角色</th><th>核心场景</th></tr>
<tr><td>老板 / 厂长</td><td>查实时看板、看工厂日报、审重要单据</td></tr>
<tr><td>班组长</td><td>现场审核报工、扫码分配、查本组任务</td></tr>
<tr><td>财务</td><td>查工资 / 对账、确认工资条</td></tr>
<tr><td>业务</td><td>客户管理、订单跟进、外勤报价</td></tr>
</table>
<h4>与 PC 管理端的区别</h4>
<ul>
<li>✅ 手机端能做的：审核、查询、扫码、轻度配置</li>
<li>❌ 手机端<strong>不能</strong>做的：批量导入、复杂报表导出、初始化配置、生产计划全流程编排</li>
<li>数据：与 PC 端实时同步（同一后端）</li>
</ul>`
          },
          {
            id: 'wx-1-2',
            title: '1.2 角色与权限',
            content: `<h3>角色与权限</h3>
<p>管理端小程序登录后，<strong>角色权限与 PC 端完全一致</strong>。例如：</p>
<ul>
<li>没有 <code>order.manage</code> 权限，看不到订单管理入口</li>
<li>只有 <code>report.audit</code> 权限，能进入审核页但不能改产品/工价</li>
</ul>
<p>权限按租户隔离，员工只能看到自己租户下的数据。</p>
<h4>切换角色（一人多租户时）</h4>
<p>「我的」→ 「切换租户 / 角色」→ 选目标租户。小程序会刷新权限与菜单。</p>`
          },
        ]
      },
      {
        id: 'wx-ch2',
        title: '第二章 首页与看板',
        icon: 'DataLine',
        children: [
          {
            id: 'wx-2-1',
            title: '2.1 首页（管理端仪表盘）',
            content: `<h3>首页</h3>
<p>登录后默认进入首页，展示：</p>
<ul>
<li>今日关键指标：产值、订单达成率、不良率</li>
<li>待办事项：待审报工、待确认工资、待处理预警</li>
<li>实时生产趋势：折线图展示当日各小时产量</li>
<li>快捷入口：根据角色推荐（审核 / 看板 / 工厂助手）</li>
</ul>`
          },
          {
            id: 'wx-2-2',
            title: '2.2 看板 / 车间大屏',
            content: `<h3>看板 / 车间大屏</h3>
<p><strong>路径</strong>：底部 tab「首页」→ 「看板」/「车间大屏」</p>
<p>与 PC 端相同：实时显示各产线进度、异常报警、交期倒计时。车间大屏建议投到 TV，做横屏自适应。</p>`
          },
        ]
      },
      {
        id: 'wx-ch3',
        title: '第三章 报工审核',
        icon: 'Document',
        children: [
          {
            id: 'wx-3-1',
            title: '3.1 批量审核',
            content: `<h3>批量审核（小程序特色）</h3>
<p><strong>路径</strong>：底部「管理」tab → 报工审核 → 批量</p>
<p>班组长在现场用手机审核最频繁，<strong>小程序为审核做了大量优化</strong>：</p>
<ul>
<li>按工序 / 班组 / 员工筛选待审</li>
<li>支持<strong>滑动审批</strong>（左滑通过 / 右滑驳回）</li>
<li>支持<strong>扫码</strong>调出报工详情（扫任务二维码定位到具体报工）</li>
<li>一次最多 20 条批量过 / 批量驳</li>
</ul>
<h4>审核要点</h4>
<ol>
<li>看员工上传的照片/视频（小程序能直接预览原图与视频）</li>
<li>核对数量（合格数 / 不良数）</li>
<li>通过 → 进入 QC 终审；驳回 → 填原因</li>
</ol>`
          },
          {
            id: 'wx-3-2',
            title: '3.2 单位审核（QC 终审）',
            content: `<h3>单位审核（QC 终审）</h3>
<p><strong>路径</strong>：底部「管理」tab → 报工单位</p>
<p>QC 终审岗用，<strong>支持按质检模板逐项打勾</strong>（详见 PC 端 6.3 节）：</p>
<ul>
<li>选择不合格项 → 必填缺陷代码 + 备注</li>
<li>测量型项目填入实测值，系统自动判定 pass/fail</li>
</ul>`
          },
          {
            id: 'wx-3-3',
            title: '3.3 审核详情',
            content: `<h3>审核详情</h3>
<p><strong>路径</strong>：报工列表 → 点某条报工</p>
<p>展示：员工 / 工序 / 数量 / 报工时间 / 照片视频 / 历史审核记录 / 关联工单 / 关联订单。</p>
<p>驳回时可选择驳回原因模板（从字典里选）或填自定义原因。</p>`
          },
        ]
      },
      {
        id: 'wx-ch4',
        title: '第四章 主数据管理',
        icon: 'Box',
        children: [
          {
            id: 'wx-4-1',
            title: '4.1 产品 / 型号 / 工序 / 工艺路线',
            content: `<h3>产品 / 型号 / 工序 / 工艺路线</h3>
<p><strong>路径</strong>：底部「管理」tab → 主数据</p>
<p>小程序支持<strong>浏览 + 轻量编辑</strong>，适合：</p>
<ul>
<li>外勤报价时翻产品库、看价格、复制产品编码给客户</li>
<li>车间现场查询某产品用的什么工艺路线、每道工序工价</li>
</ul>
<p><strong>不能</strong>在小程序做的：批量导入、复杂公式配置、删除（避免误操作）。这些需回 PC。</p>`
          },
          {
            id: 'wx-4-2',
            title: '4.2 物料 / BOM / 供应商',
            content: `<h3>物料 / BOM / 供应商</h3>
<p><strong>路径</strong>：主数据 → 物料 / BOM / 供应商</p>
<p>查询用得最多，看库存、看供应商联系方式、看某产品的 BOM 结构。</p>`
          },
          {
            id: 'wx-4-3',
            title: '4.3 批量设置型号工价',
            content: `<h3>批量设置型号工价</h3>
<p><strong>路径</strong>：主数据 → 型号 → 批量工价</p>
<p>车间调整工价时，老板/厂长在手机上<strong>勾选多个型号 + 多个工序</strong>，一键设工价。比 PC 操作快很多。</p>`
          },
        ]
      },
      {
        id: 'wx-ch5',
        title: '第五章 订单与工单',
        icon: 'List',
        children: [
          {
            id: 'wx-5-1',
            title: '5.1 订单管理',
            content: `<h3>订单管理</h3>
<p><strong>路径</strong>：底部「管理」tab → 订单</p>
<p>支持：浏览、筛选、改状态（确认 / 作废）、看订单详情、查客户联系方式。</p>
<p><strong>不能</strong>在小程序做：新建订单、编辑订单明细（需 PC）。</p>`
          },
          {
            id: 'wx-5-2',
            title: '5.2 工单 / 任务',
            content: `<h3>工单 / 任务</h3>
<p><strong>路径</strong>：底部「管理」tab → 工单 / 任务</p>
<p>小程序特色功能：</p>
<ul>
<li><strong>任务二维码</strong>：点单条任务 → 「生成任务码」→ 把图片保存到相册 → 打印贴工位，员工扫码报工</li>
<li><strong>扫码分配</strong>：扫员工码 + 扫任务码 → 一键派工</li>
<li><strong>任务跟踪</strong>：看每个任务当前进度（待报工 / 报工中 / 已完成）</li>
</ul>`
          },
          {
            id: 'wx-5-3',
            title: '5.3 客户管理',
            content: `<h3>客户管理</h3>
<p><strong>路径</strong>：底部「管理」tab → 客户</p>
<p>查客户档案、跟进记录、订单历史、联系人。客户详情页可直接拨打电话或加微信。</p>`
          },
        ]
      },
      {
        id: 'wx-ch6',
        title: '第六章 生产与计划',
        icon: 'Calendar',
        children: [
          {
            id: 'wx-6-1',
            title: '6.1 生产计划',
            content: `<h3>生产计划</h3>
<p><strong>路径</strong>：底部「管理」tab → 计划</p>
<p>小程序支持：浏览计划、看每条计划的甘特图（简化版）、改计划状态、<strong>AI 排产建议</strong>查看。</p>
<p><strong>不能</strong>在小程序做：新建复杂计划、甘特图拖拽、APS 高级选项（需 PC）。</p>`
          },
          {
            id: 'wx-6-2',
            title: '6.2 产能设置',
            content: `<h3>产能设置</h3>
<p><strong>路径</strong>：计划 → 产能</p>
<p>配置每道工序的<strong>标准工时</strong>、<strong>每日产能上限</strong>，APS 排产会用到。适合车间主任现场调整。</p>`
          },
          {
            id: 'wx-6-3',
            title: '6.3 自动化设置',
            content: `<h3>自动化设置</h3>
<p><strong>路径</strong>：底部「管理」tab → 系统 → 自动化</p>
<p>配置自动化规则：</p>
<ul>
<li>订单确认后自动派工</li>
<li>报工审核后自动推送飞书 / 钉钉</li>
<li>异常自动报警</li>
</ul>`
          },
        ]
      },
      {
        id: 'wx-ch7',
        title: '第七章 采购与仓库',
        icon: 'Goods',
        children: [
          {
            id: 'wx-7-1',
            title: '7.1 采购单 / 对账单',
            content: `<h3>采购单 / 对账单</h3>
<p><strong>路径</strong>：底部「管理」tab → 采购</p>
<p>查采购单进度（待发货 / 在途 / 已入库）、对账单确认、查供应商联系方式。</p>
<p>采购对账单的<strong>确认 / 标记已付</strong>操作可在小程序完成。</p>`
          },
          {
            id: 'wx-7-2',
            title: '7.2 仓库 / 库存',
            content: `<h3>仓库 / 库存</h3>
<p><strong>路径</strong>：底部「管理」tab → 仓库</p>
<p>查实时库存、看安全库存预警、查入库出库流水。</p>`
          },
        ]
      },
      {
        id: 'wx-ch8',
        title: '第八章 财务与工资',
        icon: 'Wallet',
        children: [
          {
            id: 'wx-8-1',
            title: '8.1 工资管理',
            content: `<h3>工资管理</h3>
<p><strong>路径</strong>：底部「管理」tab → 工资</p>
<p>支持：浏览月工资、点员工看明细、加补贴 / 扣款、确认工资、导出 Excel。</p>`
          },
          {
            id: 'wx-8-2',
            title: '8.2 工资条',
            content: `<h3>工资条</h3>
<p><strong>路径</strong>：工资 → 工资条</p>
<p>生成员工的电子工资条、查看签名进度、催签。</p>`
          },
          {
            id: 'wx-8-3',
            title: '8.3 利润分析 / 收支流水',
            content: `<h3>利润分析 / 收支流水</h3>
<p><strong>路径</strong>：底部「管理」tab → 财务</p>
<p>看月度利润、客户毛利、订单毛利。收支流水可查每笔进账出账。</p>`
          },
          {
            id: 'wx-8-4',
            title: '8.4 对账单',
            content: `<h3>对账单</h3>
<p><strong>路径</strong>：财务 → 对账单</p>
<p>客户对账单的生成、确认、催收、标记已收。</p>`
          },
        ]
      },
      {
        id: 'wx-ch9',
        title: '第九章 CRM',
        icon: 'UserFilled',
        children: [
          {
            id: 'wx-9-1',
            title: '9.1 销售机会',
            content: `<h3>销售机会</h3>
<p><strong>路径</strong>：底部「管理」tab → CRM → 销售机会</p>
<p>业务外勤时最常用：客户拜访后实时录入机会、改阶段、记跟进。</p>
<p>公海池自动回收：超期未跟进的机会自动回收到公海，业务可重新认领。</p>`
          },
          {
            id: 'wx-9-2',
            title: '9.2 客户标签 / 机会统计',
            content: `<h3>客户标签 / 机会统计</h3>
<p>客户标签用于分类（如 VIP、长期、一次性）。机会统计看转化率、阶段分布、外勤业绩。</p>`
          },
        ]
      },
      {
        id: 'wx-ch10',
        title: '第十章 设备与报表',
        icon: 'Tools',
        children: [
          {
            id: 'wx-10-1',
            title: '10.1 设备管理',
            content: `<h3>设备管理</h3>
<p><strong>路径</strong>：底部「管理」tab → 设备</p>
<p>查设备档案、看保养计划、登记保养记录、报修。</p>
<p><strong>日常点检</strong>：设备管理员现场扫码点检，避免漏检。</p>`
          },
          {
            id: 'wx-10-2',
            title: '10.2 报表',
            content: `<h3>报表</h3>
<p><strong>路径</strong>：底部「管理」tab → 报表</p>
<p>小程序支持<strong>图表速览</strong>（生产报表、采购统计、缺陷分析、利润分析），不提供 Excel 导出（需 PC）。</p>
<p>老板最常用：手机打开看本月关键指标。</p>`
          },
        ]
      },
      {
        id: 'wx-ch11',
        title: '第十一章 系统与设置',
        icon: 'Setting',
        children: [
          {
            id: 'wx-11-1',
            title: '11.1 系统设置',
            content: `<h3>系统设置</h3>
<p><strong>路径</strong>：底部「管理」tab → 系统</p>
<p>可做：</p>
<ul>
<li>查看租户信息、套餐</li>
<li>用户/角色/部门<strong>查询</strong>（增删改回 PC）</li>
<li>字典查看、打印模板查看</li>
<li>操作日志查询</li>
</ul>`
          },
          {
            id: 'wx-11-2',
            title: '11.2 考勤',
            content: `<h3>考勤</h3>
<p><strong>路径</strong>：系统 → 考勤</p>
<p>查看员工打卡记录、补卡、导出月度考勤表。员工自己打卡用「员工端」小程序（不同模式）。</p>`
          },
          {
            id: 'wx-11-3',
            title: '11.3 IM 推送配置',
            content: `<h3>IM 推送配置（小程序仅查看）</h3>
<p>飞书 / 钉钉 / 企微的 AppID、AppSecret 等敏感配置<strong>不能在小程序修改</strong>，必须回 PC 管理端（系统管理 → 飞书消息推送 / 钉钉消息推送 / 企微消息推送）。</p>
<p>小程序可查看：当前启用了哪些群、推送规则、推送日志。</p>`
          },
          {
            id: 'wx-11-4',
            title: '11.4 通知中心',
            content: `<h3>通知中心</h3>
<p><strong>路径</strong>：底部「我的」→ 通知</p>
<p>站内通知（铃铛）汇总，按事件码分类。已读 / 未读 / 一键全读。</p>`
          },
        ]
      },
      {
        id: 'wx-ch12',
        title: '第十二章 工厂助手 / AI 中心',
        icon: 'MagicStick',
        children: [
          {
            id: 'wx-12-1',
            title: '12.1 工厂助手（AI 对话）',
            content: `<h3>工厂助手（AI 对话）</h3>
<p><strong>路径</strong>：底部「管理」tab → AI → 工厂助手</p>
<p>小程序 AI 助手与 PC 完全同步：</p>
<ul>
<li>支持多轮对话 + <code>context_id</code> 上下文</li>
<li>问「今天产量 / 本月毛利 / 哪个工序卡交期 / 帮我写个催货话术」</li>
<li>语音输入：长按麦克风按钮直接说话</li>
</ul>`
          },
          {
            id: 'wx-12-2',
            title: '12.2 AI 深度分析 / 统计',
            content: `<h3>AI 深度分析 / 统计</h3>
<p><strong>深度分析</strong>：因果分析，帮你定位「为什么本月不良率上升」。</p>
<p><strong>AI 统计</strong>：AI 调用量、按场景拆解（问得最多的是什么）、调用成功率。</p>`
          },
        ]
      },
      {
        id: 'wx-ch13',
        title: '第十三章 小程序常见问题',
        icon: 'QuestionFilled',
        children: [
          {
            id: 'wx-13-1',
            title: '13.1 登录与权限',
            content: `<h3>登录与权限</h3>
<h4>Q1：登录后看不到某些菜单？</h4>
<p>权限问题。让 PC 端超级管理员在「系统管理 → 角色」里给该员工加对应权限码（如 <code>order.manage</code>、<code>report.audit</code>）。</p>
<h4>Q2：登录后显示「无租户」？</h4>
<p>该手机号没绑定到任何租户。让管理员在「用户管理」里给该员工绑定手机号。</p>
<h4>Q3：登录态过期？</h4>
<p>默认 token 8 小时有效。超期会自动跳登录页，重新验证码登录即可。</p>`
          },
          {
            id: 'wx-13-2',
            title: '13.2 数据同步',
            content: `<h3>数据同步</h3>
<h4>Q1：手机上看到的订单状态和 PC 不一致？</h4>
<p>下拉刷新页面。辰科MES 没有走实时推送，每页进入时拉取最新。</p>
<h4>Q2：上传照片失败？</h4>
<ul>
<li>检查微信是否授权「使用相册」</li>
<li>单张最大 100MB（可在 PC 端 .env 调 <code>FILE_MAX_UPLOAD_SIZE</code>）</li>
<li>网络问题：切换 WiFi / 数据流量重试</li>
</ul>`
          },
          {
            id: 'wx-13-3',
            title: '13.3 拍照与扫码',
            content: `<h3>拍照与扫码</h3>
<h4>Q1：报工拍照模糊？</h4>
<p>小程序拍照调用微信原生相机，点击对焦后等 1 秒再按快门。避免逆光。</p>
<h4>Q2：扫码扫不出来？</h4>
<ul>
<li>二维码太小：手机距离 15~30cm</li>
<li>模糊：对焦后再扫</li>
<li>屏幕太暗：调亮屏幕</li>
<li>仍扫不出：用手输任务码兜底</li>
</ul>`
          },
          {
            id: 'wx-13-4',
            title: '13.4 与 PC 端数据对应',
            content: `<h3>与 PC 端数据对应</h3>
<p>小程序管理端、PC 管理端、H5 端 三者共享同一后端，<strong>数据完全一致</strong>。差异只在交互方式：</p>
<table>
<tr><th>场景</th><th>推荐</th></tr>
<tr><td>车间走动审核</td><td>小程序</td></tr>
<tr><td>复杂报表导出</td><td>PC</td></tr>
<tr><td>外勤报价 / 客户管理</td><td>小程序</td></tr>
<tr><td>初始化配置 / 批量导入</td><td>PC</td></tr>
<tr><td>客户下单</td><td>客户端 H5 / 小程序</td></tr>
<tr><td>员工报工 / 查工资</td><td>员工端 H5 / 小程序</td></tr>
</table>`
          },
        ]
      },
    ]
  },
  {
    id: 'part5',
    title: '第五篇：新功能速递（更新至 2026-09）',
    icon: 'DataBoard',
    children: [
      {
        id: 'p5-ch1',
        title: '第一章 报表导出（PC）',
        icon: 'DataBoard',
        children: [
          {
            id: 'p5-1-1',
            title: '1.1 产量报表导出',
            content: `<h3>产量报表导出</h3>
<p><strong>使用者</strong>：厂长 / 生产计划员 / 财务</p>
<p><strong>操作路径</strong>：Admin-Pro → 报表 → 产量报表 → 右上角「导出」</p>
<h4>操作步骤</h4>
<ol>
<li>进入「产量报表」页面</li>
<li>顶部选择统计区间（支持快捷：今日/本周/本月/本季/自定义）</li>
<li>可选筛选：产品型号、车间、工序、操作员工</li>
<li>点击「<strong>导出</strong>」→ 选 Excel / CSV → 「开始导出」</li>
<li>系统提示任务已创建，到「<strong>报表 → 导出中心</strong>」查看进度</li>
<li>状态「已完成」时点「<strong>下载</strong>」</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>导出任务默认保留 <strong>7 天</strong>，到期自动清理</li>
<li>大数据量（>10 万行）建议选 CSV 格式</li>
<li>「导出中心」支持按类型/时间/状态筛选</li>
<li>处理中超 30 分钟异常请刷新，仍异常联系管理员</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>批量下载</strong>：勾选多条「已完成」→「打包下载」</li>
<li><strong>良率 / 库存 / 对账单</strong> 报表同样流程</li>
</ul>`
          },
          {
            id: 'p5-1-2',
            title: '1.2 良率报表导出（含缺陷 TOP10）',
            content: `<h3>良率报表导出</h3>
<p><strong>使用者</strong>：厂长 / 质检主管 / 生产经理</p>
<p><strong>操作路径</strong>：Admin-Pro → 报表 → 良率报表 → 「导出」</p>
<h4>操作步骤</h4>
<ol>
<li>进入「良率报表」</li>
<li>选择时间区间、车间、产品型号</li>
<li>页面默认显示合格率、不良率、缺陷码占比</li>
<li>点击「<strong>导出</strong>」→ 选 Excel → 「开始导出」</li>
<li>导出的 Excel 额外包含<strong>「缺陷 TOP10」明细</strong></li>
</ol>
<h4>注意事项</h4>
<ul>
<li>良率 = 合格数 / 总报工数</li>
<li>勾选「对比上期」会在 Excel 中多出对比列</li>
<li>TOP10 缺陷可作为<strong>质量改善专题</strong>的输入</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>点缺陷码 → 跳到「缺陷分析」详细页</li>
<li>右上角「列设置」可勾选导出字段</li>
</ul>`
          },
          {
            id: 'p5-1-3',
            title: '1.3 库存报表导出',
            content: `<h3>库存报表导出</h3>
<p><strong>使用者</strong>：仓库管理员 / 财务 / 采购</p>
<p><strong>操作路径</strong>：Admin-Pro → 仓库 → 库存 → 「导出」</p>
<h4>操作步骤</h4>
<ol>
<li>进入「库存」页</li>
<li>筛选仓库、物料分类、库存状态（在库/安全库存以下/积压）</li>
<li>点击「<strong>导出</strong>」→ 选「<strong>当前快照</strong>」或「<strong>带流水</strong>」</li>
<li>带流水：包含最近 30 天出入库流水（适合月结对账）</li>
<li>导出任务到「导出中心」下载</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>库存金额字段需先在「系统设置 → 计价方式」开启</li>
<li>安全库存以下的物料导出时<strong>标红</strong></li>
<li>物料编码/批次号保留前导 0</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>打印盘点表</strong>：勾选多条 → 选空白列手填</li>
<li>物料详情 → 「库存参数」设置安全库存</li>
</ul>`
          },
          {
            id: 'p5-1-4',
            title: '1.4 对账单导出（Excel / PDF）',
            content: `<h3>对账单导出</h3>
<p><strong>使用者</strong>：财务 / 销售客服</p>
<p><strong>操作路径</strong>：Admin-Pro → 财务 → 对账单 → 「导出」</p>
<h4>操作步骤</h4>
<ol>
<li>进入「对账单」页</li>
<li>选客户、对账周期（如「2026-05」）</li>
<li>系统自动汇总该周期内已交付订单金额、税额、已收/未收</li>
<li>点击「<strong>导出</strong>」→ 选格式：<ul>
<li><strong>对账单 Excel</strong>：标准对账模板</li>
<li><strong>对账单 PDF</strong>：已加盖电子章，直接发客户</li>
</ul></li>
<li>完成后到「导出中心」下载</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>PDF 对账单需先在「系统设置 → 电子签章」上传公司印章</li>
<li>已确认的对账单 PDF 带「<strong>已确认</strong>」水印</li>
<li>客户邮箱发送：导出完成后点「<strong>邮件发送</strong>」</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>批量导出</strong>：勾选多份 → 打 ZIP 包</li>
<li>对账单同步到客户 H5 → 客户在线确认/异议</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch2',
        title: '第二章 模具/工装管理（PC + H5）',
        icon: 'Tools',
        children: [
          {
            id: 'p5-2-1',
            title: '2.1 模具档案',
            content: `<h3>模具档案</h3>
<p><strong>使用者</strong>：设备管理员 / 生产主管</p>
<p><strong>操作路径</strong>：Admin-Pro → 生产 → 模具管理 → 「+ 新建模具」</p>
<h4>操作步骤</h4>
<ol>
<li>进入「模具管理」页</li>
<li>点「<strong>+ 新建模具</strong>」</li>
<li>填写：<ul>
<li><strong>模具编码</strong>（必填，建议 <code>MOLD-</code> 前缀）</li>
<li>名称 / 类型（注塑/冲压/压铸/工装夹具）</li>
<li>关联产品（可选）</li>
<li>设计寿命（次/件）、当前累计次数</li>
<li>存放位置、责任人</li>
</ul></li>
<li>点「保存」</li>
</ol>
<h4>列表关键字段</h4>
<table>
<tr><th>字段</th><th>说明</th></tr>
<tr><td>模具编码</td><td>唯一，扫描二维码即显示</td></tr>
<tr><td>寿命进度</td><td>进度条 + 百分比；80% 黄色，100% 红色</td></tr>
<tr><td>累计次数</td><td>随员工报工自动累加</td></tr>
<tr><td>最近维保</td><td>上次维保日期；超期会标红</td></tr>
<tr><td>状态</td><td>正常 / 维保中 / 待报废</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>模具编码一旦保存<strong>不可修改</strong></li>
<li>关联产品后，该产品的报工<strong>自动累计</strong>到模具</li>
<li>支持 Excel 批量导入</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>扫码查看</strong>：H5 扫码查模具详情/维保历史</li>
<li><strong>打印模具卡</strong>：详情页「打印」→ A6 模具卡</li>
</ul>`
          },
          {
            id: 'p5-2-2',
            title: '2.2 寿命预警与冻结',
            content: `<h3>模具寿命预警</h3>
<p><strong>使用者</strong>：设备管理员 / 班组长</p>
<p><strong>操作路径</strong>：Admin-Pro → 生产 → 模具管理 → 顶部「寿命预警」</p>
<h4>触发规则</h4>
<table>
<tr><th>进度</th><th>颜色</th><th>系统动作</th></tr>
<tr><td>≥ 80%</td><td>🟡 黄色</td><td>列表标黄 + IM 推送设备管理员/班组长</td></tr>
<tr><td>≥ 95%</td><td>🟠 橙色</td><td>推送升级到车间主任</td></tr>
<tr><td>≥ 100%</td><td>🔴 红色</td><td><strong>自动冻结关联产品的报工</strong>，必须先维保</td></tr>
</table>
<h4>接收预警</h4>
<ul>
<li>飞书 / 钉钉 / 企微：设备管理员、关联车间班组长、红色时厂长</li>
<li>站内通知：右上角「铃铛」红点</li>
</ul>
<h4>处理方法</h4>
<ol>
<li>收到预警 → 进入「模具管理」找到该模具</li>
<li>点「<strong>登记维保</strong>」（见 2.3）</li>
<li>维保完成后，寿命进度清零</li>
<li>红色预警：系统冻结报工，维保提交后自动解冻</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>阈值可在「系统设置 → 模具参数」调整（默认 80/95/100）</li>
<li>寿命进度支持<strong>手动校正</strong>（更换关键零件后），需填校正原因</li>
<li>误报：「预警记录」页可标记「已处理 / 误报」</li>
</ul>`
          },
          {
            id: 'p5-2-3',
            title: '2.3 维保记录登记（PC + H5）',
            content: `<h3>维保记录登记</h3>
<p><strong>使用者</strong>：设备员 / 班组长</p>
<p><strong>操作路径</strong>：Admin-Pro → 生产 → 模具管理 → 详情 → 「维保记录」</p>
<h4>操作步骤（PC）</h4>
<ol>
<li>找到目标模具 → 进入详情</li>
<li>「维保记录」tab → 点「<strong>+ 新建记录</strong>」</li>
<li>选<strong>维保类型</strong>：<ul>
<li>日常清洁（最常用）</li>
<li>定期保养（周/月）</li>
<li>故障维修（非计划停机）</li>
<li>寿命校正（更换零件后重置寿命）</li>
</ul></li>
<li>填写维保说明、上传现场照片（最多 9 张）</li>
<li>「保存」</li>
</ol>
<h4>移动端登记（H5，车间现场推荐）</h4>
<ol>
<li>H5 → 「生产工具」tab → 「<strong>扫码登记维保</strong>」</li>
<li>扫模具码 → 直接填写</li>
<li>适合不方便开电脑的场景</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>「<strong>故障维修</strong>」必须勾选「停机时长」字段</li>
<li>维保记录<strong>不可删除</strong>，填错可「作废」（保留痕迹）</li>
<li>「<strong>寿命校正</strong>」：填「重置后次数」，系统自动算消耗量</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>「故障维修」可勾选「使用备件」自动扣减备件库存</li>
<li>列表「导出」按时间段生成维保台账 Excel</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch3',
        title: '第三章 条码打印机直连（PC）',
        icon: 'Document',
        children: [
          {
            id: 'p5-3-1',
            title: '3.1 浏览器 / Lodop 直连',
            content: `<h3>浏览器 / Lodop 直连</h3>
<p><strong>使用者</strong>：仓库 / 车间文员</p>
<p><strong>操作路径</strong>：Admin-Pro → 仓库 → 库存 / 工单 → 详情 → 「打印标签」</p>
<h4>首次使用：安装 Lodop 插件</h4>
<ol>
<li>Admin-Pro → 系统管理 → 打印设置 → 「<strong>下载 Lodop 控件</strong>」</li>
<li>安装后<strong>刷新页面</strong>（Windows 可能要重启浏览器）</li>
<li>点「<strong>测试打印</strong>」→ 选打印机 → 打印测试页成功即可</li>
</ol>
<h4>操作步骤</h4>
<ol>
<li>进入「库存 / 工单 / 产品型号」详情页</li>
<li>点「<strong>打印标签</strong>」→ 选标签模板（如「产品码 50×30mm」）</li>
<li>选打印机 → 设置打印份数 → 「<strong>打印</strong>」</li>
<li>Lodop 弹窗显示预览 → 点「<strong>确定</strong>」出标</li>
</ol>
<h4>注意事项</h4>
<ul>
<li><strong>仅 Windows + Chrome / Edge / 360</strong> 浏览器支持</li>
<li>标签模板可在「打印设置」按需添加（自定义尺寸、二维码位置、字段）</li>
<li>打印失败排查：见「<a>常见问题 Q2</a>」</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>批量打印</strong>：列表页勾选多条 → 「批量打标」</li>
<li>模板支持变量（产品名/编码/批次/数量），新打印时自动套用</li>
</ul>`
          },
          {
            id: 'p5-3-2',
            title: '3.2 ZPL 网络打印（多车间多机）',
            content: `<h3>ZPL 网络打印</h3>
<p><strong>适用场景</strong>：Zebra / TSC 等工业条码机，机器固定 IP 接入车间网络。</p>
<p><strong>使用者</strong>：车间 IT / 仓库主管</p>
<p><strong>操作路径</strong>：Admin-Pro → 系统管理 → 打印设置 → 「网络打印机」</p>
<h4>添加打印机</h4>
<ol>
<li>进入「网络打印机」页 → 「<strong>+ 新增打印机</strong>」</li>
<li>填写：<ul>
<li><strong>打印机名称</strong>（如 "车间 1 号 ZEBRA"）</li>
<li><strong>IP 地址</strong>（如 192.168.1.100）</li>
<li><strong>端口</strong>（默认 9100）</li>
<li><strong>DPI / 标签尺寸</strong></li>
</ul></li>
<li>点「<strong>测试连接</strong>」→ 看到「测试页已发送」即成功</li>
<li>保存</li>
</ol>
<h4>打印标签</h4>
<ul>
<li>「打印标签」时，<strong>打印机下拉里选网络打印机</strong>即可</li>
<li>系统自动生成 ZPL 指令并发送</li>
<li>适合<strong>多车间多打印机</strong>的场景</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>打印机与服务器<strong>必须同网段</strong>（或能互通）</li>
<li><strong>防火墙</strong>：9100 端口需在打印机所在网络放行</li>
<li><strong>离线缓存</strong>：网络不通时打印任务<strong>自动入队</strong>，恢复后<strong>重试 3 次</strong></li>
</ul>
<h4>相关操作</h4>
<ul>
<li>列表显示打印机状态（在线/离线/缺纸/忙）</li>
<li>每台打印机可查最近 100 条<strong>打印历史</strong></li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch4',
        title: '第四章 SPC 统计过程控制（PC）',
        icon: 'DataBoard',
        children: [
          {
            id: 'p5-4-1',
            title: '4.1 控制图管理（Xbar-R / P / np / c / u）',
            content: `<h3>控制图管理</h3>
<p><strong>使用者</strong>：质管部 / 工艺工程师</p>
<p><strong>操作路径</strong>：Admin-Pro → 生产 → SPC 控制图</p>
<h4>操作步骤</h4>
<ol>
<li>进入「SPC 控制图」页</li>
<li>点「<strong>+ 新建控制图</strong>」</li>
<li>填写：<ul>
<li><strong>名称</strong>（如 "CNC 外径 Xbar-R"）</li>
<li><strong>图表类型</strong>：<ul>
<li><code>Xbar-R</code>（计量型，最常用）：均值 + 极差</li>
<li><code>P</code>（计件不良率）</li>
<li><code>np</code>（不良数）</li>
<li><code>c</code>（缺陷数）</li>
<li><code>u</code>（单位缺陷数）</li>
</ul></li>
<li>关联工序、关联产品（可选）</li>
<li>样本量（默认 5）</li>
<li>目标值 / 规格中心、UCL / LCL（控制上下限）</li>
</ul></li>
<li>点「保存」</li>
</ol>
<h4>控制图类型选择建议</h4>
<table>
<tr><th>数据类型</th><th>推荐图表</th><th>典型场景</th></tr>
<tr><td>尺寸 / 重量 / 长度</td><td>Xbar-R</td><td>机加工外径、注塑件重量</td></tr>
<tr><td>是否合格（计数）</td><td>P</td><td>焊点合格率、装配一次合格率</td></tr>
<tr><td>缺陷数</td><td>c</td><td>表面缺陷数</td></tr>
<tr><td>每单位缺陷</td><td>u</td><td>铸件气孔数 / 100 件</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>UCL / LCL <strong>建议先点「自动计算」</strong>，再根据经验微调</li>
<li>同一工序不同设备可建<strong>多张</strong>图</li>
<li>控制图可<strong>停用 / 启用</strong>，停用后不再监控但保留历史</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>复制控制图</strong>：列表「复制」快速建同类型图</li>
<li>详情「导出 PNG」或「导出 PDF」</li>
</ul>`
          },
          {
            id: 'p5-4-2',
            title: '4.2 样本录入与判异',
            content: `<h3>样本录入与查看</h3>
<p><strong>使用者</strong>：QC 质检员 / 班组长</p>
<p><strong>操作路径</strong>：Admin-Pro → 生产 → SPC 控制图 → 详情 → 「样本录入」</p>
<h4>手动录入</h4>
<ol>
<li>控制图详情页 → 「<strong>样本录入</strong>」tab</li>
<li>选择<strong>测量批次</strong>（每批 = 一次抽样的 N 个数据）</li>
<li>输入 N 个测量值（如 50.1, 50.2, 49.9, 50.0, 50.3）</li>
<li>点「<strong>保存</strong>」→ 系统自动计算均值/极差/标准差</li>
<li>数据点落到控制图上，<strong>越界点标红</strong></li>
</ol>
<h4>异常判定（判异规则）</h4>
<table>
<tr><th>规则</th><th>含义</th></tr>
<tr><td><strong>1 点出界</strong></td><td>任一数据点 > UCL 或 < LCL</td></tr>
<tr><td><strong>连续 9 点在中心线同侧</strong></td><td>过程均值偏移</td></tr>
<tr><td><strong>连续 6 点递增 / 递减</strong></td><td>趋势性偏移</td></tr>
<tr><td><strong>连续 2 点接近控制限（2σ 内）</strong></td><td>即将失控</td></tr>
</table>
<p>以上任一情况，<strong>系统红色提示 + IM 推送</strong>。</p>
<h4>注意事项</h4>
<ul>
<li><strong>样本量必须 = 控制图设定的 N</strong></li>
<li>录入时<strong>单位一致</strong>（mm / cm / g 不可混用）</li>
<li>录入错误可「<strong>作废</strong>」该批次（保留痕迹）</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>详情「<strong>导出 CSV</strong>」原始数据</li>
<li>详情「<strong>打印</strong>」 → A4 横版含图 + 判异记录</li>
</ul>`
          },
          {
            id: 'p5-4-3',
            title: '4.3 Cpk 判异标准',
            content: `<h3>Cpk 判异标准</h3>
<p><strong>Cpk（过程能力指数）</strong> 是衡量“工序能否稳定满足规格”的指标，<strong>越大越好</strong>。</p>
<h4>Cpk 判读表</h4>
<table>
<tr><th>Cpk 值</th><th>评价</th><th>建议动作</th></tr>
<tr><td><strong>≥ 1.67</strong></td><td>优（过剩）</td><td>可考虑放宽公差以降低成本</td></tr>
<tr><td><strong>1.33 ~ 1.67</strong></td><td><strong>充足</strong>（行业标准）</td><td>维持现状</td></tr>
<tr><td><strong>1.00 ~ 1.33</strong></td><td>尚可</td><td>关注 4M 变化（人 / 机 / 料 / 法）</td></tr>
<tr><td><strong>< 1.00</strong></td><td>不足</td><td><strong>必须停线整顿</strong>，做 PFMEA</td></tr>
</table>
<h4>Cpk 在哪里看</h4>
<ul>
<li>控制图详情页 → 「<strong>能力分析</strong>」面板</li>
<li>系统<strong>每月自动重算 Cpk</strong>，并归档历史趋势图</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>至少需要 <strong>25 个子组（≥ 125 个数据点）</strong>才统计可靠</li>
<li>数据非正态时，Cpk 仅供参考，可看「<strong>Ppk</strong>」（整体能力）</li>
<li>Cpk < 1 时，控制图即使“看起来正常”也<strong>不能放过</strong></li>
</ul>
<h4>相关操作</h4>
<ul>
<li>报表 → SPC 月报，含每张图的 Cpk 趋势 + 排名</li>
<li>AI 助手问「某控制图 Cpk 为什么这个月下降」可获得因果分析</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch5',
        title: '第五章 可配置审批流（PC + H5）',
        icon: 'Edit',
        children: [
          {
            id: 'p5-5-1',
            title: '5.1 维护审批流（可视化拖拽）',
            content: `<h3>维护审批流</h3>
<p><strong>使用者</strong>：系统管理员 / 厂长</p>
<p><strong>操作路径</strong>：Admin-Pro → 系统 → 审批流配置</p>
<h4>操作步骤</h4>
<ol>
<li>进入「<strong>审批流配置</strong>」页</li>
<li>点「<strong>+ 新建审批流</strong>」</li>
<li>填写：<ul>
<li><strong>名称</strong>（如 "生产报工 3 级审批"）</li>
<li><strong>业务类型</strong>：<code>report</code> 报工 / <code>mold_scrap</code> 模具报废 / <code>salary_adjust</code> 工资调整</li>
<li>是否启用</li>
</ul></li>
<li>进入「<strong>步骤配置</strong>」：<ul>
<li>点「+ 添加步骤」→ 设置步骤顺序、审批角色、是否必经、触发条件</li>
<li><strong>拖拽调整顺序</strong></li>
</ul></li>
<li>点「<strong>保存</strong>」 → 立即生效</li>
</ol>
<h4>内置审批流（参考）</h4>
<table>
<tr><th>业务</th><th>步骤</th></tr>
<tr><td>报工（默认）</td><td>班组长 → 质检员 → 自动入账</td></tr>
<tr><td>模具报废</td><td>班组长 → 设备主管 → 厂长</td></tr>
<tr><td>工资调整</td><td>班组长 → 财务 → 厂长</td></tr>
<tr><td>订单变更</td><td>销售 → 生产计划员 → 厂长</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>同一业务只能有 <strong>1 个「启用」流程</strong>；多个时按"优先级"取</li>
<li>现有<strong>在途审批不受流程变更影响</strong>，新提交才用新流程</li>
<li>角色对应的具体人员在「系统 → 角色」配置</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>列表「<strong>复制</strong>」 → 快速建新流程</li>
<li>历史版本可查（<strong>灰度上线、随时回滚</strong>）</li>
</ul>`
          },
          {
            id: 'p5-5-2',
            title: '5.2 审核视角（PC + H5 + IM 卡片）',
            content: `<h3>审核视角</h3>
<p><strong>使用者</strong>：班组长 / 质检员 / 财务 / 厂长</p>
<p><strong>操作路径</strong>：<ul>
<li>PC：Admin-Pro → 生产 → 报工审核 / 业务对应页 → 「待我审批」</li>
<li>H5：手机端「<strong>消息</strong>」 → 「<strong>待我审批</strong>」卡片 / 飞书 / 钉钉卡片</li>
</ul></p>
<h4>PC 审核步骤</h4>
<ol>
<li>登录后右上角「<strong>铃铛</strong>」红点显示待审数</li>
<li>点「<strong>报工审核</strong>」或对应业务 → 「<strong>待我审批</strong>」列表</li>
<li>选中一条 → 看到申请人/工序/数量/照片/AI 预审结论（详见 <a>第六章 9. AI 自动审核</a>）</li>
<li>审核动作：<ul>
<li><strong>通过</strong>：→ 进入下一级 / 流程结束</li>
<li><strong>驳回</strong>：填写驳回原因（<strong>必填</strong>）→ 退回申请人</li>
<li><strong>转交</strong>：选其他审批人（<strong>仅同角色</strong>）</li>
</ul></li>
<li>提交后系统通知申请人</li>
</ol>
<h4>H5 审核（车间现场推荐）</h4>
<ul>
<li>班组长在车间：<strong>飞书 / 钉钉卡片</strong>直接点「<strong>通过 / 驳回</strong>」按钮，<strong>不打开网页</strong></li>
<li>需开启「<code>card_actions_enabled</code>」，配置回调 URL <code>{域名}/api/dingtalk/card_action</code></li>
</ul>
<h4>注意事项</h4>
<ul>
<li><strong>驳回原因建议结构化</strong>（如"照片不清晰 / 数量异常 / 与工艺不符"）</li>
<li>同一报工的<strong>审核历史</strong>可点击展开查看</li>
<li>终审通过后，<strong>该报工不能再驳回</strong>（有问题走「异常申报」流程）</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>批量审核</strong>：勾选多条同类审批 → 批量通过/驳回</li>
<li>审批超时提醒：超 4 小时未审自动 IM 催办</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch6',
        title: '第六章 PWA 离线报工（H5）',
        icon: 'Cellphone',
        children: [
          {
            id: 'p5-6-1',
            title: '6.1 安装与启动（添加到主屏）',
            content: `<h3>安装与启动</h3>
<p><strong>使用者</strong>：所有操作员工</p>
<p><strong>操作路径</strong>：H5 → 浏览器首次访问 → 「添加到主屏幕」</p>
<h4>安装步骤</h4>
<ol>
<li>用手机浏览器（<strong>Chrome / Safari / 微信内置</strong>）打开 H5 链接</li>
<li>浏览器弹出「<strong>添加到主屏幕</strong>」提示（或手动：浏览器菜单 → 分享 → 添加到主屏幕）</li>
<li>桌面出现「<strong>辰科MES H5</strong>」图标，<strong>全屏启动</strong>，无浏览器地址栏</li>
</ol>
<h4>启动效果</h4>
<ul>
<li><strong>离线可启动</strong>：无网络时打开 App，可看历史任务和缓存数据</li>
<li>左上角有“离线”角标：网络恢复后角标消失</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>仅 <strong>H5 端</strong>支持 PWA；Admin-Pro 后台仍需联网</li>
<li>iOS Safari 需 <strong>iOS 11.3+</strong>；Android Chrome <strong>61+</strong></li>
<li>首次联网时<strong>自动下载离线包</strong>（约 2 MB），第二次起<strong>秒开</strong></li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>更新提示</strong>：服务器发布新版本时，App 内顶部弹“有新版本，点击刷新”</li>
<li>App 内「设置 → 清除缓存」（不影响服务器数据）</li>
</ul>`
          },
          {
            id: 'p5-6-2',
            title: '6.2 离线报工与重放',
            content: `<h3>离线报工与重放</h3>
<p><strong>使用者</strong>：操作员工</p>
<p><strong>操作路径</strong>：H5 主页 → 「扫码报工」 / 「我的任务」</p>
<h4>离线报工流程</h4>
<ol>
<li>无网络时打开 H5</li>
<li>进入「<strong>扫码报工</strong>」→ 扫任务二维码（或从「我的任务」选）</li>
<li>输入合格数 / 不良数、上传照片 / 视频</li>
<li>填备注 → 点「<strong>提交</strong>」</li>
<li>弹窗提示「<strong>已暂存到本地，待联网后自动提交</strong>」→ 在「<strong>我的 → 离线队列</strong>」可看到</li>
</ol>
<h4>联网后自动重放</h4>
<ul>
<li>网络恢复后，App <strong>自动检测离线队列</strong> → 按时间顺序依次提交</li>
<li>每条提交后：<ul>
<li><strong>成功</strong>：从离线队列移除，弹“提交成功”</li>
<li><strong>失败</strong>：保留在队列，红字提示原因（如“任务已被别人报完”），可手动「<strong>重试</strong>」或「<strong>删除</strong>」</li>
</ul></li>
</ul>
<h4>注意事项</h4>
<ul>
<li>离线时可拍照，照片暂存本地；联网后与表单一起上传</li>
<li>队列容量：<strong>最多保留 50 条</strong>，超出后<strong>最早的丢弃并提示</strong></li>
<li>离线时<strong>不能查看</strong>最新任务（数据是缓存的），需联网刷新</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>离线队列管理</strong>：「我的 → 离线队列」可看全部、重试、删除</li>
<li>右上角「<strong>刷新</strong>」 → 联网时主动拉取最新数据</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch7',
        title: '第七章 拍照自动计数（H5）',
        icon: 'Cellphone',
        children: [
          {
            id: 'p5-7-1',
            title: '7.1 拍照自动计数操作',
            content: `<h3>拍照自动计数</h3>
<p><strong>价值</strong>：拍一张产品照片，<strong>AI 自动数出零件数</strong>，免去手动数。</p>
<p><strong>使用者</strong>：操作员工</p>
<p><strong>操作路径</strong>：H5 → 报工页 → 「<strong>AI 数一下零件</strong>」按钮</p>
<h4>操作步骤</h4>
<ol>
<li>进入报工页（扫码或选任务）</li>
<li>在「<strong>合格数</strong>」输入框右侧点「<strong>AI 数一下零件</strong>」按钮</li>
<li>弹出相机 → <strong>拍产品正面</strong>（光线好、零件不重叠）</li>
<li>等待 1~3 秒，AI 识别完成后：<ul>
<li><strong>自动填入合格数</strong></li>
<li>显示<strong>置信度</strong>：高（绿色）/ 中（黄色）/ 低（红色，需人工复核）</li>
</ul></li>
<li>复核无误 → 继续报工</li>
</ol>
<h4>适用与不适用</h4>
<table>
<tr><th>✅ 适合</th><th>❌ 不适合</th></tr>
<tr><td>标准件散落在桌面</td><td>重叠 / 堆叠</td></tr>
<tr><td>颜色 / 形状一致</td><td>多种零件混放</td></tr>
<tr><td>光线均匀</td><td>强反光 / 强阴影</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>AI 数的是「<strong>照片中能识别的数量</strong>」，不是「你今天的合格数」。<strong>两个概念不要混</strong></li>
<li><strong>置信度低</strong>时建议人工数 + 在备注里说明</li>
<li>支持<strong>一次提交多张照片</strong>（系统取<strong>识别最多</strong>的那张）</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>「我的 → AI 识别记录」可看所有 AI 数过的图</li>
<li>识别错误时点「<strong>纠错</strong>」→ 帮 AI 学习（需启用反馈学习）</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch8',
        title: '第八章 语音报工（H5）',
        icon: 'Cellphone',
        children: [
          {
            id: 'p5-8-1',
            title: '8.1 语音报工操作与话术',
            content: `<h3>语音报工</h3>
<p><strong>价值</strong>：边干活边说话，<strong>AI 自动解析"做了 50 个好的，2 个有划痕"</strong> → 填入表单。</p>
<p><strong>使用者</strong>：操作员工</p>
<p><strong>操作路径</strong>：H5 → 报工页 → 备注框旁「<strong>🎙 录音</strong>」按钮</p>
<h4>操作步骤</h4>
<ol>
<li>进入报工页</li>
<li>准备录入时，点备注框旁的「<strong>🎙 录音</strong>」按钮（首次会弹权限请求：允许使用麦克风）</li>
<li>说出内容（参考话术见下表）</li>
<li>说完后再次点「<strong>🎙 停止</strong>」</li>
<li>AI 解析后：<ul>
<li><strong>good_qty（合格数）</strong> 自动填入</li>
<li><strong>bad_qty（不良数）</strong> 自动填入</li>
<li><strong>defect_keywords（缺陷关键词）</strong> 自动填入备注</li>
</ul></li>
<li>核对 → 继续提交</li>
</ol>
<h4>推荐话术</h4>
<table>
<tr><th>场景</th><th>话术</th></tr>
<tr><td>只报数量</td><td>"50 个好的"</td></tr>
<tr><td>报合格+不良</td><td>"做了 50 个好的，2 个有划痕"</td></tr>
<tr><td>报不良品</td><td>"3 个是次品，变形"</td></tr>
<tr><td>报进度</td><td>"今天到第 80 件"</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li><strong>需要 HTTPS 环境</strong>（麦克风权限限制）</li>
<li>单次录音<strong>最长 60 秒</strong>，超长内容分段录</li>
<li>方言 / 噪声严重时识别率下降，建议<strong>标准普通话</strong></li>
<li>解析后的数字<strong>仍要人工核对</strong>（特别是"一"和"七"等音近字）</li>
</ul>
<h4>相关操作</h4>
<ul>
<li><strong>语音 + 拍照</strong>可同时使用：先 AI 数 → 再语音补充不良信息</li>
<li>AI 解析后任何字段都可<strong>手动改</strong>，AI 不会重复触发</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch9',
        title: '第九章 AI 自动审核（PC + H5）',
        icon: 'Edit',
        children: [
          {
            id: 'p5-9-1',
            title: '9.1 自动通过（低风险）与人工审核（中/高风险）',
            content: `<h3>AI 自动审核</h3>
<p><strong>价值</strong>：低风险报工<strong>自动通过</strong>，省去班组长 50% 的审核工作。</p>
<p>AI 从 <strong>6 个维度</strong>评估：<strong>良率、员工熟练度、照片质量、缺陷严重度、工序、时段</strong>。</p>
<p><strong>使用者</strong>：班组长（被替代部分工作）/ 系统（自动处理）</p>
<p><strong>操作路径</strong>：<ul>
<li>PC：Admin-Pro → 生产 → 报工审核 → 看「<strong>AI 预审</strong>」标签</li>
<li>H5：报工提交后立即看到 AI 提示</li>
</ul></p>
<h4>三级风险与体验</h4>
<table>
<tr><th>风险等级</th><th>评分</th><th>体验</th></tr>
<tr><td><strong>低风险</strong></td><td>< 20</td><td>报工<strong>秒级自动通过</strong>，员工 H5 收到推送：“AI 已自动审核通过”</td></tr>
<tr><td><strong>中风险</strong></td><td>20 ~ 59</td><td>提交给班组长<strong>正常审核</strong>，AI 给出<strong>风险点提示</strong>（如"良率比上周低 5%"）</td></tr>
<tr><td><strong>高风险</strong></td><td>≥ 60</td><td><strong>强制人工审核</strong> + 弹窗提示，并<strong>推送给车间主任</strong></td></tr>
</table>
<h4>班组长审核页 AI 辅助</h4>
<ul>
<li>报工列表每条带「<strong>AI 预审</strong>」徽章：<ul>
<li>🟢 <strong>低风险</strong>：可一键通过</li>
<li>🟡 <strong>中风险</strong>：查看 AI 给出的原因</li>
<li>🔴 <strong>高风险</strong>：必须重点看照片 / 视频，<strong>不可一键通过</strong></li>
</ul></li>
<li>鼠标悬停徽章，<strong>展开 6 维度雷达图</strong>（一键看懂哪里可疑）</li>
</ul>
<h4>6 维度评分（参考）</h4>
<table>
<tr><th>维度</th><th>说明</th></tr>
<tr><td>良率</td><td>低于该员工历史均值则加分</td></tr>
<tr><td>熟练度</td><td>新员工 / 转岗员工加分</td></tr>
<tr><td>照片质量</td><td>模糊 / 缺照片 / 角度异常加分</td></tr>
<tr><td>缺陷严重度</td><td>不良数 > 阈值则加分</td></tr>
<tr><td>工序</td><td>高风险工序（如焊接）加分</td></tr>
<tr><td>时段</td><td>深夜 / 加班时段加分</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>AI 通过<strong>不代表无错</strong>，管理员可<strong>事后抽查</strong>（建议每周抽 5%）</li>
<li>「报工审核 → AI 审核规则」可调整风险阈值（默认 20）</li>
<li>触发<strong>高风险</strong>会<strong>自动抄送车间主任</strong>（即使你只是班组长）</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>管理员可在「<strong>系统 → AI 设置</strong>」单独关闭某个维度的评分</li>
<li>AI 自动通过记录<strong>保留完整证据</strong>（照片 / 视频 / 各项评分），可随时审计</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch10',
        title: '第十章 AI 缺陷分类（H5）',
        icon: 'Cellphone',
        children: [
          {
            id: 'p5-10-1',
            title: '10.1 拍照识别缺陷 + 缺陷库',
            content: `<h3>AI 缺陷分类</h3>
<p><strong>价值</strong>：拍一张不良品照片，AI 自动识别<strong>是什么缺陷</strong>（划痕 / 变形 / 气泡...），自动填入备注。</p>
<p><strong>使用者</strong>：操作员工 / 质检员</p>
<p><strong>操作路径</strong>：H5 → 报工页（填不良数时）→ 「<strong>📷 识别缺陷</strong>」按钮</p>
<h4>操作步骤</h4>
<ol>
<li>报工时填了「不良数 > 0」后，出现「<strong>📷 识别缺陷</strong>」按钮</li>
<li>点 → 弹出相机 → <strong>拍不良品特写</strong>（对准缺陷部位、对焦清晰）</li>
<li>等待 1~3 秒，AI 识别：<ul>
<li><strong>缺陷代码</strong>（如 <code>SCRATCH</code> 划痕）</li>
<li><strong>缺陷名称</strong>（中文）</li>
<li><strong>置信度</strong>（高 / 中 / 低）</li>
</ul></li>
<li>自动填入备注框 → 可<strong>手动补充</strong>细节（如"在左下角"）</li>
<li>提交报工</li>
</ol>
<h4>缺陷库</h4>
<ul>
<li>系统预置 <strong>30+ 常见缺陷</strong>（划痕、变形、气泡、杂质、缺口、错位...）</li>
<li>管理员可在「<strong>主数据 → 缺陷代码</strong>」<strong>自定义缺陷码</strong></li>
<li>报工后 AI 也会把新缺陷<strong>加入学习</strong>（需开启反馈学习）</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>AI 识别的缺陷会<strong>自动同步到「缺陷分析报表」</strong>，可做 TOP 10 排名</li>
<li>置信度低时建议<strong>手动选缺陷码</strong>（从下拉列表）</li>
<li><strong>多缺陷</strong>照片可重复识别（每次识别后追加到备注）</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>报表 → 缺陷分析 → 看某缺陷<strong>最近 30 天趋势</strong></li>
<li>报表 → 缺陷分析 → 「按员工分组」看哪类员工高频出某缺陷</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch11',
        title: '第十一章 智能报工建议（H5）',
        icon: 'Cellphone',
        children: [
          {
            id: 'p5-11-1',
            title: '11.1 智能推荐任务（Top 3 + 原因）',
            content: `<h3>智能报工建议</h3>
<p><strong>价值</strong>：打开 H5，<strong>AI 主动告诉你"今天该报哪个"</strong>——不用自己翻任务列表。</p>
<p><strong>使用者</strong>：操作员工</p>
<p><strong>操作路径</strong>：H5 → 主页顶部「<strong>💡 智能推荐</strong>」紫色卡片</p>
<h4>操作步骤</h4>
<ol>
<li>登录 H5 → 主页</li>
<li>顶部出现紫色「<strong>💡 智能推荐</strong>」卡片，显示 <strong>Top 3</strong> 推荐任务</li>
<li>每条推荐带<strong>推荐理由</strong>（可点 "?" 查看）：<ul>
<li>「<strong>距上次报工 2 天，剩 50 件</strong>」（最紧急）</li>
<li>「<strong>你擅长的工序</strong>」（熟练度高）</li>
<li>「<strong>新到任务，金额 ¥120</strong>」（高单价）</li>
</ul></li>
<li>点某条任务 → 直接跳到报工页</li>
<li>不感兴趣可点「<strong>换一批</strong>」 → 重新推荐</li>
</ol>
<h4>推荐算法综合因素</h4>
<table>
<tr><th>因素</th><th>权重</th><th>解释</th></tr>
<tr><td>紧急度</td><td>高</td><td>交期 / 剩余数量</td></tr>
<tr><td>熟练度</td><td>中</td><td>历史报工数据</td></tr>
<tr><td>金额</td><td>中</td><td>工价 × 预计件数</td></tr>
<tr><td>时段</td><td>低</td><td>适合当前时间的工序</td></tr>
</table>
<h4>注意事项</h4>
<ul>
<li>推荐<strong>不替代正常任务列表</strong>；不想用推荐可点「<strong>查看全部任务</strong>」</li>
<li>报工完成后，<strong>推荐自动刷新</strong>（下次进入主页时）</li>
<li>管理员可关闭推荐：「<strong>系统 → AI 设置</strong>」</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>「我的 → 推荐历史」可看最近 30 天的推荐 + 你点了哪些</li>
<li>AI 助手对话可反馈“我更想看高单价的”，AI 会<strong>记住你的偏好</strong></li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch12',
        title: '第十二章 换班交接摘要（H5）',
        icon: 'Cellphone',
        children: [
          {
            id: 'p5-12-1',
            title: '12.1 生成换班摘要 + 示例',
            content: `<h3>换班交接摘要</h3>
<p><strong>价值</strong>：交接班时不用口述半天，<strong>AI 自动生成摘要</strong>：“本班做了 45 单 120 件，发现 3 次模具预警，1 个工单延期风险”。</p>
<p><strong>使用者</strong>：班组长 / 车间主任</p>
<p><strong>操作路径</strong>：H5 → 主页 → 「<strong>📋 交接摘要</strong>」卡片 → 「<strong>生成摘要</strong>」</p>
<h4>操作步骤</h4>
<ol>
<li>主页找到「<strong>📋 交接摘要</strong>」卡片（首页中部偏下）</li>
<li>确认<strong>班次起止时间</strong>（默认 8 小时前到现在）</li>
<li>点「<strong>生成摘要</strong>」按钮</li>
<li>AI 在 5~10 秒内生成结构化摘要：<ul>
<li><strong>产量</strong>：本班次报工单数 / 件数 / 工时</li>
<li><strong>质量</strong>：合格数 / 不良数 / 良率</li>
<li><strong>订单</strong>：完成 / 在制 / 延期预警</li>
<li><strong>异常</strong>：模具预警 / 设备故障 / 物料不足</li>
<li><strong>建议</strong>：下个班次重点关注什么</li>
</ul></li>
<li>摘要可：<ul>
<li><strong>复制</strong>到剪贴板（发群 / 邮件）</li>
<li><strong>推送</strong>到飞书 / 钉钉群</li>
<li><strong>保存</strong>为 PDF 存档</li>
</ul></li>
</ol>
<h4>摘要内容示例</h4>
<blockquote>
<p><strong>本班次（2026-06-15 08:00 ~ 16:00）摘要</strong></p>
<ul>
<li>报工：<strong>45 单 / 120 件 / 8.5 工时</strong>（达成率 95%）</li>
<li>良率：<strong>96.5%</strong>（较上日 ↑1.2%）</li>
<li>完成订单：<strong>3 单</strong>（D-20260612001, D-20260613005, D-20260614002）</li>
<li>延期预警：<strong>1 单</strong>（D-20260611008 交期 6/16，需下个班次加急）</li>
<li>模具预警：<strong>2 次</strong>（MOLD-005 寿命 92%, MOLD-007 寿命 85%）</li>
<li>异常报警：无</li>
<li><strong>建议</strong>：下个班次优先冲 MOLD-005 的 K005 工单，避免交期逾期。</li>
</ul>
</blockquote>
<h4>注意事项</h4>
<ul>
<li>摘要生成<strong>需要联网</strong>（调用 AI 接口）</li>
<li>摘要<strong>不是流水账</strong>，是<strong>重点 + 建议</strong>，适合直接发班组长群</li>
<li>同一班次可<strong>多次生成</strong>，以最新一次为准</li>
</ul>
<h4>相关操作</h4>
<ul>
<li>可在「<strong>系统 → AI 设置</strong>」开启「<strong>交接班前 30 分钟自动生成</strong>」</li>
<li>每天 20:00 自动生成日报并推送管理群（详见 in-app help ch12.5）</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch13',
        title: '第十三章 AI 员工对话（H5 + IM）',
        icon: 'ChatDotSquare',
        children: [
          {
            id: 'p5-13-1',
            title: '13.1 H5 端使用 AI 员工',
            content: `<h3>H5 端使用 AI 员工</h3>
<p><strong>价值</strong>：不用找班组长或管理员，直接问 AI 就能查到订单进度、生产计划、任务完成情况等信息。</p>
<p><strong>使用者</strong>：所有员工</p>
<p><strong>操作路径</strong>：H5 → 底部导航「AI 员工」</p>
<h4>操作步骤</h4>
<ol>
<li>登录 H5 手机端</li>
<li>底部导航栏找到「<strong>AI 员工</strong>」入口（机器人图标）</li>
<li>进入后看到可用的 AI 员工列表，点击一个开始对话</li>
<li>在输入框输入问题，例如：<ul>
<li>"订单 ORD-20260601 现在做到哪了？"</li>
<li>"今天有哪些生产计划？"</li>
<li>"设备 #003 的状态怎么样？"</li>
<li>"库存还有多少钢材？"</li>
</ul></li>
<li>AI 会调用系统工具查询数据并回复</li>
</ol>
<h4>对话功能</h4>
<ul>
<li><strong>新建对话</strong>：点击右上角菜单 → 「新对话」，清空当前对话历史</li>
<li><strong>删除对话</strong>：点击右上角菜单 → 「删除对话」，删除当前对话记录</li>
<li><strong>工具调用提示</strong>：当 AI 使用工具查询数据时，消息下方会显示 "Used: query_order_status" 等提示</li>
</ul>
<h4>注意事项</h4>
<ul>
<li>AI 员工只能查询数据，不能修改任何业务数据</li>
<li>如果 AI 回答不准确，请以系统实际数据为准</li>
<li>AI 员工需要管理员先在后台创建并启用</li>
</ul>`
          },
          {
            id: 'p5-13-2',
            title: '13.2 在飞书/企微/钉钉中使用 AI 员工',
            content: `<h3>在 IM 中使用 AI 员工</h3>
<p><strong>价值</strong>：不用打开 H5，直接在飞书/企微/钉钉里给机器人发消息就能查询生产数据。</p>
<p><strong>使用者</strong>：已绑定 IM 账号的员工</p>
<h4>前置条件</h4>
<ol>
<li>管理员已在后台配置好飞书/企微/钉钉消息推送</li>
<li>管理员已创建 AI 员工并勾选了对应渠道</li>
<li>员工已在 H5「个人中心」绑定了 IM 账号</li>
</ol>
<h4>使用方式</h4>
<ol>
<li>打开飞书/企微/钉钉</li>
<li>找到 辰科MES 机器人应用</li>
<li>直接发送消息，例如：<ul>
<li>"查一下订单 D-20260601 的进度"</li>
<li>"今天我的任务有哪些？"</li>
<li>"设备磨床的运行状态"</li>
</ul></li>
<li>机器人会自动回复查询结果</li>
</ol>
<h4>注意事项</h4>
<ul>
<li>机器人回复的是 AI 生成的内容，重要数据请以系统为准</li>
<li>如果机器人没有回复，联系管理员检查 AI 员工配置</li>
<li>支持连续对话，AI 会记住上下文</li>
</ul>`
          },
        ]
      },
      {
        id: 'p5-ch15',
        title: '附录 常见问题（Q&A）',
        icon: 'QuestionFilled',
        children: [
          {
            id: 'p5-15-1',
            title: 'Q1~Q10 常见问题解答',
            content: `<h3>常见问题</h3>
<h4>Q1：报表导出任务一直"处理中"怎么办？</h4>
<ol>
<li>刷新「<strong>导出中心</strong>」页面看最新状态</li>
<li>等 30 分钟仍“处理中”：联系系统管理员查 Celery worker 是否在跑</li>
<li>提供任务 ID 让管理员查日志：<code>/tmp/lightmes-celery/worker.log</code></li>
</ol>
<h4>Q2：Lodop 打印没反应？</h4>
<ol>
<li>确认浏览器是 <strong>Chrome / Edge / 360</strong></li>
<li>检查浏览器是否拦截 Lodop 插件</li>
<li>重新安装 Lodop 控件，重启浏览器</li>
<li>仍失败改用 <strong>ZPL 网络打印</strong></li>
</ol>
<h4>Q3：模具寿命预警频繁推送？</h4>
<ul>
<li>阈值设置过低（默认 80%）：调到 90%</li>
<li>某些模具设计保守：在预警记录里「<strong>标记误报</strong>」</li>
</ul>
<h4>Q4：SPC 控制图全红，但 Cpk 还 1.5？</h4>
<ul>
<li>控制图异常 ≠ 过程能力不足。最近几批设备有调整（如换刀）</li>
<li>检查 4M 变化（人 / 机 / 料 / 法）</li>
<li>控制图反映“现在”，Cpk 反映“过去”</li>
</ul>
<h4>Q5：审批流改完之后历史报工怎么办？</h4>
<ul>
<li><strong>不影响</strong>，在途审批仍按老流程继续</li>
<li>新提交才走新流程</li>
</ul>
<h4>Q6：PWA 离线队列一直提交失败？</h4>
<ul>
<li>90% 是“任务已被别人报完”：进入报工详情看状态</li>
<li>其他：网络问题、任务已被作废</li>
<li>「<strong>重试</strong>」3 次仍失败 → 「<strong>删除</strong>」该条并联系班组长</li>
</ul>
<h4>Q7：AI 数零件数和实际对不上？</h4>
<ul>
<li>检查照片：重叠 / 反光 / 角度异常</li>
<li>拍照时<strong>铺平 / 散开 / 自然光</strong>最佳</li>
<li>AI 只能数“照片里能看到的”，以你<strong>实际合格数</strong>为准</li>
</ul>
<h4>Q8：语音报工解析错了（"一"被识别成"七"）？</h4>
<ul>
<li>改用<strong>标准数字读法</strong>："一 → 幺" / "二 → 两" / "七 → 拐"</li>
<li>解析后<strong>人工核对</strong>（必做）</li>
<li>反复错误的字段可<strong>手填</strong>覆盖</li>
</ul>
<h4>Q9：AI 自动审核把我的报工"误判"高风险？</h4>
<ul>
<li>高风险 ≠ 错误，是更谨慎。审核员会重点看</li>
<li>检查照片是否清晰、是否按时报工、有无不良率波动</li>
<li>「我的 → AI 审核记录」看每次的 6 维度雷达图</li>
</ul>
<h4>Q10：换班摘要生成失败 / 内容不准？</h4>
<ul>
<li>联网问题：换班摘要需联网调 AI</li>
<li>内容不准：摘要基于最近 N 小时报工数据，确认你的报工已提交</li>
<li>重要决策请结合系统数据 + 现场观察</li>
</ul>`
          },
        ]
      },
    ]
  },
]

export function getGuideData(): GuideSection[] {
  return guideData
}

export function flattenSections(sections: GuideSection[]): GuideSection[] {
  const result: GuideSection[] = []
  function walk(list: GuideSection[]) {
    for (const s of list) {
      if (s.content) {
        result.push(s)
      }
      if (s.children) {
        walk(s.children)
      }
    }
  }
  walk(sections)
  return result
}

export function findSectionById(id: string): GuideSection | undefined {
  function walk(list: GuideSection[]): GuideSection | undefined {
    for (const s of list) {
      if (s.id === id) return s
      if (s.children) {
        const found = walk(s.children)
        if (found) return found
      }
    }
    return undefined
  }
  return walk(guideData)
}

export function getBreadcrumb(id: string): GuideSection[] {
  const path: GuideSection[] = []
  function walk(list: GuideSection[]): boolean {
    for (const s of list) {
      path.push(s)
      if (s.id === id) return true
      if (s.children && walk(s.children)) return true
      path.pop()
    }
    return false
  }
  walk(guideData)
  return path
}

export default guideData
