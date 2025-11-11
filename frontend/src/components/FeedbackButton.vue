<template>
  <div class="feedback-button-wrapper">
    <!-- 浮动反馈按钮 -->
    <el-tooltip content="问题登记" placement="right">
      <el-button
        class="feedback-floating-button"
        type="primary"
        :icon="EditPen"
        circle
        size="large"
        @click="dialogVisible = true"
      />
    </el-tooltip>

    <!-- 反馈对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="问题登记"
      width="600px"
      :before-close="handleClose"
    >
      <!-- 自动收集的上下文信息显示（只读） -->
      <el-alert
        v-if="showContext"
        title="以下信息将与您的反馈一起提交"
        type="info"
        :closable="false"
        class="context-alert"
      >
        <div class="context-info">
          <p v-if="contextInfo.username">
            <strong>当前用户:</strong> {{ contextInfo.username }}
          </p>
          <p v-if="contextInfo.projectName">
            <strong>所属项目:</strong> {{ contextInfo.projectName }}
          </p>
          <p v-if="contextInfo.companyName">
            <strong>所属公司:</strong> {{ contextInfo.companyName }}
          </p>
          <p v-if="contextInfo.pageTitle">
            <strong>当前页面:</strong> {{ contextInfo.pageTitle }}
          </p>
        </div>
      </el-alert>

      <!-- 反馈表单 -->
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        class="feedback-form"
      >
        <el-form-item label="反馈类型" prop="feedbackType">
          <el-radio-group v-model="formData.feedbackType">
            <el-radio value="bug">Bug反馈</el-radio>
            <el-radio value="suggestion">功能建议</el-radio>
            <el-radio value="general">一般问题</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="formData.priority">
            <el-radio value="low">低</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="high">高</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="问题描述" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="6"
            placeholder="请详细描述您遇到的问题或建议..."
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            提交
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { EditPen } from '@element-plus/icons-vue'
import { submitFeedback, type FeedbackSubmitData } from '@/api/endpoints/feedback'

// 路由
const route = useRoute()

// 对话框显示状态
const dialogVisible = ref(false)
const submitting = ref(false)

// 表单引用
const formRef = ref<FormInstance>()

// 表单数据
const formData = reactive<{
  content: string
  feedbackType: 'bug' | 'suggestion' | 'general'
  priority: 'low' | 'medium' | 'high'
}>({
  content: '',
  feedbackType: 'general',
  priority: 'medium'
})

// 表单验证规则
const rules: FormRules = {
  content: [
    { required: true, message: '请输入问题描述', trigger: 'blur' },
    { min: 10, message: '问题描述至少10个字符', trigger: 'blur' }
  ],
  feedbackType: [
    { required: true, message: '请选择反馈类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

// 上下文信息（自动收集）
const contextInfo = computed(() => {
  // 从localStorage或全局状态获取用户信息
  // 这里使用简单的示例，实际应从Pinia store获取
  const username = localStorage.getItem('username') || '游客'

  // 从路由信息获取页面上下文
  const pageTitle = route.meta?.title as string || route.name as string || '未知页面'
  const pageRoute = route.path

  // 从路由参数获取项目信息（如果有）
  const projectId = route.params.projectId
    ? Number(route.params.projectId)
    : route.query.projectId
    ? Number(route.query.projectId)
    : undefined

  // 项目名称可以从全局状态获取
  const projectName = localStorage.getItem('currentProjectName') || undefined

  // 公司信息（如果系统有）
  const companyName = localStorage.getItem('companyName') || undefined
  const companyId = localStorage.getItem('companyId')
    ? Number(localStorage.getItem('companyId'))
    : undefined

  return {
    username,
    projectId,
    projectName,
    companyId,
    companyName,
    pageRoute,
    pageTitle
  }
})

// 是否显示上下文信息
const showContext = computed(() => {
  return !!(
    contextInfo.value.username ||
    contextInfo.value.projectName ||
    contextInfo.value.companyName ||
    contextInfo.value.pageTitle
  )
})

// 关闭对话框
const handleClose = () => {
  // 如果有内容，询问是否确认关闭
  if (formData.content.trim()) {
    ElMessageBox.confirm(
      '您有未提交的反馈内容，确定要关闭吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      resetForm()
      dialogVisible.value = false
    }).catch(() => {
      // 取消关闭
    })
  } else {
    resetForm()
    dialogVisible.value = false
  }
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  formData.content = ''
  formData.feedbackType = 'general'
  formData.priority = 'medium'
}

// 提交反馈
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    // 验证表单
    const valid = await formRef.value.validate()
    if (!valid) return

    submitting.value = true

    // 构建提交数据
    const submitData: FeedbackSubmitData = {
      content: formData.content,
      feedbackType: formData.feedbackType,
      priority: formData.priority,
      ...contextInfo.value
    }

    // 调用API提交
    const response = await submitFeedback(submitData)

    if (response.data.success) {
      ElMessage.success(response.data.message || '反馈提交成功，感谢您的宝贵意见！')
      resetForm()
      dialogVisible.value = false
    } else {
      ElMessage.error('提交失败，请稍后重试')
    }
  } catch (error: any) {
    console.error('提交反馈失败:', error)
    ElMessage.error(error.response?.data?.error || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.feedback-button-wrapper {
  // 浮动按钮样式
  .feedback-floating-button {
    position: fixed;
    left: 20px;
    bottom: 20px;
    z-index: 9999;
    width: 56px;
    height: 56px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;

    &:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }
  }

  // 对话框内容样式
  .context-alert {
    margin-bottom: 20px;

    .context-info {
      font-size: 13px;
      line-height: 1.8;

      p {
        margin: 4px 0;
        color: #606266;

        strong {
          color: #303133;
          margin-right: 8px;
        }
      }
    }
  }

  .feedback-form {
    margin-top: 20px;

    :deep(.el-textarea__inner) {
      font-family: inherit;
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
}

// 暗色模式适配
.dark {
  .feedback-floating-button {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);

    &:hover {
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    }
  }

  .context-info p {
    color: var(--el-text-color-regular);

    strong {
      color: var(--el-text-color-primary);
    }
  }
}
</style>
