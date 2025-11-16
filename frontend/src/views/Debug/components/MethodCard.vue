<template>
  <el-card class="method-card" :body-style="{ padding: '0' }">
    <template #header>
      <div class="card-header">
        <span class="method-title" :style="{ color }">{{ title }}</span>
        <el-tag :type="statusType" size="small">{{ statusText }}</el-tag>
      </div>
    </template>

    <div class="card-body">
      <!-- 统计信息 -->
      <div class="statistics">
        <div class="stat-item">
          <span class="label">识别章节:</span>
          <span class="value">{{ result.chapters?.length || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="label">总字数:</span>
          <span class="value">{{ formatNumber(result.statistics?.total_words || 0) }}</span>
        </div>
        <div class="stat-item">
          <span class="label">耗时:</span>
          <span class="value">{{ result.performance?.elapsed_formatted || '-' }}</span>
        </div>
        <div v-if="accuracy" class="stat-item">
          <span class="label">F1分数:</span>
          <span class="value f1-score" :class="getF1Class(accuracy.f1_score)">
            {{ (accuracy.f1_score * 100).toFixed(1) }}%
          </span>
        </div>
      </div>

      <!-- 章节列表 -->
      <div class="chapter-list">
        <div class="chapter-list-header">
          <span>章节列表</span>
          <el-button size="small" text @click="toggleExpanded">
            {{ expanded ? '收起' : '展开全部' }}
          </el-button>
        </div>

        <div v-if="!result.success" class="error-message">
          <el-alert :title="result.error || '解析失败'" type="error" :closable="false" />
        </div>

        <div v-else class="chapters-container" :class="{ collapsed: !expanded }">
          <ChapterTreeItem
            v-for="chapter in result.chapters"
            :key="chapter.id"
            :chapter="chapter"
            :ground-truth="groundTruth"
            :level="0"
          />
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ParseMethodResult, ChapterNode, MethodAccuracy } from '@/api/parser-debug'
import ChapterTreeItem from './ChapterTreeItem.vue'

interface Props {
  title: string
  result: ParseMethodResult
  groundTruth?: ChapterNode[] | null
  accuracy?: MethodAccuracy | null
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  color: '#409EFF'
})

const expanded = ref(false)

const statusType = computed(() => {
  if (!props.result.success) return 'danger'
  if (props.accuracy) {
    if (props.accuracy.f1_score >= 0.9) return 'success'
    if (props.accuracy.f1_score >= 0.7) return ''
    if (props.accuracy.f1_score >= 0.5) return 'warning'
    return 'danger'
  }
  return 'info'
})

const statusText = computed(() => {
  if (!props.result.success) return '失败'
  if (props.accuracy) {
    return `F1: ${(props.accuracy.f1_score * 100).toFixed(1)}%`
  }
  return '成功'
})

const toggleExpanded = () => {
  expanded.value = !expanded.value
}

const formatNumber = (num: number) => {
  if (num >= 10000) return `${(num / 10000).toFixed(1)}万`
  return num.toString()
}

const getF1Class = (f1: number) => {
  if (f1 >= 0.9) return 'excellent'
  if (f1 >= 0.7) return 'good'
  if (f1 >= 0.5) return 'fair'
  return 'poor'
}
</script>

<style scoped lang="scss">
.method-card {
  border: 2px solid #e4e7ed;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .method-title {
    font-weight: 600;
    font-size: 16px;
  }
}

.card-body {
  padding: 16px;
}

.statistics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;

  .stat-item {
    display: flex;
    justify-content: space-between;
    font-size: 14px;

    .label {
      color: #909399;
    }

    .value {
      font-weight: 600;
      color: #303133;

      &.f1-score {
        font-size: 16px;

        &.excellent {
          color: #67C23A;
        }

        &.good {
          color: #409EFF;
        }

        &.fair {
          color: #E6A23C;
        }

        &.poor {
          color: #F56C6C;
        }
      }
    }
  }
}

.chapter-list {
  .chapter-list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid #ebeef5;

    span {
      font-weight: 600;
      font-size: 14px;
      color: #303133;
    }
  }

  .error-message {
    padding: 12px 0;
  }

  .chapters-container {
    max-height: 400px;
    overflow-y: auto;

    &.collapsed {
      max-height: 200px;
    }
  }
}
</style>
