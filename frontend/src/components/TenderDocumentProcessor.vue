<template>
  <div class="tender-document-processor">
    <!-- 折叠面板 -->
    <el-collapse v-model="activeNames" accordion>
      <!-- 步骤1: 文档上传 -->
      <el-collapse-item name="upload">
        <template #title>
          <div class="collapse-title">
            <i class="bi bi-upload me-2 text-primary"></i>
            <span>步骤1: 上传招标文档（可选）</span>
            <el-tag v-if="uploadedFile" type="success" size="small" class="ms-2">
              已上传
            </el-tag>
          </div>
        </template>

        <div class="upload-section">
          <!-- 显示已上传的文档 -->
          <div v-if="hasExistingDocument" class="existing-document">
            <el-alert type="success" :closable="false">
              <template #title>
                <div class="d-flex align-items-center justify-content-between">
                  <div>
                    <i class="bi bi-file-earmark-check-fill me-2"></i>
                    <span class="me-3">{{ existingDocumentInfo.name }}</span>
                    <el-tag size="small" type="success">已上传</el-tag>
                  </div>
                  <div>
                    <el-button
                      size="small"
                      @click="handlePreviewExisting"
                    >
                      <i class="bi bi-eye me-1"></i>
                      预览
                    </el-button>
                    <el-button
                      size="small"
                      @click="handleClearExisting"
                    >
                      <i class="bi bi-arrow-repeat me-1"></i>
                      重新上传
                    </el-button>
                  </div>
                </div>
              </template>
            </el-alert>
          </div>

          <!-- 上传新文档 -->
          <div v-else>
            <el-upload
              ref="uploadRef"
              drag
              :auto-upload="false"
              :limit="1"
              accept=".doc,.docx"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
            >
              <i class="bi bi-cloud-upload" style="font-size: 48px; color: var(--el-color-primary)"></i>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 .doc 和 .docx 格式，文件大小不超过 50MB（可选上传，用于辅助解析）
                </div>
              </template>
            </el-upload>

            <div v-if="uploadedFile" class="mt-3">
              <el-alert type="success" :closable="false">
                <template #title>
                  <div class="d-flex align-items-center justify-content-between">
                    <span>
                      <i class="bi bi-check-circle-fill me-2"></i>
                      已选择文件: {{ uploadedFile.name }}
                    </span>
                    <el-button
                      type="primary"
                      size="small"
                      :loading="parsing"
                      @click="handleParse"
                    >
                      <i v-if="!parsing" class="bi bi-file-earmark-code me-1"></i>
                      {{ parsing ? '解析中...' : '解析文档结构' }}
                    </el-button>
                  </div>
                </template>
              </el-alert>
            </div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 步骤2: 章节选择 (解析完成后显示) -->
      <el-collapse-item v-if="chapters.length > 0" name="chapters">
        <template #title>
          <div class="collapse-title">
            <i class="bi bi-list-nested me-2 text-success"></i>
            <span>步骤2: 选择章节</span>
            <el-tag v-if="selectedCount > 0" type="success" size="small" class="ms-2">
              已选 {{ selectedCount }} 个
            </el-tag>
          </div>
        </template>

        <div class="chapter-section">
          <!-- 统计信息 -->
          <div class="stats-grid mb-3">
            <div class="stat-card">
              <div class="stat-label">总章节数</div>
              <div class="stat-value">{{ totalChapters }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">已选择</div>
              <div class="stat-value text-success">{{ selectedCount }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">选中字数</div>
              <div class="stat-value text-info">{{ formatWordCount(selectedWordCount) }}</div>
            </div>
          </div>

          <!-- 批量操作 -->
          <div class="batch-operations mb-3">
            <el-button-group>
              <el-button size="small" @click="handleSelectAll">
                <i class="bi bi-check-all me-1"></i> 全选
              </el-button>
              <el-button size="small" @click="handleUnselectAll">
                <i class="bi bi-x me-1"></i> 全不选
              </el-button>
              <el-button size="small" type="success" @click="handleSelectTech">
                <i class="bi bi-cpu me-1"></i> 仅选技术章节
              </el-button>
              <el-button size="small" type="warning" @click="handleExcludeContract">
                <i class="bi bi-file-x me-1"></i> 排除合同条款
              </el-button>
            </el-button-group>
          </div>

          <!-- 章节树 -->
          <ChapterTree
            ref="chapterTreeRef"
            :chapters="chapters"
            @check="handleChapterCheck"
          />

          <!-- 保存操作 -->
          <div class="save-actions mt-4">
            <el-space :size="16">
              <el-button
                type="info"
                size="large"
                :disabled="selectedCount === 0"
                :loading="savingResponse"
                @click="handleSaveAsResponse"
              >
                <i class="bi bi-file-earmark-arrow-down me-1"></i>
                另存为应答文件
              </el-button>
              <el-button
                type="success"
                size="large"
                :disabled="selectedCount === 0"
                :loading="savingTechnical"
                @click="handleSaveAsTechnical"
              >
                <i class="bi bi-file-code me-1"></i>
                另存为技术需求
              </el-button>
            </el-space>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 解析进度提示 -->
    <div v-if="parsing" class="parsing-progress mt-3">
      <el-alert type="info" :closable="false">
        <template #title>
          <div class="d-flex align-items-center">
            <el-icon class="is-loading me-2">
              <Loading />
            </el-icon>
            <span>{{ parsingMessage }}</span>
          </div>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import ChapterTree from './ChapterTree.vue'
import { tenderApi } from '@/api/endpoints/tender'
import type { UploadFile, UploadInstance } from 'element-plus'

// 章节数据类型
interface Chapter {
  id: string
  title: string
  level: number
  word_count?: number
  children?: Chapter[]
  [key: string]: any
}

// Props
interface Props {
  projectId: number
  companyId: number
  projectDetail?: any // 项目详情数据
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  success: [type: 'response' | 'technical']
  refresh: []
  preview: [fileUrl: string, fileName: string]
}>()

// 状态
const uploadRef = ref<UploadInstance>()
const chapterTreeRef = ref<InstanceType<typeof ChapterTree>>()
const activeNames = ref(['upload'])
const fileList = ref<UploadFile[]>([])
const uploadedFile = ref<File | null>(null)
const parsing = ref(false)
const parsingMessage = ref('正在解析文档结构...')
const chapters = ref<Chapter[]>([])
const selectedChapterIds = ref<string[]>([])
const selectedChapterNodes = ref<Chapter[]>([])
const savingResponse = ref(false)
const savingTechnical = ref(false)
const existingDocumentInfo = ref<any>(null) // 已存在的文档信息

// 计算属性
const totalChapters = computed(() => {
  const countChapters = (chaps: Chapter[]): number => {
    let count = chaps.length
    chaps.forEach(chap => {
      if (chap.children && chap.children.length > 0) {
        count += countChapters(chap.children)
      }
    })
    return count
  }
  return countChapters(chapters.value)
})

const selectedCount = computed(() => selectedChapterIds.value.length)

const selectedWordCount = computed(() => {
  return selectedChapterNodes.value.reduce((sum, node) => {
    return sum + (node.word_count || 0)
  }, 0)
})

// 计算是否有已上传的文档
const hasExistingDocument = computed(() => {
  return existingDocumentInfo.value !== null
})

// 文件上传处理
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    uploadedFile.value = file.raw
    fileList.value = [file]
  }
}

const handleFileRemove = () => {
  uploadedFile.value = null
  fileList.value = []
  chapters.value = []
  selectedChapterIds.value = []
}

// 预览已上传的文档
const handlePreviewExisting = () => {
  if (existingDocumentInfo.value) {
    emit('preview', existingDocumentInfo.value.path, existingDocumentInfo.value.name)
  }
}

// 清除已存在的文档，允许重新上传
const handleClearExisting = () => {
  existingDocumentInfo.value = null
  chapters.value = []
  selectedChapterIds.value = []
  activeNames.value = ['upload']
}

// 解析文档
const handleParse = async () => {
  if (!uploadedFile.value) {
    ElMessage.warning('请先上传文档')
    return
  }

  parsing.value = true
  parsingMessage.value = '正在解析文档结构...'

  try {
    // 调用API解析文档
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    formData.append('company_id', props.companyId.toString())
    formData.append('project_id', props.projectId.toString())

    const response = await tenderApi.parseDocumentStructure(formData)

    if (response.success) {
      // 后端直接返回chapters，不在data字段中
      chapters.value = (response as any).chapters || []

      ElMessage.success('文档解析成功')

      // 自动展开章节选择面板
      activeNames.value = ['chapters']
    } else {
      throw new Error((response as any).message || (response as any).error || '解析失败')
    }
  } catch (error) {
    console.error('文档解析失败:', error)
    ElMessage.error(`解析失败: ${error instanceof Error ? error.message : '未知错误'}`)
  } finally {
    parsing.value = false
  }
}

// 章节选择处理
const handleChapterCheck = (checkedKeys: string[], checkedNodes: Chapter[]) => {
  selectedChapterIds.value = checkedKeys
  selectedChapterNodes.value = checkedNodes
}

// 批量操作
const handleSelectAll = () => {
  const allKeys = getAllChapterIds(chapters.value)
  chapterTreeRef.value?.setCheckedKeys(allKeys)
}

const handleUnselectAll = () => {
  chapterTreeRef.value?.setCheckedKeys([])
}

const handleSelectTech = () => {
  // 筛选包含"技术"关键词的章节
  const techKeys = filterChaptersByKeywords(chapters.value, ['技术', '方案', '实施', '系统'])
  chapterTreeRef.value?.setCheckedKeys(techKeys)
}

const handleExcludeContract = () => {
  // 排除包含"合同"关键词的章节
  const allKeys = getAllChapterIds(chapters.value)
  const contractKeys = filterChaptersByKeywords(chapters.value, ['合同', '条款', '协议'])
  const excludedKeys = allKeys.filter(key => !contractKeys.includes(key))
  chapterTreeRef.value?.setCheckedKeys(excludedKeys)
}

// 辅助函数：获取所有章节ID
const getAllChapterIds = (chaps: Chapter[]): string[] => {
  const ids: string[] = []
  chaps.forEach(chap => {
    ids.push(chap.id)
    if (chap.children && chap.children.length > 0) {
      ids.push(...getAllChapterIds(chap.children))
    }
  })
  return ids
}

// 辅助函数：根据关键词筛选章节
const filterChaptersByKeywords = (chaps: Chapter[], keywords: string[]): string[] => {
  const ids: string[] = []
  chaps.forEach(chap => {
    const matchesKeyword = keywords.some(keyword => chap.title.includes(keyword))
    if (matchesKeyword) {
      ids.push(chap.id)
    }
    if (chap.children && chap.children.length > 0) {
      ids.push(...filterChaptersByKeywords(chap.children, keywords))
    }
  })
  return ids
}

// 保存为应答文件
const handleSaveAsResponse = async () => {
  if (selectedCount.value === 0) {
    ElMessage.warning('请先选择章节')
    return
  }

  savingResponse.value = true

  try {
    // 调用API保存
    await tenderApi.saveResponseFile(props.projectId, selectedChapterIds.value)

    ElMessage.success('应答文件保存成功')
    emit('success', 'response')
    emit('refresh')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(`保存失败: ${error instanceof Error ? error.message : '未知错误'}`)
  } finally {
    savingResponse.value = false
  }
}

// 保存为技术需求
const handleSaveAsTechnical = async () => {
  if (selectedCount.value === 0) {
    ElMessage.warning('请先选择章节')
    return
  }

  savingTechnical.value = true

  try {
    // 调用API保存
    await tenderApi.saveTechnicalChapters(props.projectId, selectedChapterIds.value)

    ElMessage.success('技术需求保存成功')
    emit('success', 'technical')
    emit('refresh')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(`保存失败: ${error instanceof Error ? error.message : '未知错误'}`)
  } finally {
    savingTechnical.value = false
  }
}

// 格式化字数
const formatWordCount = (count: number) => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  }
  return count.toLocaleString()
}

// 辅助函数：从路径中提取文件名
const extractFilenameFromPath = (path: string): string => {
  if (!path) return '招标文档'

  try {
    // 处理反斜杠和正斜杠
    const normalizedPath = path.replace(/\\/g, '/')
    const parts = normalizedPath.split('/')
    const filename = parts[parts.length - 1]

    // URL解码
    return decodeURIComponent(filename)
  } catch (e) {
    console.warn('提取文件名失败:', e)
    return '招标文档'
  }
}

// 初始化已有数据
const initializeExistingData = () => {
  if (!props.projectDetail) return

  // 提取step1_data
  let step1Data = props.projectDetail.step1_data
  if (typeof step1Data === 'string') {
    try {
      step1Data = JSON.parse(step1Data)
    } catch (e) {
      console.warn('解析step1_data失败:', e)
      step1Data = null
    }
  }

  // 检查是否有已上传的招标文档
  // 优先从数据库字段读取（新架构 + 旧数据兼容）
  if (props.projectDetail.tender_document_path) {
    const filename = props.projectDetail.original_filename ||
                     extractFilenameFromPath(props.projectDetail.tender_document_path)

    existingDocumentInfo.value = {
      path: props.projectDetail.tender_document_path,
      name: filename,
      uploadedAt: props.projectDetail.created_at
    }
  }
  // 备选：从 step1_data JSON 读取（兼容旧数据）
  else if (step1Data?.file_path) {
    const filename = step1Data.file_name ||
                     extractFilenameFromPath(step1Data.file_path)

    existingDocumentInfo.value = {
      path: step1Data.file_path,
      name: filename,
      uploadedAt: props.projectDetail.created_at
    }
  }

  // 加载已解析的章节
  if (step1Data?.chapters && Array.isArray(step1Data.chapters) && step1Data.chapters.length > 0) {
    chapters.value = step1Data.chapters
    // 自动展开章节面板
    activeNames.value = ['chapters']
  }
}

// 监听projectDetail变化
watch(() => props.projectDetail, () => {
  initializeExistingData()
}, { immediate: true })

// 组件挂载时初始化
onMounted(() => {
  initializeExistingData()
})
</script>

<style scoped lang="scss">
.tender-document-processor {
  margin-bottom: 20px;

  .collapse-title {
    display: flex;
    align-items: center;
    font-size: 16px;
    font-weight: 600;
  }

  .upload-section {
    padding: 20px;

    :deep(.el-upload-dragger) {
      width: 100%;
      padding: 40px;
    }
  }

  .chapter-section {
    padding: 20px;

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;

      .stat-card {
        background: var(--el-bg-color-page);
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 8px;
        padding: 16px;
        text-align: center;

        .stat-label {
          font-size: 12px;
          color: var(--el-text-color-secondary);
          margin-bottom: 8px;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
      }
    }

    .batch-operations {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .save-actions {
      display: flex;
      justify-content: center;
      padding-top: 20px;
      border-top: 1px solid var(--el-border-color-lighter);
    }
  }

  .parsing-progress {
    :deep(.el-alert__title) {
      display: flex;
      align-items: center;
    }
  }
}
</style>
