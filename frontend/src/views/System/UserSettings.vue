<template>
  <div class="user-settings-page">
    <PageHeader title="用户设置" icon="bi-gear" />

    <div class="settings-container">
      <el-card class="settings-card">
        <el-tabs v-model="activeTab" class="settings-tabs">
          <!-- 修改密码标签页 -->
          <el-tab-pane label="修改密码" name="password">
            <template #label>
              <span class="tab-label">
                <el-icon><Lock /></el-icon>
                修改密码
              </span>
            </template>

            <el-form
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="120px"
              class="password-form"
            >
              <el-form-item label="当前密码" prop="oldPassword">
                <el-input
                  v-model="passwordForm.oldPassword"
                  type="password"
                  placeholder="请输入当前密码"
                  show-password
                  clearable
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="新密码" prop="newPassword">
                <el-input
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="请输入新密码（至少6个字符）"
                  show-password
                  clearable
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
                <template #extra>
                  <el-text type="info" size="small">密码长度至少为6个字符</el-text>
                </template>
              </el-form-item>

              <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入新密码"
                  show-password
                  clearable
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item>
                <el-space>
                  <el-button type="primary" :loading="loading" @click="handleChangePassword">
                    <el-icon><Check /></el-icon>
                    确认修改
                  </el-button>
                  <el-button @click="resetPasswordForm">
                    <el-icon><RefreshLeft /></el-icon>
                    重置
                  </el-button>
                </el-space>
              </el-form-item>
            </el-form>

            <el-alert
              title="温馨提示"
              type="warning"
              :closable="false"
              show-icon
              class="mt-4"
            >
              <ul class="tips-list">
                <li>修改密码后需要重新登录</li>
                <li>请妥善保管您的密码，不要告诉他人</li>
                <li>建议定期更换密码，提高账号安全性</li>
              </ul>
            </el-alert>
          </el-tab-pane>

          <!-- 基本信息标签页 -->
          <el-tab-pane label="基本信息" name="profile">
            <template #label>
              <span class="tab-label">
                <el-icon><User /></el-icon>
                基本信息
              </span>
            </template>

            <el-form label-width="120px" class="profile-form">
              <el-form-item label="用户名">
                <el-input
                  :model-value="userStore.currentUser?.username || '-'"
                  readonly
                  disabled
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="邮箱">
                <el-input
                  :model-value="userStore.currentUser?.email || '-'"
                  readonly
                  disabled
                >
                  <template #prefix>
                    <el-icon><Message /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="角色">
                <el-tag :type="getRoleType(userStore.currentUser?.role)" size="large">
                  {{ userStore.currentUser?.role || '-' }}
                </el-tag>
              </el-form-item>

              <el-form-item label="用户ID">
                <el-text>{{ userStore.currentUser?.id || '-' }}</el-text>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Lock, Check, RefreshLeft, User, Message } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { authApi } from '@/api/endpoints/auth'

const router = useRouter()
const userStore = useUserStore()

// 当前激活的标签页
const activeTab = ref('password')

// 表单引用
const passwordFormRef = ref<FormInstance>()

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 加载状态
const loading = ref(false)

// 表单验证规则
const passwordRules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value && value === passwordForm.oldPassword) {
          callback(new Error('新密码不能与当前密码相同'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

/**
 * 重置密码表单
 */
function resetPasswordForm() {
  passwordFormRef.value?.resetFields()
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

/**
 * 处理修改密码
 */
async function handleChangePassword() {
  if (!passwordFormRef.value) return

  // 验证表单
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true

  try {
    const response = await authApi.changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
      confirm_password: passwordForm.confirmPassword
    })

    if (response.success) {
      ElMessage.success('密码修改成功，请重新登录')

      // 清空表单
      resetPasswordForm()

      // 2秒后退出登录
      setTimeout(async () => {
        await userStore.logout()
        router.push('/login')
      }, 2000)
    } else {
      ElMessage.error(response.message || '修改密码失败')
    }
  } catch (error: any) {
    console.error('修改密码失败:', error)

    // 处理特定错误
    if (error.response?.status === 401) {
      ElMessage.error(error.response.data?.message || '当前密码错误')
    } else {
      ElMessage.error(error.response?.data?.message || '修改密码失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 获取角色标签类型
 */
function getRoleType(role?: string) {
  const roleMap: Record<string, any> = {
    '管理员': 'danger',
    '高级管理': 'danger',
    '项目经理': 'warning',
    '内部员工': 'success',
    '普通用户': 'info'
  }
  return roleMap[role || ''] || 'info'
}
</script>

<style scoped lang="scss">
.user-settings-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.settings-container {
  max-width: 800px;
  margin: 20px auto 0;
}

.settings-card {
  :deep(.el-card__body) {
    padding: 0;
  }
}

.settings-tabs {
  :deep(.el-tabs__header) {
    margin: 0;
    padding: 0 20px;
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
  }

  :deep(.el-tabs__content) {
    padding: 30px 20px;
  }

  .tab-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;

    .el-icon {
      font-size: 16px;
    }
  }
}

.password-form,
.profile-form {
  max-width: 500px;

  :deep(.el-form-item__label) {
    font-weight: 500;
  }

  :deep(.el-input) {
    width: 100%;
  }
}

.tips-list {
  margin: 0;
  padding-left: 20px;
  color: #909399;
  font-size: 13px;
  line-height: 1.8;

  li {
    margin: 4px 0;
  }
}

.mt-4 {
  margin-top: 24px;
}

// 响应式适配
@media (max-width: 768px) {
  .user-settings-page {
    padding: 12px;
  }

  .settings-container {
    margin-top: 12px;
  }

  .password-form,
  .profile-form {
    max-width: 100%;

    :deep(.el-form-item__label) {
      width: 100px !important;
      font-size: 13px;
    }
  }

  .settings-tabs {
    :deep(.el-tabs__header) {
      padding: 0 12px;
    }

    :deep(.el-tabs__content) {
      padding: 20px 12px;
    }

    .tab-label {
      font-size: 13px;

      .el-icon {
        font-size: 14px;
      }
    }
  }
}
</style>
