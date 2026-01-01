<template>
  <el-dialog
    v-model="visible"
    title="从招标文件选择章节"
    width="800px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <!-- 提示信息：无章节数据 -->
    <el-alert
      v-if="!hasChapters && !loading"
      type="warning"
      :closable="false"
      show-icon
    >
      <template #title>
        当前项目尚未解析招标文档章节，请先在项目管理中上传并解析招标文档。
      </template>
    </el-alert>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在加载章节数据...</span>
    </div>

    <!-- 章节选择区域 -->
    <div v-else-if="hasChapters" class="chapter-selector">
      <!-- 统计信息 -->
      <div class="stats-row">
        <el-tag type="info">总章节: {{ totalChapters }}</el-tag>
        <el-tag type="success">已选择: {{ selectedCount }}</el-tag>
        <el-tag type="primary">选中字数: {{ formatWordCount(selectedWordCount) }}</el-tag>
      </div>

      <!-- 批量操作按钮 -->
      <div class="batch-operations">
        <el-button-group>
          <el-button size="small" @click="handleSelectAll">
            <el-icon><Check /></el-icon> 全选
          </el-button>
          <el-button size="small" @click="handleUnselectAll">
            <el-icon><Close /></el-icon> 全不选
          </el-button>
          <el-button size="small" type="success" @click="handleSelectTech">
            <el-icon><Cpu /></el-icon> 仅选技术章节
          </el-button>
        </el-button-group>
      </div>

      <!-- 章节树 -->
      <ChapterTree
        ref="chapterTreeRef"
        :chapters="chapters"
        :show-checkbox="true"
        :show-search="true"
        @check="handleChapterCheck"
      />
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :disabled="selectedCount === 0"
          :loading="saving"
          @click="handleConfirm"
        >
          <el-icon><DocumentCopy /></el-icon>
          生成模板文件 ({{ selectedCount }}章)
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Check, Close, Cpu, DocumentCopy } from '@element-plus/icons-vue'
import ChapterTree from '@/components/ChapterTree.vue'
import { tenderApi } from '@/api/endpoints/tender'

// 章节类型
interface Chapter {
  id: string
  title: string
  level: number
  word_count?: number
  chapter_type?: string
  children?: Chapter[]
}

// Props
interface Props {
  modelValue: boolean
  projectId: number | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success', fileInfo: { filePath: string; filename: string }): void
}>()

// 响应式状态
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const saving = ref(false)
const chapters = ref<Chapter[]>([])
const selectedChapterIds = ref<string[]>([])
const selectedChapterNodes = ref<Chapter[]>([])
const chapterTreeRef = ref<InstanceType<typeof ChapterTree>>()

// 计算属性
const hasChapters = computed(() => chapters.value.length > 0)

const totalChapters = computed(() => {
  const countChapters = (chaps: Chapter[]): number => {
    let count = chaps.length
    chaps.forEach(chap => {
      if (chap.children?.length) {
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

// 加载章节数据
const loadChapters = async () => {
  if (!props.projectId) return

  loading.value = true
  try {
    const response = await tenderApi.getProject(props.projectId)
    const projectData = response.data

    if (projectData?.step1_data?.chapters) {
      chapters.value = projectData.step1_data.chapters
    } else {
      chapters.value = []
    }
  } catch (error) {
    console.error('加载章节失败:', error)
    ElMessage.error('加载章节数据失败')
    chapters.value = []
  } finally {
    loading.value = false
  }
}

// 格式化字数
const formatWordCount = (count: number) => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  }
  return count.toLocaleString()
}

// 章节选择处理
const handleChapterCheck = (checkedKeys: string[], checkedNodes: Chapter[]) => {
  selectedChapterIds.value = checkedKeys
  selectedChapterNodes.value = checkedNodes
}

// 批量操作：获取所有章节ID
const getAllChapterIds = (chaps: Chapter[]): string[] => {
  const ids: string[] = []
  chaps.forEach(chap => {
    ids.push(chap.id)
    if (chap.children?.length) {
      ids.push(...getAllChapterIds(chap.children))
    }
  })
  return ids
}

// 批量操作：按关键词过滤章节
const filterChaptersByKeywords = (chaps: Chapter[], keywords: string[]): string[] => {
  const ids: string[] = []
  chaps.forEach(chap => {
    const matchesKeyword = keywords.some(keyword => chap.title.includes(keyword))
    if (matchesKeyword) {
      ids.push(chap.id)
    }
    if (chap.children?.length) {
      ids.push(...filterChaptersByKeywords(chap.children, keywords))
    }
  })
  return ids
}

const handleSelectAll = () => {
  const allKeys = getAllChapterIds(chapters.value)
  chapterTreeRef.value?.setCheckedKeys(allKeys)
  // 手动触发更新
  selectedChapterIds.value = allKeys
  selectedChapterNodes.value = chapterTreeRef.value?.getCheckedNodes() || []
}

const handleUnselectAll = () => {
  chapterTreeRef.value?.setCheckedKeys([])
  selectedChapterIds.value = []
  selectedChapterNodes.value = []
}

const handleSelectTech = () => {
  const techKeywords = ['技术', '方案', '实施', '系统', '功能', '需求', '架构', '设计', '开发', '部署']
  const techKeys = filterChaptersByKeywords(chapters.value, techKeywords)
  chapterTreeRef.value?.setCheckedKeys(techKeys)
  // 手动触发更新
  selectedChapterIds.value = techKeys
  selectedChapterNodes.value = chapterTreeRef.value?.getCheckedNodes() || []
}

// 确认生成模板
const handleConfirm = async () => {
  if (selectedCount.value === 0) {
    ElMessage.warning('请先选择章节')
    return
  }

  saving.value = true
  try {
    // 调用后端API保存选中章节为技术需求文档
    const result = await tenderApi.saveTechnicalChapters(
      props.projectId!,
      selectedChapterIds.value
    )

    if (result.success && result.data) {
      ElMessage.success('模板文件已生成')
      emit('success', {
        filePath: result.data.file_path,
        filename: result.data.filename
      })
      visible.value = false
    } else {
      throw new Error(result.error || '生成失败')
    }
  } catch (error: any) {
    console.error('生成模板失败:', error)
    ElMessage.error(error.message || '生成模板文件失败')
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  selectedChapterIds.value = []
  selectedChapterNodes.value = []
  visible.value = false
}

// 监听对话框打开
watch(visible, (newVal) => {
  if (newVal && props.projectId) {
    loadChapters()
  }
})
</script>

<style scoped lang="scss">
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: var(--el-text-color-secondary);

  .el-icon {
    font-size: 32px;
    margin-bottom: 12px;
  }
}

.chapter-selector {
  .stats-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }

  .batch-operations {
    margin-bottom: 16px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
