<!--
  S3 可视化审批流设计器 V1
  steps 为唯一数据源；bpmn-js 仅做可视化渲染（线性主干，条件/会签/或签直接标注在节点）。
  条件分支语义映射引擎 condition_rule：满足→走本步，不满足→跳过本步。
-->
<template>
  <div class="flow-builder">
    <div class="flow-builder__top">
      <div class="flow-builder__title">
        <span class="font-semibold">{{ flow?.name || '审批流设计' }}</span>
        <el-tag v-if="flow" size="small">{{ BIZ_TYPES[flow.biz_type] || flow.biz_type }}</el-tag>
      </div>
      <div class="flex items-center gap-2">
        <el-button @click="emit('close')">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">{{ saving ? '保存中…' : '保存审批流' }}</el-button>
      </div>
    </div>

    <div class="flow-builder__body">
      <div class="flow-builder__canvas-wrap">
        <div ref="canvasRef" class="flow-builder__canvas" />
        <div v-if="!steps.length" class="flow-builder__empty">暂无审批步骤</div>
      </div>

      <div class="flow-builder__side">
        <div class="side-head">
          <span class="font-semibold">审批步骤</span>
          <el-button size="small" type="primary" plain @click="addStep(-1)">+ 添加步骤</el-button>
        </div>

        <div class="side-list">
          <div
            v-for="(s, i) in steps"
            :key="i"
            class="step-item"
            :class="{ 'step-item--on': i === selected }"
            @click="selected = i"
          >
            <div class="step-item__idx">{{ i + 1 }}</div>
            <div class="step-item__main">
              <div class="step-item__name">{{ stepName(s) }}</div>
              <div class="step-item__meta">
                <el-tag size="small" :type="signTagType(s.sign_mode)">{{ SIGN_MODE_LABELS[s.sign_mode] }}</el-tag>
                <el-tag v-if="s.condition_rule" size="small" type="warning">条件：{{ conditionText(s.condition_rule) }}</el-tag>
              </div>
            </div>
            <div class="step-item__ops">
              <el-button size="small" circle :disabled="i === 0" @click.stop="moveStep(i, -1)">↑</el-button>
              <el-button size="small" circle :disabled="i === steps.length - 1" @click.stop="moveStep(i, 1)">↓</el-button>
              <el-button size="small" circle type="danger" plain :disabled="steps.length <= 1" @click.stop="removeStep(i)">×</el-button>
            </div>
          </div>
        </div>

        <el-divider class="!my-3">节点配置</el-divider>
        <div v-if="steps[selected]" class="node-config">
          <el-form label-position="top" size="small">
            <el-form-item label="步骤名称">
              <el-input v-model="steps[selected].label" placeholder="如：车间主任审核" />
            </el-form-item>
            <el-form-item label="审批角色">
              <el-select v-model="steps[selected].approver_role" style="width:100%">
                <el-option v-for="(l, k) in ROLE_LABELS" :key="k" :label="l" :value="k" />
              </el-select>
            </el-form-item>
            <el-form-item label="审批方式">
              <el-select v-model="steps[selected].sign_mode" style="width:100%">
                <el-option v-for="(l, k) in SIGN_MODE_LABELS" :key="k" :label="l" :value="k" />
              </el-select>
            </el-form-item>
            <el-form-item label="条件分支（满足则必须走本步，否则跳过）">
              <el-switch v-model="condOn" />
            </el-form-item>
            <template v-if="condOn">
              <div class="grid grid-cols-2 gap-2">
                <el-form-item label="字段">
                  <el-input v-model="condRule.field" placeholder="如 amount / quantity" />
                </el-form-item>
                <el-form-item label="运算符">
                  <el-select v-model="condRule.op" style="width:100%">
                    <el-option v-for="op in ['>', '>=', '<', '<=', '==', '!=', 'contains']" :key="op" :label="op" :value="op" />
                  </el-select>
                </el-form-item>
              </div>
              <el-form-item label="对比值">
                <el-input v-model="condValue" placeholder="如 10000" />
              </el-form-item>
            </template>
            <el-form-item label="必审">
              <el-checkbox v-model="steps[selected].is_required">必须由本人审批通过才算过</el-checkbox>
            </el-form-item>
            <el-form-item label="可跳过">
              <el-checkbox v-model="steps[selected].can_skip">允许跳过</el-checkbox>
            </el-form-item>
          </el-form>
        </div>
        <el-empty v-else description="点击左侧步骤进行配置" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, reactive, ref, watch } from 'vue'
import BpmnModeler from 'bpmn-js/lib/Modeler'
import 'bpmn-js/dist/assets/diagram-js.css'
import 'bpmn-js/dist/assets/bpmn-js.css'
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn.css'
import { ElMessage } from 'element-plus'
import {
  approvalApi,
  type ApprovalFlowOut,
  type ApprovalStep,
  type ConditionRule,
  BIZ_TYPES,
  ROLE_LABELS,
  SIGN_MODE_LABELS,
  conditionText,
} from '@/api/approval'

const props = defineProps<{ flow: ApprovalFlowOut | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'saved'): void }>()

const canvasRef = ref<HTMLElement>()
let modeler: BpmnModeler | null = null

type EditableStep = {
  approver_role: string
  is_required: boolean
  can_skip: boolean
  label: string
  sign_mode: ApprovalStep['sign_mode']
  condition_rule: ApprovalStep['condition_rule']
}

const steps = ref<EditableStep[]>([])
const selected = ref(-1)
const saving = ref(false)

const condOn = ref(false)
const condRule = reactive({ field: '', op: '>' as string })
const condValue = ref('')

function stepName(s: EditableStep): string {
  const r = ROLE_LABELS[s.approver_role] || s.approver_role
  return `${s.label || r}（${r}）`
}
function signTagType(s: EditableStep['sign_mode']): 'primary' | 'success' | 'warning' | 'info' {
  if (s === 'and') return 'success'
  if (s === 'or') return 'warning'
  return 'primary'
}

function watchSelected() {
  const s = steps.value[selected.value]
  if (!s) { condOn.value = false; return }
  if (s.condition_rule) {
    condOn.value = true
    condRule.field = s.condition_rule.field
    condRule.op = s.condition_rule.op
    condValue.value = String(Array.isArray(s.condition_rule.value) ? s.condition_rule.value.join(',') : s.condition_rule.value)
  } else {
    condOn.value = false
    condRule.field = s.condition_rule?.field || 'amount'
    condRule.op = '>'
    condValue.value = ''
  }
}

watch(condOn, (v) => {
  const s = steps.value[selected.value]
  if (!s) return
  if (v) {
    const field = condRule.field || 'amount'
    s.condition_rule = { field: condRule.field || 'amount', op: condRule.op as ConditionRule['op'], value: condValue.value || 0, else_role: null }
  } else {
    s.condition_rule = null
  }
})

// ---- steps 编辑 ----
function addStep(after: number) {
  const step: EditableStep = { approver_role: 'leader', is_required: true, can_skip: false, label: '', sign_mode: 'single', condition_rule: null }
  const idx = after < 0 ? steps.value.length : after + 1
  steps.value.splice(idx, 0, step)
  selected.value = idx
  render()
}
function removeStep(i: number) {
  steps.value.splice(i, 1)
  if (selected.value >= steps.value.length) selected.value = steps.value.length - 1
  render()
}
function moveStep(i: number, dir: number) {
  const j = i + dir
  if (j < 0 || j >= steps.value.length) return
  const arr = steps.value
  ;[arr[i], arr[j]] = [arr[j], arr[i]]
  selected.value = j
  render()
}

// ---- bpmn 渲染（线性主干；步骤即节点，会签/或签/条件标注其内）----
const XML_HEAD = `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
  id="defs_1" targetNamespace="http://cenkor/approval">`

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/\n/g, '&#10;')
}

function buildXml(list: EditableStep[]): string {
  const nodes: string[] = []
  const edges: string[] = []
  const shapes: string[] = []
  const dEdges: string[] = []
  let y = 110

  nodes.push(`<bpmn:startEvent id="start" name=""/>`)
  shapes.push(`<bpmndi:BPMNShape id="start_vi" bpmnElement="start"><dc:Bounds x="200" y="${y}" width="36" height="36"/></bpmndi:BPMNShape>`)
  dEdges.push('')

  let prev = 'start'
  y += 80

  list.forEach((s, i) => {
    const id = `step_${i}`
    const role = ROLE_LABELS[s.approver_role] || s.approver_role
    let name = s.label ? `${s.label} · ${role}` : role
    if (s.sign_mode && s.sign_mode !== 'single') name += `\n【${SIGN_MODE_LABELS[s.sign_mode]}】`
    if (s.condition_rule) name = `⛳ ${conditionText(s.condition_rule)}\n${name}`

    const yc = y
    nodes.push(`<bpmn:userTask id="${id}" name="${esc(name)}"/>`)
    shapes.push(`<bpmndi:BPMNShape id="${id}_vi" bpmnElement="${id}"><dc:Bounds x="150" y="${yc}" width="185" height="80"/><bpmndi:BPMNLabel><dc:Bounds x="150" y="${yc}" width="185" height="80"/></bpmndi:BPMNLabel></bpmndi:BPMNShape>`)
    edges.push(`<bpmn:sequenceFlow id="${prev}_${id}" sourceRef="${prev}" targetRef="${id}"/>`)
    dEdges.push(`<bpmndi:BPMNEdge id="${prev}_${id}_di" bpmnElement="${prev}_${id}"><di:waypoint x="218" y="${yc - 34}"/><di:waypoint x="218" y="${yc - 4}"/></bpmndi:BPMNEdge>`)
    prev = id
    y += 120
  })

  nodes.push(`<bpmn:endEvent id="end" name=""/>`)
  shapes.push(`<bpmndi:BPMNShape id="end_vi" bpmnElement="end"><dc:Bounds x="200" y="${y}" width="36" height="36"/></bpmndi:BPMNShape>`)
  edges.push(`<bpmn:sequenceFlow id="${prev}_end" sourceRef="${prev}" targetRef="end"/>`)
  dEdges.push(`<bpmndi:BPMNEdge id="${prev}_end_di" bpmnElement="${prev}_end"><di:waypoint x="218" y="${y - 30}"/><di:waypoint x="218" y="${y - 6}"/></bpmndi:BPMNEdge>`)

  return `${XML_HEAD}
  <bpmn:process id="Process_1" isExecutable="false">
  ${nodes.join('\n  ')}
  ${edges.join('\n  ')}
  </bpmn:process>
  <bpmndi:BPMNDiagram id="diag_1">
    <bpmndi:BPMNPlane id="plane_1" bpmnElement="Process_1">
    ${shapes.join('\n    ')}
    ${dEdges.join('\n    ')}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`
}

async function render() {
  if (!modeler) return
  try {
    await nextTick()
    await modeler.importXML(buildXml(steps.value))
    ;(modeler.get('canvas') as any).zoom('fit-viewport')
  } catch (e) {
    console.error('[FlowBuilder] render failed', e)
  }
}

function initModeler() {
  if (!canvasRef.value) return
  modeler = new BpmnModeler({ container: canvasRef.value })
  modeler.on('selection.changed', (e: any) => {
    const el = e.newSelection && e.newSelection[0]
    if (!el) return
    const id: string = el.id || ''
    if (id.startsWith('step_')) {
      const i = Number(id.replace('step_', ''))
      if (i >= 0 && i < steps.value.length) selected.value = i
    }
  })
}

// ---- 保存 ----
function save() {
  if (!props.flow) return
  if (!steps.value.length) { ElMessage.warning('至少需要一个审批步骤'); return }
  saving.value = true
  const payload = steps.value.map((s, i) => ({
    approver_role: s.approver_role,
    is_required: s.is_required,
    can_skip: s.can_skip,
    label: s.label || '',
    step_order: i + 1,
    sign_mode: s.sign_mode,
    condition_rule: s.condition_rule,
    assignee_ids: null,
  }))
  approvalApi.setSteps(props.flow.id, payload as never)
    .then(() => { ElMessage.success('审批流已保存'); emit('saved') })
    .finally(() => { saving.value = false })
}

onMounted(async () => {
  initModeler()
  steps.value = (props.flow?.steps || []).map((s) => ({
    approver_role: s.approver_role,
    is_required: s.is_required,
    can_skip: s.can_skip,
    label: s.label || '',
    sign_mode: s.sign_mode || 'single',
    condition_rule: s.condition_rule || null,
  }))
  if (!steps.value.length) steps.value = [{ approver_role: 'leader', is_required: true, can_skip: false, label: '', sign_mode: 'single', condition_rule: null }]
  selected.value = 0
  await nextTick()
  await render()
})
</script>

<style scoped>
.flow-builder { display: flex; flex-direction: column; height: 100%; }
.flow-builder__top { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; border-bottom: 1px solid var(--el-border-color-light); }
.flow-builder__title { display: flex; align-items: center; gap: 10px; font-size: 16px; }
.flow-builder__body { flex: 1; display: flex; min-height: 0; }
.flow-builder__canvas-wrap { flex: 1; position: relative; min-width: 0; background: #fafafa; }
.flow-builder__canvas { width: 100%; height: 100%; }
.flow-builder__empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--el-text-color-secondary); pointer-events: none; }
.flow-builder__side { width: 350px; border-left: 1px solid var(--el-border-color-light); padding: 14px; overflow-y: auto; }
.side-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.side-list { display: flex; flex-direction: column; gap: 8px; }
.step-item { display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px; border: 1px solid var(--el-border-color-light); border-radius: 8px; cursor: pointer; }
.step-item--on { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.step-item__idx { width: 22px; height: 22px; flex-shrink: 0; border-radius: 50%; background: var(--el-color-primary); color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; }
.step-item__main { flex: 1; min-width: 0; }
.step-item__name { font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.step-item__meta { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.step-item__ops { display: flex; flex-direction: column; gap: 4px; }
.node-config { padding-bottom: 8px; }
</style>