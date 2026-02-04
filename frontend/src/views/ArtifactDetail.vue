<!-- 文物详情页面 -->
<template>
  <layout>
    <div class="artifact-page" v-loading="loading">
      <el-card v-if="artifact" class="artifact-card">
        <template #header>
          <div class="card-header">
            <span>文物详情</span>
            <el-button @click="goBack">返回</el-button>
          </div>
        </template>

        <!-- 基本信息 -->
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="文物名称">
            {{ artifact.name }}
          </el-descriptions-item>
          <el-descriptions-item label="类别">
            {{ artifact.category }}
          </el-descriptions-item>
          <el-descriptions-item label="年代">
            {{ artifact.era }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(artifact.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ artifact.description }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 文物图片 -->
        <el-divider content-position="left">文物图片</el-divider>
        <div class="image-container">
          <el-image
            :src="getImageUrl(artifact.image_url)"
            fit="contain"
            style="max-width: 100%; max-height: 600px"
            :preview-src-list="[getImageUrl(artifact.image_url)]"
          />
        </div>

        <!-- 借出归还历史 -->
        <el-divider content-position="left">借出归还历史</el-divider>
        <el-table :data="history" stripe v-loading="historyLoading">
          <el-table-column prop="borrow_date" label="借出日期" width="120" />
          <el-table-column prop="borrower_name" label="借用人" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="归还情况" width="120">
            <template #default="{ row }">
              <span v-if="row.status === 'returned'">已归还</span>
              <span v-else>未归还</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { artifactApi, type Artifact } from '@/api/artifact'
import { borrowApi, type BorrowRecord } from '@/api/borrow'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const historyLoading = ref(false)
const artifact = ref<Artifact | null>(null)
const history = ref<BorrowRecord[]>([])

const getImageUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `/uploads/${url}`
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    borrowed: 'warning',
    returned: 'success',
    overdue: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    borrowed: '借出中',
    returned: '已归还',
    overdue: '逾期'
  }
  return textMap[status] || status
}

const goBack = () => {
  router.back()
}

const fetchArtifact = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('无效的文物ID')
    router.back()
    return
  }

  loading.value = true
  try {
    const response = await artifactApi.getDetail(id)
    artifact.value = response.data
  } catch (error) {
    console.error('获取文物详情失败:', error)
    ElMessage.error('获取文物详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

const fetchHistory = async () => {
  const id = Number(route.params.id)
  if (!id) return

  historyLoading.value = true
  try {
    const response = await borrowApi.getList({ artifact_id: id, page: 1, page_size: 100 })
    history.value = response.data.items
  } catch (error) {
    console.error('获取借出历史失败:', error)
  } finally {
    historyLoading.value = false
  }
}

onMounted(() => {
  fetchArtifact()
  fetchHistory()
})
</script>

<style scoped>
.artifact-page {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
