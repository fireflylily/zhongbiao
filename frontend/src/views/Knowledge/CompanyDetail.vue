<template>
  <div class="company-detail">
    <!-- 顶部导航栏 -->
    <div class="detail-header">
      <el-button @click="handleBack" icon="ArrowLeft">返回列表</el-button>
      <div class="header-title">
        <h2>{{ isNewMode ? '新建企业' : (companyData.company_name || '企业详情') }}</h2>
        <el-tag v-if="!isNewMode && companyData.industry_type" type="info">
          {{ getIndustryLabel(companyData.industry_type) }}
        </el-tag>
      </div>
    </div>

    <!-- 加载状态 -->
    <Loading v-if="loading" text="加载企业信息中..." />

    <!-- 详情内容 -->
    <div v-else class="detail-content">
      <!-- Tab 导航 -->
      <el-tabs v-model="activeTab" class="company-tabs" @tab-change="handleTabChange">
        <!-- 基础信息 Tab -->
        <el-tab-pane name="basic">
          <template #label>
            <span class="tab-label">
              <el-icon><OfficeBuilding /></el-icon>
              基础信息
            </span>
          </template>
          <BasicInfoTab
            :company-id="companyId"
            :company-data="companyData"
            :is-new-mode="isNewMode"
            @update="handleDataUpdate"
            @created="handleCompanyCreated"
          />
        </el-tab-pane>

        <!-- 资质信息 Tab -->
        <el-tab-pane name="qualification">
          <template #label>
            <span class="tab-label">
              <el-icon><Medal /></el-icon>
              资质信息
            </span>
          </template>
          <QualificationTab
            :company-id="companyId"
            :company-data="companyData"
            @update="handleDataUpdate"
          />
        </el-tab-pane>

        <!-- 被授权人信息 Tab -->
        <el-tab-pane name="personnel">
          <template #label>
            <span class="tab-label">
              <el-icon><User /></el-icon>
              被授权人信息
            </span>
          </template>
          <PersonnelTab
            :company-id="companyId"
            :company-data="companyData"
            @update="handleDataUpdate"
          />
        </el-tab-pane>

        <!-- 财务信息 Tab -->
        <el-tab-pane name="financial">
          <template #label>
            <span class="tab-label">
              <el-icon><Wallet /></el-icon>
              财务信息
            </span>
          </template>
          <FinancialTab
            :company-id="companyId"
            :company-data="companyData"
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
import { companyApi } from '@/api/endpoints/company'
import { OfficeBuilding, Medal, User, Wallet, ArrowLeft } from '@element-plus/icons-vue'

// 导入Tab组件（暂时注释，后续实现）
import BasicInfoTab from './components/BasicInfoTab.vue'
import QualificationTab from './components/QualificationTab.vue'
import PersonnelTab from './components/PersonnelTab.vue'
import FinancialTab from './components/FinancialTab.vue'

// Router
const route = useRoute()
const router = useRouter()

// Hooks
const { error } = useNotification()

// 状态
const loading = ref(false)
const activeTab = ref('basic')
const companyId = ref<number>(0)
const companyData = ref<any>({})
const isNewMode = ref(false) // 是否为新建模式

// 行业类型映射
const industryMap: Record<string, string> = {
  technology: '科技',
  manufacturing: '制造业',
  finance: '金融',
  education: '教育',
  healthcare: '医疗',
  retail: '零售',
  construction: '建筑',
  other: '其他'
}

// 获取行业标签
const getIndustryLabel = (industryType: string) => {
  return industryMap[industryType] || industryType
}

// 加载企业数据
const loadCompanyData = async () => {
  loading.value = true
  try {
    const response = await companyApi.getCompany(companyId.value)
    if (response.success && response.data) {
      companyData.value = response.data
    } else {
      error('加载失败', '无法获取企业信息')
      handleBack()
    }
  } catch (err) {
    console.error('加载企业数据失败:', err)
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
  // 重新加载企业数据
  await loadCompanyData()
}

// 企业创建成功处理
const handleCompanyCreated = (newCompanyId: number) => {
  // 切换到编辑模式并加载新创建的企业数据
  isNewMode.value = false
  companyId.value = newCompanyId
  // 更新路由，但不触发导航
  router.replace(`/knowledge/company/${newCompanyId}`)
  // 加载企业数据
  loadCompanyData()
}

// 返回列表
const handleBack = () => {
  router.push('/knowledge/company-library')
}

// 生命周期
onMounted(() => {
  // 从路由获取企业ID
  const id = route.params.id

  if (id === 'new') {
    // 新建模式
    isNewMode.value = true
    companyId.value = 0
  } else if (id) {
    // 编辑模式
    companyId.value = parseInt(id as string, 10)
    if (isNaN(companyId.value)) {
      error('参数错误', '无效的企业ID')
      handleBack()
      return
    }
    loadCompanyData()
  } else {
    error('参数错误', '缺少企业ID')
    handleBack()
  }
})
</script>

<style scoped lang="scss">
.company-detail {
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

.company-tabs {
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
