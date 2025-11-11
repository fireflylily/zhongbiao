<template>
  <div class="resume-detail">
    <!-- 顶部导航栏 -->
    <div class="detail-header">
      <el-button @click="handleBack" icon="ArrowLeft">返回列表</el-button>
      <div class="header-title">
        <h2>{{ resumeData.name || '简历详情' }}</h2>
        <el-tag v-if="resumeData.education_level" :type="getEducationTagType(resumeData.education_level)">
          {{ resumeData.education_level }}
        </el-tag>
        <el-tag v-if="resumeData.current_position" type="info">
          {{ resumeData.current_position }}
        </el-tag>
        <el-tag v-if="resumeData.status" :type="getStatusTagType(resumeData.status)">
          {{ getStatusLabel(resumeData.status) }}
        </el-tag>
      </div>
    </div>

    <!-- 加载状态 -->
    <Loading v-if="loading" text="加载简历信息中..." />

    <!-- 详情内容 -->
    <div v-else class="detail-content">
      <!-- Tab 导航 -->
      <el-tabs v-model="activeTab" class="resume-tabs" @tab-change="handleTabChange">
        <!-- 基本信息 Tab -->
        <el-tab-pane name="basic">
          <template #label>
            <span class="tab-label">
              <el-icon><User /></el-icon>
              基本信息
            </span>
          </template>
          <ResumeBasicInfoTab
            :resume-id="resumeId"
            :resume-data="resumeData"
            @update="handleDataUpdate"
          />
        </el-tab-pane>

        <!-- 教育信息 Tab -->
        <el-tab-pane name="education">
          <template #label>
            <span class="tab-label">
              <el-icon><Reading /></el-icon>
              教育信息
            </span>
          </template>
          <ResumeEducationTab
            :resume-id="resumeId"
            :resume-data="resumeData"
            @update="handleDataUpdate"
          />
        </el-tab-pane>

        <!-- 工作信息 Tab -->
        <el-tab-pane name="work">
          <template #label>
            <span class="tab-label">
              <el-icon><Briefcase /></el-icon>
              工作信息
            </span>
          </template>
          <ResumeWorkTab
            :resume-id="resumeId"
            :resume-data="resumeData"
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
          <ResumeAttachmentsTab
            :resume-id="resumeId"
            :resume-data="resumeData"
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
import { User, Reading, Briefcase, Folder, ArrowLeft } from '@element-plus/icons-vue'

// Tab组件
import ResumeBasicInfoTab from './components/ResumeBasicInfoTab.vue'
import ResumeEducationTab from './components/ResumeEducationTab.vue'
import ResumeWorkTab from './components/ResumeWorkTab.vue'
import ResumeAttachmentsTab from './components/ResumeAttachmentsTab.vue'

// Router
const route = useRoute()
const router = useRouter()

// Hooks
const { error } = useNotification()

// 状态
const loading = ref(false)
const activeTab = ref('basic')
const resumeId = ref<number>(0)
const resumeData = ref<any>({})

// 学历标签类型
const getEducationTagType = (education: string) => {
  if (education === '博士') return 'danger'
  if (education === '硕士') return 'warning'
  if (education === '本科') return 'success'
  return 'info'
}

// 状态标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'warning'
    case 'archived': return 'info'
    default: return 'info'
  }
}

// 状态标签文本
const getStatusLabel = (status: string) => {
  switch (status) {
    case 'active': return '活跃'
    case 'inactive': return '离职'
    case 'archived': return '已归档'
    default: return status
  }
}

// 加载简历数据
const loadResumeData = async () => {
  loading.value = true
  try {
    const response = await knowledgeApi.getResume(resumeId.value)
    if (response.success && response.data) {
      resumeData.value = response.data
    } else {
      error('加载失败', '无法获取简历信息')
      handleBack()
    }
  } catch (err) {
    console.error('加载简历数据失败:', err)
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
  // 重新加载简历数据
  await loadResumeData()
}

// 返回列表
const handleBack = () => {
  router.push('/knowledge/resume-library')
}

// 生命周期
onMounted(() => {
  // 从路由获取简历ID
  const id = route.params.id
  if (id) {
    resumeId.value = parseInt(id as string, 10)
    if (isNaN(resumeId.value)) {
      error('参数错误', '无效的简历ID')
      handleBack()
      return
    }
    loadResumeData()
  } else {
    error('参数错误', '缺少简历ID')
    handleBack()
  }
})
</script>

<style scoped lang="scss">
.resume-detail {
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

.resume-tabs {
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
