/*
 * 归还记录状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { returnApi, type ReturnRecord } from '@/api/return'

export const useReturnStore = defineStore('return', () => {
  const returnRecords = ref<ReturnRecord[]>([])
  const currentRecord = ref<ReturnRecord | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)

  // 获取归还记录列表
  const fetchReturnRecords = async (params?: {
    page?: number
    page_size?: number
    conclusion?: string
    artifact_id?: number
  }) => {
    loading.value = true
    try {
      const response = await returnApi.getList(params)
      returnRecords.value = response.data.items
      total.value = response.data.total
      page.value = response.data.page
      pageSize.value = response.data.page_size
    } catch (error) {
      console.error('获取归还记录失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取归还记录详情
  const fetchReturnDetail = async (id: number) => {
    loading.value = true
    try {
      const response = await returnApi.getDetail(id)
      currentRecord.value = response.data
    } catch (error) {
      console.error('获取归还记录详情失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 创建归还记录
  const createReturnRecord = async (data: any) => {
    loading.value = true
    try {
      await returnApi.create(data)
      await fetchReturnRecords({ page: 1, page_size: pageSize.value })
    } catch (error) {
      console.error('创建归还记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新鉴定结论
  const updateConclusion = async (id: number, data: any) => {
    loading.value = true
    try {
      await returnApi.updateConclusion(id, data)
      await fetchReturnRecords({ page: page.value, page_size: pageSize.value })
    } catch (error) {
      console.error('更新鉴定结论失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除归还记录
  const deleteReturnRecord = async (id: number) => {
    loading.value = true
    try {
      await returnApi.delete(id)
      await fetchReturnRecords({ page: page.value, page_size: pageSize.value })
    } catch (error) {
      console.error('删除归还记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    returnRecords,
    currentRecord,
    loading,
    total,
    page,
    pageSize,
    fetchReturnRecords,
    fetchReturnDetail,
    createReturnRecord,
    updateConclusion,
    deleteReturnRecord
  }
})
