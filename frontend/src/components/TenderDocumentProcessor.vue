<template>
  <div class="tender-document-processor">
    <!-- 两列布局 -->
    <el-row :gutter="20">
      <!-- 左列：步骤1 上传招标文档 (占比稍小) -->
      <el-col :xs="24" :sm="24" :md="10" :lg="10">
        <el-card shadow="hover" class="step-card">
          <template #header>
            <div class="card-header">
              <i class="bi bi-upload me-2 text-primary"></i>
              <span class="step-title">步骤1: 上传招标文档（可选）</span>
              <el-tag v-if="uploadedFile || hasExistingDocument" type="success" size="small" class="ms-2">
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
            <!-- 未选择文件时：显示上传框 -->
            <el-upload
              v-if="!uploadedFile"
              ref="uploadRef"
              drag
              :auto-upload="false"
              :limit="1"
              accept=".docx"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
            >
              <i class="bi bi-cloud-upload" style="font-size: 36px; color: var(--el-color-primary)"></i>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  <div>推荐使用 <strong>.docx</strong> 格式（兼容性更好），文件大小不超过 50MB</div>
                  <div class="text-warning" style="font-size: 12px; margin-top: 4px;">
                    <i class="bi bi-exclamation-triangle-fill me-1"></i>
                    注意：旧版 .doc 格式暂不支持章节解析，请先转换为 .docx
                  </div>
                </div>
              </template>
            </el-upload>

            <!-- 已选择文件时：显示文件状态和解析进度（替换上传框位置） -->
            <div v-else class="selected-file-status">
              <el-alert type="success" :closable="false">
                <template #title>
                  <div class="d-flex align-items-center justify-content-between">
                    <span>
                      <i class="bi bi-check-circle-fill me-2"></i>
                      已选择文件: {{ uploadedFile.name }}
                    </span>
                    <el-button
                      size="small"
                      @click="handleClearFile"
                    >
                      <i class="bi bi-arrow-repeat me-1"></i>
                      重新选择
                    </el-button>
                  </div>
                </template>
              </el-alert>

              <!-- 解析进度整合到这里 -->
              <div v-if="parsing" class="parsing-status mt-2">
                <div class="d-flex align-items-center text-info">
                  <el-icon class="is-loading me-2"><Loading /></el-icon>
                  <span>{{ parsingMessage }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 快捷操作区 -->
          <div v-if="hasExistingDocument || responseFileInfo || technicalFileInfo" class="quick-actions">
            <!-- 上部：选择器区域（slot） -->
            <div class="selectors-area">
              <slot name="selectors"></slot>
            </div>

            <!-- 下部：操作按钮 -->
            <div class="action-buttons">
              <div v-if="responseFileInfo" class="quick-action-item">
                <el-button type="primary" size="large" @click="emit('start-business')">
                  <i class="bi bi-rocket-takeoff me-1"></i>
                  开始商务应答
                </el-button>
                <span class="action-hint">确认公司和应答文件模板后开始。</span>
              </div>

              <div v-if="technicalFileInfo" class="quick-action-item">
                <el-button type="primary" size="large" @click="emit('start-p2p')">
                  <i class="bi bi-arrow-left-right me-1"></i>
                  开始点对点应答
                </el-button>
                <span class="action-hint">根据标书要求，选做。</span>
              </div>

              <div v-if="technicalFileInfo" class="quick-action-item">
                <el-button type="primary" size="large" @click="emit('start-proposal')">
                  <i class="bi bi-file-code me-1"></i>
                  开始技术方案编写
                </el-button>
                <span class="action-hint">开始应答。</span>
              </div>
            </div>
          </div>
        </div>
        </el-card>
      </el-col>

      <!-- 右列：步骤2 选择章节 (占比稍大，解析完成后显示) -->
      <el-col :xs="24" :sm="24" :md="14" :lg="14">
        <el-card v-if="chapters.length > 0" shadow="hover" class="step-card">
          <template #header>
            <div class="card-header">
              <i class="bi bi-list-nested me-2 text-success"></i>
              <span class="step-title">步骤2: 选择章节</span>
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
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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
  responseFileInfo?: any // 商务应答模板文件信息
  technicalFileInfo?: any // 技术需求文件信息
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  success: [type: 'response' | 'technical']
  refresh: []
  preview: [fileUrl: string, fileName: string]
  parseComplete: [] // 🆕 文档解析完成事件
  'start-business': [] // 开始商务应答
  'start-p2p': [] // 开始点对点应答
  'start-proposal': [] // 开始技术方案编写
}>()

// 状态
const uploadRef = ref<UploadInstance>()
const chapterTreeRef = ref<InstanceType<typeof ChapterTree>>()
const fileList = ref<UploadFile[]>([])
const uploadedFile = ref<File | null>(null)
const parsing = ref(false)
const parsingMessage = ref('正在解析文档结构...')
const enriching = ref(false)  // 是否正在补充章节信息（字数、定位）
const enrichingFilePath = ref('')  // 用于补充信息的文件路径
const enrichingTocEndIdx = ref(0)  // 目录结束位置
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

// 🆕 文件验证函数
const validateFile = (file: File): { valid: boolean; error?: string } => {
  // 检查文件格式
  const fileName = file.name.toLowerCase()
  if (!fileName.endsWith('.docx')) {
    return {
      valid: false,
      error: '仅支持 .docx 格式的文件，请先将 .doc 文件另存为 .docx 格式'
    }
  }

  // 检查文件大小（50MB = 50 * 1024 * 1024 bytes）
  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    return {
      valid: false,
      error: `文件大小不能超过 50MB，当前文件大小: ${(file.size / 1024 / 1024).toFixed(2)}MB`
    }
  }

  return { valid: true }
}

// 文件上传处理（🆕 自动解析）
const handleFileChange = async (file: UploadFile) => {
  if (!file.raw) return

  // 验证文件
  const validation = validateFile(file.raw)
  if (!validation.valid) {
    ElMessage.error(validation.error || '文件验证失败')
    // 清空文件选择
    uploadedFile.value = null
    fileList.value = []
    return
  }

  // 设置已选择的文件
  uploadedFile.value = file.raw
  fileList.value = [file]

  // 🆕 自动触发解析（延迟500ms让用户看到文件已选择）
  ElMessage.success({
    message: '文件上传成功，系统正在自动提取项目基本信息',
    duration: 2000
  })

  setTimeout(() => {
    handleParse()
  }, 500)
}

const handleFileRemove = () => {
  uploadedFile.value = null
  fileList.value = []
  chapters.value = []
  selectedChapterIds.value = []
}

// 重新选择文件（清除当前选择）
const handleClearFile = () => {
  uploadedFile.value = null
  fileList.value = []
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
}

// 解析文档（异步分阶段加载）
const handleParse = async () => {
  if (!uploadedFile.value) {
    ElMessage.warning('请先上传文档')
    return
  }

  parsing.value = true
  parsingMessage.value = '正在识别文档目录（AI分析中）...'

  try {
    // 阶段1：快速解析，获取目录树结构
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    formData.append('company_id', props.companyId.toString())
    formData.append('project_id', props.projectId.toString())

    console.log('🚀 [阶段1] 开始快速解析...')
    const quickResponse = await tenderApi.parseDocumentStructureQuick(formData)

    if (quickResponse.success) {
      // 立即显示目录树（此时字数显示为 -1 或加载中）
      chapters.value = (quickResponse as any).chapters || []
      enrichingFilePath.value = (quickResponse as any).file_path || ''
      enrichingTocEndIdx.value = (quickResponse as any).toc_end_idx || 0

      // 关闭解析状态，开启补充信息状态
      parsing.value = false
      enriching.value = true

      ElMessage.success({
        message: '目录识别完成（DeepSeek V3），正在分析字数...',
        duration: 2000
      })

      console.log('✅ [阶段1] 目录识别完成，章节数:', chapters.value.length)

      // 阶段2：补充字数和定位信息（必须等待完成后再触发AI提取）
      console.log('📊 [阶段2] 开始补充章节信息...')
      try {
        const enrichResponse = await tenderApi.enrichChapters({
          project_id: props.projectId,
          file_path: enrichingFilePath.value,
          chapters: chapters.value,
          toc_end_idx: enrichingTocEndIdx.value
        })

        if (enrichResponse.success) {
          // 更新章节数据（包含字数）
          chapters.value = (enrichResponse as any).chapters || chapters.value

          console.log('✅ [阶段2] 章节信息补充完成，总字数:',
            (enrichResponse as any).statistics?.total_words || 0)

          ElMessage.success({
            message: '文档解析完成',
            duration: 2000
          })
        } else {
          console.warn('⚠️ [阶段2] 补充信息失败:', (enrichResponse as any).error)
          // 补充信息失败不影响目录显示，只是字数无法显示
          ElMessage.warning('字数统计失败，但目录结构已识别')
        }
      } catch (enrichError) {
        console.error('⚠️ [阶段2] 补充信息异常:', enrichError)
        ElMessage.warning('字数统计失败，但目录结构已识别')
      } finally {
        enriching.value = false
      }

      // 🔧 修复：在enrichChapters完成后再emit事件，确保AI提取时章节数据完整
      console.log('🎯 [TenderDocumentProcessor] 章节信息补充完成，现在emit parseComplete 事件')
      emit('parseComplete')
      // 同时 emit refresh 事件，重新加载项目详情
      emit('refresh')

    } else {
      throw new Error((quickResponse as any).message || (quickResponse as any).error || '解析失败')
    }
  } catch (error) {
    console.error('文档解析失败:', error)
    parsing.value = false
    enriching.value = false

    const errorMessage = error instanceof Error ? error.message : '未知错误'

    // ⭐️ 特殊处理：.doc 格式不支持的错误
    if (errorMessage.includes('.doc') || errorMessage.includes('另存为') || errorMessage.includes('docx')) {
      // 使用 MessageBox 显示详细的转换引导
      ElMessageBox.alert(
        errorMessage,
        '不支持 .doc 格式',
        {
          confirmButtonText: '我知道了',
          type: 'warning',
          dangerouslyUseHTMLString: false,
          customStyle: {
            width: '500px'
          }
        }
      )
    } else {
      // 其他错误使用普通提示
      ElMessage.error(`解析失败: ${errorMessage}`)
    }
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

    // 不在这里显示成功提示，由父组件统一处理
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

    // 不在这里显示成功提示，由父组件统一处理
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
  }
}

// 监听projectDetail变化（immediate: true 确保组件挂载时立即执行）
watch(() => props.projectDetail, () => {
  initializeExistingData()
}, { immediate: true })
</script>

<style scoped lang="scss">
.tender-document-processor {
  margin-bottom: 16px; // 从20px减小到16px

  .step-card {
    height: 100%;
    display: flex;
    flex-direction: column;

    :deep(.el-card__header) {
      background: var(--el-fill-color-light);
      border-bottom: 2px solid var(--el-border-color-lighter);
      padding: 12px 20px;
    }

    :deep(.el-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 16px;
    }
  }

  // 响应式布局：小屏幕下章节卡片上移
  @media (max-width: 768px) {
    .step-card:last-child {
      margin-top: 20px;
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    font-size: 15px;
    font-weight: 600;

    .step-title {
      flex: 1;
    }
  }

  .upload-section {
    display: flex;
    flex-direction: column;
    height: 100%;

    :deep(.el-upload-dragger) {
      width: 100%;
      padding: 20px 16px; // 从30px 20px减小到20px 16px
      cursor: pointer;
      transition: all 0.3s ease;

      // 🆕 悬停效果 - 更明显的视觉反馈
      &:hover {
        border-color: var(--el-color-primary);
        background-color: var(--el-color-primary-light-9);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);

        .el-upload__text {
          color: var(--el-color-primary);
        }

        .bi-cloud-upload {
          transform: scale(1.1);
          transition: transform 0.3s ease;
        }
      }

      // 🆕 点击效果
      &:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
      }
    }

    // 增强文本提示的可见性
    :deep(.el-upload__text) {
      transition: color 0.3s ease;

      em {
        color: var(--el-color-primary);
        font-weight: 600;
        text-decoration: underline;
      }
    }

    // 图标动画
    :deep(.bi-cloud-upload) {
      transition: transform 0.3s ease, color 0.3s ease;
    }
  }

  .chapter-section {
    display: flex;
    flex-direction: column;
    flex: 1;

    .stats-grid {
      display: flex;
      gap: 10px;

      .stat-card {
        flex: 1;
        background: var(--el-bg-color-page);
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 8px;
        padding: 10px;
        text-align: center;

        .stat-label {
          font-size: 12px;
          color: var(--el-text-color-secondary);
          margin-bottom: 6px;
        }

        .stat-value {
          font-size: 20px;
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
      margin-top: auto;
      padding-top: 20px;
      border-top: 1px solid var(--el-border-color-lighter);
    }
  }

  .parsing-status {
    padding: 12px;
    background: var(--el-color-info-light-9);
    border-radius: 4px;
  }

  // 快捷操作区样式
  .quick-actions {
    display: flex;
    flex-direction: column;
    flex: 1;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px dashed var(--el-border-color-lighter);

    .selectors-area {
      margin-bottom: 8px;

      // 如果slot没有内容，隐藏该区域
      &:empty {
        display: none;
      }
    }

    .action-buttons {
      display: flex;
      flex-direction: column;
      flex: 1;
      justify-content: flex-end;
      gap: 6px;
    }
  }

  .quick-action-item {
    display: flex;
    align-items: center;
    gap: 12px;

    .el-button {
      flex-shrink: 0;
      width: 200px;
    }

    .action-hint {
      color: var(--el-text-color-secondary);
      font-size: 13px;
    }
  }
}
</style>
