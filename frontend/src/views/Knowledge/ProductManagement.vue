<template>
  <div class="product-management">
    <!-- 统计信息 -->
    <div class="stats-bar">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon categories">
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
          <div class="stat-icon items">
            <el-icon :size="32" color="#67c23a"><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">分类项目</div>
            <div class="stat-value">{{ totalItems }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon tags">
            <el-icon :size="32" color="#e6a23c"><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">能力标签</div>
            <div class="stat-value">{{ capabilityStats.tagCount }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon capabilities">
            <el-icon :size="32" color="#909399"><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">能力条目</div>
            <div class="stat-value">{{ capabilityStats.capabilityCount }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Tab 切换 -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 产品分类 Tab -->
      <el-tab-pane label="产品分类" name="categories">
        <div class="tab-toolbar">
          <el-button type="primary" @click="handleCreateCategory">
            <el-icon><Plus /></el-icon>
            新建分类
          </el-button>
        </div>

        <Loading v-if="loadingCategories" text="加载中..." />
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
                    <el-button text type="primary" size="small" @click="handleAddItem(category)">
                      <el-icon><Plus /></el-icon>
                      添加项
                    </el-button>
                    <el-button text type="warning" size="small" @click="handleEditCategory(category)">
                      编辑
                    </el-button>
                    <el-button text type="danger" size="small" @click="handleDeleteCategory(category)">
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
                      <el-button text type="warning" size="small" @click="handleEditItem(category, row)">
                        编辑
                      </el-button>
                      <el-button text type="danger" size="small" @click="handleDeleteItem(category, row)">
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>

      <!-- 产品能力 Tab -->
      <el-tab-pane label="产品能力" name="capabilities">
        <el-row :gutter="20">
          <!-- 左侧：标签树 -->
          <el-col :span="8">
            <Card title="能力标签">
              <template #extra>
                <el-button type="primary" size="small" @click="handleCreateTag">
                  <el-icon><Plus /></el-icon>
                  新建标签
                </el-button>
              </template>

              <Loading v-if="loadingTags" text="加载中..." />
              <Empty v-else-if="!tags.length" type="no-data" description="暂无标签" />

              <el-tree
                v-else
                :data="tags"
                :props="treeProps"
                node-key="tag_id"
                default-expand-all
                highlight-current
                @node-click="handleTagClick"
              >
                <template #default="{ node, data }">
                  <div class="tree-node">
                    <span class="node-label">{{ node.label }}</span>
                    <span class="node-actions">
                      <el-button link type="primary" size="small" @click.stop="handleAddChildTag(data)">
                        <el-icon><Plus /></el-icon>
                      </el-button>
                      <el-button link type="warning" size="small" @click.stop="handleEditTag(data)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                      <el-button link type="danger" size="small" @click.stop="handleDeleteTag(data)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </span>
                  </div>
                </template>
              </el-tree>
            </Card>
          </el-col>

          <!-- 右侧：能力列表 -->
          <el-col :span="16">
            <Card :title="currentTagName ? `${currentTagName} - 能力列表` : '全部能力'">
              <template #extra>
                <div class="capabilities-toolbar">
                  <el-input
                    v-model="searchKeyword"
                    placeholder="搜索能力名称..."
                    clearable
                    style="width: 200px"
                    @keyup.enter="searchCapabilities"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                  <el-button type="primary" @click="handleExtractCapabilities">
                    <el-icon><MagicStick /></el-icon>
                    从文档提取
                  </el-button>
                </div>
              </template>

              <Loading v-if="loadingCapabilities" text="加载中..." />
              <Empty v-else-if="!capabilities.length" type="no-data" description="暂无能力数据" />

              <el-table v-else :data="capabilities" stripe max-height="500">
                <el-table-column prop="capability_name" label="能力名称" width="180" show-overflow-tooltip />
                <el-table-column prop="capability_type" label="类型" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getTypeTagType(row.capability_type)" size="small">
                      {{ row.capability_type || '未分类' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="capability_description" label="描述" show-overflow-tooltip />
                <el-table-column prop="doc_name" label="来源文档" width="150" show-overflow-tooltip />
                <el-table-column prop="confidence_score" label="置信度" width="80" align="center">
                  <template #default="{ row }">
                    <el-progress
                      :percentage="Math.round((row.confidence_score || 0) * 100)"
                      :stroke-width="6"
                      :show-text="false"
                      :color="getConfidenceColor(row.confidence_score)"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="verified" label="验证" width="70" align="center">
                  <template #default="{ row }">
                    <el-icon v-if="row.verified" color="#67c23a"><CircleCheck /></el-icon>
                    <el-icon v-else color="#909399"><Clock /></el-icon>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="handleViewCapability(row)">
                      详情
                    </el-button>
                    <el-button
                      link
                      :type="row.verified ? 'warning' : 'success'"
                      size="small"
                      @click="handleToggleVerify(row)"
                    >
                      {{ row.verified ? '取消验证' : '验证' }}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 分页 -->
              <div class="pagination-wrapper" v-if="capabilityTotal > capabilityPageSize">
                <el-pagination
                  v-model:current-page="capabilityPage"
                  v-model:page-size="capabilityPageSize"
                  :total="capabilityTotal"
                  :page-sizes="[10, 20, 50]"
                  layout="total, sizes, prev, pager, next"
                  @size-change="loadCapabilities"
                  @current-change="loadCapabilities"
                />
              </div>
            </Card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

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

    <!-- 标签编辑对话框 -->
    <el-dialog
      v-model="tagDialogVisible"
      :title="tagFormMode === 'create' ? '新建标签' : '编辑标签'"
      width="500px"
    >
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="100px">
        <el-form-item label="标签名称" prop="tag_name">
          <el-input v-model="tagForm.tag_name" placeholder="如：风控产品、实修能力" />
        </el-form-item>
        <el-form-item label="标签代码" prop="tag_code">
          <el-input
            v-model="tagForm.tag_code"
            placeholder="英文代码，如: risk_control"
            :disabled="tagFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="父级标签" prop="parent_tag_id">
          <el-tree-select
            v-model="tagForm.parent_tag_id"
            :data="tags"
            :props="{ label: 'tag_name', value: 'tag_id', children: 'children' }"
            placeholder="选择父级标签（可选）"
            check-strictly
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="tagForm.description"
            type="textarea"
            :rows="3"
            placeholder="标签的详细描述"
          />
        </el-form-item>
        <el-form-item label="示例关键词" prop="example_keywords">
          <el-input
            v-model="tagForm.example_keywords"
            type="textarea"
            :rows="2"
            placeholder="逗号分隔的关键词，用于AI匹配"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTag" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 能力详情对话框 -->
    <el-dialog
      v-model="capabilityDialogVisible"
      title="能力详情"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="currentCapability">
        <el-descriptions-item label="能力名称" :span="2">
          {{ currentCapability.capability_name }}
        </el-descriptions-item>
        <el-descriptions-item label="能力类型">
          {{ currentCapability.capability_type || '未分类' }}
        </el-descriptions-item>
        <el-descriptions-item label="置信度">
          {{ Math.round((currentCapability.confidence_score || 0) * 100) }}%
        </el-descriptions-item>
        <el-descriptions-item label="关联标签">
          {{ currentCapability.tag_name || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="验证状态">
          <el-tag :type="currentCapability.verified ? 'success' : 'info'">
            {{ currentCapability.verified ? '已验证' : '待验证' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="来源文档" :span="2">
          {{ currentCapability.doc_name || '未知' }}
        </el-descriptions-item>
        <el-descriptions-item label="能力描述" :span="2">
          {{ currentCapability.capability_description || '无描述' }}
        </el-descriptions-item>
        <el-descriptions-item label="原文摘录" :span="2">
          <div class="original-text">
            {{ currentCapability.original_text || '无' }}
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="capabilityDialogVisible = false">关闭</el-button>
        <el-button
          :type="currentCapability?.verified ? 'warning' : 'success'"
          @click="handleToggleVerifyInDialog"
        >
          {{ currentCapability?.verified ? '取消验证' : '标记为已验证' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 能力提取对话框 -->
    <el-dialog
      v-model="extractDialogVisible"
      title="从文档提取能力"
      width="600px"
    >
      <el-form label-width="100px">
        <el-form-item label="选择文档">
          <el-select
            v-model="extractForm.doc_ids"
            multiple
            filterable
            placeholder="选择要提取能力的文档"
            style="width: 100%"
          >
            <el-option
              v-for="doc in availableDocs"
              :key="doc.doc_id"
              :label="doc.doc_name"
              :value="doc.doc_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联标签">
          <el-tree-select
            v-model="extractForm.tag_id"
            :data="tags"
            :props="{ label: 'tag_name', value: 'tag_id', children: 'children' }"
            placeholder="选择要关联的标签（可选）"
            check-strictly
            clearable
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="extractDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleStartExtract"
          :loading="extracting"
          :disabled="!extractForm.doc_ids.length"
        >
          开始提取
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Card, Loading, Empty } from '@/components'
import { useNotification } from '@/composables'
import {
  Grid, Tickets, Collection, Cpu, Plus, Edit, Delete,
  Search, MagicStick, CircleCheck, Clock
} from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

// API 基础路径
const API_BASE = '/api'
const CAPABILITY_API_BASE = '/api/capability'

// Hooks
const { success, error } = useNotification()
const userStore = useUserStore()

// 获取当前企业ID
const companyId = computed(() => userStore.currentCompanyId || 1)

// Tab 状态
const activeTab = ref('categories')

// ========================================
// 产品分类相关状态
// ========================================
const loadingCategories = ref(false)
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

// ========================================
// 产品能力相关状态
// ========================================
const capabilityStats = reactive({
  tagCount: 0,
  capabilityCount: 0,
  verifiedCount: 0
})

// 标签相关
const loadingTags = ref(false)
const tags = ref<any[]>([])
const treeProps = {
  label: 'tag_name',
  children: 'children'
}
const currentTagId = ref<number | null>(null)
const currentTagName = ref('')

// 能力列表相关
const loadingCapabilities = ref(false)
const capabilities = ref<any[]>([])
const searchKeyword = ref('')
const capabilityPage = ref(1)
const capabilityPageSize = ref(20)
const capabilityTotal = ref(0)

// 标签对话框
const tagDialogVisible = ref(false)
const tagFormMode = ref<'create' | 'edit'>('create')
const tagForm = ref({
  tag_id: null as number | null,
  tag_name: '',
  tag_code: '',
  parent_tag_id: null as number | null,
  description: '',
  example_keywords: ''
})
const tagFormRef = ref<FormInstance>()
const tagRules = {
  tag_name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
  tag_code: [{ required: true, message: '请输入标签代码', trigger: 'blur' }]
}

// 能力详情对话框
const capabilityDialogVisible = ref(false)
const currentCapability = ref<any>(null)

// 能力提取对话框
const extractDialogVisible = ref(false)
const extractForm = reactive({
  doc_ids: [] as number[],
  tag_id: null as number | null
})
const availableDocs = ref<any[]>([])
const extracting = ref(false)

// ========================================
// 产品分类方法
// ========================================
const loadCategories = async () => {
  loadingCategories.value = true
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
    loadingCategories.value = false
  }
}

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
        headers: { 'Content-Type': 'application/json' },
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

const handleDeleteCategory = async (category: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类 "${category.category_name}" 吗？此操作将同时删除该分类下的所有项目。`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
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
        headers: { 'Content-Type': 'application/json' },
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

const handleDeleteItem = async (category: any, item: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${item.item_name}" 吗？`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
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

// ========================================
// 产品能力方法
// ========================================
const loadTags = async () => {
  loadingTags.value = true
  try {
    const response = await fetch(`${CAPABILITY_API_BASE}/tags?company_id=${companyId.value}`)
    const result = await response.json()

    if (result.success) {
      tags.value = result.data || []
      capabilityStats.tagCount = countTags(tags.value)
    } else {
      error('加载失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('加载标签失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loadingTags.value = false
  }
}

const countTags = (tagList: any[]): number => {
  return tagList.reduce((sum, tag) => {
    return sum + 1 + (tag.children ? countTags(tag.children) : 0)
  }, 0)
}

const loadCapabilities = async () => {
  loadingCapabilities.value = true
  try {
    const params = new URLSearchParams({
      company_id: String(companyId.value),
      page: String(capabilityPage.value),
      page_size: String(capabilityPageSize.value)
    })

    if (currentTagId.value) {
      params.append('tag_id', String(currentTagId.value))
    }
    if (searchKeyword.value) {
      params.append('keyword', searchKeyword.value)
    }

    const response = await fetch(`${CAPABILITY_API_BASE}/capabilities?${params}`)
    const result = await response.json()

    if (result.success) {
      capabilities.value = result.data || []
      capabilityTotal.value = result.total || 0
      capabilityStats.capabilityCount = capabilityTotal.value
      capabilityStats.verifiedCount = capabilities.value.filter((c: any) => c.verified).length
    } else {
      error('加载失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('加载能力列表失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loadingCapabilities.value = false
  }
}

const searchCapabilities = () => {
  capabilityPage.value = 1
  loadCapabilities()
}

const handleTagClick = (data: any) => {
  currentTagId.value = data.tag_id
  currentTagName.value = data.tag_name
  capabilityPage.value = 1
  loadCapabilities()
}

const handleCreateTag = () => {
  tagFormMode.value = 'create'
  tagForm.value = {
    tag_id: null,
    tag_name: '',
    tag_code: '',
    parent_tag_id: null,
    description: '',
    example_keywords: ''
  }
  tagDialogVisible.value = true
}

const handleAddChildTag = (parentTag: any) => {
  tagFormMode.value = 'create'
  tagForm.value = {
    tag_id: null,
    tag_name: '',
    tag_code: '',
    parent_tag_id: parentTag.tag_id,
    description: '',
    example_keywords: ''
  }
  tagDialogVisible.value = true
}

const handleEditTag = (tag: any) => {
  tagFormMode.value = 'edit'
  tagForm.value = {
    tag_id: tag.tag_id,
    tag_name: tag.tag_name,
    tag_code: tag.tag_code,
    parent_tag_id: tag.parent_tag_id,
    description: tag.description || '',
    example_keywords: tag.example_keywords || ''
  }
  tagDialogVisible.value = true
}

const handleSaveTag = async () => {
  if (!tagFormRef.value) return

  await tagFormRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const isEdit = tagFormMode.value === 'edit'
      const url = isEdit
        ? `${CAPABILITY_API_BASE}/tags/${tagForm.value.tag_id}`
        : `${CAPABILITY_API_BASE}/tags`

      const payload = {
        ...tagForm.value,
        company_id: companyId.value
      }

      const response = await fetch(url, {
        method: isEdit ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      const result = await response.json()

      if (result.success) {
        success(isEdit ? '更新成功' : '创建成功')
        tagDialogVisible.value = false
        await loadTags()
      } else {
        error(isEdit ? '更新失败' : '创建失败', result.error || '未知错误')
      }
    } catch (err) {
      console.error('保存标签失败:', err)
      error('保存失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      saving.value = false
    }
  })
}

const handleDeleteTag = async (tag: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${tag.tag_name}" 吗？`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    const response = await fetch(`${CAPABILITY_API_BASE}/tags/${tag.tag_id}`, {
      method: 'DELETE'
    })
    const result = await response.json()

    if (result.success) {
      success('删除成功')
      await loadTags()
      if (currentTagId.value === tag.tag_id) {
        currentTagId.value = null
        currentTagName.value = ''
        loadCapabilities()
      }
    } else {
      error('删除失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('删除标签失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

const handleViewCapability = (capability: any) => {
  currentCapability.value = capability
  capabilityDialogVisible.value = true
}

const handleToggleVerify = async (capability: any) => {
  try {
    const response = await fetch(`${CAPABILITY_API_BASE}/capabilities/${capability.capability_id}/verify`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ verified: !capability.verified })
    })

    const result = await response.json()

    if (result.success) {
      capability.verified = !capability.verified
      success(capability.verified ? '已验证' : '已取消验证')
    } else {
      error('操作失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('切换验证状态失败:', err)
    error('操作失败', err instanceof Error ? err.message : '未知错误')
  }
}

const handleToggleVerifyInDialog = async () => {
  if (!currentCapability.value) return
  await handleToggleVerify(currentCapability.value)
}

const handleExtractCapabilities = async () => {
  extractForm.doc_ids = []
  extractForm.tag_id = currentTagId.value

  try {
    const response = await fetch(`/api/documents?company_id=${companyId.value}&limit=100`)
    const result = await response.json()
    if (result.success) {
      availableDocs.value = result.data || []
    }
  } catch (err) {
    console.error('加载文档列表失败:', err)
  }

  extractDialogVisible.value = true
}

const handleStartExtract = async () => {
  extracting.value = true
  try {
    const response = await fetch(`${CAPABILITY_API_BASE}/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id: companyId.value,
        doc_ids: extractForm.doc_ids,
        tag_id: extractForm.tag_id
      })
    })

    const result = await response.json()

    if (result.success) {
      success('提取完成', `成功提取 ${result.extracted_count || 0} 个能力`)
      extractDialogVisible.value = false
      loadCapabilities()
    } else {
      error('提取失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('能力提取失败:', err)
    error('提取失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    extracting.value = false
  }
}

// 工具函数
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    '功能': 'primary',
    '接口': 'success',
    '服务': 'warning',
    '支持能力': 'info'
  }
  return typeMap[type] || 'info'
}

const getConfidenceColor = (score: number) => {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

// 生命周期
onMounted(() => {
  loadCategories()
  loadTags()
  loadCapabilities()
})

// 监听 Tab 切换，懒加载数据
watch(activeTab, (tab) => {
  if (tab === 'categories' && !categories.value.length) {
    loadCategories()
  } else if (tab === 'capabilities' && !tags.value.length) {
    loadTags()
    loadCapabilities()
  }
})

// 监听企业变化
watch(companyId, () => {
  loadTags()
  loadCapabilities()
})
</script>

<style scoped lang="scss">
.product-management {
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
          border-radius: 12px;

          &.categories {
            background: #ecf5ff;
          }
          &.items {
            background: #f0f9eb;
          }
          &.tags {
            background: #fdf6ec;
          }
          &.capabilities {
            background: #f4f4f5;
          }
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

  .tab-toolbar {
    margin-bottom: 16px;
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

  .tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;

    .node-label {
      flex: 1;
    }

    .node-actions {
      display: none;
    }

    &:hover .node-actions {
      display: flex;
      gap: 4px;
    }
  }

  .capabilities-toolbar {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }

  .original-text {
    max-height: 200px;
    overflow-y: auto;
    padding: 8px;
    background: #f5f7fa;
    border-radius: 4px;
    font-size: 13px;
    line-height: 1.6;
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
