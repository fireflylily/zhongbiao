<!--
  工作台Dashboard页面

  功能:
  - KPI关键指标展示
  - 项目列表管理（含文档状态、删除等功能）
-->

<template>
  <div class="dashboard-page">
    <!-- KPI统计卡片 -->
    <el-row :gutter="12" class="kpi-cards">
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <div class="kpi-card">
          <div class="kpi-icon" style="background: #ecf5ff; color: #409eff">
            <i class="bi bi-folder-fill"></i>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ statistics.totalProjects }}</div>
            <div class="kpi-label">总项目数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <div class="kpi-card">
          <div class="kpi-icon" style="background: #fdf6ec; color: #e6a23c">
            <i class="bi bi-clock-fill"></i>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ statistics.inProgressProjects }}</div>
            <div class="kpi-label">进行中</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <div class="kpi-card">
          <div class="kpi-icon" style="background: #f0f9eb; color: #67c23a">
            <i class="bi bi-trophy-fill"></i>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ statistics.wonThisMonth }}</div>
            <div class="kpi-label">本月中标</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <div class="kpi-card">
          <div class="kpi-icon" style="background: #fef0f0; color: #f56c6c">
            <i class="bi bi-list-task"></i>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ statistics.pendingTasks }}</div>
            <div class="kpi-label">待处理</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 项目列表 -->
    <Card title="项目列表" class="projects-card">
      <template #actions>
        <el-button type="primary" :loading="creating" @click="handleCreateProject">
          <i class="bi bi-plus-lg"></i> 新建项目
        </el-button>
        <IconButton icon="bi-arrow-clockwise" tooltip="刷新" @click="refreshProjects" />
      </template>

      <Loading v-if="loadingProjects" :visible="true" :fullscreen="false" text="加载项目列表..." />

      <Empty v-else-if="projects.length === 0" type="no-data" description="暂无项目">
        <template #action>
          <el-button type="primary" @click="handleCreateProject">创建第一个项目</el-button>
        </template>
      </Empty>

      <template v-else>
        <el-table :data="projects" stripe style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" fixed />
          <el-table-column prop="project_name" label="项目名称" min-width="200" fixed>
            <template #default="{ row }">
              <el-link type="primary" @click="handleViewProject(row)">
                {{ row.project_name }}
              </el-link>
            </template>
          </el-table-column>

          <el-table-column prop="tenderer" label="招标人" min-width="180" show-overflow-tooltip />
          <el-table-column prop="authorized_person_name" label="被授权人" width="100" />

          <!-- 文档生成状态列 -->
          <el-table-column label="商务应答" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="hasBusinessResponse(row)" type="success" size="small">
                <i class="bi bi-check-circle-fill"></i> 已生成
              </el-tag>
              <el-tag v-else type="info" size="small">
                <i class="bi bi-dash-circle"></i> 未生成
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="技术点对点" width="110" align="center">
            <template #default="{ row }">
              <el-tag v-if="hasPointToPoint(row)" type="success" size="small">
                <i class="bi bi-check-circle-fill"></i> 已生成
              </el-tag>
              <el-tag v-else type="info" size="small">
                <i class="bi bi-dash-circle"></i> 未生成
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="技术方案" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="hasTechProposal(row)" type="success" size="small">
                <i class="bi bi-check-circle-fill"></i> 已生成
              </el-tag>
              <el-tag v-else type="info" size="small">
                <i class="bi bi-dash-circle"></i> 未生成
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="最后融合" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="hasFinalMerge(row)" type="success" size="small">
                <i class="bi bi-check-circle-fill"></i> 已融合
              </el-tag>
              <el-tag v-else type="info" size="small">
                <i class="bi bi-dash-circle"></i> 未融合
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="项目状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'active'" type="success">进行中</el-tag>
              <el-tag v-else-if="row.status === 'completed'" type="primary">已完成</el-tag>
              <el-tag v-else-if="row.status === 'archived'" type="info">已归档</el-tag>
              <el-tag v-else type="info">草稿</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <IconButton
                icon="bi-eye"
                type="primary"
                tooltip="查看详情"
                @click="handleViewProject(row)"
              />
              <IconButton
                icon="bi-trash"
                type="danger"
                tooltip="删除项目"
                @click="handleDeleteProject(row)"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { tenderApi, companyApi } from '@/api'
import { useNotification } from '@/composables'
import { Card, Loading, Empty, IconButton } from '@/components'
import { ElMessageBox } from 'element-plus'
import type { Project } from '@/types'
import dayjs from 'dayjs'

// ==================== Composables ====================

const router = useRouter()
const projectStore = useProjectStore()
const { success, error: showError } = useNotification()

// ==================== State ====================

const loadingStats = ref(false)
const loadingProjects = ref(false)
const creating = ref(false)

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
      // 处理分页数据，转换字段名以匹配前端
      const rawData = response.data.items || response.data || []
      projects.value = rawData.map((project: any) => ({
        id: project.project_id,
        project_name: project.project_name,
        project_number: project.project_number,
        company_name: project.company_name,
        tenderer: project.tenderer,
        authorized_person_name: project.authorized_person_name,
        status: project.status,
        created_at: project.created_at,
        ...project
      }))
      total.value = response.data.total || projects.value.length
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
 * 创建新项目并跳转
 */
async function handleCreateProject(): Promise<void> {
  creating.value = true
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
  } finally {
    creating.value = false
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
 * 删除项目
 */
async function handleDeleteProject(project: Project): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${project.project_name}" 吗？此操作将同时删除项目的所有文档，且不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await tenderApi.deleteProject(project.id)
    success(`已删除项目: ${project.project_name}`)
    await loadProjects()
  } catch (err: any) {
    if (err !== 'cancel') {
      showError('删除失败: ' + (err.message || '未知错误'))
    }
  }
}

/**
 * 判断是否有商务应答文档
 */
function hasBusinessResponse(project: any): boolean {
  return !!project.business_response_file || project.business_response_status === 'completed'
}

/**
 * 判断是否有技术点对点文档
 */
function hasPointToPoint(project: any): boolean {
  return !!project.point_to_point_file || project.point_to_point_status === 'completed'
}

/**
 * 判断是否有技术方案文档
 */
function hasTechProposal(project: any): boolean {
  return !!project.tech_proposal_file || project.tech_proposal_status === 'completed' || !!project.technical_data
}

/**
 * 判断是否有最后融合文档
 */
function hasFinalMerge(project: any): boolean {
  return !!project.final_merge_file || project.merge_status === 'completed'
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
  background: var(--bg-light, #f8f9fa);
}

// ==================== KPI卡片 ====================

.kpi-cards {
  margin-bottom: 16px;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  height: 72px;
}

.kpi-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.kpi-info {
  flex: 1;
  min-width: 0;
}

.kpi-value {
  font-size: 26px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

// ==================== 项目列表 ====================

.projects-card {
  margin-bottom: 16px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .kpi-cards {
    .el-col {
      margin-bottom: 12px;
    }
  }

  .pagination-wrapper {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .kpi-card {
    padding: 12px 16px;
    height: auto;
  }

  .kpi-value {
    font-size: 22px;
  }
}
</style>
