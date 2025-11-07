<template>
  <div class="chapter-tree">
    <!-- 搜索框 -->
    <div v-if="showSearch" class="chapter-search mb-3">
      <el-input
        v-model="searchKeyword"
        placeholder="🔍 搜索章节..."
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <i class="bi bi-search"></i>
        </template>
      </el-input>
    </div>

    <!-- 章节树 -->
    <div class="chapter-tree-container">
      <el-tree
        ref="treeRef"
        :data="filteredChapters"
        :props="treeProps"
        :show-checkbox="showCheckbox"
        :check-strictly="false"
        :default-expand-all="false"
        :expand-on-click-node="false"
        node-key="id"
        @check="handleCheck"
      >
        <template #default="{ node, data }">
          <div class="chapter-tree-node">
            <span class="chapter-title">
              <i :class="getChapterIcon(data)" class="me-1"></i>
              {{ data.title }}
            </span>
            <span class="chapter-meta">
              <el-tag v-if="data.level" size="small" type="info">
                {{ getLevelText(data.level) }}
              </el-tag>
              <span v-if="data.word_count" class="word-count text-muted ms-2">
                {{ formatWordCount(data.word_count) }}字
              </span>
            </span>
          </div>
        </template>
      </el-tree>

      <!-- 空状态 -->
      <el-empty
        v-if="!filteredChapters || filteredChapters.length === 0"
        description="暂无章节数据"
        :image-size="80"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ElTree } from 'element-plus'

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
  chapters: Chapter[]
  showCheckbox?: boolean
  showSearch?: boolean
  defaultCheckedKeys?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  showCheckbox: true,
  showSearch: true,
  defaultCheckedKeys: () => []
})

// Emits
const emit = defineEmits<{
  check: [checkedKeys: string[], checkedNodes: Chapter[]]
  select: [node: Chapter]
}>()

// 状态
const treeRef = ref<InstanceType<typeof ElTree>>()
const searchKeyword = ref('')
const filteredChapters = ref<Chapter[]>([])

// 树配置
const treeProps = {
  children: 'children',
  label: 'title'
}

// 初始化
filteredChapters.value = props.chapters

// 监听章节数据变化
watch(
  () => props.chapters,
  (newChapters) => {
    filteredChapters.value = newChapters
    // 设置默认选中
    if (props.defaultCheckedKeys.length > 0 && treeRef.value) {
      treeRef.value.setCheckedKeys(props.defaultCheckedKeys)
    }
  },
  { immediate: true }
)

// 搜索过滤
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    filteredChapters.value = props.chapters
    return
  }

  const keyword = searchKeyword.value.toLowerCase()
  filteredChapters.value = filterChapters(props.chapters, keyword)
}

// 递归过滤章节
const filterChapters = (chapters: Chapter[], keyword: string): Chapter[] => {
  const result: Chapter[] = []

  for (const chapter of chapters) {
    if (chapter.title.toLowerCase().includes(keyword)) {
      result.push(chapter)
    } else if (chapter.children && chapter.children.length > 0) {
      const filteredChildren = filterChapters(chapter.children, keyword)
      if (filteredChildren.length > 0) {
        result.push({
          ...chapter,
          children: filteredChildren
        })
      }
    }
  }

  return result
}

// 处理复选框变化
const handleCheck = () => {
  if (!treeRef.value) return

  const checkedKeys = treeRef.value.getCheckedKeys() as string[]
  const checkedNodes = treeRef.value.getCheckedNodes() as Chapter[]

  emit('check', checkedKeys, checkedNodes)
}

// 获取章节图标
const getChapterIcon = (chapter: Chapter) => {
  if (chapter.children && chapter.children.length > 0) {
    return 'bi bi-folder'
  }
  return 'bi bi-file-earmark-text'
}

// 获取层级文本
const getLevelText = (level: number) => {
  const levelMap: Record<number, string> = {
    1: '一级',
    2: '二级',
    3: '三级',
    4: '四级',
    5: '五级'
  }
  return levelMap[level] || `${level}级`
}

// 格式化字数
const formatWordCount = (count: number) => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  }
  return count.toLocaleString()
}

// 暴露方法给父组件
const setCheckedKeys = (keys: string[]) => {
  treeRef.value?.setCheckedKeys(keys)
}

const getCheckedKeys = () => {
  return treeRef.value?.getCheckedKeys() as string[]
}

const getCheckedNodes = () => {
  return treeRef.value?.getCheckedNodes() as Chapter[]
}

defineExpose({
  setCheckedKeys,
  getCheckedKeys,
  getCheckedNodes
})
</script>

<style scoped lang="scss">
.chapter-tree {
  .chapter-search {
    :deep(.el-input__prefix) {
      display: flex;
      align-items: center;
    }
  }

  .chapter-tree-container {
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 4px;
    padding: 15px;
    background: var(--el-bg-color-page);
    max-height: 500px;
    overflow-y: auto;

    :deep(.el-tree) {
      background: transparent;
    }

    .chapter-tree-node {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex: 1;
      padding-right: 8px;

      .chapter-title {
        display: flex;
        align-items: center;
        font-size: 14px;
        color: var(--el-text-color-primary);

        i {
          color: var(--el-color-primary);
        }
      }

      .chapter-meta {
        display: flex;
        align-items: center;
        gap: 8px;

        .word-count {
          font-size: 12px;
        }
      }
    }
  }
}
</style>
