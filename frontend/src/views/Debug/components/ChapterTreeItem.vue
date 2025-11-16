<template>
  <div class="chapter-tree-item" :style="{ paddingLeft: `${level * 20}px` }">
    <div class="chapter-row" :class="matchStatusClass">
      <span class="level-badge" :class="`level-${chapter.level}`">
        L{{ chapter.level }}
      </span>
      <span class="chapter-title">{{ chapter.title }}</span>
      <span class="chapter-info">
        <span class="word-count">{{ chapter.word_count }}字</span>
        <el-icon v-if="matchStatus === 'matched'" class="match-icon success">
          <CircleCheck />
        </el-icon>
        <el-icon v-else-if="matchStatus === 'missed'" class="match-icon error">
          <CircleClose />
        </el-icon>
        <el-icon v-else-if="matchStatus === 'false_positive'" class="match-icon warning">
          <Warning />
        </el-icon>
      </span>
    </div>

    <!-- 递归渲染子章节 -->
    <div v-if="chapter.children && chapter.children.length > 0" class="children">
      <ChapterTreeItem
        v-for="child in chapter.children"
        :key="child.id"
        :chapter="child"
        :ground-truth="groundTruth"
        :level="level + 1"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheck, CircleClose, Warning } from '@element-plus/icons-vue'
import type { ChapterNode } from '@/api/parser-debug'

interface Props {
  chapter: ChapterNode
  groundTruth?: ChapterNode[] | null
  level: number
}

const props = defineProps<Props>()

// 计算匹配状态
const matchStatus = computed(() => {
  if (!props.groundTruth) return 'unknown'

  // 扁平化ground truth
  const flattenChapters = (chapters: ChapterNode[]): ChapterNode[] => {
    const result: ChapterNode[] = []
    for (const ch of chapters) {
      result.push(ch)
      if (ch.children && ch.children.length > 0) {
        result.push(...flattenChapters(ch.children))
      }
    }
    return result
  }

  const truthFlat = flattenChapters(props.groundTruth)

  // 规范化标题用于匹配
  const normalizeTitle = (title: string) => {
    return title
      .replace(/^\d+\.\s*/, '')
      .replace(/^\d+\.\d+\s*/, '')
      .replace(/^第[一二三四五六七八九十\d]+[章节部分]\s*/, '')
      .replace(/\s+/g, '')
      .toLowerCase()
  }

  const normalizedCurrent = normalizeTitle(props.chapter.title)
  const isMatched = truthFlat.some(
    (ch) => normalizeTitle(ch.title) === normalizedCurrent
  )

  return isMatched ? 'matched' : 'false_positive'
})

const matchStatusClass = computed(() => {
  return {
    'status-matched': matchStatus.value === 'matched',
    'status-false-positive': matchStatus.value === 'false_positive',
    'status-unknown': matchStatus.value === 'unknown'
  }
})
</script>

<style scoped lang="scss">
.chapter-tree-item {
  margin-bottom: 4px;
}

.chapter-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.2s;
  cursor: pointer;

  &:hover {
    background: #f5f7fa;
  }

  &.status-matched {
    background: #f0f9ff;
    border-left: 3px solid #67C23A;
  }

  &.status-false-positive {
    background: #fef0f0;
    border-left: 3px solid #F56C6C;
  }

  &.status-unknown {
    background: transparent;
  }
}

.level-badge {
  display: inline-block;
  min-width: 32px;
  padding: 2px 6px;
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
  color: white;

  &.level-1 {
    background: #409EFF;
  }

  &.level-2 {
    background: #67C23A;
  }

  &.level-3 {
    background: #E6A23C;
  }
}

.chapter-title {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 8px;

  .word-count {
    font-size: 12px;
    color: #909399;
  }

  .match-icon {
    font-size: 18px;

    &.success {
      color: #67C23A;
    }

    &.error {
      color: #F56C6C;
    }

    &.warning {
      color: #E6A23C;
    }
  }
}

.children {
  margin-left: 0;
}
</style>
