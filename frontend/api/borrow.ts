/*
 * 借出记录相关 API
 */
import request from './index'

export interface BorrowRecord {
  id: number
  artifact_id: number
  artifact_name: string
  borrower_name: string
  borrower_contact: string
  borrow_date: string
  expected_return_date: string
  photo_url: string
  notes: string
  status: 'borrowed' | 'returned' | 'overdue'
  created_at: string
}

export interface BorrowRecordCreate {
  artifact_id: number
  borrower_name: string
  borrower_contact: string
  borrow_date: string
  expected_return_date: string
  photo: File
  notes?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const borrowApi = {
  // 获取借出记录列表
  getList(params?: {
    page?: number
    page_size?: number
    status?: string
    artifact_id?: number
  }) {
    return request.get<PaginatedResponse<BorrowRecord>>('/borrow', { params })
  },

  // 获取借出记录详情
  getDetail(id: number) {
    return request.get<BorrowRecord>(`/borrow/${id}`)
  },

  // 创建借出记录
  create(data: BorrowRecordCreate) {
    const formData = new FormData()
    formData.append('artifact_id', data.artifact_id.toString())
    formData.append('borrower_name', data.borrower_name)
    formData.append('borrower_contact', data.borrower_contact)
    formData.append('borrow_date', data.borrow_date)
    formData.append('expected_return_date', data.expected_return_date)
    formData.append('photo', data.photo)
    if (data.notes) formData.append('notes', data.notes)
    return request.post<BorrowRecord>('/borrow', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 更新借出记录
  update(id: number, data: Partial<BorrowRecordCreate>) {
    return request.put<BorrowRecord>(`/borrow/${id}`, data)
  },

  // 删除借出记录
  delete(id: number) {
    return request.delete(`/borrow/${id}`)
  }
}
