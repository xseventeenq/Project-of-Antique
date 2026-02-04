<!-- 归还记录列表页面 -->
<template>
  <layout>
    <el-card class="records-card">
      <template #header>
        <div class="card-header">
          <span>归还记录（鉴定报告）</span>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-bar">
        <el-select
          v-model="filters.conclusion"
          placeholder="结论筛选"
          clearable
          style="width: 150px"
          @change="handleSearch"
        >
          <el-option label="全部" value="" />
          <el-option label="确认为真品" value="authentic" />
          <el-option label="结果存疑" value="suspicious" />
          <el-option label="确认为仿品" value="fake" />
        </el-select>
      </div>

      <!-- 数据表格 -->
      <el-table :data="records" stripe v-loading="loading">
        <el-table-column prop="artifact_name" label="文物名称" width="200" />
        <el-table-column prop="return_date" label="归还日期" width="120" />
        <el-table-column label="AI 对比结论" width="120">
          <template #default="{ row }">
            <el-tag
              v-if="row.comparison_result"
              :type="getConclusionType(row.comparison_result.conclusion)"
            >
              {{ getConclusionText(row.comparison_result.conclusion) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="相似度" width="120">
          <template #default="{ row }">
            <span v-if="row.comparison_result">
              {{ row.comparison_result.confidence }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="鉴定师结论" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.conclusion" :type="getConclusionType(row.conclusion)">
              {{ getConclusionText(row.conclusion) }}
            </el-tag>
            <el-tag v-else type="info">待确认</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="appraiser_name" label="鉴定师" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              查看报告
            </el-button>
            <el-button
              v-if="authStore.isAppraiser() && !row.conclusion"
              link
              type="warning"
              size="small"
              @click="handleConfirm(row)"
            >
              确认结论
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- 确认结论弹窗 -->
    <el-dialog v-model="showConfirmDialog" title="确认鉴定结论" width="500px">
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
      </el-form>
      <template #footer>
        <el-button @click="showConfirmDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmSubmit">确定</el-button>
      </template>
    </el-dialog>
  </layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { returnApi, type ReturnRecord } from '@/api/return'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const records = ref<ReturnRecord[]>([])
const showConfirmDialog = ref(false)
const currentRecord = ref<ReturnRecord | null>(null)

const filters = reactive({
  conclusion: ''
})

const confirmForm = reactive({
  conclusion: '',
  notes: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
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

const fetchRecords = async () => {
  loading.value = true
  try {
    const response = await returnApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize,
      conclusion: filters.conclusion || undefined
    })
    records.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    console.error('获取归还记录失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchRecords()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  fetchRecords()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchRecords()
}

const handleView = (row: ReturnRecord) => {
  router.push(`/report/${row.id}`)
}

const handleConfirm = (row: ReturnRecord) => {
  currentRecord.value = row
  confirmForm.conclusion = ''
  confirmForm.notes = ''
  showConfirmDialog.value = true
}

const handleConfirmSubmit = async () => {
  if (!currentRecord.value || !confirmForm.conclusion) {
    ElMessage.warning('请选择结论')
    return
  }

  try {
    await returnApi.updateConclusion(currentRecord.value.id, confirmForm)
    ElMessage.success('结论确认成功')
    showConfirmDialog.value = false
    fetchRecords()
  } catch (error) {
    console.error('确认结论失败:', error)
    ElMessage.error('确认失败，请稍后重试')
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.records-card {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
