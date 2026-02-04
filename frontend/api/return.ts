/*
 * 归还记录相关 API
 */
import request from './index'

export interface DimensionResult {
  status: 'normal' | 'suspicious' | 'abnormal'
  score: number
  description: string
  annotation_url: string | null
}

export interface ComparisonResult {
  conclusion: 'authentic' | 'suspicious' | 'fake'
  confidence: number
  dimensions: {
    seal: DimensionResult
    brushwork: DimensionResult
    paper: DimensionResult
    inscription: DimensionResult
    composition: DimensionResult
    watermark: DimensionResult
  }
}

export interface ReturnRecord {
  id: number
  borrow_record_id: number
  artifact_name: string
  return_date: string
  photo_url: string
  comparison_result: ComparisonResult | null
  appraiser_id: number
  appraiser_name: string
  conclusion: string | null
  notes: string
  created_at: string
}

export interface ReturnRecordCreate {
  borrow_record_id: number
  return_date: string
  photo: File
  notes?: string
}

export interface UpdateConclusionRequest {
  conclusion: 'authentic' | 'suspicious' | 'fake'
  notes?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const returnApi = {
  // 获取归还记录列表
  getList(params?: {
    page?: number
    page_size?: number
    conclusion?: string
    artifact_id?: number
  }) {
    return request.get<PaginatedResponse<ReturnRecord>>('/return', { params })
  },

  // 获取归还记录详情
  getDetail(id: number) {
    return request.get<ReturnRecord>(`/return/${id}`)
  },

  // 创建归还记录（触发 AI 对比）
  create(data: ReturnRecordCreate) {
    const formData = new FormData()
    formData.append('borrow_record_id', data.borrow_record_id.toString())
    formData.append('return_date', data.return_date)
    formData.append('photo', data.photo)
    if (data.notes) formData.append('notes', data.notes)
    return request.post<ReturnRecord>('/return', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 更新鉴定结论
  updateConclusion(id: number, data: UpdateConclusionRequest) {
    return request.patch<ReturnRecord>(`/return/${id}/conclusion`, data)
  },

  // 删除归还记录
  delete(id: number) {
    return request.delete(`/return/${id}`)
  }
}
