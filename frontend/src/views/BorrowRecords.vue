<!-- 借出记录列表页面 -->
<template>
  <layout>
    <el-card class="records-card">
      <template #header>
        <div class="card-header">
          <span>借出记录</span>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-bar">
        <el-select
          v-model="filters.status"
          placeholder="状态筛选"
          clearable
          style="width: 150px"
          @change="handleSearch"
        >
          <el-option label="全部" value="" />
          <el-option label="借出中" value="borrowed" />
          <el-option label="已归还" value="returned" />
          <el-option label="逾期" value="overdue" />
        </el-select>
      </div>

      <!-- 数据表格 -->
      <el-table :data="records" stripe v-loading="loading">
        <el-table-column prop="artifact_name" label="文物名称" width="200" />
        <el-table-column prop="borrower_name" label="借用人" width="120" />
        <el-table-column prop="borrower_contact" label="联系方式" width="150" />
        <el-table-column prop="borrow_date" label="借出日期" width="120" />
        <el-table-column prop="expected_return_date" label="预计归还" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              查看详情
            </el-button>
            <el-button
              v-if="row.status === 'borrowed' && authStore.isAppraiser()"
              link
              type="success"
              size="small"
              @click="handleReturn(row)"
            >
              归还
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
  </layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { borrowApi, type BorrowRecord } from '@/api/borrow'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const records = ref<BorrowRecord[]>([])

const filters = reactive({
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

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

const fetchRecords = async () => {
  loading.value = true
  try {
    const response = await borrowApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize,
      status: filters.status || undefined
    })
    records.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    console.error('获取借出记录失败:', error)
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

const handleView = (row: BorrowRecord) => {
  // 跳转到文物详情页
  router.push(`/artifacts/${row.artifact_id}`)
}

const handleReturn = (row: BorrowRecord) => {
  router.push(`/return?borrow_id=${row.id}`)
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
