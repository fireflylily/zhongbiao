<!--
  工作台Dashboard页面

  功能:
  - KPI关键指标展示
  - 快捷入口
  - 进行中的项目列表
-->

<template>
  <div class="dashboard-page">
    <!-- KPI统计卡片 -->
    <el-row :gutter="16" class="kpi-cards">
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <Card shadow="hover" :loading="loadingStats">
          <el-statistic title="总项目数" :value="statistics.totalProjects">
            <template #prefix>
              <i class="bi bi-folder-fill statistic-icon" style="color: #409eff"></i>
            </template>
          </el-statistic>
        </Card>
      </el-col>

      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <Card shadow="hover" :loading="loadingStats">
          <el-statistic title="进行中项目" :value="statistics.inProgressProjects">
            <template #prefix>
              <i class="bi bi-clock-fill statistic-icon" style="color: #e6a23c"></i>
            </template>
          </el-statistic>
        </Card>
      </el-col>

      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <Card shadow="hover" :loading="loadingStats">
          <el-statistic title="本月中标" :value="statistics.wonThisMonth">
            <template #prefix>
              <i class="bi bi-trophy-fill statistic-icon" style="color: #67c23a"></i>
            </template>
          </el-statistic>
        </Card>
      </el-col>

      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <Card shadow="hover" :loading="loadingStats">
          <el-statistic title="待处理任务" :value="statistics.pendingTasks">
            <template #prefix>
              <i class="bi bi-list-task statistic-icon" style="color: #f56c6c"></i>
            </template>
          </el-statistic>
        </Card>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <Card title="快捷入口" class="quick-actions-card">
      <div class="quick-actions">
        <div
          v-for="action in quickActions"
          :key="action.name"
          class="action-item"
          @click="handleQuickAction(action)"
        >
          <div class="action-icon" :style="{ background: action.color }">
            <i :class="action.icon"></i>
          </div>
          <div class="action-label">{{ action.label }}</div>
        </div>
      </div>
    </Card>

    <!-- 进行中的项目列表 -->
    <Card title="进行中的项目" class="projects-card">
      <template #actions>
        <IconButton icon="bi-arrow-clockwise" tooltip="刷新" @click="refreshProjects" />
      </template>

      <Loading v-if="loadingProjects" :visible="true" :fullscreen="false" text="加载项目列表..." />

      <Empty v-else-if="projects.length === 0" type="no-data" description="暂无进行中的项目">
        <template #action>
          <el-button type="primary" @click="handleCreateProject">创建第一个项目</el-button>
        </template>
      </Empty>

      <template v-else>
        <el-table :data="projects" stripe style="width: 100%">
          <el-table-column prop="project_name" label="项目名称" min-width="200">
            <template #default="{ row }">
              <el-link type="primary" @click="handleViewProject(row)">
                {{ row.project_name }}
              </el-link>
            </template>
          </el-table-column>

          <el-table-column prop="project_number" label="项目编号" width="150" />

          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="company_name" label="关联企业" width="200" />

          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <IconButton
                icon="bi-eye"
                type="primary"
                tooltip="查看详情"
                @click="handleViewProject(row)"
              />
              <IconButton
                icon="bi-play-circle"
                type="success"
                tooltip="继续处理"
                @click="handleContinueProject(row)"
              />
              <IconButton
                icon="bi-archive"
                type="warning"
                tooltip="归档"
                @click="handleArchiveProject(row)"
              />
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { tenderApi, companyApi } from '@/api'
import { useNotification } from '@/composables'
import { Card, Loading, Empty, IconButton } from '@/components'
import type { Project } from '@/types'
import dayjs from 'dayjs'

// ==================== Composables ====================

const router = useRouter()
const projectStore = useProjectStore()
const { success, error: showError, confirm } = useNotification()

// ==================== State ====================

const loadingStats = ref(false)
const loadingProjects = ref(false)

// KPI统计数据
const statistics = ref({
  totalProjects: 0,
  inProgressProjects: 0,
  wonThisMonth: 0,
  pendingTasks: 0
})

// 项目列表
const projects = ref<Project[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 快捷入口配置
const quickActions = [
  {
    name: 'start-tender',
    label: '开始投标',
    icon: 'bi bi-play-circle-fill',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    route: '/tender-management'
  },
  {
    name: 'business-response',
    label: '商务应答',
    icon: 'bi bi-briefcase-fill',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    route: '/business-response'
  },
  {
    name: 'point-to-point',
    label: '点对点应答',
    icon: 'bi bi-arrow-left-right',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    route: '/point-to-point'
  },
  {
    name: 'tech-proposal',
    label: '技术方案',
    icon: 'bi bi-file-code-fill',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    route: '/tech-proposal'
  },
  {
    name: 'tender-scoring',
    label: '标书评分',
    icon: 'bi bi-star-fill',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    route: '/tender-scoring'
  },
  {
    name: 'knowledge',
    label: '知识中心',
    icon: 'bi bi-book-fill',
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    route: '/knowledge/company-library'
  }
]

// ==================== Computed ====================

// ==================== Methods ====================

/**
 * 加载统计数据
 */
async function loadStatistics(): Promise<void> {
  loadingStats.value = true

  try {
    const response = await tenderApi.getDashboardStatistics()

    if (response.success && response.data) {
      statistics.value = {
        totalProjects: response.data.totalProjects,
        inProgressProjects: response.data.inProgressProjects,
        wonThisMonth: response.data.wonThisMonth,
        pendingTasks: response.data.pendingTasks
      }
    }
  } catch (err: any) {
    showError('加载统计数据失败: ' + err.message)
  } finally {
    loadingStats.value = false
  }
}

/**
 * 加载项目列表
 */
async function loadProjects(): Promise<void> {
  loadingProjects.value = true

  try {
    const response = await tenderApi.getProjects({
      page: currentPage.value,
      page_size: pageSize.value
    })

    if (response.success && response.data) {
      // 处理分页数据
      if (Array.isArray(response.data)) {
        projects.value = response.data
        total.value = response.data.length
      } else if (response.data.items) {
        projects.value = response.data.items
        total.value = response.data.total || 0
      }
    }
  } catch (err: any) {
    showError('加载项目列表失败: ' + err.message)
  } finally {
    loadingProjects.value = false
  }
}

/**
 * 刷新项目列表
 */
async function refreshProjects(): Promise<void> {
  await loadProjects()
  success('刷新成功')
}

/**
 * 处理快捷操作
 */
async function handleQuickAction(action: any): Promise<void> {
  if (action.name === 'start-tender') {
    await handleCreateProject()
  } else {
    router.push(action.route)
  }
}

/**
 * 创建新项目并跳转
 */
async function handleCreateProject(): Promise<void> {
  try {
    // 获取公司列表，使用第一个公司作为默认值
    const companiesResponse = await companyApi.getCompanies()
    const companies = companiesResponse.data || []

    if (companies.length === 0) {
      showError('无法创建项目：请先添加公司信息')
      return
    }

    // 创建空白项目
    const response = await tenderApi.createProject({
      project_name: '新项目',
      project_number: `PRJ-${Date.now()}`,
      company_id: companies[0].company_id
    })

    const projectId = (response as any).project_id
    success('创建成功')

    // 跳转到项目详情页
    router.push({
      name: 'TenderManagementDetail',
      params: { id: projectId }
    })
  } catch (err: any) {
    showError('创建项目失败: ' + err.message)
  }
}

/**
 * 查看项目详情
 */
function handleViewProject(project: Project): void {
  projectStore.setCurrentProject(project as any)
  router.push({
    name: 'TenderManagementDetail',
    params: { id: project.id }
  })
}

/**
 * 继续处理项目
 */
function handleContinueProject(project: Project): void {
  projectStore.setCurrentProject(project as any)
  router.push({
    name: 'TenderManagementDetail',
    params: { id: project.id }
  })
}

/**
 * 归档项目
 */
async function handleArchiveProject(project: Project): Promise<void> {
  const confirmed = await confirm(
    `确定要归档项目"${project.project_name}"吗?`,
    '归档项目',
    '归档后项目将不再显示在进行中列表'
  )

  if (confirmed) {
    try {
      await projectStore.updateProject(project.id, { status: 'archived' as any })
      success('项目已归档')
      await loadProjects()
    } catch (err: any) {
      showError('归档失败: ' + err.message)
    }
  }
}

/**
 * 分页大小变化
 */
function handleSizeChange(size: number): void {
  pageSize.value = size
  currentPage.value = 1
  loadProjects()
}

/**
 * 页码变化
 */
function handlePageChange(page: number): void {
  currentPage.value = page
  loadProjects()
}

/**
 * 获取状态类型
 */
function getStatusType(status: string): string {
  const typeMap: Record<string, string> = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    won: 'success',
    lost: 'danger',
    archived: 'info'
  }
  return typeMap[status] || 'info'
}

/**
 * 获取状态标签
 */
function getStatusLabel(status: string): string {
  const labelMap: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    won: '已中标',
    lost: '未中标',
    archived: '已归档'
  }
  return labelMap[status] || status
}

/**
 * 格式化日期
 */
function formatDate(date: string | Date): string {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// ==================== Lifecycle ====================

onMounted(() => {
  loadStatistics()
  loadProjects()
})
</script>

<style scoped lang="scss">
.dashboard-page {
  // 不设置padding,使用page-content的默认padding即可
  background: var(--bg-light, #f8f9fa);
}

// ==================== KPI卡片 ====================

.kpi-cards {
  margin-bottom: var(--spacing-xl, 32px);
}

.statistic-icon {
  font-size: 24px;
  margin-right: 8px;
}

// ==================== 快捷入口 ====================

.quick-actions-card {
  margin-bottom: var(--spacing-xl, 32px);
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-lg, 24px);
  padding: var(--spacing-md, 16px) 0;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm, 12px);
  padding: var(--spacing-lg, 24px);
  background: var(--bg-white, #ffffff);
  border-radius: var(--border-radius-md, 8px);
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md, 0 4px 12px rgba(0, 0, 0, 0.15));
  }
}

.action-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.action-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #333);
  text-align: center;
}

// ==================== 项目列表 ====================

.projects-card {
  margin-bottom: var(--spacing-xl, 32px);
}

.pagination-wrapper {
  margin-top: var(--spacing-lg, 24px);
  display: flex;
  justify-content: flex-end;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .dashboard-page {
    padding: var(--spacing-md, 16px);
  }

  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md, 16px);
  }

  .action-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }

  .action-label {
    font-size: 12px;
  }

  .pagination-wrapper {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
