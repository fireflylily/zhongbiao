<template>
  <div class="demo-container">
    <!-- 页面头部 -->
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h1>🧰 工具函数演示中心</h1>
          <p class="subtitle">
            展示项目中所有工具函数和组合式函数的实际应用示例
          </p>
        </div>
        <el-tag type="primary" size="large">v2.0.0</el-tag>
      </div>
    </el-card>

    <!-- Tab导航 -->
    <el-card class="demo-tabs-card">
      <el-tabs v-model="activeTab" type="border-card" @tab-click="handleTabClick">
        <!-- 格式化工具 -->
        <el-tab-pane name="format">
          <template #label>
            <span class="tab-label">
              <el-icon><Calendar /></el-icon>
              格式化工具
            </span>
          </template>
          <format-demo />
        </el-tab-pane>

        <!-- 验证工具 -->
        <el-tab-pane name="validation">
          <template #label>
            <span class="tab-label">
              <el-icon><CircleCheck /></el-icon>
              验证工具
            </span>
          </template>
          <validation-demo />
        </el-tab-pane>

        <!-- 辅助函数 -->
        <el-tab-pane name="helpers">
          <template #label>
            <span class="tab-label">
              <el-icon><Tools /></el-icon>
              辅助函数
            </span>
          </template>
          <helpers-demo />
        </el-tab-pane>

        <!-- 组合式函数 -->
        <el-tab-pane name="composables">
          <template #label>
            <span class="tab-label">
              <el-icon><Connection /></el-icon>
              组合式函数
            </span>
          </template>
          <composables-demo />
        </el-tab-pane>

        <!-- 使用指南 -->
        <el-tab-pane name="guide">
          <template #label>
            <span class="tab-label">
              <el-icon><Document /></el-icon>
              使用指南
            </span>
          </template>
          <usage-guide />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 页脚信息 -->
    <el-card class="footer-card">
      <div class="footer-content">
        <div>
          <el-icon><InfoFilled /></el-icon>
          <span>这些工具函数和组合式函数已在整个项目中使用，确保代码的一致性和可维护性。</span>
        </div>
        <el-link type="primary" href="https://github.com" target="_blank">
          查看源码
          <el-icon><Right /></el-icon>
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Calendar,
  CircleCheck,
  Tools,
  Connection,
  Document,
  InfoFilled,
  Right
} from '@element-plus/icons-vue'
import FormatDemo from './FormatDemo.vue'
import ValidationDemo from './ValidationDemo.vue'
import HelpersDemo from './HelpersDemo.vue'
import ComposablesDemo from './ComposablesDemo.vue'

const activeTab = ref('format')

function handleTabClick() {
  // Tab切换时可以添加埋点等逻辑
  console.log('当前Tab:', activeTab.value)
}
</script>

<script lang="ts">
// 使用指南组件
import { defineComponent, h } from 'vue'
import { ElCard, ElDescriptions, ElDescriptionsItem, ElAlert, ElDivider } from 'element-plus'

const UsageGuide = defineComponent({
  name: 'UsageGuide',
  setup() {
    return () =>
      h('div', { class: 'usage-guide' }, [
        h(
          ElCard,
          { class: 'guide-card' },
          {
            default: () => [
              h('h2', '📚 工具函数库使用指南'),
              h(ElDivider),

              // 快速开始
              h('h3', '🚀 快速开始'),
              h(
                ElAlert,
                {
                  type: 'success',
                  title: '导入方式',
                  closable: false
                },
                {
                  default: () =>
                    h('pre', { style: { marginTop: '8px' } }, [
                      h(
                        'code',
                        "import { formatDate, isEmail, debounce, storage } from '@/utils'"
                      )
                    ])
                }
              ),

              h(ElDivider),

              // 模块说明
              h('h3', '📦 模块说明'),
              h(
                ElDescriptions,
                { column: 1, border: true },
                {
                  default: () => [
                    h(
                      ElDescriptionsItem,
                      { label: 'format.ts' },
                      { default: () => '格式化工具：日期、数字、货币、文件大小、隐私信息等' }
                    ),
                    h(
                      ElDescriptionsItem,
                      { label: 'validation.ts' },
                      {
                        default: () =>
                          '验证工具：邮箱、手机、身份证、URL验证，以及Element Plus表单规则'
                      }
                    ),
                    h(
                      ElDescriptionsItem,
                      { label: 'constants.ts' },
                      { default: () => '常量定义：HTTP状态码、文件类型、业务状态、UI配置等' }
                    ),
                    h(
                      ElDescriptionsItem,
                      { label: 'helpers.ts' },
                      {
                        default: () =>
                          '辅助函数：防抖节流、深拷贝、数组处理、树形数据、本地存储等'
                      }
                    )
                  ]
                }
              ),

              h(ElDivider),

              // 组合式函数
              h('h3', '🔌 组合式函数 (Composables)'),
              h(
                ElDescriptions,
                { column: 1, border: true },
                {
                  default: () => [
                    h(
                      ElDescriptionsItem,
                      { label: 'useNotification' },
                      { default: () => '消息通知：success, warning, error, info, confirm' }
                    ),
                    h(
                      ElDescriptionsItem,
                      { label: 'useAsync' },
                      { default: () => '异步处理：loading状态、错误处理、请求取消' }
                    ),
                    h(
                      ElDescriptionsItem,
                      { label: 'useFileUpload' },
                      { default: () => '文件上传：文件选择、上传进度、拖拽上传' }
                    ),
                    h(
                      ElDescriptionsItem,
                      { label: 'useForm' },
                      { default: () => '表单处理：表单验证、错误提示' }
                    ),
                    h(
                      ElDescriptionsItem,
                      { label: 'useSSE' },
                      { default: () => 'SSE流处理：实时数据流、自动重连' }
                    )
                  ]
                }
              ),

              h(ElDivider),

              // 最佳实践
              h('h3', '💡 最佳实践'),
              h('ul', { class: 'best-practices' }, [
                h('li', '✅ 统一使用工具函数，避免重复编写相同逻辑'),
                h('li', '✅ 在组件中优先使用组合式函数封装可复用逻辑'),
                h('li', '✅ 使用TypeScript类型提示，提高开发效率'),
                h('li', '✅ 参考本演示页面了解各函数的具体用法'),
                h('li', '✅ 遇到新需求时，先检查是否已有相应工具函数')
              ]),

              h(ElDivider),

              // 代码示例
              h('h3', '📝 代码示例'),
              h(
                'div',
                { class: 'code-examples' },
                h('pre', { class: 'code-block' }, [
                  h('code', [
                    '// 1. 格式化日期\n',
                    "const dateStr = formatDate(new Date(), 'YYYY-MM-DD HH:mm:ss')\n\n",
                    '// 2. 验证邮箱\n',
                    "if (isEmail(email)) { /* ... */ }\n\n",
                    '// 3. 防抖搜索\n',
                    'const debouncedSearch = debounce(search, 500)\n\n',
                    '// 4. 本地存储\n',
                    "storage.set('userInfo', { name: 'Alice' })\n",
                    "const userInfo = storage.get('userInfo')\n\n",
                    '// 5. 使用组合式函数\n',
                    'const { success } = useNotification()\n',
                    "success('操作成功！')"
                  ])
                ])
              ),

              h(ElDivider),

              // 性能优化建议
              h('h3', '⚡ 性能优化建议'),
              h(
                ElAlert,
                { type: 'warning', title: '注意事项', closable: false },
                {
                  default: () =>
                    h('ul', { style: { marginTop: '8px', marginBottom: 0 } }, [
                      h('li', '防抖/节流函数建议在组件外部定义，避免重复创建'),
                      h('li', 'deepClone适用于小对象，大数据量建议使用其他方案'),
                      h('li', '本地存储有容量限制（通常5-10MB），注意数据大小'),
                      h('li', '异步操作记得处理错误和loading状态')
                    ])
                }
              )
            ]
          }
        )
      ])
  }
})

export default {
  components: { UsageGuide }
}
</script>

<style scoped lang="scss">
.demo-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
      color: #303133;
    }

    .subtitle {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }
}

.demo-tabs-card {
  margin-bottom: 20px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.footer-card {
  .footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
    color: #606266;

    > div {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}

// 使用指南样式
:deep(.usage-guide) {
  .guide-card {
    h2 {
      font-size: 24px;
      color: #303133;
      margin-top: 0;
    }

    h3 {
      font-size: 18px;
      color: #409eff;
      margin-top: 24px;
      margin-bottom: 16px;
    }

    .best-practices {
      list-style: none;
      padding: 0;
      margin: 0;

      li {
        padding: 8px 0;
        color: #606266;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }
      }
    }

    .code-examples {
      .code-block {
        background: #f5f7fa;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;

        code {
          font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
          font-size: 13px;
          line-height: 1.6;
          color: #303133;
        }
      }
    }
  }
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-tabs--border-card) {
  border: none;
  box-shadow: none;
}

:deep(.el-tabs__header) {
  background-color: #f5f7fa;
  border-bottom: 2px solid #e4e7ed;
}
</style>
