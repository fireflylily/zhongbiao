<template>
  <div class="test-checklist">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <el-alert
        :title="error"
        type="error"
        show-icon
        :closable="false"
      />
    </div>

    <!-- 测试清单内容 -->
    <div v-else-if="checklist" class="checklist-content">
      <!-- 核心回归测试 -->
      <el-card class="checklist-section" shadow="never">
        <template #header>
          <div class="section-header">
            <div class="header-left">
              <i class="bi-shield-check section-icon"></i>
              <span class="section-title">{{ checklist.core_tests.name }}</span>
              <el-tag type="danger" size="small" effect="dark">核心</el-tag>
            </div>
            <div class="header-right">
              <span class="test-count">{{ coreTestsStatus.passed }}/{{ coreTestsStatus.total }}</span>
              <el-button
                size="small"
                type="primary"
                @click="runAllCoreTests"
                :loading="isRunningAll"
                :disabled="isRunningAll"
              >
                <i class="bi-play-fill"></i> 全部运行
              </el-button>
            </div>
          </div>
        </template>

        <div class="test-list">
          <div
            v-for="test in checklist.core_tests.tests"
            :key="test.id"
            class="test-item"
            :class="getTestStatusClass(test.full_path)"
          >
            <div class="test-info">
              <i :class="getTestStatusIcon(test.full_path)" class="test-status-icon"></i>
              <div class="test-details">
                <div class="test-name">{{ test.name }}</div>
                <div class="test-path">{{ test.file }}</div>
              </div>
            </div>
            <div class="test-actions">
              <el-tag
                v-if="testStatus[test.full_path]?.status === 'passed'"
                type="success"
                size="small"
                effect="plain"
              >
                ✓ 通过
              </el-tag>
              <el-tag
                v-else-if="testStatus[test.full_path]?.status === 'failed'"
                type="danger"
                size="small"
                effect="plain"
              >
                ✗ 失败
              </el-tag>
              <el-tag
                v-else
                type="info"
                size="small"
                effect="plain"
              >
                未运行
              </el-tag>
              <el-button
                size="small"
                @click="runSingleTest(test.full_path)"
                :loading="runningTests[test.full_path]"
                :disabled="runningTests[test.full_path]"
              >
                运行
              </el-button>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 测试套件 -->
      <div v-for="(suite, suiteName) in checklist.test_suites" :key="suiteName" class="suite-section">
        <el-card shadow="never">
          <template #header>
            <div class="section-header">
              <div class="header-left">
                <i class="bi-folder-check section-icon"></i>
                <span class="section-title">{{ suite.description }}</span>
                <el-tag size="small" effect="plain">{{ suite.tests.length }} 个测试</el-tag>
              </div>
              <el-button
                size="small"
                type="primary"
                plain
                @click="runSuite(suiteName)"
                :loading="runningSuites[suiteName]"
                :disabled="runningSuites[suiteName]"
              >
                <i class="bi-play-fill"></i> 运行套件
              </el-button>
            </div>
          </template>

          <div class="test-list">
            <div
              v-for="test in suite.tests"
              :key="test.id"
              class="test-item"
              :class="{ 'is-directory': test.is_directory }"
            >
              <div class="test-info">
                <i :class="test.is_directory ? 'bi-folder' : 'bi-file-earmark-code'" class="test-icon"></i>
                <div class="test-details">
                  <div class="test-name">{{ test.name }}</div>
                  <div class="test-path">{{ test.file }}</div>
                </div>
              </div>
              <div class="test-actions" v-if="!test.is_directory">
                <el-button
                  size="small"
                  @click="runSingleTest(test.full_path)"
                  :loading="runningTests[test.full_path]"
                  :disabled="runningTests[test.full_path]"
                >
                  运行
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 测试输出对话框 -->
    <el-dialog
      v-model="showOutputDialog"
      title="测试输出"
      width="70%"
      :close-on-click-modal="false"
    >
      <div class="test-output">
        <pre v-if="currentTestOutput" class="output-content">{{ currentTestOutput }}</pre>
        <el-empty v-else description="无输出" />
      </div>
      <template #footer>
        <el-button @click="showOutputDialog = false">关闭</el-button>
        <el-button type="primary" @click="copyOutput">复制输出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { testRunnerApi, type Checklist, type TestStatus } from '@/api/test-runner'

// ==================== State ====================

const loading = ref(true)
const error = ref<string | null>(null)
const checklist = ref<Checklist | null>(null)
const testStatus = ref<Record<string, TestStatus>>({})

const runningTests = ref<Record<string, boolean>>({})
const runningSuites = ref<Record<string, boolean>>({})
const isRunningAll = ref(false)

const showOutputDialog = ref(false)
const currentTestOutput = ref<string>('')

// ==================== Computed ====================

const coreTestsStatus = computed(() => {
  if (!checklist.value) return { total: 0, passed: 0 }

  const total = checklist.value.core_tests.tests.length
  const passed = checklist.value.core_tests.tests.filter(
    test => testStatus.value[test.full_path]?.status === 'passed'
  ).length

  return { total, passed }
})

// ==================== Methods ====================

/**
 * 加载测试清单
 */
const loadChecklist = async () => {
  try {
    loading.value = true
    error.value = null

    const response = await testRunnerApi.getChecklist()

    if (response.success) {
      checklist.value = response.checklist
    } else {
      error.value = '加载测试清单失败'
    }
  } catch (err: any) {
    error.value = err.message || '网络错误'
  } finally {
    loading.value = false
  }
}

/**
 * 加载测试状态
 */
const loadTestStatus = async () => {
  try {
    const response = await testRunnerApi.getChecklistStatus()

    if (response.success) {
      testStatus.value = response.test_status
    }
  } catch (err) {
    console.error('加载测试状态失败:', err)
  }
}

/**
 * 运行单个测试
 */
const runSingleTest = async (testPath: string) => {
  try {
    runningTests.value[testPath] = true

    const response = await testRunnerApi.runSingleTest(testPath)

    if (response.success && response.passed) {
      ElMessage.success(`测试通过: ${testPath.split('::')[1] || testPath}`)

      // 更新状态
      testStatus.value[testPath] = {
        available: true,
        status: 'passed',
        last_run: new Date().toISOString()
      }
    } else {
      ElMessage.error(`测试失败: ${testPath.split('::')[1] || testPath}`)

      // 更新状态
      testStatus.value[testPath] = {
        available: true,
        status: 'failed',
        last_run: new Date().toISOString()
      }
    }

    // 显示输出
    currentTestOutput.value = response.output || ''
    showOutputDialog.value = true

  } catch (err: any) {
    ElMessage.error(`运行失败: ${err.message}`)
  } finally {
    runningTests.value[testPath] = false
  }
}

/**
 * 运行所有核心测试
 */
const runAllCoreTests = async () => {
  if (!checklist.value) return

  isRunningAll.value = true

  for (const test of checklist.value.core_tests.tests) {
    await runSingleTest(test.full_path)
  }

  isRunningAll.value = false
  ElMessage.success('所有核心测试已完成')
}

/**
 * 运行测试套件
 */
const runSuite = async (suiteName: string) => {
  ElMessage.info(`运行测试套件: ${suiteName}`)
  runningSuites.value[suiteName] = true

  try {
    // 调用原有的测试运行API
    const response = await fetch('/api/testing/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        test_type: 'backend',
        test_path: `tests/`  // 简化处理，实际应该根据suite映射
      })
    })

    const data = await response.json()

    if (data.success) {
      ElMessage.success(`套件 ${suiteName} 测试完成`)
      await loadTestStatus()
    } else {
      ElMessage.error(`套件运行失败: ${data.error}`)
    }
  } catch (err: any) {
    ElMessage.error(`运行失败: ${err.message}`)
  } finally {
    runningSuites.value[suiteName] = false
  }
}

/**
 * 获取测试状态图标
 */
const getTestStatusIcon = (testPath: string) => {
  const status = testStatus.value[testPath]?.status

  if (status === 'passed') return 'bi-check-circle-fill'
  if (status === 'failed') return 'bi-x-circle-fill'
  return 'bi-circle'
}

/**
 * 获取测试状态类
 */
const getTestStatusClass = (testPath: string) => {
  const status = testStatus.value[testPath]?.status

  if (status === 'passed') return 'test-passed'
  if (status === 'failed') return 'test-failed'
  return 'test-unknown'
}

/**
 * 复制输出
 */
const copyOutput = () => {
  if (!currentTestOutput.value) return

  navigator.clipboard.writeText(currentTestOutput.value).then(() => {
    ElMessage.success('输出已复制到剪贴板')
  })
}

// ==================== Lifecycle ====================

onMounted(async () => {
  await loadChecklist()
  await loadTestStatus()
})
</script>

<style scoped lang="scss">
.test-checklist {
  .loading-state {
    padding: 20px;
  }

  .error-state {
    padding: 20px;
  }

  .checklist-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .checklist-section,
  .suite-section {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;

        .section-icon {
          font-size: 20px;
          color: var(--el-color-primary);
        }

        .section-title {
          font-weight: 600;
          font-size: 16px;
        }
      }

      .header-right {
        display: flex;
        align-items: center;
        gap: 12px;

        .test-count {
          font-weight: 600;
          font-size: 14px;
          color: var(--el-text-color-secondary);
        }
      }
    }
  }

  .test-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .test-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      border-radius: 6px;
      background: var(--el-fill-color-lighter);
      transition: all 0.3s ease;

      &:hover {
        background: var(--el-fill-color-light);
      }

      &.test-passed {
        border-left: 3px solid #67C23A;
      }

      &.test-failed {
        border-left: 3px solid #F56C6C;
      }

      &.test-unknown {
        border-left: 3px solid #909399;
      }

      &.is-directory {
        background: var(--el-fill-color-blank);
        border: 1px dashed var(--el-border-color);
      }

      .test-info {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;

        .test-status-icon {
          font-size: 20px;

          &.bi-check-circle-fill {
            color: #67C23A;
          }

          &.bi-x-circle-fill {
            color: #F56C6C;
          }

          &.bi-circle {
            color: #909399;
          }
        }

        .test-icon {
          font-size: 18px;
          color: var(--el-color-primary);
        }

        .test-details {
          flex: 1;

          .test-name {
            font-weight: 500;
            font-size: 14px;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }

          .test-path {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            font-family: 'Courier New', monospace;
          }
        }
      }

      .test-actions {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }
  }

  .test-output {
    .output-content {
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 16px;
      border-radius: 4px;
      font-family: 'Courier New', Consolas, monospace;
      font-size: 12px;
      line-height: 1.5;
      max-height: 500px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}
</style>
