/*
 * 归还记录和AI对比相关 API
 */
import request from './index'

export interface ReturnRecord {
  id: number
  borrow_id: number
  artifact_name: string
  comparison_score?: number
  ai_conclusion?: string
  appraiser_conclusion?: string
  is_verified: boolean
  verified_by?: string
  verified_at?: string
  photo_url_before?: string
  photo_url_after?: string
  created_at: string
  updated_at: string
}

export interface ComparisonResult extends ReturnRecord {}

export interface CreateReturnRequest {
  borrow_id: number
  photo_url_after: string
  appraiser_notes?: string
}

export interface ComparisonResponse {
  similarity_score: number
  conclusion: string
  confidence: number
  details: {
    color_similarity: number
    texture_similarity: number
    shape_similarity: number
    overall_condition: string
  }
}

export interface ReturnListResponse {
  items: ReturnRecord[]
  total: number
  page: number
  page_size: number
}

export const returnApi = {
  // 创建归还记录并触发 AI 对比
  create(data: CreateReturnRequest) {
    return request.post<ComparisonResult>('/returns', data)
  },

  // 获取归还记录列表
  getList(params?: { page?: number; page_size?: number; is_verified?: boolean }) {
    return request.get<ReturnListResponse>('/returns', { params })
  },

  // 获取单个归还记录详情
  getById(id: number) {
    return request.get<ReturnRecord>(`/returns/${id}`)
  },

  // 鉴定师复核
  verify(id: number, data: { appraiser_conclusion: string; is_verified: boolean }) {
    return request.post<ReturnRecord>(`/returns/${id}/verify`, data)
  },

  // 仅进行 AI 对比（不创建归还记录）
  comparePhotos(data: { photo_url_before: string; photo_url_after: string }) {
    return request.post<ComparisonResponse>('/returns/compare', data)
  }
}
