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
        <el-tag v-if="caseData.case_status" :type="getCaseStatusType(caseData.case_status)">
          {{ getCaseStatusLabel(caseData.case_status) }}
        </el-tag>
      </div>
    </div>

    <!-- 加载状态 -->
    <Loading v-if="loading" text="加载案例信息中..." />

    <!-- 详情内容 -->
    <div v-else class="detail-content">
      <!-- Tab 导航 -->
      <el-tabs v-model="activeTab" class="case-tabs" @tab-change="handleTabChange">
        <!-- 基本信息 Tab -->
        <el-tab-pane name="basic">
          <template #label>
            <span class="tab-label">
              <el-icon><Document /></el-icon>
              基本信息
            </span>
          </template>
          <CaseBasicInfoTab
            :case-id="caseId"
            :case-data="caseData"
            @update="handleDataUpdate"
          />
        </el-tab-pane>

        <!-- 合同信息 Tab -->
        <el-tab-pane name="contract">
          <template #label>
            <span class="tab-label">
              <el-icon><DocumentCopy /></el-icon>
              合同信息
            </span>
          </template>
          <CaseContractInfoTab
            :case-id="caseId"
            :case-data="caseData"
            @update="handleDataUpdate"
          />
        </el-tab-pane>

        <!-- 附件管理 Tab -->
        <el-tab-pane name="attachments">
          <template #label>
            <span class="tab-label">
              <el-icon><Folder /></el-icon>
              附件管理
            </span>
          </template>
          <CaseAttachmentsTab
            :case-id="caseId"
            :case-data="caseData"
            @update="handleDataUpdate"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loading } from '@/components'
import { useNotification } from '@/composables'
import { knowledgeApi } from '@/api/endpoints/knowledge'
import { Document, DocumentCopy, Folder, ArrowLeft } from '@element-plus/icons-vue'

// Tab组件
import CaseBasicInfoTab from './components/CaseBasicInfoTab.vue'
import CaseContractInfoTab from './components/CaseContractInfoTab.vue'
import CaseAttachmentsTab from './components/CaseAttachmentsTab.vue'

// Router
const route = useRoute()
const router = useRouter()

// Hooks
const { error } = useNotification()

// 状态
const loading = ref(false)
const activeTab = ref('basic')
const caseId = ref<number>(0)
const caseData = ref<any>({})

// 案例状态标签类型
const getCaseStatusType = (status: string) => {
  switch (status) {
    case 'success': return 'success'
    case 'in_progress': return 'warning'
    case 'pending_acceptance': return 'info'
    default: return 'info'
  }
}

// 案例状态标签文本
const getCaseStatusLabel = (status: string) => {
  switch (status) {
    case 'success': return '成功'
    case 'in_progress': return '进行中'
    case 'pending_acceptance': return '待验收'
    default: return status
  }
}

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

// Tab 切换处理
const handleTabChange = (tabName: string) => {
  console.log('切换到Tab:', tabName)
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
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.case-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 20px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
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
</style>
