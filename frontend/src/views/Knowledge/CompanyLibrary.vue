<template>
  <div class="company-library">
    <!-- 统计信息 -->
    <div class="stats-bar">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#409eff"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">总企业数</div>
            <div class="stat-value">{{ allCompanies.length }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#67c23a"><Filter /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">筛选结果</div>
            <div class="stat-value">{{ filteredCompanies.length }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <Card title="企业列表">
      <!-- 搜索和筛选区域 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filters">
          <el-form-item label="搜索">
            <el-input
              v-model="filters.keyword"
              placeholder="搜索企业名称、社会信用代码..."
              clearable
              style="width: 300px"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="行业类型">
            <el-select
              v-model="filters.industry"
              placeholder="全部行业"
              clearable
              style="width: 150px"
              @change="handleSearch"
            >
              <el-option label="全部行业" value="" />
              <el-option label="科技" value="technology" />
              <el-option label="制造业" value="manufacturing" />
              <el-option label="金融" value="finance" />
              <el-option label="教育" value="education" />
              <el-option label="医疗" value="healthcare" />
              <el-option label="零售" value="retail" />
              <el-option label="建筑" value="construction" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="handleResetFilters">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
          </el-form-item>
          <el-form-item style="margin-left: auto;">
            <el-dropdown split-button type="primary" @click="handleCreate" @command="handleCreateCommand">
              <el-icon><Plus /></el-icon>
              新建企业
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="manual">
                    <el-icon><Edit /></el-icon>
                    手动创建
                  </el-dropdown-item>
                  <el-dropdown-item command="extract" divided>
                    <el-icon><DocumentCopy /></el-icon>
                    从标书创建
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-form-item>
        </el-form>
      </div>

      <!-- 智能提取对话框 -->
      <CompanyInfoExtractorDialog
        v-model="showExtractorDialog"
        @success="handleExtractSuccess"
      />

      <Loading v-if="loading" text="加载中..." />
      <Empty v-else-if="!filteredCompanies.length" type="no-data" description="暂无企业数据" />
      <el-table v-else :data="filteredCompanies" stripe style="width: 100%">
        <el-table-column prop="company_id" label="ID" width="70" fixed />
        <el-table-column prop="company_name" label="企业名称" min-width="200" fixed show-overflow-tooltip />
        <el-table-column prop="social_credit_code" label="统一社会信用代码" width="180" show-overflow-tooltip />
        <el-table-column prop="legal_representative" label="法定代表人" width="120" />
        <el-table-column prop="registered_capital" label="注册资本" width="120" />
        <el-table-column prop="employee_count" label="员工人数" width="100" align="center" />
        <el-table-column label="资质完成度" width="180" align="center">
          <template #default="{ row }">
            <div class="qualification-progress">
              <el-progress
                :percentage="row.qualification_progress || 0"
                :color="getProgressColor(row.qualification_progress || 0)"
                :stroke-width="8"
              />
              <span class="progress-text">{{ row.qualification_completed || 0 }}/{{ row.qualification_total || 17 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="product_count" label="产品数" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.product_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="document_count" label="文档数" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success">{{ row.document_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" width="160" show-overflow-tooltip />

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="handleView(row)">
              查看详情
            </el-button>
            <el-button text type="warning" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </Card>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, Loading, Empty } from '@/components'
import { useNotification } from '@/composables'
import { companyApi } from '@/api/endpoints/company'
import { OfficeBuilding, Filter, Search, RefreshLeft, Plus, Edit, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import CompanyInfoExtractorDialog from '@/components/CompanyInfoExtractorDialog.vue'

// Router
const router = useRouter()

// Hooks
const { success, error } = useNotification()

// 状态
const loading = ref(false)
const allCompanies = ref<any[]>([])
const filters = ref({
  keyword: '',
  industry: ''
})
const showExtractorDialog = ref(false) // 智能提取对话框


// 标准资质类型总数（与后端保持一致）
const STANDARD_QUALIFICATION_TOTAL = 17

// 计算属性：筛选后的企业列表
const filteredCompanies = computed(() => {
  let result = [...allCompanies.value]

  // 关键词搜索
  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    result = result.filter((company) => {
      return (
        company.company_name?.toLowerCase().includes(keyword) ||
        company.social_credit_code?.toLowerCase().includes(keyword) ||
        company.company_code?.toLowerCase().includes(keyword)
      )
    })
  }

  // 行业筛选
  if (filters.value.industry) {
    result = result.filter((company) => company.industry_type === filters.value.industry)
  }

  return result
})

// 方法
const loadCompanies = async () => {
  loading.value = true
  try {
    // 调用API加载企业列表
    const response = await companyApi.getCompanies()

    // 处理响应数据
    const rawData = response.data || []

    // 为每个企业加载资质信息并计算完成度
    const companiesWithQualifications = await Promise.all(
      rawData.map(async (company: any) => {
        let qualificationCompleted = 0

        // 尝试获取企业资质信息
        try {
          const qualResponse = await companyApi.getCompanyQualifications(company.company_id)
          if (qualResponse.data) {
            // 计算已上传的资质数量
            qualificationCompleted = Object.keys(qualResponse.data).length
          }
        } catch (err) {
          console.error(`加载企业${company.company_id}资质信息失败:`, err)
        }

        const qualificationTotal = STANDARD_QUALIFICATION_TOTAL
        const qualificationProgress = qualificationTotal > 0
          ? Math.round((qualificationCompleted / qualificationTotal) * 100)
          : 0

        return {
          company_id: company.company_id,
          company_name: company.company_name || '未命名',
          company_code: company.company_code || '',
          social_credit_code: company.social_credit_code || '-',
          legal_representative: company.legal_representative || '-',
          registered_capital: company.registered_capital || '-',
          employee_count: company.employee_count || '-',
          industry_type: company.industry_type || '',
          product_count: company.product_count || 0,
          document_count: company.document_count || 0,
          qualification_completed: qualificationCompleted,
          qualification_total: qualificationTotal,
          qualification_progress: qualificationProgress,
          created_at: company.created_at || '-',
          updated_at: company.updated_at || '-',
          ...company
        }
      })
    )

    allCompanies.value = companiesWithQualifications
  } catch (err) {
    console.error('加载企业列表失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  // 筛选逻辑由 computed 自动处理
}

// 重置筛选
const handleResetFilters = () => {
  filters.value.keyword = ''
  filters.value.industry = ''
}

// 进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

// 新建企业 - 直接跳转到企业详情页
const handleCreate = () => {
  router.push('/knowledge/company/new')
}

// 下拉菜单命令处理
const handleCreateCommand = (command: string) => {
  if (command === 'manual') {
    router.push('/knowledge/company/new')
  } else if (command === 'extract') {
    showExtractorDialog.value = true
  }
}

// 智能提取成功处理
const handleExtractSuccess = (newCompanyId: number) => {
  // 跳转到新创建的公司详情页
  router.push(`/knowledge/company/${newCompanyId}`)
}

// 查看详情
const handleView = (row: any) => {
  // TODO: 跳转到详情页
  router.push(`/knowledge/company/${row.company_id}`)
}

// 编辑企业
const handleEdit = (row: any) => {
  // TODO: 跳转到编辑页（与详情页相同）
  router.push(`/knowledge/company/${row.company_id}`)
}

// 删除企业
const handleDelete = async (row: any) => {
  try {
    // 确认删除
    await ElMessageBox.confirm(
      `确定要删除企业 "${row.company_name}" 吗？此操作将同时删除企业的所有产品和文档，且不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await companyApi.deleteCompany(row.company_id)
    success('删除成功', `已删除企业: ${row.company_name}`)

    // 重新加载列表
    await loadCompanies()
  } catch (err) {
    console.error('删除企业失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 生命周期
onMounted(() => {
  loadCompanies()
})
</script>

<style scoped lang="scss">
.company-library {
  // 移除padding，避免与page-content的padding叠加
}

.stats-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;

  .stat-card {
    flex: 1;
    cursor: default;

    :deep(.el-card__body) {
      padding: 16px;
    }

    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .stat-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        background: #f0f9ff;
        border-radius: 12px;
      }

      .stat-info {
        flex: 1;

        .stat-label {
          font-size: 14px;
          color: #909399;
          margin-bottom: 4px;
        }

        .stat-value {
          font-size: 28px;
          font-weight: bold;
          color: #303133;
        }
      }
    }
  }
}

.filter-section {
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;

  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.qualification-progress {
  display: flex;
  flex-direction: column;
  gap: 4px;

  .progress-text {
    font-size: 12px;
    color: #606266;
    text-align: center;
  }
}
</style>
