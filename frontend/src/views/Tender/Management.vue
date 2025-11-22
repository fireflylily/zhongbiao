<template>
  <div class="tender-management">
    <Card title="项目列表">
      <template #actions>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          <i class="bi bi-plus-lg"></i> 新建项目
        </el-button>
      </template>

      <Loading v-if="loading" text="加载中..." />
      <Empty v-else-if="!projects.length" type="no-data" description="暂无项目" />
      <el-table v-else :data="projects" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" fixed />
        <el-table-column prop="name" label="项目名称" min-width="200" fixed>
          <template #default="{ row }">
            <el-link type="primary" @click="handleView(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="company_name" label="公司名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.company_name">{{ row.company_name }}</span>
            <el-text v-else type="info" size="small">未关联公司</el-text>
          </template>
        </el-table-column>
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
              @click="handleView(row)"
            />
            <IconButton
              icon="bi-trash"
              type="danger"
              tooltip="删除项目"
              @click="handleDelete(row)"
            />
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div v-if="projects.length > 0" class="pagination-wrapper">
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
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, Loading, Empty, IconButton } from '@/components'
import { useNotification } from '@/composables'
import { tenderApi } from '@/api/endpoints/tender'
import { companyApi } from '@/api/endpoints/company'
import dayjs from 'dayjs'

// 状态
const loading = ref(false)
const creating = ref(false)
const projects = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Hooks
const router = useRouter()
const { success, error } = useNotification()

// 方法
const loadProjects = async () => {
  loading.value = true
  try {
    // 调用API加载项目列表
    const response = await tenderApi.getProjects({
      page: currentPage.value,
      page_size: pageSize.value
    })

    // 处理响应数据，转换字段名以匹配前端
    const rawData = response.data?.items || response.data || []
    projects.value = rawData.map((project: any) => ({
      id: project.project_id,
      name: project.project_name,
      number: project.project_number,
      company_name: project.company_name,
      status: project.status,
      created_at: project.created_at,
      ...project
    }))

    // 更新总数
    total.value = response.data?.total || projects.value.length
  } catch (err) {
    console.error('加载项目列表失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loading.value = false
  }
}

// 判断是否有商务应答文档
const hasBusinessResponse = (project: any): boolean => {
  // 检查是否有商务应答相关文件或数据
  // 可以根据以下字段判断：
  // - project.business_response_file
  // - project.business_response_status
  // - 或者查询 file_storage 表中 business_type='business_response' 的文件
  return project.business_response_file || project.business_response_status === 'completed'
}

// 判断是否有技术点对点文档
const hasPointToPoint = (project: any): boolean => {
  // 检查是否有技术点对点应答文件
  // 可以根据以下字段判断：
  // - project.point_to_point_file
  // - project.point_to_point_status
  return project.point_to_point_file || project.point_to_point_status === 'completed'
}

// 判断是否有技术方案文档
const hasTechProposal = (project: any): boolean => {
  // 检查是否有技术方案文件
  // 可以根据以下字段判断：
  // - project.tech_proposal_file
  // - project.tech_proposal_status
  // - project.technical_data (JSON字段，可能包含方案数据)
  return project.tech_proposal_file || project.tech_proposal_status === 'completed' || !!project.technical_data
}

// 判断是否有最后融合文档
const hasFinalMerge = (project: any): boolean => {
  // 检查是否完成了最终文档融合
  // 可以根据以下字段判断：
  // - project.final_merge_file
  // - project.merge_status
  // - project.status === 'completed' (完成状态可能意味着已融合)
  return project.final_merge_file || project.merge_status === 'completed'
}

const handleView = (row: any) => {
  // 跳转到项目详情页
  router.push({
    name: 'TenderManagementDetail',
    params: { id: row.id }
  })
}

const handleDelete = async (row: any) => {
  try {
    // 确认删除
    if (!confirm(`确定要删除项目 "${row.name}" 吗？此操作将同时删除项目的所有文档，且不可恢复。`)) {
      return
    }

    await tenderApi.deleteProject(row.id)
    success('删除成功', `已删除项目: ${row.name}`)

    // 重新加载列表
    await loadProjects()
  } catch (err) {
    console.error('删除项目失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 创建新项目
const handleCreate = async () => {
  creating.value = true
  try {
    // 获取公司列表（如果有公司，可以默认使用第一个；如果没有，创建时不关联公司）
    const companiesResponse = await companyApi.getCompanies()
    const companies = companiesResponse.data || []

    // 创建空白项目
    // 如果有公司列表，使用第一个公司ID；否则不传company_id（后端会设置为NULL）
    const projectData: any = {
      project_name: '新项目',
      project_number: `PRJ-${Date.now()}`
    }

    // 只有当公司列表不为空时才设置 company_id
    if (companies.length > 0) {
      projectData.company_id = companies[0].company_id
    }

    const response = await tenderApi.createProject(projectData)

    // 后端返回格式: { success: true, project_id: xxx, message: '' }
    // apiClient.post已经返回response.data，所以response就是后端的响应体
    const projectId = (response as any).project_id
    success('创建成功')

    // 跳转到项目详情页
    router.push({
      name: 'TenderManagementDetail',
      params: { id: projectId }
    })
  } catch (err) {
    console.error('创建项目失败:', err)
    const errorMessage = err instanceof Error ? err.message : '未知错误'
    error(`创建项目失败：${errorMessage}`)
  } finally {
    creating.value = false
  }
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadProjects()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadProjects()
}

// 日期格式化
const formatDate = (date: string | Date): string => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 生命周期
onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.tender-management {
  padding: var(--spacing-lg, 24px);
  background: var(--bg-light, #f8f9fa);
  min-height: 100vh;
}

// ==================== 分页 ====================

.pagination-wrapper {
  margin-top: var(--spacing-lg, 24px);
  display: flex;
  justify-content: flex-end;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .tender-management {
    padding: var(--spacing-md, 16px);
  }

  .pagination-wrapper {
    justify-content: center;
  }
}
</style>
