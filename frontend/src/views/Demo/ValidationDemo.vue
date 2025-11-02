<template>
  <el-card class="demo-card">
    <template #header>
      <div class="card-header">
        <span>验证工具演示</span>
        <el-tag type="success">validation.ts</el-tag>
      </div>
    </template>

    <!-- 基础验证 -->
    <el-divider content-position="left">
      <el-icon><CircleCheck /></el-icon>
      基础验证
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="isEmpty(空值检测)">
          <el-space>
            <el-tag :type="isEmpty('') ? 'success' : 'danger'">
              isEmpty('') = {{ isEmpty('') }}
            </el-tag>
            <el-tag :type="!isEmpty('hello') ? 'success' : 'danger'">
              isEmpty('hello') = {{ isEmpty('hello') }}
            </el-tag>
          </el-space>
        </demo-item>

        <demo-item label="isEmail(邮箱验证)">
          <el-space direction="vertical">
            <el-tag :type="isEmail('test@example.com') ? 'success' : 'danger'">
              'test@example.com' = {{ isEmail('test@example.com') }}
            </el-tag>
            <el-tag :type="!isEmail('invalid-email') ? 'success' : 'danger'">
              'invalid-email' = {{ isEmail('invalid-email') }}
            </el-tag>
          </el-space>
        </demo-item>

        <demo-item label="isPhone(手机号验证)">
          <el-space direction="vertical">
            <el-tag :type="isPhone('13812345678') ? 'success' : 'danger'">
              '13812345678' = {{ isPhone('13812345678') }}
            </el-tag>
            <el-tag :type="!isPhone('12345678901') ? 'success' : 'danger'">
              '12345678901' = {{ isPhone('12345678901') }}
            </el-tag>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="isURL(URL验证)">
          <el-space direction="vertical">
            <el-tag :type="isURL('https://example.com') ? 'success' : 'danger'">
              'https://example.com' = {{ isURL('https://example.com') }}
            </el-tag>
            <el-tag :type="!isURL('not-a-url') ? 'success' : 'danger'">
              'not-a-url' = {{ isURL('not-a-url') }}
            </el-tag>
          </el-space>
        </demo-item>

        <demo-item label="isIdCard(身份证验证)">
          <el-space direction="vertical">
            <el-tag :type="isIdCard('110101199001011234') ? 'success' : 'danger'">
              '110101199001011234' = {{ isIdCard('110101199001011234') }}
            </el-tag>
            <el-tag :type="!isIdCard('123456789012345678') ? 'success' : 'danger'">
              '123456789012345678' = {{ isIdCard('123456789012345678') }}
            </el-tag>
          </el-space>
        </demo-item>

        <demo-item label="isCreditCode(统一社会信用代码)">
          <el-space direction="vertical">
            <el-tag :type="isCreditCode('91110000000000000A') ? 'success' : 'danger'">
              '91110000000000000A' = {{ isCreditCode('91110000000000000A') }}
            </el-tag>
            <el-tag :type="!isCreditCode('invalid-code') ? 'success' : 'danger'">
              'invalid-code' = {{ isCreditCode('invalid-code') }}
            </el-tag>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- 文件验证 -->
    <el-divider content-position="left">
      <el-icon><Document /></el-icon>
      文件验证
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="isValidFileType(文件类型验证)">
          <el-space direction="vertical">
            <el-tag :type="isValidFileType('test.pdf', ['.pdf', '.doc']) ? 'success' : 'danger'">
              'test.pdf' in ['.pdf', '.doc'] = {{ isValidFileType('test.pdf', ['.pdf', '.doc']) }}
            </el-tag>
            <el-tag :type="!isValidFileType('test.exe', ['.pdf', '.doc']) ? 'success' : 'danger'">
              'test.exe' in ['.pdf', '.doc'] = {{ isValidFileType('test.exe', ['.pdf', '.doc']) }}
            </el-tag>
          </el-space>
        </demo-item>

        <demo-item label="isValidFileSize(文件大小验证)">
          <el-space direction="vertical">
            <el-tag :type="isValidFileSize(5 * 1024 * 1024, 10 * 1024 * 1024) ? 'success' : 'danger'">
              5MB ≤ 10MB = {{ isValidFileSize(5 * 1024 * 1024, 10 * 1024 * 1024) }}
            </el-tag>
            <el-tag :type="!isValidFileSize(15 * 1024 * 1024, 10 * 1024 * 1024) ? 'success' : 'danger'">
              15MB ≤ 10MB = {{ isValidFileSize(15 * 1024 * 1024, 10 * 1024 * 1024) }}
            </el-tag>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="checkPasswordStrength(密码强度)">
          <el-space direction="vertical">
            <el-tag>弱密码 '123456' = {{ checkPasswordStrength('123456') }}</el-tag>
            <el-tag type="warning">中等 'abc123' = {{ checkPasswordStrength('abc123') }}</el-tag>
            <el-tag type="success">强 'Abc123!@#' = {{ checkPasswordStrength('Abc123!@#') }}</el-tag>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- Element Plus 表单验证规则 -->
    <el-divider content-position="left">
      <el-icon><Edit /></el-icon>
      Element Plus 表单验证规则
    </el-divider>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱" />
          </el-form-item>

          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>

          <el-form-item label="身份证号" prop="idCard">
            <el-input v-model="form.idCard" placeholder="请输入身份证号" />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" />
          </el-form-item>

          <el-form-item label="URL" prop="url">
            <el-input v-model="form.url" placeholder="请输入网址" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item>
        <el-button type="primary" @click="submitForm">验证表单</el-button>
        <el-button @click="resetForm">重置表单</el-button>
      </el-form-item>
    </el-form>

    <!-- 验证结果 -->
    <el-alert v-if="validationResult" :type="validationResult.type" :title="validationResult.message" show-icon />
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { CircleCheck, Document, Edit } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import {
  isEmpty,
  isEmail,
  isPhone,
  isURL,
  isIdCard,
  isCreditCode,
  isValidFileType,
  isValidFileSize,
  checkPasswordStrength,
  required,
  emailRule,
  phoneRule,
  idCardRule,
  passwordRule,
  urlRule
} from '@/utils'

// 表单数据
const form = reactive({
  email: '',
  phone: '',
  idCard: '',
  password: '',
  confirmPassword: '',
  url: ''
})

// 表单引用
const formRef = ref<FormInstance>()

// 验证规则
const rules = {
  email: [required('请输入邮箱'), emailRule()],
  phone: [required('请输入手机号'), phoneRule()],
  idCard: [required('请输入身份证号'), idCardRule()],
  password: [required('请输入密码'), passwordRule()],
  confirmPassword: [
    required('请再次输入密码'),
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  url: [urlRule()]
}

// 验证结果
const validationResult = ref<{ type: 'success' | 'error'; message: string } | null>(null)

// 提交表单
async function submitForm() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    validationResult.value = {
      type: 'success',
      message: '表单验证通过！所有字段都符合要求。'
    }
  } catch (error) {
    validationResult.value = {
      type: 'error',
      message: '表单验证失败！请检查输入的内容。'
    }
  }
}

// 重置表单
function resetForm() {
  formRef.value?.resetFields()
  validationResult.value = null
}
</script>

<script lang="ts">
// DemoItem 组件
import { defineComponent, h } from 'vue'

const DemoItem = defineComponent({
  name: 'DemoItem',
  props: {
    label: String,
    code: String
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'demo-item' }, [
        h('div', { class: 'demo-label' }, props.label),
        h('div', { class: 'demo-result' }, slots.default?.()),
        props.code ? h('div', { class: 'demo-code' }, h('code', props.code)) : null
      ])
  }
})

export default {
  components: { DemoItem }
}
</script>

<style scoped lang="scss">
.demo-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.demo-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;

  .demo-label {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
    font-weight: 500;
  }

  .demo-result {
    font-size: 16px;
    color: #303133;
    margin-bottom: 8px;
    padding: 8px;
    background: white;
    border-radius: 4px;
  }

  .demo-code {
    font-size: 12px;
    color: #909399;

    code {
      background: #e9ecef;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }
  }
}

:deep(.el-divider) {
  margin: 24px 0;

  .el-divider__text {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #409eff;
  }
}

:deep(.el-form) {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

:deep(.el-alert) {
  margin-top: 20px;
}
</style>
