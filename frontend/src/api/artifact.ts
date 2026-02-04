/*
 * 文物相关 API
 */
import request from './index'

export interface Artifact {
  id: number
  name: string
  category: string
  era: string
  description: string
  image_url: string
  created_at: string
  updated_at: string
}

export interface ArtifactCreate {
  name: string
  category: string
  era: string
  description: string
  image: File
}

export interface ArtifactUpdate {
  name?: string
  category?: string
  era?: string
  description?: string
  image?: File
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const artifactApi = {
  // 获取文物列表
  getList(params?: { page?: number; page_size?: number; search?: string }) {
    return request.get<PaginatedResponse<Artifact>>('/artifacts', { params })
  },

  // 获取文物详情
  getDetail(id: number) {
    return request.get<Artifact>(`/artifacts/${id}`)
  },

  // 创建文物
  create(data: ArtifactCreate) {
    const formData = new FormData()
    formData.append('name', data.name)
    formData.append('category', data.category)
    formData.append('era', data.era)
    formData.append('description', data.description)
    formData.append('image', data.image)
    return request.post<Artifact>('/artifacts', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 更新文物
  update(id: number, data: ArtifactUpdate) {
    if (data.image) {
      const formData = new FormData()
      if (data.name) formData.append('name', data.name)
      if (data.category) formData.append('category', data.category)
      if (data.era) formData.append('era', data.era)
      if (data.description) formData.append('description', data.description)
      formData.append('image', data.image)
      return request.put<Artifact>(`/artifacts/${id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    return request.put<Artifact>(`/artifacts/${id}`, data)
  },

  // 删除文物
  delete(id: number) {
    return request.delete(`/artifacts/${id}`)
  }
}
