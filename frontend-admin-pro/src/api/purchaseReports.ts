import { http } from '@/utils/http'

export type PurchaseStatisticsOut = {
  supplier_id: number
  supplier_name: string | null
  material_id: number
  material_code: string | null
  material_name: string | null
  order_qty: number
  received_qty: number
  returned_qty: number
  net_qty: number
  order_amount: number
  received_amount: number
  returned_amount: number
  net_amount: number
}

export const purchaseReportsApi = {
  getPurchaseStatistics(params: { month?: string; supplier_id?: number }) {
    return http.request<{ items: PurchaseStatisticsOut[] }>({ url: '/admin/reports/purchase', method: 'GET', params })
  },
}
