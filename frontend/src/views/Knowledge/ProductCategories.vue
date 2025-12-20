<template>
  <div class="product-categories">
    <!-- 统计信息 -->
    <div class="stats-bar">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#409eff"><Grid /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">产品分类</div>
            <div class="stat-value">{{ categories.length }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#67c23a"><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">总项目数</div>
            <div class="stat-value">{{ totalItems }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <Card title="产品分类管理">
      <template #extra>
        <el-button type="primary" @click="handleCreateCategory">
          <el-icon><Plus /></el-icon>
          新建分类
        </el-button>
      </template>

      <Loading v-if="loading" text="加载中..." />
      <Empty v-else-if="!categories.length" type="no-data" description="暂无产品分类" />

      <div v-else class="categories-list">
        <el-collapse v-model="activeCategories" accordion>
          <el-collapse-item
            v-for="category in categories"
            :key="category.category_id"
            :name="category.category_id"
          >
            <template #title>
              <div class="category-header">
                <div class="category-info">
                  <span class="category-name">{{ category.category_name }}</span>
                  <el-tag size="small" type="info" class="category-tag">
                    {{ category.items.length }} 项
                  </el-tag>
                </div>
                <div class="category-actions" @click.stop>
                  <el-button
                    text
                    type="primary"
                    size="small"
                    @click="handleAddItem(category)"
                  >
                    <el-icon><Plus /></el-icon>
                    添加项
                  </el-button>
                  <el-button
                    text
                    type="warning"
                    size="small"
                    @click="handleEditCategory(category)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    text
                    type="danger"
                    size="small"
                    @click="handleDeleteCategory(category)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </template>

            <div class="items-container">
              <el-table :data="category.items" stripe>
                <el-table-column prop="item_name" label="项目名称" width="200" />
                <el-table-column prop="item_code" label="代码" width="180" />
                <el-table-column prop="item_description" label="描述" show-overflow-tooltip />
                <el-table-column prop="item_order" label="排序" width="80" align="center" />
                <el-table-column label="操作" width="180" fixed="right">
                  <template #default="{ row }">
                    <el-button
                      text
                      type="warning"
                      size="small"
                      @click="handleEditItem(category, row)"
                    >
                      编辑
                    </el-button>
                    <el-button
                      text
                      type="danger"
                      size="small"
                      @click="handleDeleteItem(category, row)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </Card>

    <!-- 分类编辑对话框 -->
    <el-dialog
      v-model="categoryDialogVisible"
      :title="categoryFormMode === 'create' ? '新建分类' : '编辑分类'"
      width="500px"
    >
      <el-form :model="categoryForm" :rules="categoryRules" ref="categoryFormRef" label-width="100px">
        <el-form-item label="分类名称" prop="category_name">
          <el-input v-model="categoryForm.category_name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类代码" prop="category_code">
          <el-input
            v-model="categoryForm.category_code"
            placeholder="请输入分类代码（英文）"
            :disabled="categoryFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="分类描述" prop="category_description">
          <el-input
            v-model="categoryForm.category_description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>
        <el-form-item label="排序" prop="category_order">
          <el-input-number v-model="categoryForm.category_order" :min="1" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 项目编辑对话框 -->
    <el-dialog
      v-model="itemDialogVisible"
      :title="itemFormMode === 'create' ? '新建项目' : '编辑项目'"
      width="500px"
    >
      <el-form :model="itemForm" :rules="itemRules" ref="itemFormRef" label-width="100px">
        <el-form-item label="项目名称" prop="item_name">
          <el-input v-model="itemForm.item_name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目代码" prop="item_code">
          <el-input v-model="itemForm.item_code" placeholder="请输入项目代码（英文）" />
        </el-form-item>
        <el-form-item label="项目描述" prop="item_description">
          <el-input
            v-model="itemForm.item_description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item label="排序" prop="item_order">
          <el-input-number v-model="itemForm.item_order" :min="1" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveItem" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Card, Loading, Empty } from '@/components'
import { useNotification } from '@/composables'
import { Grid, Tickets, Plus } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'

// API 基础路径
const API_BASE = '/api'

// Hooks
const { success, error } = useNotification()

// 状态
const loading = ref(false)
const saving = ref(false)
const categories = ref<any[]>([])
const activeCategories = ref<number[]>([])

// 分类对话框
const categoryDialogVisible = ref(false)
const categoryFormMode = ref<'create' | 'edit'>('create')
const categoryForm = ref({
  category_id: null as number | null,
  category_name: '',
  category_code: '',
  category_description: '',
  category_order: 999
})
const categoryFormRef = ref<FormInstance>()
const categoryRules = {
  category_name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  category_code: [{ required: true, message: '请输入分类代码', trigger: 'blur' }]
}

// 项目对话框
const itemDialogVisible = ref(false)
const itemFormMode = ref<'create' | 'edit'>('create')
const currentCategory = ref<any>(null)
const itemForm = ref({
  item_id: null as number | null,
  item_name: '',
  item_code: '',
  item_description: '',
  item_order: 999
})
const itemFormRef = ref<FormInstance>()
const itemRules = {
  item_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }]
}

// 计算属性
const totalItems = computed(() => {
  return categories.value.reduce((sum, cat) => sum + cat.items.length, 0)
})

// 方法
const loadCategories = async () => {
  loading.value = true
  try {
    const response = await fetch(`${API_BASE}/product-categories`)
    const result = await response.json()

    if (result.success) {
      categories.value = result.data || []
    } else {
      error('加载失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('加载产品分类失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loading.value = false
  }
}

// 新建分类
const handleCreateCategory = () => {
  categoryFormMode.value = 'create'
  categoryForm.value = {
    category_id: null,
    category_name: '',
    category_code: '',
    category_description: '',
    category_order: 999
  }
  categoryDialogVisible.value = true
}

// 编辑分类
const handleEditCategory = (category: any) => {
  categoryFormMode.value = 'edit'
  categoryForm.value = {
    category_id: category.category_id,
    category_name: category.category_name,
    category_code: category.category_code,
    category_description: category.category_description || '',
    category_order: category.category_order || 999
  }
  categoryDialogVisible.value = true
}

// 保存分类
const handleSaveCategory = async () => {
  if (!categoryFormRef.value) return

  await categoryFormRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const isEdit = categoryFormMode.value === 'edit'
      const url = isEdit
        ? `${API_BASE}/product-categories/${categoryForm.value.category_id}`
        : `${API_BASE}/product-categories`

      const response = await fetch(url, {
        method: isEdit ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(categoryForm.value)
      })

      const result = await response.json()

      if (result.success) {
        success(isEdit ? '更新成功' : '创建成功', result.message)
        categoryDialogVisible.value = false
        await loadCategories()
      } else {
        error(isEdit ? '更新失败' : '创建失败', result.error || '未知错误')
      }
    } catch (err) {
      console.error('保存分类失败:', err)
      error('保存失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      saving.value = false
    }
  })
}

// 删除分类
const handleDeleteCategory = async (category: any) => {
  try {
    if (!confirm(`确定要删除分类 "${category.category_name}" 吗？此操作将同时删除该分类下的所有项目。`)) {
      return
    }

    const response = await fetch(`${API_BASE}/product-categories/${category.category_id}`, {
      method: 'DELETE'
    })

    const result = await response.json()

    if (result.success) {
      success('删除成功', result.message)
      await loadCategories()
    } else {
      error('删除失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('删除分类失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 添加项目
const handleAddItem = (category: any) => {
  currentCategory.value = category
  itemFormMode.value = 'create'
  itemForm.value = {
    item_id: null,
    item_name: '',
    item_code: '',
    item_description: '',
    item_order: 999
  }
  itemDialogVisible.value = true
}

// 编辑项目
const handleEditItem = (category: any, item: any) => {
  currentCategory.value = category
  itemFormMode.value = 'edit'
  itemForm.value = {
    item_id: item.item_id,
    item_name: item.item_name,
    item_code: item.item_code || '',
    item_description: item.item_description || '',
    item_order: item.item_order || 999
  }
  itemDialogVisible.value = true
}

// 保存项目
const handleSaveItem = async () => {
  if (!itemFormRef.value || !currentCategory.value) return

  await itemFormRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const isEdit = itemFormMode.value === 'edit'
      const url = isEdit
        ? `${API_BASE}/product-category-items/${itemForm.value.item_id}`
        : `${API_BASE}/product-categories/${currentCategory.value.category_id}/items`

      const response = await fetch(url, {
        method: isEdit ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(itemForm.value)
      })

      const result = await response.json()

      if (result.success) {
        success(isEdit ? '更新成功' : '创建成功', result.message)
        itemDialogVisible.value = false
        await loadCategories()
      } else {
        error(isEdit ? '更新失败' : '创建失败', result.error || '未知错误')
      }
    } catch (err) {
      console.error('保存项目失败:', err)
      error('保存失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      saving.value = false
    }
  })
}

// 删除项目
const handleDeleteItem = async (category: any, item: any) => {
  try {
    if (!confirm(`确定要删除项目 "${item.item_name}" 吗？`)) {
      return
    }

    const response = await fetch(`${API_BASE}/product-category-items/${item.item_id}`, {
      method: 'DELETE'
    })

    const result = await response.json()

    if (result.success) {
      success('删除成功', result.message)
      await loadCategories()
    } else {
      error('删除失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('删除项目失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 生命周期
onMounted(() => {
  loadCategories()
})
</script>

<style scoped lang="scss">
.product-categories {
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

.categories-list {
  .category-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding-right: 20px;

    .category-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .category-name {
        font-size: 16px;
        font-weight: 500;
        color: #303133;
      }

      .category-tag {
        font-size: 12px;
      }
    }

    .category-actions {
      display: flex;
      gap: 8px;
    }
  }

  .items-container {
    padding: 16px 0 0 0;
  }
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;

  &:hover {
    background: #ecf5ff;
  }
}

:deep(.el-collapse-item__content) {
  padding: 0 16px 16px 16px;
}
</style>
