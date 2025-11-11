<template>
  <div class="case-library">
    <!-- 统计信息 -->
    <div class="stats-bar">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#409eff"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">总案例数</div>
            <div class="stat-value">{{ allCases.length }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#67c23a"><SuccessFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">成功案例</div>
            <div class="stat-value">{{ successCasesCount }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#e6a23c"><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">合同总额</div>
            <div class="stat-value">{{ totalContractAmount }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <Card title="案例列表">
      <template #header-right>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建案例
        </el-button>
      </template>

      <!-- 搜索和筛选区域 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filters">
          <el-form-item label="搜索">
            <el-input
              v-model="filters.keyword"
              placeholder="搜索案例标题、客户名称..."
              clearable
              style="width: 300px"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="行业">
            <el-select
              v-model="filters.industry"
              placeholder="全部行业"
              clearable
              style="width: 150px"
              @change="handleSearch"
            >
              <el-option label="全部行业" value="" />
              <el-option label="科技" value="科技" />
              <el-option label="制造业" value="制造业" />
              <el-option label="金融" value="金融" />
              <el-option label="教育" value="教育" />
              <el-option label="医疗" value="医疗" />
              <el-option label="建筑" value="建筑" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          <el-form-item label="合同类型">
            <el-select
              v-model="filters.contractType"
              placeholder="全部类型"
              clearable
              style="width: 120px"
              @change="handleSearch"
            >
              <el-option label="全部类型" value="" />
              <el-option label="合同" value="合同" />
              <el-option label="订单" value="订单" />
            </el-select>
          </el-form-item>
          <el-form-item label="案例状态">
            <el-select
              v-model="filters.caseStatus"
              placeholder="全部状态"
              clearable
              style="width: 120px"
              @change="handleSearch"
            >
              <el-option label="全部状态" value="" />
              <el-option label="成功" value="success" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="待验收" value="pending_acceptance" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="handleResetFilters">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <Loading v-if="loading" text="加载中..." />
      <Empty v-else-if="!filteredCases.length" type="no-data" description="暂无案例数据" />
      <el-table v-else :data="filteredCases" stripe style="width: 100%">
        <el-table-column prop="case_id" label="ID" width="70" fixed />
        <el-table-column prop="case_title" label="案例标题" min-width="200" fixed show-overflow-tooltip />
        <el-table-column prop="customer_name" label="客户名称" width="180" show-overflow-tooltip />
        <el-table-column prop="industry" label="所属行业" width="100" />
        <el-table-column prop="contract_type" label="合同类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.contract_type === '合同' ? 'primary' : 'success'" size="small">
              {{ row.contract_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="contract_amount" label="合同金额" width="120" align="right" />
        <el-table-column prop="contract_start_date" label="合同开始日期" width="120" />
        <el-table-column prop="contract_end_date" label="合同结束日期" width="120" />
        <el-table-column prop="case_status" label="案例状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getCaseStatusType(row.case_status)" size="small">
              {{ getCaseStatusLabel(row.case_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" show-overflow-tooltip />

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

    <!-- 新建案例对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建案例"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="120px"
      >
        <el-form-item label="所属企业" prop="company_id">
          <el-select
            v-model="createForm.company_id"
            placeholder="请选择企业"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="company in companies"
              :key="company.company_id"
              :label="company.company_name"
              :value="company.company_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="案例标题" prop="case_title">
          <el-input v-model="createForm.case_title" placeholder="请输入案例标题/合同名称" />
        </el-form-item>
        <el-form-item label="客户名称" prop="customer_name">
          <el-input v-model="createForm.customer_name" placeholder="请输入甲方客户名称" />
        </el-form-item>
        <el-form-item label="所属行业" prop="industry">
          <el-select v-model="createForm.industry" placeholder="请选择行业" style="width: 100%">
            <el-option label="科技" value="科技" />
            <el-option label="制造业" value="制造业" />
            <el-option label="金融" value="金融" />
            <el-option label="教育" value="教育" />
            <el-option label="医疗" value="医疗" />
            <el-option label="建筑" value="建筑" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="合同类型" prop="contract_type">
          <el-radio-group v-model="createForm.contract_type">
            <el-radio label="合同">合同</el-radio>
            <el-radio label="订单">订单</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="合同金额" prop="contract_amount">
          <el-input v-model="createForm.contract_amount" placeholder="如：100万元、百万级" />
        </el-form-item>
        <el-form-item label="合同日期" prop="contract_dates">
          <el-date-picker
            v-model="contract_dates"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="案例状态" prop="case_status">
          <el-radio-group v-model="createForm.case_status">
            <el-radio label="success">成功</el-radio>
            <el-radio label="in_progress">进行中</el-radio>
            <el-radio label="pending_acceptance">待验收</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleConfirmCreate">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, Loading, Empty } from '@/components'
import { useNotification } from '@/composables'
import { knowledgeApi } from '@/api/endpoints/knowledge'
import { companyApi } from '@/api/endpoints/company'
import { formatDate } from '@/utils/formatters'
import {
  Document,
  SuccessFilled,
  Money,
  Plus,
  Search,
  RefreshLeft
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { Case } from '@/types'

// Router
const router = useRouter()

// Hooks
const { success, error } = useNotification()

// 状态
const loading = ref(false)
const allCases = ref<Case[]>([])
const companies = ref<any[]>([])
const filters = ref({
  keyword: '',
  industry: '',
  contractType: '',
  caseStatus: ''
})

// 新建案例相关
const createDialogVisible = ref(false)
const creating = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = ref({
  company_id: null as number | null,
  case_title: '',
  customer_name: '',
  industry: '',
  contract_type: '合同' as '订单' | '合同',
  contract_amount: '',
  case_status: 'success' as 'success' | 'in_progress' | 'pending_acceptance'
})
const contract_dates = ref<[string, string] | null>(null)

const createFormRules: FormRules = {
  company_id: [
    { required: true, message: '请选择所属企业', trigger: 'change' }
  ],
  case_title: [
    { required: true, message: '请输入案例标题', trigger: 'blur' },
    { min: 2, max: 200, message: '案例标题长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  customer_name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ],
  contract_type: [
    { required: true, message: '请选择合同类型', trigger: 'change' }
  ]
}

// 计算属性
const filteredCases = computed(() => {
  let result = [...allCases.value]

  // 关键词搜索
  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    result = result.filter((c) => {
      return (
        c.case_title?.toLowerCase().includes(keyword) ||
        c.customer_name?.toLowerCase().includes(keyword) ||
        c.case_number?.toLowerCase().includes(keyword)
      )
    })
  }

  // 行业筛选
  if (filters.value.industry) {
    result = result.filter((c) => c.industry === filters.value.industry)
  }

  // 合同类型筛选
  if (filters.value.contractType) {
    result = result.filter((c) => c.contract_type === filters.value.contractType)
  }

  // 案例状态筛选
  if (filters.value.caseStatus) {
    result = result.filter((c) => c.case_status === filters.value.caseStatus)
  }

  return result
})

const successCasesCount = computed(() => {
  return allCases.value.filter(c => c.case_status === 'success').length
})

const totalContractAmount = computed(() => {
  // 简单统计：计算数值型金额
  let total = 0
  allCases.value.forEach(c => {
    if (c.contract_amount) {
      // 尝试提取数字（支持"100万元"、"1000000"等格式）
      const match = c.contract_amount.match(/[\d.]+/)
      if (match) {
        const num = parseFloat(match[0])
        if (c.contract_amount.includes('万')) {
          total += num * 10000
        } else if (c.contract_amount.includes('亿')) {
          total += num * 100000000
        } else {
          total += num
        }
      }
    }
  })

  if (total >= 100000000) {
    return `${(total / 100000000).toFixed(2)}亿`
  } else if (total >= 10000) {
    return `${(total / 10000).toFixed(2)}万`
  }
  return total.toFixed(2)
})

// 方法
const loadCases = async () => {
  loading.value = true
  try {
    const response = await knowledgeApi.getCases()
    if (response.success && response.data) {
      allCases.value = response.data.map((c: any) => ({
        ...c,
        contract_start_date: c.contract_start_date ? formatDate(c.contract_start_date, 'date') : '-',
        contract_end_date: c.contract_end_date ? formatDate(c.contract_end_date, 'date') : '-',
        created_at: c.created_at ? formatDate(c.created_at) : '-'
      }))
    }
  } catch (err) {
    console.error('加载案例列表失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loading.value = false
  }
}

const loadCompanies = async () => {
  try {
    const response = await companyApi.getCompanies()
    if (response.success && response.data) {
      companies.value = response.data
    }
  } catch (err) {
    console.error('加载企业列表失败:', err)
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
  filters.value.contractType = ''
  filters.value.caseStatus = ''
}

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

// 新建案例
const handleCreate = () => {
  createDialogVisible.value = true
}

// 确认创建案例
const handleConfirmCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    creating.value = true
    try {
      const response = await knowledgeApi.createCase({
        company_id: createForm.value.company_id!,
        case_title: createForm.value.case_title,
        customer_name: createForm.value.customer_name,
        industry: createForm.value.industry || undefined,
        contract_type: createForm.value.contract_type,
        contract_amount: createForm.value.contract_amount || undefined,
        contract_start_date: contract_dates.value?.[0],
        contract_end_date: contract_dates.value?.[1],
        case_status: createForm.value.case_status
      })

      if (response.success) {
        success('创建成功', '案例创建成功')
        createDialogVisible.value = false
        await loadCases()
      } else {
        error('创建失败', response.error || '未知错误')
      }
    } catch (err) {
      console.error('创建案例失败:', err)
      error('创建失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      creating.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  createForm.value = {
    company_id: null,
    case_title: '',
    customer_name: '',
    industry: '',
    contract_type: '合同',
    contract_amount: '',
    case_status: 'success'
  }
  contract_dates.value = null
  createFormRef.value?.resetFields()
}

// 查看详情
const handleView = (row: Case) => {
  // TODO: 跳转到详情页
  router.push(`/knowledge/case/${row.case_id}`)
}

// 编辑案例
const handleEdit = (row: Case) => {
  // TODO: 跳转到编辑页（与详情页相同）
  router.push(`/knowledge/case/${row.case_id}`)
}

// 删除案例
const handleDelete = async (row: Case) => {
  try {
    // 确认删除
    if (!confirm(`确定要删除案例 "${row.case_title}" 吗？此操作不可恢复。`)) {
      return
    }

    const response = await knowledgeApi.deleteCase(row.case_id)
    if (response.success) {
      success('删除成功', `已删除案例: ${row.case_title}`)
      await loadCases()
    } else {
      error('删除失败', response.error || '未知错误')
    }
  } catch (err) {
    console.error('删除案例失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 生命周期
onMounted(() => {
  loadCases()
  loadCompanies()
})
</script>

<style scoped lang="scss">
.case-library {
  padding: 20px;
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
</style>
