/*
 * 借出记录状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { borrowApi, type BorrowRecord } from '@/api/borrow'

export const useBorrowStore = defineStore('borrow', () => {
  const borrowRecords = ref<BorrowRecord[]>([])
  const currentRecord = ref<BorrowRecord | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)

  // 获取借出记录列表
  const fetchBorrowRecords = async (params?: {
    page?: number
    page_size?: number
    status?: string
    artifact_id?: number
  }) => {
    loading.value = true
    try {
      const response = await borrowApi.getList(params)
      borrowRecords.value = response.data.items
      total.value = response.data.total
      page.value = response.data.page
      pageSize.value = response.data.page_size
    } catch (error) {
      console.error('获取借出记录失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取借出记录详情
  const fetchBorrowDetail = async (id: number) => {
    loading.value = true
    try {
      const response = await borrowApi.getDetail(id)
      currentRecord.value = response.data
    } catch (error) {
      console.error('获取借出记录详情失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 创建借出记录
  const createBorrowRecord = async (data: any) => {
    loading.value = true
    try {
      await borrowApi.create(data)
      await fetchBorrowRecords({ page: 1, page_size: pageSize.value })
    } catch (error) {
      console.error('创建借出记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除借出记录
  const deleteBorrowRecord = async (id: number) => {
    loading.value = true
    try {
      await borrowApi.delete(id)
      await fetchBorrowRecords({ page: page.value, page_size: pageSize.value })
    } catch (error) {
      console.error('删除借出记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    borrowRecords,
    currentRecord,
    loading,
    total,
    page,
    pageSize,
    fetchBorrowRecords,
    fetchBorrowDetail,
    createBorrowRecord,
    deleteBorrowRecord
  }
})
