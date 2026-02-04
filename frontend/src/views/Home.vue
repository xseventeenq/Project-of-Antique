<!-- 首页 - 简洁型布局 -->
<template>
  <layout>
    <div class="home-page">
      <el-row :gutter="20">
        <!-- 快捷操作卡片 -->
        <el-col :span="6" v-if="authStore.isAppraiser()">
          <el-card class="action-card" shadow="hover" @click="goTo('/borrow')">
            <div class="card-content">
              <el-icon class="card-icon" color="#409eff"><DocumentAdd /></el-icon>
              <div class="card-title">借出存档</div>
              <div class="card-desc">创建新的借出记录</div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6" v-if="authStore.isAppraiser()">
          <el-card class="action-card" shadow="hover" @click="goTo('/return')">
            <div class="card-content">
              <el-icon class="card-icon" color="#67c23a"><DocumentChecked /></el-icon>
              <div class="card-title">收回对比</div>
              <div class="card-desc">AI 智能对比鉴定</div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="action-card" shadow="hover" @click="goTo('/borrow-records')">
            <div class="card-content">
              <el-icon class="card-icon" color="#e6a23c"><FolderOpened /></el-icon>
              <div class="card-title">借出记录</div>
              <div class="card-desc">查看借出历史</div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="action-card" shadow="hover" @click="goTo('/return-records')">
            <div class="card-content">
              <el-icon class="card-icon" color="#f56c6c"><Document /></el-icon>
              <div class="card-title">归还记录</div>
              <div class="card-desc">查看鉴定报告</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 统计数据 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <el-card class="stat-card">
            <el-statistic title="总借出次数" :value="stats.totalBorrows" />
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <el-statistic title="总归还次数" :value="stats.totalReturns" />
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <el-statistic title="待处理归还" :value="stats.pendingReturns" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 最近记录 -->
      <el-card class="recent-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>最近借出记录</span>
            <el-link type="primary" @click="goTo('/borrow-records')">查看全部</el-link>
          </div>
        </template>
        <el-table :data="recentBorrows" stripe>
          <el-table-column prop="artifact_name" label="文物名称" />
          <el-table-column prop="borrower_name" label="借用人" />
          <el-table-column prop="borrow_date" label="借出日期" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { DocumentAdd, DocumentChecked, FolderOpened, Document } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { borrowApi, type BorrowRecord } from '@/api/borrow'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  totalBorrows: 0,
  totalReturns: 0,
  pendingReturns: 0
})

const recentBorrows = ref<BorrowRecord[]>([])

const goTo = (path: string) => {
  router.push(path)
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

const fetchData = async () => {
  try {
    const [borrowRes] = await Promise.all([
      borrowApi.getList({ page: 1, page_size: 5 })
    ])

    recentBorrows.value = borrowRes.data.items
    stats.value.totalBorrows = borrowRes.data.total
    // TODO: 从后端获取完整的统计数据
    stats.value.totalReturns = 0
    stats.value.pendingReturns = 0
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home-page {
  max-width: 1400px;
  margin: 0 auto;
}

.action-card {
  cursor: pointer;
  transition: transform 0.3s;
  height: 140px;
}

.action-card:hover {
  transform: translateY(-5px);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.card-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.card-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.card-desc {
  font-size: 13px;
  color: #909399;
}

.stat-card {
  text-align: center;
}

.recent-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
