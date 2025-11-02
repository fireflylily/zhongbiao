<template>
  <el-card class="demo-card">
    <template #header>
      <div class="card-header">
        <span>格式化工具演示</span>
        <el-tag type="success">format.ts</el-tag>
      </div>
    </template>

    <!-- 日期格式化 -->
    <el-divider content-position="left">
      <el-icon><Calendar /></el-icon>
      日期格式化
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="formatDate" :code="formatDate(now)">
          {{ formatDate(now) }}
        </demo-item>
        <demo-item label="formatDateTime" :code="formatDateTime(now)">
          {{ formatDateTime(now) }}
        </demo-item>
        <demo-item label="formatRelativeTime" :code="formatRelativeTime(pastTime)">
          {{ formatRelativeTime(pastTime) }}
        </demo-item>
      </el-col>
      <el-col :span="12">
        <demo-item label="自定义格式" :code="formatDate(now, 'YYYY年MM月DD日')">
          {{ formatDate(now, 'YYYY年MM月DD日') }}
        </demo-item>
        <demo-item label="时间格式" :code="formatDate(now, 'HH:mm:ss')">
          {{ formatDate(now, 'HH:mm:ss') }}
        </demo-item>
      </el-col>
    </el-row>

    <!-- 数字格式化 -->
    <el-divider content-position="left">
      <el-icon><Coin /></el-icon>
      数字格式化
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="formatNumber(千分位)" :code="formatNumber(1234567.89, 2)">
          {{ formatNumber(1234567.89, 2) }}
        </demo-item>
        <demo-item label="formatCurrency(货币)" :code="formatCurrency(1234567.89)">
          {{ formatCurrency(1234567.89) }}
        </demo-item>
        <demo-item label="formatPercentage(百分比)" :code="formatPercentage(0.8765)">
          {{ formatPercentage(0.8765) }}
        </demo-item>
      </el-col>
      <el-col :span="12">
        <demo-item label="formatFileSize(文件大小)" :code="formatFileSize(1073741824)">
          {{ formatFileSize(1073741824) }}
        </demo-item>
        <demo-item label="formatFileSize(小文件)" :code="formatFileSize(2048)">
          {{ formatFileSize(2048) }}
        </demo-item>
      </el-col>
    </el-row>

    <!-- 隐私信息格式化 -->
    <el-divider content-position="left">
      <el-icon><Lock /></el-icon>
      隐私信息格式化
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="formatPhone(手机号)" :code="formatPhone('13812345678')">
          {{ formatPhone('13812345678') }}
        </demo-item>
        <demo-item label="formatIdCard(身份证)" :code="formatIdCard('110101199001011234')">
          {{ formatIdCard('110101199001011234') }}
        </demo-item>
      </el-col>
      <el-col :span="12">
        <demo-item label="formatBankCard(银行卡)" :code="formatBankCard('6222000011112222')">
          {{ formatBankCard('6222000011112222') }}
        </demo-item>
      </el-col>
    </el-row>

    <!-- 文本处理 -->
    <el-divider content-position="left">
      <el-icon><Document /></el-icon>
      文本处理
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="truncateText(文本截断)" :code="truncateText(longText, 20)">
          {{ truncateText(longText, 20) }}
        </demo-item>
        <demo-item label="toCamelCase(驼峰)" :code="toCamelCase('user_name')">
          {{ toCamelCase('user_name') }}
        </demo-item>
        <demo-item label="toSnakeCase(下划线)" :code="toSnakeCase('userName')">
          {{ toSnakeCase('userName') }}
        </demo-item>
      </el-col>
      <el-col :span="12">
        <demo-item label="capitalize(首字母大写)" :code="capitalize('hello world')">
          {{ capitalize('hello world') }}
        </demo-item>
      </el-col>
    </el-row>

    <!-- URL参数处理 -->
    <el-divider content-position="left">
      <el-icon><Link /></el-icon>
      URL参数处理
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="24">
        <demo-item
          label="objectToQueryString"
          :code="objectToQueryString({ page: 1, size: 20, keyword: '测试' })"
        >
          {{ objectToQueryString({ page: 1, size: 20, keyword: '测试' }) }}
        </demo-item>
        <demo-item
          label="queryStringToObject"
          :code="JSON.stringify(queryStringToObject('page=1&size=20&keyword=测试'))"
        >
          {{ JSON.stringify(queryStringToObject('page=1&size=20&keyword=测试')) }}
        </demo-item>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Calendar, Coin, Lock, Document, Link } from '@element-plus/icons-vue'
import {
  formatDate,
  formatDateTime,
  formatRelativeTime,
  formatNumber,
  formatCurrency,
  formatPercentage,
  formatFileSize,
  formatPhone,
  formatIdCard,
  formatBankCard,
  truncateText,
  toCamelCase,
  toSnakeCase,
  capitalize,
  objectToQueryString,
  queryStringToObject
} from '@/utils'

// 测试数据
const now = ref(new Date())
const pastTime = ref(Date.now() - 2 * 60 * 60 * 1000) // 2小时前
const longText = ref('这是一段很长的文本内容，用于测试文本截断功能是否正常工作。')
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
    return () => h('div', { class: 'demo-item' }, [
      h('div', { class: 'demo-label' }, props.label),
      h('div', { class: 'demo-result' }, slots.default?.()),
      h('div', { class: 'demo-code' }, h('code', props.code))
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
</style>
