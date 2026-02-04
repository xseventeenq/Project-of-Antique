<!-- 借出存档页面 -->
<template>
  <layout>
    <el-card class="borrow-card">
      <template #header>
        <div class="card-header">
          <span>借出存档</span>
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
        <!-- 文物选择 -->
        <el-form-item label="选择文物" prop="artifact_id">
          <el-select
            v-model="form.artifact_id"
            placeholder="请选择文物"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="artifact in artifacts"
              :key="artifact.id"
              :label="artifact.name"
              :value="artifact.id"
            />
          </el-select>
        </el-form-item>

        <!-- 借用人信息 -->
        <el-form-item label="借用人姓名" prop="borrower_name">
          <el-input v-model="form.borrower_name" placeholder="请输入借用人姓名" />
        </el-form-item>

        <el-form-item label="借用人联系方式" prop="borrower_contact">
          <el-input v-model="form.borrower_contact" placeholder="请输入联系方式" />
        </el-form-item>

        <!-- 日期选择 -->
        <el-form-item label="借出日期" prop="borrow_date">
          <el-date-picker
            v-model="form.borrow_date"
            type="date"
            placeholder="选择借出日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="预计归还日期" prop="expected_return_date">
          <el-date-picker
            v-model="form.expected_return_date"
            type="date"
            placeholder="选择预计归还日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <!-- 照片上传 -->
        <el-form-item label="借出照片" prop="photo">
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
              <div>上传借出照片</div>
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
            提交存档
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules, type UploadFile } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import { artifactApi, type Artifact } from '@/api/artifact'
import { borrowApi } from '@/api/borrow'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const artifacts = ref<Artifact[]>([])
const photoFile = ref<File | null>(null)
const photoPreview = ref('')

const form = reactive({
  artifact_id: undefined as number | undefined,
  borrower_name: '',
  borrower_contact: '',
  borrow_date: '',
  expected_return_date: '',
  notes: ''
})

const rules: FormRules = {
  artifact_id: [{ required: true, message: '请选择文物', trigger: 'change' }],
  borrower_name: [{ required: true, message: '请输入借用人姓名', trigger: 'blur' }],
  borrower_contact: [{ required: true, message: '请输入联系方式', trigger: 'blur' }],
  borrow_date: [{ required: true, message: '请选择借出日期', trigger: 'change' }],
  expected_return_date: [{ required: true, message: '请选择预计归还日期', trigger: 'change' }],
  photo: [{ required: true, message: '请上传借出照片', trigger: 'change' }]
}

const goBack = () => {
  router.back()
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
      ElMessage.error('请上传借出照片')
      return
    }

    loading.value = true

    await borrowApi.create({
      artifact_id: form.artifact_id!,
      borrower_name: form.borrower_name,
      borrower_contact: form.borrower_contact,
      borrow_date: form.borrow_date,
      expected_return_date: form.expected_return_date,
      photo: photoFile.value,
      notes: form.notes
    })

    ElMessage.success('借出存档创建成功')
    router.push('/borrow-records')
  } catch (error) {
    console.error('创建借出记录失败:', error)
    ElMessage.error('创建失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  photoFile.value = null
  photoPreview.value = ''
}

const fetchArtifacts = async () => {
  try {
    const response = await artifactApi.getList({ page: 1, page_size: 1000 })
    artifacts.value = response.data.items
  } catch (error) {
    console.error('获取文物列表失败:', error)
  }
}

onMounted(() => {
  fetchArtifacts()
  // 设置默认日期为今天
  const today = new Date().toISOString().split('T')[0]
  form.borrow_date = today
})
</script>

<style scoped>
.borrow-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
</style>
