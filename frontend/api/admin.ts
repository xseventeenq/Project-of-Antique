/*
 * 管理员相关 API
 */
import request from './index'

export interface User {
  id: number
  username: string
  role: 'admin' | 'appraiser' | 'staff'
  is_active: boolean
  created_at: string
}

export interface CreateUserRequest {
  username: string
  password: string
  role: 'admin' | 'appraiser' | 'staff'
}

export const adminApi = {
  // 获取用户列表
  getUserList(params?: { page?: number; page_size?: number }) {
    return request.get('/admin/users', { params })
  },

  // 创建用户
  createUser(data: CreateUserRequest) {
    return request.post('/admin/users', data)
  },

  // 删除用户
  deleteUser(id: number) {
    return request.delete(`/admin/users/${id}`)
  },

  // 删除借出记录
  deleteBorrowRecord(id: number) {
    return request.delete(`/admin/borrow/${id}`)
  },

  // 删除归还记录
  deleteReturnRecord(id: number) {
    return request.delete(`/admin/return/${id}`)
  },

  // 删除文物
  deleteArtifact(id: number) {
    return request.delete(`/admin/artifacts/${id}`)
  }
}
