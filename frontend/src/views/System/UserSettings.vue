<template>
  <div class="user-settings-page">
    <div class="container py-4">
      <PageHeader title="用户设置" icon="bi-gear" />

      <!-- 设置面板 -->
      <div class="row mt-4">
        <div class="col-md-3">
          <!-- 左侧导航 -->
          <div class="card">
            <div class="list-group list-group-flush">
              <a
                href="#"
                :class="['list-group-item', 'list-group-item-action', { active: activeTab === 'password' }]"
                @click.prevent="activeTab = 'password'"
              >
                <i class="bi bi-key me-2"></i>
                修改密码
              </a>
              <a
                href="#"
                :class="['list-group-item', 'list-group-item-action', { active: activeTab === 'profile' }]"
                @click.prevent="activeTab = 'profile'"
              >
                <i class="bi bi-person me-2"></i>
                基本信息
              </a>
            </div>
          </div>
        </div>

        <div class="col-md-9">
          <!-- 修改密码 -->
          <div v-if="activeTab === 'password'" class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-key me-2"></i>
                修改密码
              </h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="handleChangePassword">
                <!-- 旧密码 -->
                <div class="mb-3">
                  <label for="oldPassword" class="form-label">当前密码 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      id="oldPassword"
                      v-model="passwordForm.oldPassword"
                      :type="showOldPassword ? 'text' : 'password'"
                      class="form-control"
                      :class="{ 'is-invalid': errors.oldPassword }"
                      placeholder="请输入当前密码"
                      required
                    />
                    <button
                      class="btn btn-outline-secondary"
                      type="button"
                      @click="showOldPassword = !showOldPassword"
                    >
                      <i :class="showOldPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="errors.oldPassword" class="invalid-feedback">
                      {{ errors.oldPassword }}
                    </div>
                  </div>
                </div>

                <!-- 新密码 -->
                <div class="mb-3">
                  <label for="newPassword" class="form-label">新密码 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      id="newPassword"
                      v-model="passwordForm.newPassword"
                      :type="showNewPassword ? 'text' : 'password'"
                      class="form-control"
                      :class="{ 'is-invalid': errors.newPassword }"
                      placeholder="请输入新密码（至少6个字符）"
                      required
                    />
                    <button
                      class="btn btn-outline-secondary"
                      type="button"
                      @click="showNewPassword = !showNewPassword"
                    >
                      <i :class="showNewPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="errors.newPassword" class="invalid-feedback">
                      {{ errors.newPassword }}
                    </div>
                  </div>
                  <small class="form-text text-muted">密码长度至少为6个字符</small>
                </div>

                <!-- 确认新密码 -->
                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">确认新密码 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <input
                      id="confirmPassword"
                      v-model="passwordForm.confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      class="form-control"
                      :class="{ 'is-invalid': errors.confirmPassword }"
                      placeholder="请再次输入新密码"
                      required
                    />
                    <button
                      class="btn btn-outline-secondary"
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                    >
                      <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="errors.confirmPassword" class="invalid-feedback">
                      {{ errors.confirmPassword }}
                    </div>
                  </div>
                </div>

                <!-- 提交按钮 -->
                <div class="d-flex justify-content-end gap-2">
                  <button
                    type="button"
                    class="btn btn-secondary"
                    @click="resetPasswordForm"
                  >
                    <i class="bi bi-x-circle me-1"></i>
                    重置
                  </button>
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status"></span>
                    <i v-else class="bi bi-check-circle me-1"></i>
                    确认修改
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- 基本信息 -->
          <div v-if="activeTab === 'profile'" class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-person me-2"></i>
                基本信息
              </h5>
            </div>
            <div class="card-body">
              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">用户名</label>
                <div class="col-sm-9">
                  <input type="text" readonly class="form-control-plaintext" :value="userStore.user?.username || '-'" />
                </div>
              </div>
              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">邮箱</label>
                <div class="col-sm-9">
                  <input type="text" readonly class="form-control-plaintext" :value="userStore.user?.email || '-'" />
                </div>
              </div>
              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">角色</label>
                <div class="col-sm-9">
                  <input type="text" readonly class="form-control-plaintext" :value="userStore.user?.role || '-'" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { showToast } from '@/utils/toast'
import PageHeader from '@/components/PageHeader.vue'
import { authApi } from '@/api/endpoints/auth'

const router = useRouter()
const userStore = useUserStore()

// 当前激活的标签页
const activeTab = ref('password')

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 显示/隐藏密码
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// 表单错误
const errors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 加载状态
const loading = ref(false)

/**
 * 重置密码表单
 */
function resetPasswordForm() {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  errors.oldPassword = ''
  errors.newPassword = ''
  errors.confirmPassword = ''
  showOldPassword.value = false
  showNewPassword.value = false
  showConfirmPassword.value = false
}

/**
 * 验证表单
 */
function validateForm(): boolean {
  // 清空错误
  errors.oldPassword = ''
  errors.newPassword = ''
  errors.confirmPassword = ''

  let isValid = true

  // 验证旧密码
  if (!passwordForm.oldPassword) {
    errors.oldPassword = '请输入当前密码'
    isValid = false
  }

  // 验证新密码
  if (!passwordForm.newPassword) {
    errors.newPassword = '请输入新密码'
    isValid = false
  } else if (passwordForm.newPassword.length < 6) {
    errors.newPassword = '新密码长度至少为6个字符'
    isValid = false
  }

  // 验证确认密码
  if (!passwordForm.confirmPassword) {
    errors.confirmPassword = '请确认新密码'
    isValid = false
  } else if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  // 验证新旧密码不同
  if (passwordForm.oldPassword && passwordForm.newPassword && passwordForm.oldPassword === passwordForm.newPassword) {
    errors.newPassword = '新密码不能与当前密码相同'
    isValid = false
  }

  return isValid
}

/**
 * 处理修改密码
 */
async function handleChangePassword() {
  // 验证表单
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const response = await authApi.changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
      confirm_password: passwordForm.confirmPassword
    })

    if (response.success) {
      showToast.success('密码修改成功，请重新登录')

      // 清空表单
      resetPasswordForm()

      // 2秒后退出登录
      setTimeout(async () => {
        await userStore.logout()
        router.push('/login')
      }, 2000)
    } else {
      showToast.error(response.message || '修改密码失败')
    }
  } catch (error: any) {
    console.error('修改密码失败:', error)

    // 处理特定错误
    if (error.response?.status === 401) {
      if (error.response.data?.message) {
        errors.oldPassword = error.response.data.message
      } else {
        errors.oldPassword = '当前密码错误'
      }
    } else {
      showToast.error(error.response?.data?.message || '修改密码失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.user-settings-page {
  min-height: 100vh;
  background-color: #f8f9fa;

  .list-group-item {
    border-left: 3px solid transparent;
    transition: all 0.2s;

    &:hover {
      background-color: #f8f9fa;
    }

    &.active {
      border-left-color: #0d6efd;
      background-color: #e7f1ff;
      color: #0d6efd;
    }

    i {
      width: 20px;
    }
  }

  .card {
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border: none;
  }

  .card-header {
    background-color: #fff;
    border-bottom: 2px solid #f0f0f0;
  }

  .input-group {
    .btn-outline-secondary {
      border-color: #ced4da;

      &:hover {
        background-color: #e9ecef;
        border-color: #ced4da;
        color: #495057;
      }
    }
  }

  .form-control-plaintext {
    color: #495057;
  }
}
</style>
