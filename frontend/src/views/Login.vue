<!-- 登录页面 -->
<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">古玩字画智能对比系统</h1>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="demo-accounts">
        <p class="demo-title">测试账号:</p>
        <p>管理员: admin / admin123</p>
        <p>鉴定师: appraiser / appraiser123</p>
        <p>工作人员: staff / staff123</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    const response = await authApi.login(loginForm)
    const { access_token, user } = response.data

    // 保存 token 和用户信息
    authStore.setToken(access_token)
    authStore.setUser(user)

    ElMessage.success('登录成功，正在跳转...')

    console.log('[Login] Token saved:', access_token.substring(0, 20) + '...')
    console.log('[Login] User saved:', user)
    console.log('[Login] localStorage token:', localStorage.getItem('token'))

    // 跳转到首页
    setTimeout(() => {
      router.push('/').then(() => {
        console.log('[Login] Navigation succeeded')
      }).catch((err) => {
        console.error('[Login] Navigation failed:', err)
      })
    }, 500)
  } catch (error: any) {
    if (error.response?.status === 401) {
      ElMessage.error('用户名或密码错误')
    } else {
      console.error('登录失败:', error)
      ElMessage.error('登录失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.login-title {
  font-size: 24px;
  font-weight: 500;
  color: #303133;
  text-align: center;
  margin: 0 0 30px 0;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.demo-accounts {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
  font-size: 12px;
  color: #909399;
}

.demo-title {
  font-weight: 500;
  margin-bottom: 10px;
}

.demo-accounts p {
  margin: 5px 0;
}
</style>
