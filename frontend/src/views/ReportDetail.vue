<!-- 对比报告详情页面 -->
<template>
  <layout>
    <div class="report-page" v-loading="loading">
      <el-card v-if="record" class="report-card">
        <template #header>
          <div class="card-header">
            <span>鉴定报告 #{{ record.id }}</span>
            <el-button @click="goBack">返回</el-button>
          </div>
        </template>

        <!-- 基本信息 -->
        <el-descriptions title="基本信息" :column="2" border class="mb-20">
          <el-descriptions-item label="文物名称">
            {{ record.artifact_name }}
          </el-descriptions-item>
          <el-descriptions-item label="归还日期">
            {{ record.return_date }}
          </el-descriptions-item>
          <el-descriptions-item label="鉴定师">
            {{ record.appraiser_name }}
          </el-descriptions-item>
          <el-descriptions-item label="鉴定师结论">
            <el-tag v-if="record.conclusion" :type="getConclusionType(record.conclusion)">
              {{ getConclusionText(record.conclusion) }}
            </el-tag>
            <el-tag v-else type="info">待确认</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ record.notes || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- AI 对比结果 -->
        <div v-if="record.comparison_result">
          <el-divider content-position="left">AI 对比结果</el-divider>

          <!-- 整体结论 -->
          <el-result
            :icon="getResultIcon(record.comparison_result.conclusion)"
            :title="getResultTitle(record.comparison_result.conclusion)"
            :sub-title="`相似度: ${record.comparison_result.confidence}%`"
            class="mb-20"
          >
            <template #extra>
              <el-progress
                type="circle"
                :percentage="record.comparison_result.confidence"
                :color="getSimilarityColor(record.comparison_result.confidence)"
                :width="150"
              />
            </template>
          </el-result>

          <!-- 分维度结果 -->
          <el-divider content-position="left">分维度分析</el-divider>
          <el-row :gutter="20">
            <el-col
              :span="12"
              v-for="(dimension, key) in record.comparison_result.dimensions"
              :key="key"
            >
              <el-card class="dimension-card" shadow="hover">
                <div class="dimension-header">
                  <span class="dimension-name">{{ getDimensionName(key) }}</span>
                  <el-tag :type="getDimensionTagType(dimension.status)">
                    {{ getDimensionStatusText(dimension.status) }}
                  </el-tag>
                </div>
                <el-progress
                  :percentage="dimension.score"
                  :color="getSimilarityColor(dimension.score)"
                  :stroke-width="12"
                />
                <p class="dimension-desc">{{ dimension.description }}</p>
              </el-card>
            </el-col>
          </el-row>

          <!-- 鉴定师确认 -->
          <el-divider content-position="left">鉴定师确认</el-divider>
          <el-card v-if="authStore.isAppraiser() && !record.conclusion" shadow="never">
            <el-form :model="confirmForm" label-width="100px">
              <el-form-item label="最终结论">
                <el-select v-model="confirmForm.conclusion" placeholder="请选择结论">
                  <el-option label="确认为真品" value="authentic" />
                  <el-option label="结果存疑" value="suspicious" />
                  <el-option label="确认为仿品" value="fake" />
                </el-select>
              </el-form-item>
              <el-form-item label="备注">
                <el-input
                  v-model="confirmForm.notes"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入备注（可选）"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleConfirm">确认结论</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
        <el-empty v-else description="暂无对比结果" />
      </el-card>
    </div>
  </layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { returnApi, type ReturnRecord } from '@/api/return'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const record = ref<ReturnRecord | null>(null)

const confirmForm = reactive({
  conclusion: '',
  notes: ''
})

const getConclusionType = (conclusion: string) => {
  const typeMap: Record<string, any> = {
    authentic: 'success',
    suspicious: 'warning',
    fake: 'danger'
  }
  return typeMap[conclusion] || 'info'
}

const getConclusionText = (conclusion: string) => {
  const textMap: Record<string, string> = {
    authentic: '确认为真品',
    suspicious: '结果存疑',
    fake: '确认为仿品'
  }
  return textMap[conclusion] || conclusion
}

const getSimilarityColor = (similarity: number) => {
  if (similarity >= 90) return '#67c23a'
  if (similarity >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getResultIcon = (conclusion: string) => {
  if (conclusion === 'authentic') return 'success'
  if (conclusion === 'suspicious') return 'warning'
  return 'error'
}

const getResultTitle = (conclusion: string) => {
  const titleMap: Record<string, string> = {
    authentic: 'AI 确认为真品',
    suspicious: 'AI 结果存疑',
    fake: 'AI 确认为仿品'
  }
  return titleMap[conclusion] || 'AI 对比完成'
}

const getDimensionName = (key: string) => {
  const names: Record<string, string> = {
    seal: '印章特征',
    brushwork: '笔触特征',
    paper: '纸张材质',
    inscription: '题跋落款',
    composition: '整体构图',
    watermark: '水印标记'
  }
  return names[key] || key
}

const getDimensionTagType = (status: string) => {
  const typeMap: Record<string, any> = {
    normal: 'success',
    suspicious: 'warning',
    abnormal: 'danger'
  }
  return typeMap[status] || 'info'
}

const getDimensionStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    normal: '正常',
    suspicious: '存疑',
    abnormal: '异常'
  }
  return textMap[status] || status
}

const goBack = () => {
  router.back()
}

const handleConfirm = async () => {
  if (!record.value || !confirmForm.conclusion) {
    ElMessage.warning('请选择结论')
    return
  }

  try {
    await returnApi.updateConclusion(record.value.id, confirmForm)
    ElMessage.success('结论确认成功')
    // 重新获取数据
    fetchReport()
  } catch (error) {
    console.error('确认结论失败:', error)
    ElMessage.error('确认失败，请稍后重试')
  }
}

const fetchReport = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('无效的报告ID')
    router.back()
    return
  }

  loading.value = true
  try {
    const response = await returnApi.getDetail(id)
    record.value = response.data
  } catch (error) {
    console.error('获取报告详情失败:', error)
    ElMessage.error('获取报告详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchReport()
})
</script>

<style scoped>
.report-page {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mb-20 {
  margin-bottom: 20px;
}

.dimension-card {
  margin-bottom: 15px;
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.dimension-name {
  font-weight: 500;
  font-size: 16px;
  color: #303133;
}

.dimension-desc {
  margin: 10px 0 0 0;
  font-size: 13px;
  color: #606266;
}
</style>
