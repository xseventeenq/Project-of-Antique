/*
 * 借出记录相关 API
 */
import request from './index'

export interface BorrowRecord {
  id: number
  artifact_id: number
  artifact: {
    id: number
    artifact_id: string
    name: string
    author: string
    category: string
  } | null
  borrow_photo_url: string
  borrow_date: string
  expected_return_date: string | null
  status: 'borrowed' | 'returned'
  operator_id: number
  created_at: string
}

export interface CreateBorrowRequest {
  artifact_name: string
  artifact_category?: string
  artifact_period?: string
  artifact_description?: string
  borrower_name: string
  borrower_contact?: string
  expected_return_date?: string
  photo_url?: string
}

export interface BorrowListResponse {
  items: BorrowRecord[]
  total: number
  page: number
  page_size: number
}

export const borrowApi = {
  // 创建借出记录（需要使用FormData上传文件）
  create(formData: FormData) {
    return request.post<BorrowRecord>('/borrow-records', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 上传照片
  uploadPhoto(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<{photo_url: string; photo_path: string}>('/borrow-records/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取借出记录列表
  getList(params?: { page?: number; page_size?: number; status?: string }) {
    // 将前端的 page/page_size 转换为后端的 skip/limit
    const page = params?.page || 1
    const page_size = params?.page_size || 10
    const skip = (page - 1) * page_size
    const limit = page_size

    return request.get<BorrowListResponse>('/borrow-records', {
      params: { skip, limit, artifact_id: params?.status }
    })
  },

  // 获取单个借出记录详情
  getById(id: number) {
    return request.get<BorrowRecord>(`/borrow-records/${id}`)
  },

  // 根据文物ID获取借出记录
  getByArtifactId(artifactId: string) {
    return request.get<BorrowRecord>(`/borrow-records/artifact/${artifactId}`)
  },

  // 更新借出记录
  update(id: number, data: Partial<CreateBorrowRequest>) {
    return request.put<BorrowRecord>(`/borrow-records/${id}`, data)
  },

  // 删除借出记录
  delete(id: number) {
    return request.delete(`/borrow-records/${id}`)
  }
}
