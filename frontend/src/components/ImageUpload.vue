<!-- 图片上传组件 -->
<template>
  <div class="image-upload">
    <el-upload
      class="upload-demo"
      :action="uploadUrl"
      :headers="headers"
      :show-file-list="false"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :accept="accept"
    >
      <div v-if="!imageUrl" class="upload-placeholder">
        <el-icon class="upload-icon"><Plus /></el-icon>
        <div class="upload-text">{{ placeholder }}</div>
      </div>
      <div v-else class="image-preview">
        <img :src="imageUrl" alt="上传的图片" />
        <div class="image-mask">
          <el-icon @click.stop="handleRemove" class="remove-icon"><Delete /></el-icon>
        </div>
      </div>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { UploadProps } from 'element-plus'

interface Props {
  modelValue: string
  accept?: string
  placeholder?: string
  maxSize?: number // MB
}

const props = withDefaults(defineProps<Props>(), {
  accept: 'image/jpeg,image/png,image/gif',
  placeholder: '上传图片',
  maxSize: 10
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const uploadUrl = computed(() => {
  // 返回后端上传接口 URL
  return '/api/upload'
})

const headers = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

const imageUrl = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLtSize = file.size / 1024 / 1024 < props.maxSize

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }
  if (!isLtSize) {
    ElMessage.error(`图片大小不能超过 ${props.maxSize}MB！`)
    return false
  }
  return true
}

const handleSuccess: UploadProps['onSuccess'] = (response) => {
  if (response.url) {
    imageUrl.value = response.url
    ElMessage.success('上传成功')
  }
}

const handleError: UploadProps['onError'] = () => {
  ElMessage.error('上传失败')
}

const handleRemove = () => {
  imageUrl.value = ''
}
</script>

<style scoped>
.image-upload {
  display: inline-block;
}

.upload-placeholder {
  width: 200px;
  height: 200px;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-placeholder:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 40px;
  color: #8c939d;
}

.upload-text {
  margin-top: 10px;
  font-size: 14px;
  color: #8c939d;
}

.image-preview {
  position: relative;
  width: 200px;
  height: 200px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: none;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.image-preview:hover .image-mask {
  display: flex;
}

.remove-icon {
  font-size: 30px;
  color: #fff;
}
</style>
