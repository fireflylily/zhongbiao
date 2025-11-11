<template>
  <div class="stats-card">
    <h4 v-if="title" class="stats-title">{{ title }}</h4>
    <el-row :gutter="gutter">
      <el-col
        v-for="stat in statItems"
        :key="stat.key"
        :span="span"
      >
        <div class="stat-item">
          <el-statistic
            :title="stat.label"
            :value="getStatValue(stat.key)"
            :precision="stat.precision"
            :value-style="valueStyle"
          >
            <template v-if="stat.prefix" #prefix>
              <span class="stat-prefix">{{ stat.prefix }}</span>
            </template>
            <template v-if="stat.suffix" #suffix>
              <span class="stat-suffix">{{ stat.suffix }}</span>
            </template>
          </el-statistic>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface StatItem {
  key: string
  label: string
  suffix?: string
  prefix?: string
  precision?: number
}

export interface StatsCardProps {
  /**
   * 卡片标题
   */
  title?: string

  /**
   * 统计数据对象
   */
  stats: Record<string, any>

  /**
   * 统计项配置
   * 如果不提供，将使用默认的商务应答统计项
   */
  statItems?: StatItem[]

  /**
   * 每个统计项的栅格占位
   * @default 6
   */
  span?: number

  /**
   * 统计项之间的间距
   * @default 20
   */
  gutter?: number

  /**
   * 数值样式
   */
  valueStyle?: Record<string, string>
}

const props = withDefaults(defineProps<StatsCardProps>(), {
  span: 6,
  gutter: 20,
  valueStyle: () => ({})
})

// 默认统计项配置（商务应答）
const defaultStatItems: StatItem[] = [
  { key: 'total_replacements', label: '文本替换', suffix: '处' },
  { key: 'tables_processed', label: '表格处理', suffix: '个' },
  { key: 'cells_filled', label: '单元格填充', suffix: '个' },
  { key: 'images_inserted', label: '图片插入', suffix: '张' }
]

// 使用提供的统计项或默认配置
const statItems = computed(() => {
  return props.statItems || defaultStatItems
})

/**
 * 获取统计值，支持嵌套属性访问
 * @param key 统计项的键，支持点号分隔的嵌套路径
 */
const getStatValue = (key: string): number => {
  const keys = key.split('.')
  let value: any = props.stats

  for (const k of keys) {
    value = value?.[k]
    if (value === undefined || value === null) break
  }

  return typeof value === 'number' ? value : 0
}
</script>

<style scoped lang="scss">
.stats-card {
  padding: 20px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  margin-bottom: 20px;

  .stats-title {
    margin: 0 0 20px 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .stat-item {
    text-align: center;
    padding: 16px;
    background: var(--el-bg-color);
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);
    transition: all 0.3s ease;

    &:hover {
      border-color: var(--el-color-primary);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }

    :deep(.el-statistic) {
      .el-statistic__head {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin-bottom: 8px;
      }

      .el-statistic__content {
        font-size: 24px;
        font-weight: 600;
        color: var(--el-color-primary);
      }
    }

    .stat-prefix,
    .stat-suffix {
      font-size: 14px;
      color: var(--el-text-color-secondary);
      margin: 0 4px;
    }
  }
}
</style>
