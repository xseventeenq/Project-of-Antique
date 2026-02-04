<!-- 收回对比页面 -->
<template>
  <layout>
    <el-card class="return-card">
      <template #header>
        <div class="card-header">
          <span>收回对比</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        @submit.prevent="handleSubmit"
      >
        <!-- 选择借出记录 -->
        <el-form-item label="选择借出记录" prop="borrow_record_id">
          <el-select
            v-model="form.borrow_record_id"
            placeholder="请选择借出记录"
            filterable
            style="width: 100%"
            @change="handleBorrowChange"
          >
            <el-option
              v-for="record in borrowRecords"
              :key="record.id"
              :label="`${record.artifact_name} - ${record.borrower_name}`"
              :value="record.id"
            />
          </el-select>
        </el-form-item>

        <!-- 显示借出信息 -->
        <el-card v-if="selectedBorrow" class="borrow-info" shadow="never">
          <template #header>
            <span>借出信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文物名称">
              {{ selectedBorrow.artifact_name }}
            </el-descriptions-item>
            <el-descriptions-item label="借用人">
              {{ selectedBorrow.borrower_name }}
            </el-descriptions-item>
            <el-descriptions-item label="联系方式">
              {{ selectedBorrow.borrower_contact }}
            </el-descriptions-item>
            <el-descriptions-item label="借出日期">
              {{ selectedBorrow.borrow_date }}
            </el-descriptions-item>
            <el-descriptions-item label="预计归还日期">
              {{ selectedBorrow.expected_return_date }}
            </el-descriptions-item>
            <el-descriptions-item label="借出照片">
              <el-image
                v-if="selectedBorrow.photo_url"
                :src="getImageUrl(selectedBorrow.photo_url)"
                style="width: 100px; height: 100px"
                fit="cover"
                :preview-src-list="[getImageUrl(selectedBorrow.photo_url)]"
              />
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 归还日期 -->
        <el-form-item label="归还日期" prop="return_date">
          <el-date-picker
            v-model="form.return_date"
            type="date"
            placeholder="选择归还日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <!-- 归还照片上传 -->
        <el-form-item label="归还照片" prop="photo">
          <el-upload
            class="photo-uploader"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handlePhotoChange"
            accept="image/*"
          >
            <img v-if="photoPreview" :src="photoPreview" class="photo-preview" />
            <div v-else class="upload-placeholder">
              <el-icon class="upload-icon"><Plus /></el-icon>
              <div>上传归还照片</div>
            </div>
          </el-upload>
        </el-form-item>

        <!-- 备注 -->
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息（可选）"
          />
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            提交对比
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AI 对比结果弹窗 -->
    <el-dialog
      v-model="showResultDialog"
      title="AI 对比结果"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="comparisonResult">
        <!-- 整体相似度 -->
        <el-result
          :icon="getResultIcon(comparisonResult.conclusion)"
          :title="getResultTitle(comparisonResult.conclusion)"
          :sub-title="`相似度: ${comparisonResult.confidence}%`"
        >
          <template #extra>
            <el-progress
              type="circle"
              :percentage="comparisonResult.confidence"
              :color="getSimilarityColor(comparisonResult.confidence)"
              :width="120"
            />
          </template>
        </el-result>

        <!-- 分维度结果 -->
        <el-divider>分维度分析</el-divider>
        <el-row :gutter="20">
          <el-col
            :span="12"
            v-for="(dimension, key) in comparisonResult.dimensions"
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
                :stroke-width="10"
              />
              <p class="dimension-desc">{{ dimension.description }}</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <div v-else class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>AI 正在分析中，请稍候...</p>
      </div>
      <template #footer>
        <el-button @click="showResultDialog = false">关闭</el-button>
        <el-button
          v-if="comparisonResult"
          type="primary"
          @click="goToReport"
        >
          查看详细报告
        </el-button>
      </template>
    </el-dialog>
  </layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules, type UploadFile } from 'element-plus'
import { Plus, Loading } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import { borrowApi, type BorrowRecord } from '@/api/borrow'
import { returnApi, type ComparisonResult } from '@/api/return'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const borrowRecords = ref<BorrowRecord[]>([])
const photoFile = ref<File | null>(null)
const photoPreview = ref('')
const comparisonResult = ref<ComparisonResult | null>(null)
const showResultDialog = ref(false)
const createdReturnId = ref<number | null>(null)

const form = reactive({
  borrow_record_id: undefined as number | undefined,
  return_date: '',
  notes: ''
})

const rules: FormRules = {
  borrow_record_id: [{ required: true, message: '请选择借出记录', trigger: 'change' }],
  return_date: [{ required: true, message: '请选择归还日期', trigger: 'change' }],
  photo: [{ required: true, message: '请上传归还照片', trigger: 'change' }]
}

const selectedBorrow = computed(() => {
  if (!form.borrow_record_id) return null
  return borrowRecords.value.find(r => r.id === form.borrow_record_id) || null
})

const getImageUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `/uploads/${url}`
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
    authentic: '确认为真品',
    suspicious: '结果存疑',
    fake: '确认为仿品'
  }
  return titleMap[conclusion] || '对比完成'
}

const goBack = () => {
  router.back()
}

const handleBorrowChange = () => {
  // 可以在这里加载借出记录的详细信息
}

const handlePhotoChange = (file: UploadFile) => {
  if (file.raw) {
    photoFile.value = file.raw
    photoPreview.value = URL.createObjectURL(file.raw)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    if (!photoFile.value) {
      ElMessage.error('请上传归还照片')
      return
    }

    loading.value = true
    comparisonResult.value = null
    showResultDialog.value = true

    const response = await returnApi.create({
      borrow_record_id: form.borrow_record_id!,
      return_date: form.return_date,
      photo: photoFile.value,
      notes: form.notes
    })

    createdReturnId.value = response.data.id
    comparisonResult.value = response.data.comparison_result

    ElMessage.success('归还记录创建成功，AI 对比完成')
  } catch (error) {
    console.error('创建归还记录失败:', error)
    ElMessage.error('创建失败，请稍后重试')
    showResultDialog.value = false
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  photoFile.value = null
  photoPreview.value = ''
}

const goToReport = () => {
  showResultDialog.value = false
  if (createdReturnId.value) {
    router.push(`/report/${createdReturnId.value}`)
  }
}

const fetchBorrowRecords = async () => {
  try {
    const response = await borrowApi.getList({ status: 'borrowed', page: 1, page_size: 1000 })
    borrowRecords.value = response.data.items
  } catch (error) {
    console.error('获取借出记录失败:', error)
  }
}

onMounted(() => {
  fetchBorrowRecords()
  // 设置默认日期为今天
  const today = new Date().toISOString().split('T')[0]
  form.return_date = today
})
</script>

<style scoped>
.return-card {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.borrow-info {
  margin-bottom: 20px;
}

.photo-uploader {
  display: inline-block;
}

.photo-preview {
  width: 300px;
  height: 300px;
  object-fit: cover;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.upload-placeholder {
  width: 300px;
  height: 300px;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #8c939d;
}

.upload-placeholder:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 60px;
  margin-bottom: 10px;
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
  color: #303133;
}

.dimension-desc {
  margin: 10px 0 0 0;
  font-size: 13px;
  color: #606266;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-container .el-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 20px;
}
</style>
