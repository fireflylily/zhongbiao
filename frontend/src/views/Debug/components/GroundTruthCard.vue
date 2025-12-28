<template>
  <el-card class="ground-truth-card">
    <template #header>
      <div class="card-header">
        <span class="title">✅ 正确答案（人工标注）</span>
        <el-button
          v-if="!editing"
          size="small"
          type="primary"
          @click="startEditing"
        >
          {{ modelValue ? '编辑标注' : '开始标注' }}
        </el-button>
        <div v-else class="action-buttons">
          <el-button size="small" @click="cancelEditing">取消</el-button>
          <el-button size="small" type="success" @click="saveEditing">保存</el-button>
        </div>
      </div>
    </template>

    <div class="card-body">
      <div v-if="!modelValue && !editing" class="empty-state">
        <el-empty description="尚未标注正确答案">
          <el-button type="primary" @click="startEditing">开始标注</el-button>
        </el-empty>
      </div>

      <div v-else-if="editing" class="editing-area">
        <el-alert
          title="标注说明"
          type="info"
          :closable="false"
          class="mb-3"
        >
          <p>请从左侧选择一个方法的结果作为基础，然后调整章节列表。</p>
          <p>您也可以手动添加、删除或修改章节。</p>
        </el-alert>

        <div class="template-selector mb-3">
          <span>基于方法结果:</span>
          <el-select v-model="selectedTemplate" placeholder="选择方法" @change="loadTemplate">
            <el-option v-if="availableResults?.gemini?.success" label="Gemini AI解析器" value="gemini" />
            <el-option v-if="availableResults?.docx_native?.success" label="Word大纲级别识别" value="docx_native" />
            <el-option v-if="availableResults?.toc_exact?.success" label="精确匹配(基于目录)" value="toc_exact" />
            <el-option v-if="availableResults?.azure?.success" label="Azure Form Recognizer" value="azure" />
            <el-option v-if="availableResults?.llm_level?.success" label="LLM智能层级分析" value="llm_level" />
            <el-option label="手动创建" value="manual" />
          </el-select>
        </div>

        <div class="editable-list">
          <el-button size="small" @click="addChapter" class="mb-2">
            + 添加章节
          </el-button>

          <div
            v-for="(chapter, index) in editingChapters"
            :key="index"
            class="editable-chapter"
          >
            <el-input
              v-model="chapter.title"
              placeholder="章节标题"
              size="small"
            >
              <template #prepend>
                <el-select v-model="chapter.level" style="width: 80px" size="small">
                  <el-option label="L1" :value="1" />
                  <el-option label="L2" :value="2" />
                  <el-option label="L3" :value="3" />
                </el-select>
              </template>
            </el-input>
            <el-button
              size="small"
              type="danger"
              text
              @click="removeChapter(index)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>

      <div v-else class="display-area">
        <div class="chapter-count">
          共 {{ getTotalChapters(modelValue) }} 个章节
        </div>
        <div class="chapters-container">
          <ChapterTreeItem
            v-for="chapter in modelValue"
            :key="chapter.id"
            :chapter="chapter"
            :level="0"
          />
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { ChapterNode } from '@/api/parser-debug'
import ChapterTreeItem from './ChapterTreeItem.vue'

interface Props {
  modelValue?: ChapterNode[] | null
  documentId?: string
  availableResults?: {
    gemini?: any
    docx_native?: any
    toc_exact?: any
    azure?: any
  }
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: ChapterNode[]): void
  (e: 'save', value: ChapterNode[]): void
}>()

const editing = ref(false)
const editingChapters = ref<Array<{ title: string; level: number }>>([])
const selectedTemplate = ref('')

const startEditing = () => {
  editing.value = true
  if (props.modelValue) {
    // 将现有标注扁平化为可编辑列表
    editingChapters.value = flattenForEditing(props.modelValue)
  } else {
    editingChapters.value = []
  }
}

const cancelEditing = () => {
  editing.value = false
  editingChapters.value = []
  selectedTemplate.value = ''
}

const saveEditing = () => {
  if (editingChapters.value.length === 0) {
    ElMessage.warning('请至少添加一个章节')
    return
  }

  // 转换为ChapterNode格式
  const chapters: ChapterNode[] = editingChapters.value.map((ch, index) => ({
    id: `gt_${index}`,
    level: ch.level,
    title: ch.title,
    para_start_idx: 0,
    para_end_idx: 0,
    word_count: 0,
    preview_text: '',
    auto_selected: false,
    skip_recommended: false,
    children: []
  }))

  emit('update:modelValue', chapters)
  emit('save', chapters)
  editing.value = false
}

const loadTemplate = (methodKey: string) => {
  if (methodKey === 'manual') {
    editingChapters.value = []
    return
  }

  if (!props.availableResults || !props.availableResults[methodKey]) {
    ElMessage.warning('该方法的结果不可用')
    return
  }

  const result = props.availableResults[methodKey]
  if (result.success && result.chapters) {
    editingChapters.value = flattenForEditing(result.chapters)
    ElMessage.success(`已加载${result.method_name}的结果`)
  } else {
    ElMessage.error('该方法解析失败')
  }
}

const addChapter = () => {
  editingChapters.value.push({
    title: '',
    level: 1
  })
}

const removeChapter = (index: number) => {
  editingChapters.value.splice(index, 1)
}

const flattenForEditing = (chapters: ChapterNode[]): Array<{ title: string; level: number }> => {
  const result: Array<{ title: string; level: number }> = []

  const traverse = (chs: ChapterNode[]) => {
    for (const ch of chs) {
      result.push({
        title: ch.title,
        level: ch.level
      })
      if (ch.children && ch.children.length > 0) {
        traverse(ch.children)
      }
    }
  }

  traverse(chapters)
  return result
}

const getTotalChapters = (chapters: ChapterNode[] | null | undefined): number => {
  if (!chapters) return 0

  let count = 0
  const traverse = (chs: ChapterNode[]) => {
    for (const ch of chs) {
      count++
      if (ch.children && ch.children.length > 0) {
        traverse(ch.children)
      }
    }
  }

  traverse(chapters)
  return count
}
</script>

<style scoped lang="scss">
.ground-truth-card {
  border: 2px solid #67C23A;
  grid-column: span 2;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .title {
    font-weight: 600;
    font-size: 16px;
    color: #67C23A;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }
}

.card-body {
  padding: 16px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.editing-area {
  .mb-2 {
    margin-bottom: 8px;
  }

  .mb-3 {
    margin-bottom: 16px;
  }

  .template-selector {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14px;
    color: #606266;
  }

  .editable-list {
    max-height: 400px;
    overflow-y: auto;
  }

  .editable-chapter {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 8px;
  }
}

.display-area {
  .chapter-count {
    margin-bottom: 12px;
    padding: 8px 12px;
    background: #f0f9ff;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
    color: #409EFF;
  }

  .chapters-container {
    max-height: 400px;
    overflow-y: auto;
  }
}
</style>
