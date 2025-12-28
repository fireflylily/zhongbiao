<template>
  <div class="tender-library">
    <!-- 统计信息 -->
    <div class="stats-bar">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon docs">
            <el-icon :size="32" color="#409eff"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">标书文档</div>
            <div class="stat-value">{{ stats.docCount }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon excerpts">
            <el-icon :size="32" color="#67c23a"><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">素材片段</div>
            <div class="stat-value">{{ stats.excerptCount }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon won">
            <el-icon :size="32" color="#e6a23c"><Trophy /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">中标标书</div>
            <div class="stat-value">{{ stats.wonCount }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主内容区 -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 标书文档标签页 -->
      <el-tab-pane label="标书文档" name="documents">
        <div class="tab-toolbar">
          <el-input
            v-model="docSearch"
            placeholder="搜索文档名称..."
            clearable
            style="width: 200px"
            @keyup.enter="loadDocuments"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="docBidResult" placeholder="投标结果" clearable style="width: 120px" @change="loadDocuments">
            <el-option label="全部" value="" />
            <el-option label="中标" value="中标" />
            <el-option label="未中标" value="未中标" />
            <el-option label="待定" value="待定" />
          </el-select>
          <el-button type="primary" @click="handleUploadDoc">
            <el-icon><Upload /></el-icon>
            上传标书
          </el-button>
        </div>

        <Loading v-if="loadingDocs" text="加载中..." />
        <Empty v-else-if="!documents.length" type="no-data" description="暂无标书文档" />

        <el-table v-else :data="documents" stripe>
          <el-table-column prop="doc_name" label="文档名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="project_name" label="项目名称" width="180" show-overflow-tooltip />
          <el-table-column prop="bid_result" label="投标结果" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getBidResultType(row.bid_result)">
                {{ row.bid_result || '待定' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="excerpt_count" label="片段数" width="80" align="center" />
          <el-table-column prop="bid_date" label="投标日期" width="120" />
          <el-table-column prop="created_at" label="上传时间" width="160" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleViewDoc(row)">
                查看
              </el-button>
              <el-button link type="success" size="small" @click="handleExtractExcerpts(row)">
                提取
              </el-button>
              <el-button link type="warning" size="small" @click="handleEditDoc(row)">
                编辑
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteDoc(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper" v-if="docTotal > docPageSize">
          <el-pagination
            v-model:current-page="docCurrentPage"
            v-model:page-size="docPageSize"
            :total="docTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadDocuments"
            @current-change="loadDocuments"
          />
        </div>
      </el-tab-pane>

      <!-- 素材片段标签页 -->
      <el-tab-pane label="素材片段" name="excerpts">
        <div class="tab-toolbar">
          <el-input
            v-model="excerptSearch"
            placeholder="搜索素材内容..."
            clearable
            style="width: 250px"
            @keyup.enter="loadExcerpts"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="excerptCategory" placeholder="分类" clearable style="width: 120px" @change="loadExcerpts">
            <el-option label="全部" value="" />
            <el-option label="技术方案" value="技术方案" />
            <el-option label="项目管理" value="项目管理" />
            <el-option label="售后服务" value="售后服务" />
            <el-option label="企业资质" value="企业资质" />
            <el-option label="团队介绍" value="团队介绍" />
            <el-option label="其他" value="其他" />
          </el-select>
          <el-checkbox v-model="excerptWonOnly" @change="loadExcerpts">仅中标</el-checkbox>
        </div>

        <Loading v-if="loadingExcerpts" text="加载中..." />
        <Empty v-else-if="!excerpts.length" type="no-data" description="暂无素材片段" />

        <div v-else class="excerpts-list">
          <el-card
            v-for="excerpt in excerpts"
            :key="excerpt.excerpt_id"
            class="excerpt-card"
            shadow="hover"
          >
            <template #header>
              <div class="excerpt-header">
                <div class="excerpt-title">
                  <span class="chapter-title">{{ excerpt.chapter_title || '无标题' }}</span>
                  <el-tag size="small" :type="getCategoryType(excerpt.category)">
                    {{ excerpt.category || '未分类' }}
                  </el-tag>
                  <el-tag v-if="excerpt.bid_result === '中标'" size="small" type="success">
                    中标
                  </el-tag>
                </div>
                <div class="excerpt-meta">
                  <span class="doc-name">{{ excerpt.doc_name }}</span>
                  <el-rate
                    v-model="excerpt.quality_score"
                    disabled
                    :max="5"
                    size="small"
                    :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                  />
                </div>
              </div>
            </template>
            <div class="excerpt-content">
              {{ excerpt.content?.substring(0, 300) }}{{ excerpt.content?.length > 300 ? '...' : '' }}
            </div>
            <div class="excerpt-footer">
              <div class="excerpt-tags">
                <el-tag
                  v-for="tag in (excerpt.tags || '').split(',').filter(Boolean).slice(0, 3)"
                  :key="tag"
                  size="small"
                  type="info"
                >
                  {{ tag }}
                </el-tag>
              </div>
              <div class="excerpt-actions">
                <el-button link type="primary" size="small" @click="handleViewExcerpt(excerpt)">
                  查看全文
                </el-button>
                <el-button link type="primary" size="small" @click="handleCopyExcerpt(excerpt)">
                  复制
                </el-button>
                <el-button link type="warning" size="small" @click="handleEditExcerpt(excerpt)">
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click="handleDeleteExcerpt(excerpt)">
                  删除
                </el-button>
              </div>
            </div>
          </el-card>
        </div>

        <div class="pagination-wrapper" v-if="excerptTotal > excerptPageSize">
          <el-pagination
            v-model:current-page="excerptCurrentPage"
            v-model:page-size="excerptPageSize"
            :total="excerptTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadExcerpts"
            @current-change="loadExcerpts"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 上传文档对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传标书文档"
      width="600px"
    >
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="文档文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".docx,.doc,.pdf"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">支持 .docx, .doc, .pdf 格式</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="所属公司" prop="company_id">
          <el-select
            v-model="uploadForm.company_id"
            placeholder="请选择公司"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="company in companyStore.companiesOptions"
              :key="company.value"
              :label="company.label"
              :value="company.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联产品" prop="related_products">
          <el-select
            v-model="uploadForm.related_products"
            placeholder="请选择产品分类（可多选）"
            style="width: 100%"
            multiple
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option-group
              v-for="category in productCategories"
              :key="category.category_id"
              :label="category.category_name"
            >
              <el-option
                v-for="item in category.items"
                :key="item.item_id"
                :label="item.item_name"
                :value="item.item_code"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="项目名称" prop="project_name">
          <el-input v-model="uploadForm.project_name" placeholder="投标项目名称" />
        </el-form-item>
        <el-form-item label="投标结果" prop="bid_result">
          <el-radio-group v-model="uploadForm.bid_result">
            <el-radio label="中标">中标</el-radio>
            <el-radio label="未中标">未中标</el-radio>
            <el-radio label="待定">待定</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="投标日期" prop="bid_date">
          <el-date-picker
            v-model="uploadForm.bid_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="uploadForm.notes"
            type="textarea"
            :rows="2"
            placeholder="可选备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑文档对话框 -->
    <el-dialog
      v-model="editDocDialogVisible"
      title="编辑标书信息"
      width="500px"
    >
      <el-form :model="editDocForm" label-width="100px">
        <el-form-item label="项目名称">
          <el-input v-model="editDocForm.project_name" />
        </el-form-item>
        <el-form-item label="投标结果">
          <el-radio-group v-model="editDocForm.bid_result">
            <el-radio label="中标">中标</el-radio>
            <el-radio label="未中标">未中标</el-radio>
            <el-radio label="待定">待定</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="投标日期">
          <el-date-picker
            v-model="editDocForm.bid_date"
            type="date"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editDocForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDocDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDoc" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 素材详情/编辑对话框 -->
    <el-dialog
      v-model="excerptDialogVisible"
      :title="excerptDialogMode === 'view' ? '素材详情' : '编辑素材'"
      width="700px"
    >
      <template v-if="excerptDialogMode === 'view'">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="章节标题" :span="2">
            {{ currentExcerpt?.chapter_title }}
          </el-descriptions-item>
          <el-descriptions-item label="分类">
            {{ currentExcerpt?.category || '未分类' }}
          </el-descriptions-item>
          <el-descriptions-item label="质量评分">
            <el-rate
              :model-value="currentExcerpt?.quality_score"
              disabled
              :max="5"
            />
          </el-descriptions-item>
          <el-descriptions-item label="来源文档" :span="2">
            {{ currentExcerpt?.doc_name }}
          </el-descriptions-item>
          <el-descriptions-item label="投标结果">
            <el-tag :type="getBidResultType(currentExcerpt?.bid_result)">
              {{ currentExcerpt?.bid_result || '待定' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标签">
            {{ currentExcerpt?.tags || '无' }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="excerpt-full-content">
          <h4>素材内容</h4>
          <div class="content-box">{{ currentExcerpt?.content }}</div>
        </div>
      </template>
      <template v-else>
        <el-form :model="excerptEditForm" label-width="100px">
          <el-form-item label="章节标题">
            <el-input v-model="excerptEditForm.chapter_title" />
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="excerptEditForm.category" style="width: 100%">
              <el-option label="技术方案" value="技术方案" />
              <el-option label="项目管理" value="项目管理" />
              <el-option label="售后服务" value="售后服务" />
              <el-option label="企业资质" value="企业资质" />
              <el-option label="团队介绍" value="团队介绍" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          <el-form-item label="质量评分">
            <el-rate v-model="excerptEditForm.quality_score" :max="5" />
          </el-form-item>
          <el-form-item label="标签">
            <el-input v-model="excerptEditForm.tags" placeholder="逗号分隔的标签" />
          </el-form-item>
          <el-form-item label="内容">
            <el-input
              v-model="excerptEditForm.content"
              type="textarea"
              :rows="10"
            />
          </el-form-item>
        </el-form>
      </template>
      <template #footer>
        <el-button @click="excerptDialogVisible = false">关闭</el-button>
        <el-button
          v-if="excerptDialogMode === 'view'"
          type="primary"
          @click="excerptDialogMode = 'edit'"
        >
          编辑
        </el-button>
        <el-button
          v-else
          type="primary"
          @click="handleSaveExcerpt"
          :loading="saving"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 文档预览对话框 -->
    <DocumentPreview
      v-model="previewDialogVisible"
      :file-url="previewFileUrl"
      :file-name="previewFileName"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Card, Loading, Empty } from '@/components'
import DocumentPreview from '@/components/DocumentPreview.vue'
import { useNotification } from '@/composables'
import {
  Document, Tickets, Trophy, Search, Upload
} from '@element-plus/icons-vue'
import type { FormInstance, UploadInstance } from 'element-plus'
import { ElMessageBox } from 'element-plus'
import { useCompanyStore } from '@/stores/company'

// API 基础路径
const API_BASE = '/api/tender-library'

// Hooks
const { success, error } = useNotification()
const companyStore = useCompanyStore()

// 获取当前企业ID（用于列表筛选，优先使用 companyStore）
const companyId = computed(() => companyStore.companyId || 1)

// 产品分类数据
interface ProductCategory {
  category_id: number
  category_name: string
  category_code: string
  items: { item_id: number; item_name: string; item_code: string }[]
}
const productCategories = ref<ProductCategory[]>([])

// 加载产品分类
const loadProductCategories = async () => {
  try {
    const response = await fetch('/api/product-categories')
    const result = await response.json()
    if (result.success) {
      productCategories.value = result.data || []
    }
  } catch (err) {
    console.error('加载产品分类失败:', err)
  }
}

// 统计数据
const stats = reactive({
  docCount: 0,
  excerptCount: 0,
  wonCount: 0
})

// 标签页
const activeTab = ref('documents')

// 文档列表状态
const loadingDocs = ref(false)
const documents = ref<any[]>([])
const docSearch = ref('')
const docBidResult = ref('')
const docCurrentPage = ref(1)
const docPageSize = ref(10)
const docTotal = ref(0)

// 素材片段状态
const loadingExcerpts = ref(false)
const excerpts = ref<any[]>([])
const excerptSearch = ref('')
const excerptCategory = ref('')
const excerptWonOnly = ref(false)
const excerptCurrentPage = ref(1)
const excerptPageSize = ref(10)
const excerptTotal = ref(0)

// 上传对话框
const uploadDialogVisible = ref(false)
const uploadRef = ref<UploadInstance>()
const uploadFormRef = ref<FormInstance>()
const uploadForm = reactive({
  file: null as File | null,
  company_id: null as number | null,
  related_products: [] as string[],
  project_name: '',
  bid_result: '待定',
  bid_date: '',
  notes: ''
})
const uploadRules = {
  company_id: [{ required: true, message: '请选择所属公司', trigger: 'change' }],
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }]
}
const uploading = ref(false)

// 文档预览对话框
const previewDialogVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')

// 编辑文档对话框
const editDocDialogVisible = ref(false)
const editDocForm = reactive({
  tender_doc_id: null as number | null,
  project_name: '',
  bid_result: '',
  bid_date: '',
  notes: ''
})
const saving = ref(false)

// 素材详情/编辑对话框
const excerptDialogVisible = ref(false)
const excerptDialogMode = ref<'view' | 'edit'>('view')
const currentExcerpt = ref<any>(null)
const excerptEditForm = reactive({
  excerpt_id: null as number | null,
  chapter_title: '',
  category: '',
  quality_score: 0,
  tags: '',
  content: ''
})

// 加载文档列表
const loadDocuments = async () => {
  loadingDocs.value = true
  try {
    const params = new URLSearchParams({
      company_id: String(companyId.value),
      page: String(docCurrentPage.value),
      page_size: String(docPageSize.value)
    })

    if (docSearch.value) params.append('keyword', docSearch.value)
    if (docBidResult.value) params.append('bid_result', docBidResult.value)

    const response = await fetch(`${API_BASE}/documents?${params}`)
    const result = await response.json()

    if (result.success) {
      documents.value = result.data || []
      docTotal.value = result.total || 0
      stats.docCount = docTotal.value
      stats.wonCount = documents.value.filter((d: any) => d.bid_result === '中标').length
    } else {
      error('加载失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('加载文档列表失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loadingDocs.value = false
  }
}

// 加载素材片段
const loadExcerpts = async () => {
  loadingExcerpts.value = true
  try {
    const params = new URLSearchParams({
      company_id: String(companyId.value),
      page: String(excerptCurrentPage.value),
      page_size: String(excerptPageSize.value)
    })

    if (excerptSearch.value) params.append('keyword', excerptSearch.value)
    if (excerptCategory.value) params.append('category', excerptCategory.value)
    if (excerptWonOnly.value) params.append('won_only', 'true')

    const response = await fetch(`${API_BASE}/excerpts?${params}`)
    const result = await response.json()

    if (result.success) {
      excerpts.value = result.data || []
      excerptTotal.value = result.total || 0
      stats.excerptCount = excerptTotal.value
    } else {
      error('加载失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('加载素材片段失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loadingExcerpts.value = false
  }
}

// 打开上传对话框
const handleUploadDoc = () => {
  uploadForm.file = null
  uploadForm.company_id = companyStore.companyId || null
  uploadForm.related_products = []
  uploadForm.project_name = ''
  uploadForm.bid_result = '待定'
  uploadForm.bid_date = ''
  uploadForm.notes = ''
  // 清空上传组件的文件列表
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  uploadDialogVisible.value = true
}

// 文件选择
const handleFileChange = (uploadFile: any, uploadFiles: any[]) => {
  // Element Plus upload 组件的 on-change 回调参数是 UploadFile 对象
  if (uploadFile && uploadFile.raw) {
    uploadForm.file = uploadFile.raw
  }
}

// 文件移除
const handleFileRemove = () => {
  uploadForm.file = null
}

// 提交上传
const handleSubmitUpload = async () => {
  if (!uploadForm.file) {
    error('请选择文件')
    return
  }
  if (!uploadForm.company_id) {
    error('请选择所属公司')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('company_id', String(uploadForm.company_id))
    formData.append('project_name', uploadForm.project_name)
    formData.append('bid_result', uploadForm.bid_result)
    if (uploadForm.bid_date) formData.append('bid_date', uploadForm.bid_date)
    if (uploadForm.notes) formData.append('notes', uploadForm.notes)
    if (uploadForm.related_products.length > 0) {
      formData.append('related_products', JSON.stringify(uploadForm.related_products))
    }

    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (result.success) {
      success('上传成功', result.message)
      uploadDialogVisible.value = false
      loadDocuments()
    } else {
      error('上传失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('上传失败:', err)
    error('上传失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    uploading.value = false
  }
}

// 查看文档 - 使用 DocumentPreview 组件
const handleViewDoc = (doc: any) => {
  previewFileUrl.value = doc.file_path || ''
  previewFileName.value = doc.doc_name || '文档预览'
  previewDialogVisible.value = true
}

// 提取素材
const handleExtractExcerpts = async (doc: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要从 "${doc.doc_name}" 提取素材片段吗？`,
      '提取素材',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
  } catch {
    return  // 用户点击取消
  }

  try {
    const response = await fetch(`${API_BASE}/documents/${doc.tender_doc_id}/extract`, {
      method: 'POST'
    })

    const result = await response.json()

    if (result.success) {
      success('提取完成', `成功提取 ${result.extracted_count || 0} 个片段`)
      loadDocuments()
      loadExcerpts()
    } else {
      error('提取失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('提取失败:', err)
    error('提取失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 编辑文档
const handleEditDoc = (doc: any) => {
  editDocForm.tender_doc_id = doc.tender_doc_id
  editDocForm.project_name = doc.project_name || ''
  editDocForm.bid_result = doc.bid_result || '待定'
  editDocForm.bid_date = doc.bid_date || ''
  editDocForm.notes = doc.notes || ''
  editDocDialogVisible.value = true
}

// 保存文档
const handleSaveDoc = async () => {
  saving.value = true
  try {
    const response = await fetch(`${API_BASE}/documents/${editDocForm.tender_doc_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editDocForm)
    })

    const result = await response.json()

    if (result.success) {
      success('保存成功')
      editDocDialogVisible.value = false
      loadDocuments()
    } else {
      error('保存失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('保存失败:', err)
    error('保存失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    saving.value = false
  }
}

// 删除文档
const handleDeleteDoc = async (doc: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 "${doc.doc_name}" 吗？关联的素材片段也会被删除。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return  // 用户点击取消
  }

  try {
    const response = await fetch(`${API_BASE}/documents/${doc.tender_doc_id}`, {
      method: 'DELETE'
    })

    const result = await response.json()

    if (result.success) {
      success('删除成功')
      loadDocuments()
      loadExcerpts()
    } else {
      error('删除失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('删除失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 查看素材详情
const handleViewExcerpt = (excerpt: any) => {
  currentExcerpt.value = excerpt
  excerptDialogMode.value = 'view'
  excerptDialogVisible.value = true
}

// 编辑素材
const handleEditExcerpt = (excerpt: any) => {
  currentExcerpt.value = excerpt
  excerptEditForm.excerpt_id = excerpt.excerpt_id
  excerptEditForm.chapter_title = excerpt.chapter_title || ''
  excerptEditForm.category = excerpt.category || ''
  excerptEditForm.quality_score = excerpt.quality_score || 0
  excerptEditForm.tags = excerpt.tags || ''
  excerptEditForm.content = excerpt.content || ''
  excerptDialogMode.value = 'edit'
  excerptDialogVisible.value = true
}

// 保存素材
const handleSaveExcerpt = async () => {
  saving.value = true
  try {
    const response = await fetch(`${API_BASE}/excerpts/${excerptEditForm.excerpt_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(excerptEditForm)
    })

    const result = await response.json()

    if (result.success) {
      success('保存成功')
      excerptDialogVisible.value = false
      loadExcerpts()
    } else {
      error('保存失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('保存失败:', err)
    error('保存失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    saving.value = false
  }
}

// 复制素材
const handleCopyExcerpt = async (excerpt: any) => {
  try {
    await navigator.clipboard.writeText(excerpt.content || '')
    success('已复制到剪贴板')
  } catch (err) {
    error('复制失败')
  }
}

// 删除素材
const handleDeleteExcerpt = async (excerpt: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除素材片段 "${excerpt.chapter_title || '未命名'}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return  // 用户取消
  }

  try {
    const response = await fetch(`${API_BASE}/excerpts/${excerpt.excerpt_id}`, {
      method: 'DELETE'
    })

    const result = await response.json()

    if (result.success) {
      success('删除成功')
      loadExcerpts()
    } else {
      error('删除失败', result.error || '未知错误')
    }
  } catch (err) {
    console.error('删除失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 工具函数
const getBidResultType = (result: string) => {
  if (result === '中标') return 'success'
  if (result === '未中标') return 'danger'
  return 'info'
}

const getCategoryType = (category: string) => {
  const map: Record<string, string> = {
    '技术方案': 'primary',
    '项目管理': 'success',
    '售后服务': 'warning',
    '企业资质': 'info',
    '团队介绍': '',
    '其他': 'info'
  }
  return map[category] || 'info'
}

// 生命周期
onMounted(() => {
  companyStore.fetchCompanies()
  loadProductCategories()
  loadDocuments()
  loadExcerpts()
})

// 监听标签页切换
watch(activeTab, (tab) => {
  if (tab === 'documents') {
    loadDocuments()
  } else {
    loadExcerpts()
  }
})

// 监听企业变化
watch(companyId, () => {
  loadDocuments()
  loadExcerpts()
})
</script>

<style scoped lang="scss">
.tender-library {
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

          &.docs {
            background: #ecf5ff;
          }
          &.excerpts {
            background: #f0f9eb;
          }
          &.won {
            background: #fdf6ec;
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
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 16px;
  }

  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }

  .excerpts-list {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .excerpt-card {
      .excerpt-header {
        .excerpt-title {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;

          .chapter-title {
            font-weight: 600;
            font-size: 15px;
          }
        }

        .excerpt-meta {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 13px;
          color: #909399;
        }
      }

      .excerpt-content {
        font-size: 14px;
        line-height: 1.6;
        color: #606266;
      }

      .excerpt-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #ebeef5;

        .excerpt-tags {
          display: flex;
          gap: 4px;
        }

        .excerpt-actions {
          display: flex;
          gap: 8px;
        }
      }
    }
  }

  .excerpt-full-content {
    margin-top: 16px;

    h4 {
      margin-bottom: 8px;
      color: #303133;
    }

    .content-box {
      padding: 12px;
      background: #f5f7fa;
      border-radius: 4px;
      max-height: 300px;
      overflow-y: auto;
      font-size: 14px;
      line-height: 1.8;
      white-space: pre-wrap;
    }
  }
}
</style>
