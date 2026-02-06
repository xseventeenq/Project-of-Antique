/*
 * 管理员功能相关 API
 */
import request from './index'
import type { User } from './auth'

export interface DashboardStats {
  total_users: number
  total_artifacts: number
  total_borrows: number
  total_returns: number
  pending_borrows: number
  pending_returns: number
}

export interface UserListResponse {
  items: User[]
  total: number
  page: number
  page_size: number
}

export const adminApi = {
  // 获取仪表板统计数据
  getDashboardStats() {
    return request.get<DashboardStats>('/admin/dashboard')
  },

  // 获取用户列表
  getUsers(params?: { page?: number; page_size?: number; role?: string }) {
    return request.get<UserListResponse>('/admin/users', { params })
  },

  // 创建用户
  createUser(data: { username: string; password: string; role: string }) {
    return request.post<User>('/admin/users', data)
  },

  // 更新用户
  updateUser(id: number, data: { username?: string; role?: string }) {
    return request.put<User>(`/admin/users/${id}`, data)
  },

  // 删除用户
  deleteUser(id: number) {
    return request.delete(`/admin/users/${id}`)
  },

  // 重置用户密码
  resetUserPassword(id: number, data: { new_password: string }) {
    return request.post(`/admin/users/${id}/reset-password`, data)
  }
}
