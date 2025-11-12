<template>
  <div class="case-detail">
    <!-- 顶部导航栏 -->
    <div class="detail-header">
      <el-button @click="handleBack" icon="ArrowLeft">返回列表</el-button>
      <div class="header-title">
        <h2>{{ caseData.case_title || '案例详情' }}</h2>
        <el-tag v-if="caseData.contract_type" :type="caseData.contract_type === '合同' ? 'primary' : 'success'">
          {{ caseData.contract_type }}
        </el-tag>
        <el-tag v-if="caseData.product_category" type="primary">
          {{ caseData.product_category }}
        </el-tag>
      </div>
    </div>

    <!-- 加载状态 -->
    <Loading v-if="loading" text="加载案例信息中..." />

    <!-- 详情内容 -->
    <div v-else class="detail-content">
      <CaseBasicInfoTab
        :case-id="caseId"
        :case-data="caseData"
        @update="handleDataUpdate"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loading } from '@/components'
import { useNotification } from '@/composables'
import { knowledgeApi } from '@/api/endpoints/knowledge'
import { ArrowLeft } from '@element-plus/icons-vue'

// Tab组件
import CaseBasicInfoTab from './components/CaseBasicInfoTab.vue'

// Router
const route = useRoute()
const router = useRouter()

// Hooks
const { error } = useNotification()

// 状态
const loading = ref(false)
const caseId = ref<number>(0)
const caseData = ref<any>({})

// 加载案例数据
const loadCaseData = async () => {
  loading.value = true
  try {
    const response = await knowledgeApi.getCase(caseId.value)
    if (response.success && response.data) {
      caseData.value = response.data
    } else {
      error('加载失败', '无法获取案例信息')
      handleBack()
    }
  } catch (err) {
    console.error('加载案例数据失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
    handleBack()
  } finally {
    loading.value = false
  }
}

// 数据更新处理
const handleDataUpdate = async () => {
  // 重新加载案例数据
  await loadCaseData()
}

// 返回列表
const handleBack = () => {
  router.push('/knowledge/case-library')
}

// 生命周期
onMounted(() => {
  // 从路由获取案例ID
  const id = route.params.id
  if (id) {
    caseId.value = parseInt(id as string, 10)
    if (isNaN(caseId.value)) {
      error('参数错误', '无效的案例ID')
      handleBack()
      return
    }
    loadCaseData()
  } else {
    error('参数错误', '缺少案例ID')
    handleBack()
  }
})
</script>

<style scoped lang="scss">
.case-detail {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  .header-title {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.detail-content {
  // 内容直接展示，无需额外样式
}
</style>
