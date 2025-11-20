<template>
  <div class="final-tender-page">
    <!-- 页面头部 -->
    <PageHeader title="最终标书" :show-back="false">
      <template #actions>
        <el-button @click="handleRefresh">
          <i class="bi bi-arrow-clockwise"></i> 刷新
        </el-button>
      </template>
    </PageHeader>

    <!-- 加载状态 -->
    <Loading v-if="loading" text="加载项目列表..." />

    <!-- 主要内容 -->
    <template v-else>
      <!-- 项目选择器 -->
      <el-card v-if="!form.projectId" class="project-selector-card" shadow="never">
        <div class="selector-content">
          <div class="selector-icon">
            <i class="bi bi-folder2-open"></i>
          </div>
          <h3>请选择要整合的项目</h3>
          <p class="text-muted">
            从下方列表中选择一个已完成商务应答和技术方案的项目
          </p>

          <el-select
            v-model="form.projectId"
            placeholder="选择项目"
            size="large"
            filterable
            class="project-select"
            @change="handleProjectChange"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="`${project.project_name} (${project.project_number || '-'})`"
              :value="project.id"
            >
              <div class="project-option">
                <span class="project-name">{{ project.project_name }}</span>
                <div class="project-status">
                  <el-tag type="info" size="small">{{ project.company_name }}</el-tag>
                </div>
              </div>
            </el-option>
          </el-select>

          <!-- 空状态提示 -->
          <el-empty
            v-if="!hasProjects"
            description="暂无项目"
            :image-size="120"
          >
            <template #extra>
              <el-button type="primary" @click="$router.push({ name: 'TenderManagement' })">
                <i class="bi bi-folder-plus"></i> 前往项目管理
              </el-button>
            </template>
          </el-empty>
        </div>
      </el-card>

      <!-- 当前项目信息 -->
      <template v-if="form.projectId && selectedProject">
        <el-card class="current-project-card" shadow="never">
          <div class="project-info">
            <div class="project-header">
              <h3>
                <i class="bi bi-folder-check"></i>
                {{ selectedProject.project_name }}
              </h3>
              <el-button size="small" text @click="changeProject">
                <i class="bi bi-arrow-left-right"></i> 切换项目
              </el-button>
            </div>
            <p class="project-meta">
              公司：{{ selectedProject.company_name }} |
              项目编号：{{ selectedProject.project_number || '-' }} |
              创建时间：{{ selectedProject.created_at }}
            </p>
          </div>
        </el-card>

        <!-- 文档整合面板 -->
        <DocumentMergePanel
          :project-id="form.projectId"
          :current-documents="currentDocuments"
          :key="form.projectId"
        />
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PageHeader, Loading } from '@/components'
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
  padding: 20px;

  .project-selector-card {
    margin-bottom: 20px;

    .selector-content {
      text-align: center;
      padding: 40px 20px;

      .selector-icon {
        font-size: 64px;
        color: var(--el-color-primary);
        margin-bottom: 20px;
      }

      h3 {
        margin: 0 0 12px 0;
        font-size: 24px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .text-muted {
        margin: 0 0 32px 0;
        color: var(--el-text-color-secondary);
      }

      .project-select {
        width: 100%;
        max-width: 500px;
      }

      .project-option {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        gap: 12px;

        .project-name {
          flex: 1;
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .project-status {
          display: flex;
          gap: 4px;
          flex-shrink: 0;
        }
      }
    }
  }

  .current-project-card {
    margin-bottom: 20px;

    .project-info {
      .project-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;

        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--el-text-color-primary);

          i {
            margin-right: 8px;
            color: var(--el-color-success);
          }
        }
      }

      .project-meta {
        margin: 0;
        font-size: 14px;
        color: var(--el-text-color-secondary);
      }
    }
  }
}
</style>
