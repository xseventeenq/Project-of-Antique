/*
 * 用户认证状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface User {
  id: number
  username: string
  role: 'admin' | 'appraiser' | 'staff'
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)
  const userRole = ref<string>(localStorage.getItem('userRole') || '')

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUser = (newUser: User) => {
    user.value = newUser
    localStorage.setItem('userRole', newUser.role)
    userRole.value = newUser.role
  }

  const logout = () => {
    token.value = ''
    user.value = null
    userRole.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('userRole')
  }

  const isAuthenticated = () => {
    return !!token.value
  }

  const isAdmin = () => {
    return userRole.value === 'admin'
  }

  const isAppraiser = () => {
    return userRole.value === 'appraiser' || userRole.value === 'admin'
  }

  return {
    token,
    user,
    userRole,
    setToken,
    setUser,
    logout,
    isAuthenticated,
    isAdmin,
    isAppraiser
  }
})
