<template>
  <div class="crew-progress-tracker">
    <div class="tracker-header">
      <el-icon><DataAnalysis /></el-icon>
      <span>Quality-First 智能体协作进度</span>
      <el-tag v-if="currentPhase" :type="getPhaseTagType(currentPhase)" size="small">
        {{ getPhaseLabel(currentPhase) }}
      </el-tag>
    </div>

    <div class="phase-list">
      <div
        v-for="phase in phases"
        :key="phase.key"
        class="phase-item"
        :class="{
          'phase-item--complete': phaseProgress[phase.key]?.status === 'complete',
          'phase-item--running': phaseProgress[phase.key]?.status === 'running',
          'phase-item--skipped': phaseProgress[phase.key]?.status === 'skipped',
          'phase-item--pending': !phaseProgress[phase.key],
          'phase-item--has-detail': isPhaseRunning(phase.key) && hasPhaseDetail(phase.key)
        }"
      >
        <div class="phase-main">
          <div class="phase-icon">
            <el-icon v-if="phaseProgress[phase.key]?.status === 'complete'" class="icon-success">
              <CircleCheckFilled />
            </el-icon>
            <el-icon v-else-if="phaseProgress[phase.key]?.status === 'running'" class="icon-running">
              <Loading />
            </el-icon>
            <el-icon v-else-if="phaseProgress[phase.key]?.status === 'skipped'" class="icon-skipped">
              <RemoveFilled />
            </el-icon>
            <el-icon v-else class="icon-pending">
              <Clock />
            </el-icon>
          </div>

          <div class="phase-content">
            <div class="phase-name">{{ phase.label }}</div>
            <div v-if="phaseProgress[phase.key]?.result" class="phase-result">
              <template v-if="phase.key === 'scoring_extraction'">
                {{ phaseProgress[phase.key].result.count || 0 }}个评分维度
              </template>
              <template v-else-if="phase.key === 'product_matching'">
                覆盖率 {{ ((phaseProgress[phase.key].result.coverage_rate || 0) * 100).toFixed(1) }}%
              </template>
              <template v-else-if="phase.key === 'strategy_planning'">
                预估得分 {{ phaseProgress[phase.key].result.estimated_score || 0 }}分
              </template>
              <template v-else-if="phase.key === 'material_retrieval'">
                {{ phaseProgress[phase.key].result.package_count || 0 }}个素材包
              </template>
              <template v-else-if="phase.key === 'outline_generation'">
                {{ phaseProgress[phase.key].result.chapter_count || 0 }}章节
              </template>
              <template v-else-if="phase.key === 'content_writing'">
                {{ phaseProgress[phase.key].result.chapter_count || 0 }}章，{{ phaseProgress[phase.key].result.total_words || 0 }}字
              </template>
              <template v-else-if="phase.key === 'expert_review'">
                {{ phaseProgress[phase.key].result.overall_score || 0 }}分
                <el-tag
                  :type="phaseProgress[phase.key].result.pass_recommendation ? 'success' : 'warning'"
                  size="small"
                >
                  {{ phaseProgress[phase.key].result.pass_recommendation ? '通过' : '需改进' }}
                </el-tag>
              </template>
            </div>
            <div v-else-if="phaseProgress[phase.key]?.message" class="phase-message">
              {{ phaseProgress[phase.key].message }}
            </div>
          </div>
        </div>

        <!-- 嵌入式详细进度 -->
        <transition name="slide-fade">
          <div v-if="isPhaseRunning(phase.key) && hasPhaseDetail(phase.key)" class="phase-detail">
            <!-- 步骤进度条 -->
            <div class="step-progress">
              <el-progress
                :percentage="getStepPercentage(phase.key)"
                :stroke-width="6"
                :show-text="false"
                color="#409eff"
              />
              <span class="step-text">
                {{ getStepText(phase.key) }}
              </span>
            </div>

            <!-- 已完成子项列表 -->
            <div v-if="getSubItems(phase.key).length > 0" class="sub-items">
              <transition-group name="list" tag="ul">
                <li v-for="(item, idx) in getSubItems(phase.key)" :key="idx" class="sub-item">
                  <el-icon class="item-icon"><Check /></el-icon>
                  <span>{{ item }}</span>
                </li>
              </transition-group>
            </div>

            <!-- 章节预览 (仅 content_writing 阶段) -->
            <div v-if="phase.key === 'content_writing' && chapterPreview?.content" class="chapter-preview">
              <div class="preview-header">
                <span class="chapter-number">{{ chapterPreview.currentChapter }}</span>
                <span class="chapter-title">{{ chapterPreview.currentTitle }}</span>
                <span class="word-count">{{ chapterPreview.wordCount }} 字</span>
              </div>
              <div class="preview-content" ref="previewRef">
                <div v-html="renderedPreview" class="markdown-body"></div>
                <span class="typing-cursor">|</span>
              </div>
            </div>
          </div>
        </transition>

        <div class="phase-connector" v-if="phase.key !== 'complete'">
          <div class="connector-line"></div>
        </div>
      </div>
    </div>

    <!-- 详细结果展示（可选） -->
    <el-collapse v-if="showDetails && hasResults" v-model="activeDetails" class="details-collapse">
      <el-collapse-item v-if="scoringPoints" title="评分点详情" name="scoring">
        <div class="detail-content">
          <div v-for="dim in scoringPoints.dimensions" :key="dim.name" class="dimension-item">
            <span class="dim-name">{{ dim.name }}</span>
            <span class="dim-count">{{ dim.count }}项</span>
            <span class="dim-score">{{ dim.total_score }}分</span>
          </div>
        </div>
      </el-collapse-item>

      <el-collapse-item v-if="reviewResult" title="评审详情" name="review">
        <div class="detail-content">
          <div v-if="reviewResult.strengths?.length" class="review-section">
            <h4>优势</h4>
            <ul>
              <li v-for="(item, idx) in reviewResult.strengths" :key="idx">{{ item }}</li>
            </ul>
          </div>
          <div v-if="reviewResult.weaknesses?.length" class="review-section">
            <h4>不足</h4>
            <ul>
              <li v-for="(item, idx) in reviewResult.weaknesses" :key="idx">{{ item }}</li>
            </ul>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  DataAnalysis,
  CircleCheckFilled,
  Loading,
  RemoveFilled,
  Clock,
  Check
} from '@element-plus/icons-vue'
import { marked } from 'marked'

// 细粒度进度详情接口
interface PhaseDetail {
  currentStep: number
  totalSteps: number
  stepName: string
  subItems: string[]
}

// 章节预览接口
interface ChapterPreview {
  currentChapter: string
  currentTitle: string
  content: string
  wordCount: number
}

interface Props {
  currentPhase?: string
  phaseProgress?: Record<string, any>
  phaseDetails?: Record<string, PhaseDetail>  // 新增：细粒度进度详情
  chapterPreview?: ChapterPreview | null      // 新增：章节预览
  scoringPoints?: any
  productMatch?: any
  scoringStrategy?: any
  materials?: any
  reviewResult?: any
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  currentPhase: '',
  phaseProgress: () => ({}),
  phaseDetails: () => ({}),
  chapterPreview: null,
  showDetails: false
})

const activeDetails = ref<string[]>([])
const previewRef = ref<HTMLElement | null>(null)

// 判断阶段是否正在运行
const isPhaseRunning = (phaseKey: string): boolean => {
  return props.phaseProgress[phaseKey]?.status === 'running'
}

// 判断阶段是否有详细进度
const hasPhaseDetail = (phaseKey: string): boolean => {
  const detail = props.phaseDetails?.[phaseKey]
  return !!(detail && detail.totalSteps > 0)
}

// 获取步骤百分比
const getStepPercentage = (phaseKey: string): number => {
  const detail = props.phaseDetails?.[phaseKey]
  if (!detail || detail.totalSteps === 0) return 0
  return Math.round((detail.currentStep / detail.totalSteps) * 100)
}

// 获取步骤文本
const getStepText = (phaseKey: string): string => {
  const detail = props.phaseDetails?.[phaseKey]
  if (!detail) return ''
  return `${detail.stepName} (${detail.currentStep}/${detail.totalSteps})`
}

// 获取已完成子项
const getSubItems = (phaseKey: string): string[] => {
  const detail = props.phaseDetails?.[phaseKey]
  return detail?.subItems || []
}

// 渲染 Markdown 预览内容
const renderedPreview = computed(() => {
  if (!props.chapterPreview?.content) return ''
  try {
    return marked(props.chapterPreview.content, { breaks: true })
  } catch {
    return props.chapterPreview.content
  }
})

// 自动滚动预览区域到底部
watch(() => props.chapterPreview?.content, () => {
  nextTick(() => {
    if (previewRef.value) {
      previewRef.value.scrollTop = previewRef.value.scrollHeight
    }
  })
})

// 阶段定义
const phases = [
  { key: 'scoring_extraction', label: '评分点提取' },
  { key: 'product_matching', label: '产品能力匹配' },
  { key: 'strategy_planning', label: '评分策略规划' },
  { key: 'material_retrieval', label: '历史素材检索' },
  { key: 'outline_generation', label: '大纲结构生成' },
  { key: 'content_writing', label: '技术方案撰写' },
  { key: 'expert_review', label: '专家评审' },
  { key: 'complete', label: '生成完成' }
]

// 阶段标签
const getPhaseLabel = (phase: string): string => {
  const labels: Record<string, string> = {
    'scoring_extraction': '提取评分点',
    'product_matching': '匹配产品',
    'strategy_planning': '策略规划',
    'material_retrieval': '检索素材',
    'outline_generation': '生成大纲',
    'content_writing': '撰写内容',
    'expert_review': '专家评审',
    'iteration': '迭代优化',
    'complete': '已完成'
  }
  return labels[phase] || phase
}

// 阶段标签类型
const getPhaseTagType = (phase: string): string => {
  if (phase === 'complete') return 'success'
  if (phase === 'expert_review') return 'warning'
  if (phase === 'content_writing') return 'primary'
  return 'info'
}

// 是否有结果
const hasResults = computed(() => {
  return props.scoringPoints || props.reviewResult
})
</script>

<style scoped lang="scss">
.crew-progress-tracker {
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter);

  .tracker-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);

    .el-icon {
      font-size: 20px;
      color: var(--el-color-primary);
    }

    .el-tag {
      margin-left: auto;
    }
  }

  .phase-list {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .phase-item {
    display: flex;
    flex-direction: column;
    position: relative;
    padding: 12px 0;

    &--complete {
      .phase-name {
        color: var(--el-color-success);
      }
    }

    &--running {
      .phase-name {
        color: var(--el-color-primary);
        font-weight: 600;
      }
    }

    &--skipped {
      .phase-name {
        color: var(--el-text-color-disabled);
        text-decoration: line-through;
      }
    }

    &--pending {
      .phase-name {
        color: var(--el-text-color-secondary);
      }
    }

    &--has-detail {
      padding-bottom: 16px;
    }
  }

  .phase-main {
    display: flex;
    align-items: flex-start;
  }

  .phase-icon {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    margin-right: 12px;
    z-index: 1;
    background: #fff;

    .icon-success {
      font-size: 20px;
      color: var(--el-color-success);
    }

    .icon-running {
      font-size: 18px;
      color: var(--el-color-primary);
      animation: spin 1s linear infinite;
    }

    .icon-skipped {
      font-size: 18px;
      color: var(--el-text-color-disabled);
    }

    .icon-pending {
      font-size: 18px;
      color: var(--el-text-color-secondary);
    }
  }

  .phase-content {
    flex: 1;
    min-width: 0;

    .phase-name {
      font-size: 14px;
      margin-bottom: 4px;
    }

    .phase-result {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .phase-message {
      font-size: 12px;
      color: var(--el-text-color-placeholder);
    }
  }

  .phase-connector {
    position: absolute;
    left: 13px;
    top: 40px;
    bottom: 0;

    .connector-line {
      width: 2px;
      height: 100%;
      background: var(--el-border-color-light);
    }
  }

  .phase-item--complete .phase-connector .connector-line {
    background: var(--el-color-success-light-5);
  }

  .phase-item--running .phase-connector .connector-line {
    background: linear-gradient(
      to bottom,
      var(--el-color-primary) 0%,
      var(--el-border-color-light) 100%
    );
  }

  .details-collapse {
    margin-top: 20px;
    border-top: 1px solid var(--el-border-color-lighter);
    padding-top: 16px;

    .detail-content {
      padding: 12px;
      background: var(--el-fill-color-lighter);
      border-radius: 8px;
    }

    .dimension-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 0;
      border-bottom: 1px solid var(--el-border-color-extra-light);

      &:last-child {
        border-bottom: none;
      }

      .dim-name {
        flex: 1;
        font-size: 13px;
      }

      .dim-count,
      .dim-score {
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }

    .review-section {
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }

      h4 {
        font-size: 13px;
        font-weight: 600;
        margin: 0 0 8px 0;
        color: var(--el-text-color-primary);
      }

      ul {
        margin: 0;
        padding-left: 20px;

        li {
          font-size: 12px;
          color: var(--el-text-color-regular);
          margin-bottom: 4px;
        }
      }
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 嵌入式详细进度样式
.phase-detail {
  margin-top: 12px;
  margin-left: 40px;
  padding: 16px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
  border-left: 3px solid var(--el-color-primary);

  .step-progress {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;

    .el-progress {
      flex: 1;
      max-width: 200px;
    }

    .step-text {
      font-size: 13px;
      color: var(--el-text-color-secondary);
      white-space: nowrap;
    }
  }

  .sub-items {
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .sub-item {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 10px;
      font-size: 12px;
      color: var(--el-color-success);
      background: var(--el-color-success-light-9);
      border-radius: 4px;

      .item-icon {
        font-size: 12px;
      }
    }
  }

  .chapter-preview {
    margin-top: 16px;
    border-top: 1px solid var(--el-border-color-lighter);
    padding-top: 16px;

    .preview-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;

      .chapter-number {
        font-weight: 600;
        color: var(--el-color-primary);
        font-size: 14px;
      }

      .chapter-title {
        font-weight: 500;
        font-size: 14px;
        color: var(--el-text-color-primary);
      }

      .word-count {
        margin-left: auto;
        font-size: 12px;
        color: var(--el-text-color-secondary);
        background: var(--el-fill-color);
        padding: 2px 8px;
        border-radius: 4px;
      }
    }

    .preview-content {
      max-height: 200px;
      overflow-y: auto;
      padding: 12px;
      background: #fff;
      border-radius: 6px;
      border: 1px solid var(--el-border-color);
      font-size: 13px;
      line-height: 1.8;
      color: var(--el-text-color-regular);

      .markdown-body {
        font-size: 13px;

        p {
          margin: 0 0 8px 0;
        }

        ul, ol {
          margin: 0 0 8px 0;
          padding-left: 20px;
        }
      }

      .typing-cursor {
        display: inline-block;
        animation: blink 1s infinite;
        color: var(--el-color-primary);
        font-weight: bold;
      }
    }
  }
}

// 过渡动画
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

// 列表动画
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>
