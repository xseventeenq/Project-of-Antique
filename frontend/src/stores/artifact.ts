/*
 * 文物状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { artifactApi, type Artifact, type PaginatedResponse } from '@/api/artifact'

export const useArtifactStore = defineStore('artifact', () => {
  const artifacts = ref<Artifact[]>([])
  const currentArtifact = ref<Artifact | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)

  // 获取文物列表
  const fetchArtifacts = async (params?: {
    page?: number
    page_size?: number
    search?: string
  }) => {
    loading.value = true
    try {
      const response = await artifactApi.getList(params)
      artifacts.value = response.data.items
      total.value = response.data.total
      page.value = response.data.page
      pageSize.value = response.data.page_size
    } catch (error) {
      console.error('获取文物列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取文物详情
  const fetchArtifactDetail = async (id: number) => {
    loading.value = true
    try {
      const response = await artifactApi.getDetail(id)
      currentArtifact.value = response.data
    } catch (error) {
      console.error('获取文物详情失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 创建文物
  const createArtifact = async (data: any) => {
    loading.value = true
    try {
      await artifactApi.create(data)
      await fetchArtifacts({ page: 1, page_size: pageSize.value })
    } catch (error) {
      console.error('创建文物失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新文物
  const updateArtifact = async (id: number, data: any) => {
    loading.value = true
    try {
      await artifactApi.update(id, data)
      await fetchArtifacts({ page: page.value, page_size: pageSize.value })
    } catch (error) {
      console.error('更新文物失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除文物
  const deleteArtifact = async (id: number) => {
    loading.value = true
    try {
      await artifactApi.delete(id)
      await fetchArtifacts({ page: page.value, page_size: pageSize.value })
    } catch (error) {
      console.error('删除文物失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    artifacts,
    currentArtifact,
    loading,
    total,
    page,
    pageSize,
    fetchArtifacts,
    fetchArtifactDetail,
    createArtifact,
    updateArtifact,
    deleteArtifact
  }
})
