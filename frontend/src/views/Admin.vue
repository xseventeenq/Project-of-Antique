<!-- 系统管理页面（仅管理员） -->
<template>
  <layout>
    <el-card class="admin-card">
      <template #header>
        <div class="card-header">
          <span>系统管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 用户管理 -->
        <el-tab-pane label="用户管理" name="users">
          <div class="tab-header">
            <el-button type="primary" @click="showUserDialog = true">
              新增用户
            </el-button>
          </div>
          <el-table :data="users" stripe v-loading="usersLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column label="角色" width="120">
              <template #default="{ row }">
                <el-tag :type="getRoleTagType(row.role)">
                  {{ getRoleName(row.role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">
                  {{ row.is_active ? '正常' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="handleDeleteUser(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 借出记录管理 -->
        <el-tab-pane label="借出记录" name="borrows">
          <el-table :data="borrows" stripe v-loading="borrowsLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="artifact_name" label="文物名称" width="200" />
            <el-table-column prop="borrower_name" label="借用人" width="120" />
            <el-table-column prop="borrow_date" label="借出日期" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="handleDeleteBorrow(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 归还记录管理 -->
        <el-tab-pane label="归还记录" name="returns">
          <el-table :data="returns" stripe v-loading="returnsLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="artifact_name" label="文物名称" width="200" />
            <el-table-column prop="return_date" label="归还日期" width="120" />
            <el-table-column label="AI 结论" width="120">
              <template #default="{ row }">
                <el-tag
                  v-if="row.comparison_result"
                  :type="getConclusionType(row.comparison_result?.conclusion)"
                >
                  {{ getConclusionText(row.comparison_result?.conclusion) }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="appraiser_name" label="鉴定师" width="120" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="handleDeleteReturn(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新增用户弹窗 -->
    <el-dialog v-model="showUserDialog" title="新增用户" width="500px">
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="鉴定师" value="appraiser" />
            <el-option label="工作人员" value="staff" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUserDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateUser">确定</el-button>
      </template>
    </el-dialog>
  </layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { adminApi } from '@/api/admin'
import { borrowApi, type BorrowRecord } from '@/api/borrow'
import { returnApi, type ReturnRecord } from '@/api/return'
import type { User } from '@/api/auth'

const activeTab = ref('users')
const usersLoading = ref(false)
const borrowsLoading = ref(false)
const returnsLoading = ref(false)

const users = ref<User[]>([])
const borrows = ref<BorrowRecord[]>([])
const returns = ref<ReturnRecord[]>([])

const showUserDialog = ref(false)
const userFormRef = ref<FormInstance>()

const userForm = reactive({
  username: '',
  password: '',
  role: ''
})

const userRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const getRoleName = (role: string) => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    appraiser: '鉴定师',
    staff: '工作人员'
  }
  return roleMap[role] || role
}

const getRoleTagType = (role: string) => {
  const typeMap: Record<string, any> = {
    admin: 'danger',
    appraiser: 'warning',
    staff: 'info'
  }
  return typeMap[role] || 'info'
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

const getConclusionType = (conclusion?: string) => {
  if (!conclusion) return 'info'
  const typeMap: Record<string, any> = {
    authentic: 'success',
    suspicious: 'warning',
    fake: 'danger'
  }
  return typeMap[conclusion] || 'info'
}

const getConclusionText = (conclusion?: string) => {
  if (!conclusion) return '-'
  const textMap: Record<string, string> = {
    authentic: '确认为真品',
    suspicious: '结果存疑',
    fake: '确认为仿品'
  }
  return textMap[conclusion] || conclusion
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchUsers = async () => {
  usersLoading.value = true
  try {
    const response = await adminApi.getUserList({ page: 1, page_size: 100 })
    users.value = response.data.items || response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    usersLoading.value = false
  }
}

const fetchBorrows = async () => {
  borrowsLoading.value = true
  try {
    const response = await borrowApi.getList({ page: 1, page_size: 100 })
    borrows.value = response.data.items
  } catch (error) {
    console.error('获取借出记录失败:', error)
  } finally {
    borrowsLoading.value = false
  }
}

const fetchReturns = async () => {
  returnsLoading.value = true
  try {
    const response = await returnApi.getList({ page: 1, page_size: 100 })
    returns.value = response.data.items
  } catch (error) {
    console.error('获取归还记录失败:', error)
  } finally {
    returnsLoading.value = false
  }
}

const handleCreateUser = async () => {
  if (!userFormRef.value) return

  try {
    await userFormRef.value.validate()
    await adminApi.createUser({
      username: userForm.username,
      password: userForm.password,
      role: userForm.role as any
    })
    ElMessage.success('用户创建成功')
    showUserDialog.value = false
    userFormRef.value.resetFields()
    fetchUsers()
  } catch (error) {
    console.error('创建用户失败:', error)
    ElMessage.error('创建用户失败')
  }
}

const handleDeleteUser = async (user: User) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${user.username}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await adminApi.deleteUser(user.id)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleDeleteBorrow = async (record: BorrowRecord) => {
  try {
    await ElMessageBox.confirm(`确定要删除该借出记录吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await adminApi.deleteBorrowRecord(record.id)
    ElMessage.success('删除成功')
    fetchBorrows()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除借出记录失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleDeleteReturn = async (record: ReturnRecord) => {
  try {
    await ElMessageBox.confirm(`确定要删除该归还记录吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await adminApi.deleteReturnRecord(record.id)
    ElMessage.success('删除成功')
    fetchReturns()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除归还记录失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchUsers()
  fetchBorrows()
  fetchReturns()
})
</script>

<style scoped>
.admin-card {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tab-header {
  margin-bottom: 20px;
}
</style>
