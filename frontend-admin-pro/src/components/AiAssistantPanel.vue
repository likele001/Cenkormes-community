<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="title"
    width="560px"
    class="ai-assistant-dialog"
    destroy-on-close
    append-to-body
  >
    <div class="assistant-body">
      <div class="assistant-messages" ref="msgRef">
        <div v-if="messages.length === 0" class="assistant-empty">
          <div class="assistant-empty-title">👋 我是你的 AI 业务助理</div>
          <div class="assistant-empty-sub">直接问我业务问题，或点击下方示例一键查询</div>
          <div class="assistant-suggests">
            <el-button
              v-for="(q, i) in suggests"
              :key="i"
              size="small"
              plain
              :disabled="sending"
              @click="sendQuick(q)"
            >
              {{ q }}
            </el-button>
          </div>
        </div>

        <div
          v-for="(m, idx) in messages"
          :key="idx"
          class="assistant-msg"
          :class="m.role"
        >
          <div v-if="m.role === 'user'" class="bubble bubble-user">{{ m.content }}</div>

          <div v-else-if="m.role === 'ai'" class="bubble bubble-ai">
            <div class="whitespace-pre-wrap" v-html="renderMd(m.content)"></div>
            <div v-if="m.tool" class="assistant-tool-call">🔧 调用了工具 <b>{{ m.tool }}</b></div>
          </div>

          <div v-else-if="m.role === 'tool'" class="bubble bubble-tool">
            <div class="tool-title">📊 查询结果 · {{ m.name }}</div>
            <div class="tool-body"><pre>{{ formatToolResult(m.result) }}</pre></div>
          </div>

          <div v-else-if="m.role === 'system'" class="bubble bubble-system">
            <div class="tool-title">✅ {{ m.actName }} 已执行</div>
            <div class="tool-body"><pre>{{ formatToolResult(m.result) }}</pre></div>
          </div>

          <div v-else-if="m.role === 'error'" class="bubble bubble-error">
            ❌ {{ m.content }}
          </div>
        </div>

        <div v-if="sending && !composingAi" class="assistant-thinking">
          <el-icon class="is-loading"><Loading /></el-icon> 思考中...
        </div>
      </div>

      <div class="assistant-input">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          resize="none"
          :placeholder="placeholders[sending ? 1 : 0]"
          :disabled="sending"
          @keydown.enter.exact.prevent="send"
        />
        <el-button type="primary" :loading="sending" :disabled="!input.trim()" @click="send">
          发送
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { assistantApi, type AssistantConfirmation, type AssistantTool } from '@/api/assistant'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()

type Msg =
  | { role: 'user'; content: string }
  | { role: 'ai'; content: string; tool?: string }
  | { role: 'tool'; name: string; result: unknown }
  | { role: 'system'; actName: string; result: unknown }
  | { role: 'error'; content: string }
  | { role: 'composing'; content: string }

const messages = ref<Msg[]>([])
const input = ref('')
const sending = ref(false)
const conversationId = ref<number | undefined>(undefined)
const composingAi = computed(() => messages.value.length > 0 && messages.value[messages.value.length - 1].role === 'composing')
const msgRef = ref<HTMLDivElement>()
const tools = ref<AssistantTool[]>([])

const suggests = [
  '有哪些客户？',
  '查一下最近的销售订单',
  '库存情况怎么样？',
  '生产概况如何？',
]
const placeholders = ['问我业务问题…（客户／订单／库存／生产）', '正在回复中…']

const title = computed(() =>
  tools.value.length ? `AI 业务助理 · ${tools.value.length} 个工具可用` : 'AI 业务助理'
)

async function loadTools() {
  try {
    tools.value = await assistantApi.tools()
  } catch {
    tools.value = []
  }
}

function renderMd(text: string): string {
  let t = (text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  t = t.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
  t = t.replace(/\n/g, '<br>')
  return t
}

function formatToolResult(result: unknown): string {
  if (result == null) return ''
  if (typeof result === 'string') return result
  if (Array.isArray(result)) return JSON.stringify(result, null, 2)
  if (typeof result === 'object') {
    const o = result as Record<string, unknown>
    if (Array.isArray(o.items)) {
      const head = o.items.slice(0, 8)
      const lines = head.map((it) => {
        if (it && typeof it === 'object') {
          const r = it as Record<string, unknown>
          return `${r.code ?? ''} ${r.name ?? r.product_name ?? ''}`.trim() || JSON.stringify(it)
        }
        return JSON.stringify(it)
      })
      const more = head.length < (o as { items: unknown[] }).items.length ? `\n…共 ${(o as { items: unknown[] }).items.length} 条` : ''
      return lines.join('\n') + more
    }
    return JSON.stringify(result, null, 2)
  }
  return String(result)
}

async function sendQuick(q: string) {
  input.value = q
  await send()
}

function scrollBottom() {
  nextTick(() => {
    if (msgRef.value) msgRef.value.scrollTop = msgRef.value.scrollHeight
  })
}

async function approveAction(conf: AssistantConfirmation): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `<div style="line-height:1.7">${conf.confirm_message || `确认执行 <b>${conf.name}</b>？`}<br/><pre style="margin-top:8px;font-size:12px;color:#666;white-space:pre-wrap">${JSON.stringify(
        conf.args || {},
        null,
        2,
      )}</pre></div>`,
      '二次确认',
      {
        confirmButtonText: '确认执行',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
      },
    )
  } catch {
    return // 用户取消
  }
  try {
    const res = await assistantApi.act(conf.name, conf.args || {}, conversationId.value)
    messages.value.push({ role: 'system', actName: conf.name, result: (res as { result: unknown }).result })
    ElMessage.success(`已执行 ${conf.name}`)
    scrollBottom()
  } catch (e: any) {
    ElMessage.error('执行失败：' + (e?.message || '未知错误'))
  }
}

async function send() {
  const text = input.value.trim()
  if (!text || sending.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  messages.value.push({ role: 'composing', content: '' })
  sending.value = true
  scrollBottom()
  try {
    await assistantApi.chatSse(text, conversationId.value, (ev) => {
      if (ev.type === 'delta') {
        const last = messages.value[messages.value.length - 1]
        if (last && last.role === 'composing') last.content += ev.text
      } else if (ev.type === 'tool_result') {
        messages.value.push({ role: 'tool', name: ev.name, result: ev.result })
        scrollBottom()
      } else if (ev.type === 'confirmation') {
        void approveAction(ev.data)
      } else if (ev.type === 'done') {
        if (ev.conversation_id) conversationId.value = ev.conversation_id
        const last = messages.value[messages.value.length - 1]
        if (last && last.role === 'composing' && last.content.trim() === '') {
          messages.value.pop() // 无文本回复时移除占位
        }
      } else if (ev.type === 'error') {
        messages.value.pop()
        messages.value.push({ role: 'error', content: ev.message })
      }
    })
  } catch (e: any) {
    messages.value.pop()
    messages.value.push({ role: 'error', content: e?.message || '调用失败' })
  } finally {
    sending.value = false
    scrollBottom()
  }
}

watch(
  () => props.modelValue,
  (v) => {
    if (v) {
      void loadTools()
      conversationId.value = undefined
      messages.value = []
    }
  },
)
</script>

<style scoped>
.assistant-body { display: flex; flex-direction: column; height: 460px; }
.assistant-messages { flex: 1; overflow-y: auto; padding: 4px 2px; display: flex; flex-direction: column; gap: 10px; }
.assistant-empty { text-align: center; padding: 40px 12px; color: #888; }
.assistant-empty-title { font-size: 15px; font-weight: 600; color: #333; }
.assistant-empty-sub { font-size: 12px; margin: 6px 0 16px; }
.assistant-suggests { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.assistant-msg { display: flex; }
.assistant-msg.user { justify-content: flex-end; }
.assistant-msg.tool, .assistant-msg.system { justify-content: flex-start; }
.bubble { max-width: 88%; border-radius: 10px; padding: 9px 12px; font-size: 13px; line-height: 1.6; }
.bubble-user { background: #409eff; color: #fff; }
.bubble-ai { background: #f4f6f8; color: #333; }
.bubble-error { background: #fdecec; color: #c0392b; }
.bubble-tool, .bubble-system { background: #eef6ff; border: 1px solid #d6e8ff; color: #1f5aa8; }
.assistant-tool-call { margin-top: 8px; font-size: 12px; color: #8a6d3b; }
.tool-title { font-weight: 600; margin-bottom: 4px; }
.tool-body pre { margin: 0; font-size: 12px; color: #334; white-space: pre-wrap; word-break: break-all; max-height: 160px; overflow-y: auto; }
.assistant-thinking { display: flex; align-items: center; gap: 6px; color: #999; font-size: 12px; padding: 4px 2px; }
.assistant-input { display: flex; gap: 8px; margin-top: 12px; align-items: flex-end; }
.assistant-input .el-textarea__inner { font-size: 13px; }
</style>