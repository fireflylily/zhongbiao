<template>
  <div class="final-tender-page">
    <!-- 加载状态 -->
    <Loading v-if="loading" text="加载项目列表..." />

    <!-- 主要内容 -->
    <template v-else>
      <!-- 统一的操作面板：项目选择 -->
      <el-card class="main-panel" shadow="never">
        <!-- 第一行：项目和公司选择 -->
        <div class="panel-row project-row">
          <div class="row-item">
            <label class="row-label">选择项目</label>
            <el-select
              v-model="form.projectId"
              placeholder="请选择项目"
              filterable
              @change="handleProjectChange"
              class="row-select"
            >
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="`${project.project_name} (${project.project_number || '-'})`"
                :value="project.id"
              />
            </el-select>
          </div>

          <div class="row-item">
            <label class="row-label">公司</label>
            <el-input
              :value="selectedProject?.company_name || '-'"
              disabled
              class="row-input"
            />
          </div>
        </div>

        <!-- 空状态提示 -->
        <el-empty
          v-if="!hasProjects"
          description="暂无项目"
          :image-size="100"
          style="margin-top: 20px;"
        >
          <template #extra>
            <el-button type="primary" @click="$router.push({ name: 'TenderManagement' })">
              前往项目管理
            </el-button>
          </template>
        </el-empty>

        <!-- 提示信息 -->
        <div v-if="!form.projectId && hasProjects" class="select-hint">
          请选择一个已完成商务应答和技术方案的项目进行整合
        </div>
      </el-card>

      <!-- 文档整合面板 -->
      <DocumentMergePanel
        v-if="form.projectId && selectedProject"
        :project-id="form.projectId"
        :current-documents="currentDocuments"
        :key="form.projectId"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@/components'
import DocumentMergePanel from '@/components/DocumentMergePanel.vue'
import { useProjectDocuments } from '@/composables'
import { useProjectStore } from '@/stores/project'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

// ============================================
// 使用 useProjectDocuments Composable
// ============================================
const {
  projects,
  loading,
  selectedProject,
  currentDocuments,
  hasProjects,
  loadProjects,
  handleProjectChange: handleProjectChangeComposable,
  restoreProjectFromStore
} = useProjectDocuments()

// ============================================
// 页面状态
// ============================================

const form = ref({
  projectId: null as number | null
})

// ============================================
// 方法
// ============================================

/**
 * 项目切换处理
 */
const handleProjectChange = async () => {
  await handleProjectChangeComposable(form.value.projectId, {
    onClear: () => {
      console.log('[最终标书] 项目切换，清空状态')
    },
    onDocumentsLoaded: (docs) => {
      console.log('[最终标书] 项目文档已加载:', docs)

      // 检查是否有必需的文件
      const hasBusinessResponse = !!docs.businessResponseFile
      const hasTechProposal = !!docs.techProposalFile

      if (!hasBusinessResponse || !hasTechProposal) {
        ElMessage.warning('该项目缺少商务应答或技术方案文件，无法整合')
      }
    }
  })

  // 更新URL
  if (form.value.projectId) {
    router.replace({
      name: 'FinalTender',
      query: { projectId: form.value.projectId.toString() }
    })
  }
}

/**
 * 切换项目
 */
const changeProject = () => {
  form.value.projectId = null
  router.replace({ name: 'FinalTender' })
}

/**
 * 刷新页面
 */
const handleRefresh = () => {
  loadProjects()
}

// ============================================
// 生命周期
// ============================================

onMounted(async () => {
  // 加载项目列表
  await loadProjects()

  // 从Store恢复项目（如果是从其他页面跳转过来）
  const restoredProjectId = await restoreProjectFromStore({
    onClear: () => {
      console.log('[最终标书] Store恢复，清空状态')
    },
    onDocumentsLoaded: (docs) => {
      console.log('[最终标书] Store恢复，文档已加载:', docs)
    }
  })

  // 如果成功恢复项目，同步到表单
  if (restoredProjectId) {
    form.value.projectId = restoredProjectId
    console.log('✅ 已从Store恢复项目:', restoredProjectId)
  }

  // 如果URL中有projectId参数，自动选中
  const projectIdFromRoute = route.query.projectId
  if (projectIdFromRoute && !restoredProjectId) {
    const id = Number(projectIdFromRoute)
    if (projects.value.some(p => p.id === id)) {
      form.value.projectId = id
      await handleProjectChange()
    }
  }
})
</script>

<style scoped lang="scss">
.final-tender-page {
  display: flex;
  flex-direction: column;
  gap: 20px;

  // ========================================
  // 统一的主面板样式
  // ========================================
  .main-panel {
    :deep(.el-card__body) {
      padding: 24px;
    }
  }

  .panel-row {
    display: flex;
    gap: 24px;
  }

  .project-row {
    margin-bottom: 24px;  // 1.5倍行距

    .row-item {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 12px;

      .row-label {
        flex-shrink: 0;
        width: 50px;
        font-size: 14px;
        font-weight: 500;
        color: var(--el-text-color-primary);
      }

      .row-select,
      .row-input {
        flex: 1;
      }
    }
  }

  .select-hint {
    margin-top: 20px;
    padding: 16px;
    text-align: center;
    color: var(--el-text-color-secondary);
    font-size: 14px;
    background: var(--el-fill-color-lighter);
    border-radius: 8px;
  }
}
</style>
