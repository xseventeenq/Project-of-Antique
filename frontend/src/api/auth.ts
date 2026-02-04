/*
 * 认证相关 API
 */
import request from './index'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  role?: 'admin' | 'appraiser' | 'staff'
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    username: string
    role: string
  }
}

export const authApi = {
  // 登录
  login(data: LoginRequest) {
    return request.post<LoginResponse>('/auth/login', data)
  },

  // 注册（仅管理员可用）
  register(data: RegisterRequest) {
    return request.post('/auth/register', data)
  },

  // 获取当前用户信息
  getCurrentUser() {
    return request.get('/auth/me')
  },

  // 验证 token
  verifyToken() {
    return request.get('/auth/verify-token')
  },

  // 登出（前端清除 token 即可）
  logout() {
    return Promise.resolve()
  }
}
