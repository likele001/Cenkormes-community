import { http } from '@/utils/http'
import type { ListResp } from '@/types/api'

const AI_TIMEOUT_MS = 120_000

export type AutomationOnOrderConfirm = {
  create_plan: boolean
  start_offset_days: number
  run_pipeline_after_create: boolean
}

export type AutomationOnPlanSaved = {
  run_schedule: boolean
  engine: string
  auto_release: boolean
  auto_dispatch: boolean
  allow_shortage: boolean
}

export type AutomationAudit = {
  prescreen_on_submit: boolean
  auto_leader_approve: boolean
  auto_qc_approve: boolean
  require_employee_photo: boolean
  vision_min_score: number
  block_if_prior_reject: boolean
}

export type AutomationBriefing = {
  daily_enabled: boolean
  daily_hour: number
  mode: 'rule' | 'llm'
}

export type AutomationAlerts = {
  notify_on_scan: boolean
  create_todo_on_critical: boolean
}

export type AutomationSettings = {
  enabled: boolean
  on_order_confirm: AutomationOnOrderConfirm
  on_plan_saved: AutomationOnPlanSaved
  audit: AutomationAudit
  briefing: AutomationBriefing
  alerts: AutomationAlerts
}

export type AutomationLogOut = {
  id: number
  trigger: string
  action: string
  biz_type: string | null
  biz_id: number | null
  status: string
  message: string | null
  detail_json: string | null
  created_by: number | null
  created_at: string
}

export type AutomationDryRunIn = {
  order_id?: number
  plan_id?: number
  allow_shortage?: boolean
}

export type AutomationPrecheckCheck = {
  level: string
  message: string
}

export type AutomationDryRunOut = {
  ok: boolean
  checks: AutomationPrecheckCheck[]
  readiness?: unknown
  plan_status?: string
}

export const automationApi = {
  getAutomationSettings() {
    return http.request<AutomationSettings>({ url: '/admin/automation/settings', method: 'GET' })
  },
  saveAutomationSettings(data: Partial<AutomationSettings>) {
    return http.request<AutomationSettings>({ url: '/admin/automation/settings', method: 'PUT', data })
  },
  listAutomationLogs(params?: {
    trigger?: string
    status?: string
    biz_type?: string
    biz_id?: number
    offset?: number
    limit?: number
  }) {
    return http.request<ListResp<AutomationLogOut>>({
      url: '/admin/automation/logs',
      method: 'GET',
      params,
    })
  },
  dryRunAutomation(data: AutomationDryRunIn) {
    return http.request<AutomationDryRunOut>({
      url: '/admin/automation/dry-run',
      method: 'POST',
      data,
      timeout: AI_TIMEOUT_MS,
    })
  },
}
