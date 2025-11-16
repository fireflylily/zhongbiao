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
            <div class="stat-label">合同案例</div>
            <div class="stat-value">{{ contractCasesCount }}</div>
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
      <template #actions>
        <el-button type="primary" :loading="creating" @click="handleCreate">
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
          <el-form-item label="产品分类">
            <el-select
              v-model="filters.productCategory"
              placeholder="全部产品"
              clearable
              style="width: 130px"
              @change="handleSearch"
            >
              <el-option label="全部产品" value="" />
              <el-option label="风控产品" value="风控产品" />
              <el-option label="实修" value="实修" />
              <el-option label="免密" value="免密" />
              <el-option label="风控位置" value="风控位置" />
            </el-select>
          </el-form-item>
          <el-form-item label="行业">
            <el-select
              v-model="filters.industry"
              placeholder="全部行业"
              clearable
              style="width: 120px"
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
        <el-table-column prop="product_category" label="产品分类" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.product_category" type="primary" size="small">
              {{ row.product_category }}
            </el-tag>
            <span v-else style="color: #909399">-</span>
          </template>
        </el-table-column>
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
import type { Case } from '@/types'

// Router
const router = useRouter()

// Hooks
const { success, error } = useNotification()

// 状态
const loading = ref(false)
const creating = ref(false)
const allCases = ref<Case[]>([])
const companies = ref<any[]>([])
const currentCompanyId = ref<number | undefined>()
const filters = ref({
  keyword: '',
  productCategory: '',
  industry: '',
  contractType: ''
})

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

  // 产品分类筛选
  if (filters.value.productCategory) {
    result = result.filter((c) => c.product_category === filters.value.productCategory)
  }

  // 行业筛选
  if (filters.value.industry) {
    result = result.filter((c) => c.industry === filters.value.industry)
  }

  // 合同类型筛选
  if (filters.value.contractType) {
    result = result.filter((c) => c.contract_type === filters.value.contractType)
  }

  return result
})

const contractCasesCount = computed(() => {
  return allCases.value.filter(c => c.contract_type === '合同').length
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
    // 传递company_id参数,实现权限过滤:显示当前公司的案例 + 所有公开案例
    const response = await knowledgeApi.getCases({
      company_id: currentCompanyId.value
    })
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
      // 设置默认公司为第一个公司
      if (companies.value.length > 0 && !currentCompanyId.value) {
        currentCompanyId.value = companies.value[0].company_id
        // 加载该公司的案例
        await loadCases()
      }
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
  filters.value.productCategory = ''
  filters.value.industry = ''
  filters.value.contractType = ''
}

// 新建案例 - 直接创建最小化案例并跳转到详情页
const handleCreate = async () => {
  // 检查是否有企业
  if (companies.value.length === 0) {
    error('无法创建', '请先添加企业信息')
    return
  }

  creating.value = true
  try {
    // 使用当前选中的公司创建案例
    const companyId = currentCompanyId.value || companies.value[0]?.company_id

    const response = await knowledgeApi.createCase({
      company_id: companyId,
      case_title: '新建案例',
      customer_name: '待完善',
      industry: '金融',
      contract_type: '合同'
    })

    if (response.success && response.data) {
      success('创建成功', '正在跳转到编辑页面...')
      // 跳转到详情页进行编辑
      router.push(`/knowledge/case/${response.data.case_id}`)
    } else {
      error('创建失败', response.error || '未知错误')
    }
  } catch (err) {
    console.error('创建案例失败:', err)
    error('创建失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    creating.value = false
  }
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
onMounted(async () => {
  // 先加载公司列表,loadCompanies会自动设置默认公司并加载案例
  await loadCompanies()
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
