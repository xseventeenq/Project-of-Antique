<!-- 首页 - 简洁型布局 -->
<template>
  <layout>
    <div class="home-page">
      <h1 class="welcome-title">欢迎使用古玩字画智能对比系统</h1>
      <p class="welcome-subtitle">当前用户：{{ authStore.user?.username || '未知' }} ({{ getRoleName(authStore.user?.role || '') }})</p>

      <el-row :gutter="20" style="margin-top: 30px;">
        <!-- 快捷操作卡片 - 需要鉴定师或管理员权限 -->
        <el-col :span="6" v-if="authStore.user?.role === 'admin' || authStore.user?.role === 'appraiser'">
          <el-card class="action-card" shadow="hover" @click="goTo('/borrow')">
            <div class="card-content">
              <el-icon class="card-icon" color="#409eff"><DocumentAdd /></el-icon>
              <div class="card-title">借出存档</div>
              <div class="card-desc">创建新的借出记录</div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6" v-if="authStore.user?.role === 'admin' || authStore.user?.role === 'appraiser'">
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
      <el-card class="recent-card" shadow="never" v-if="recentBorrows.length > 0">
        <template #header>
          <div class="card-header">
            <span>最近借出记录</span>
            <el-link type="primary" @click="goTo('/borrow-records')">查看全部</el-link>
          </div>
        </template>
        <el-table :data="recentBorrows" stripe>
          <el-table-column prop="artifact.name" label="文物名称" />
          <el-table-column prop="artifact.artifact_id" label="文物编号" />
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

      <!-- 空状态提示 -->
      <el-empty v-else description="暂无借出记录" style="margin-top: 20px;" />
    </div>
  </layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { DocumentAdd, DocumentChecked, FolderOpened, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
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
  console.log('[Home] Navigating to:', path)
  router.push(path)
}

const getRoleName = (role: string) => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    appraiser: '鉴定师',
    staff: '工作人员'
  }
  return roleMap[role] || role
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
  console.log('[Home] Fetching data...')
  try {
    const borrowRes = await borrowApi.getList({ page: 1, page_size: 5 })
    console.log('[Home] Data fetched:', borrowRes.data)

    recentBorrows.value = borrowRes.data.items
    stats.value.totalBorrows = borrowRes.data.total
    // TODO: 从后端获取完整的统计数据
    stats.value.totalReturns = 0
    stats.value.pendingReturns = 0
  } catch (error: any) {
    console.error('[Home] 获取数据失败:', error)
    // 不阻塞页面显示，即使数据获取失败也显示空列表
    ElMessage.warning('数据加载失败，显示空列表')
  }
}

onMounted(() => {
  console.log('[Home] Component mounted')
  console.log('[Home] Current user:', authStore.user)
  console.log('[Home] Token exists:', !!authStore.token)
  console.log('[Home] userRole:', authStore.userRole)
  console.log('[Home] isAppraiser():', authStore.isAppraiser())
  fetchData()
})
</script>

<style scoped>
.home-page {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-title {
  font-size: 28px;
  font-weight: 500;
  color: #303133;
  text-align: center;
  margin-bottom: 10px;
}

.welcome-subtitle {
  font-size: 16px;
  color: #606266;
  text-align: center;
  margin-bottom: 30px;
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
