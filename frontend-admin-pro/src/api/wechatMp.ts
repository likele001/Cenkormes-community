import { http } from '@/utils/http'

export type WechatMpRule = {
  enabled: boolean
  targets?: string[]
  template_id: string
  page: string
}

export type WechatMpSettings = {
  enabled: boolean
  appid: string
  app_secret: string
  app_secret_masked: string
  miniprogram_state: 'formal' | 'trial' | 'developer'
  rules: Record<string, WechatMpRule>
  quiet_hours: { enabled: boolean; start: string; end: string }
  default_page: string
  keyword_hints: Record<string, string[]>
}

export type WechatMpPushLog = {
  id: number
  event_code: string
  target_user_id: number | null
  openid: string
  template_id: string
  page: string | null
  title: string
  content: string
  status: string
  error_msg: string | null
  message_id: string | null
  retry_count: number
  created_at: string
  sent_at: string | null
}

export const wechatMpApi = {
  getSettings() {
    return http.request<WechatMpSettings>({ url: '/admin/system/wechat-mp', method: 'GET' })
  },
  saveSettings(data: Partial<WechatMpSettings> & { app_secret?: string }) {
    return http.request<WechatMpSettings>({ url: '/admin/system/wechat-mp', method: 'PUT', data })
  },
  testConnection() {
    return http.request<{ ok: boolean; token_preview?: string }>({
      url: '/admin/system/wechat-mp/test-connection',
      method: 'POST',
    })
  },
  testSend(data: { openid: string; template_id: string; title?: string; content?: string; page?: string }) {
    return http.request<{ ok: boolean; message_id?: string; raw?: any }>({
      url: '/admin/system/wechat-mp/test-send',
      method: 'POST',
      data,
    })
  },
  listPushLogs(params: { event_code?: string; status?: string; offset?: number; limit?: number } = {}) {
    return http.request<{ items: WechatMpPushLog[] }>({
      url: '/admin/system/wechat-mp/push-logs',
      method: 'GET',
      params,
    })
  },
  retryPushLog(logId: number) {
    return http.request<{ id: number; status: string; retry_count: number }>({
      url: `/admin/system/wechat-mp/push-logs/${logId}/retry`,
      method: 'POST',
    })
  },
}

// 事件名 → 中文标签（用于页面展示）
export const WECHAT_MP_EVENT_LABELS: Record<string, string> = {
  'report.submitted': '报工已提交',
  'report.leader_approved': '班组长已审',
  'report.qc_approved': 'QC 已审通过',
  'report.rejected': '审核拒签',
  'salary.slip_remind': '工资单提醒',
  'salary.slip_reset': '工资单重置',
  'salary.slip_rejected': '工资单拒签',
  'dispatch.assigned': '派工通知',
  'order.customer_submitted': '客户订单',
  'alert': '系统告警',
  'plan.automation_failed': '排产失败',
  'brief.daily': '每日简报',
}
