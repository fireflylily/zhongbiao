<template>
  <div class="system-status">
    <!-- 系统概览 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in overviewData" :key="item.label">
        <el-card shadow="hover" class="overview-card">
          <div class="overview-content">
            <el-icon :class="['overview-icon', item.iconClass]">
              <component :is="item.icon" />
            </el-icon>
            <div class="overview-info">
              <div class="overview-label">{{ item.label }}</div>
              <div class="overview-value">{{ item.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 服务状态 -->
    <el-card shadow="never" style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>服务状态</span>
          <el-button size="small" :icon="Refresh" @click="refreshStatus">刷新</el-button>
        </div>
      </template>

      <el-table :data="services" border>
        <el-table-column prop="name" label="服务名称" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'running' ? 'success' : 'danger'">
              {{ row.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uptime" label="运行时长" width="150" />
        <el-table-column prop="cpu" label="CPU使用率" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.cpu" :color="getProgressColor(row.cpu)" />
          </template>
        </el-table-column>
        <el-table-column prop="memory" label="内存使用率" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.memory" :color="getProgressColor(row.memory)" />
          </template>
        </el-table-column>
        <el-table-column prop="requests" label="请求数/分钟" width="130" />
        <el-table-column prop="avgResponseTime" label="平均响应时间" width="130" />
      </el-table>
    </el-card>

    <!-- 数据库状态 -->
    <el-card shadow="never" style="margin-top: 20px">
      <template #header>
        <span>数据库状态</span>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="数据库类型">{{ dbInfo.type }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ dbInfo.version }}</el-descriptions-item>
        <el-descriptions-item label="连接状态">
          <el-tag :type="dbInfo.connected ? 'success' : 'danger'">
            {{ dbInfo.connected ? '已连接' : '未连接' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="活动连接数">{{ dbInfo.activeConnections }}</el-descriptions-item>
        <el-descriptions-item label="空闲连接数">{{ dbInfo.idleConnections }}</el-descriptions-item>
        <el-descriptions-item label="最大连接数">{{ dbInfo.maxConnections }}</el-descriptions-item>
        <el-descriptions-item label="数据库大小">{{ dbInfo.size }}</el-descriptions-item>
        <el-descriptions-item label="表数量">{{ dbInfo.tables }}</el-descriptions-item>
        <el-descriptions-item label="慢查询数">{{ dbInfo.slowQueries }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 存储状态 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>磁盘使用情况</span>
          </template>

          <div style="padding: 20px">
            <el-progress
              type="circle"
              :percentage="diskUsage.percentage"
              :width="150"
              :color="getProgressColor(diskUsage.percentage)"
            >
              <span style="font-size: 14px">{{ diskUsage.percentage }}%</span>
            </el-progress>
            <div style="margin-top: 20px; text-align: center">
              <div>已使用: {{ diskUsage.used }}</div>
              <div>总容量: {{ diskUsage.total }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>缓存状态</span>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="缓存类型">Redis</el-descriptions-item>
            <el-descriptions-item label="连接状态">
              <el-tag type="success">已连接</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="使用内存">256 MB</el-descriptions-item>
            <el-descriptions-item label="键数量">1,234</el-descriptions-item>
            <el-descriptions-item label="命中率">98.5%</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统日志 -->
    <el-card shadow="never" style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>最近日志</span>
          <el-select v-model="logLevel" size="small" style="width: 120px">
            <el-option label="全部" value="all" />
            <el-option label="错误" value="error" />
            <el-option label="警告" value="warning" />
            <el-option label="信息" value="info" />
          </el-select>
        </div>
      </template>

      <el-table :data="filteredLogs" max-height="400">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLogLevelType(row.level)" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="150" />
        <el-table-column prop="message" label="消息" min-width="300" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Cpu, DataAnalysis, Document, Timer, Refresh } from '@element-plus/icons-vue'
// import { PageHeader } from '@/components' // Removed

// 系统概览数据
const overviewData = ref([
  {
    label: '系统运行时长',
    value: '15天 8小时',
    icon: Timer,
    iconClass: 'icon-primary'
  },
  {
    label: 'CPU使用率',
    value: '45%',
    icon: Cpu,
    iconClass: 'icon-success'
  },
  {
    label: '内存使用',
    value: '8.2 GB / 16 GB',
    icon: DataAnalysis,
    iconClass: 'icon-warning'
  },
  {
    label: '今日处理文档',
    value: '1,234',
    icon: Document,
    iconClass: 'icon-info'
  }
])

// 服务状态
const services = ref([
  {
    name: 'Web服务',
    status: 'running',
    uptime: '15天 8小时',
    cpu: 35,
    memory: 52,
    requests: 1234,
    avgResponseTime: '45ms'
  },
  {
    name: 'AI服务',
    status: 'running',
    uptime: '15天 8小时',
    cpu: 78,
    memory: 68,
    requests: 567,
    avgResponseTime: '1.2s'
  },
  {
    name: '文档处理服务',
    status: 'running',
    uptime: '15天 8小时',
    cpu: 42,
    memory: 45,
    requests: 234,
    avgResponseTime: '380ms'
  },
  {
    name: '知识库服务',
    status: 'running',
    uptime: '15天 8小时',
    cpu: 28,
    memory: 38,
    requests: 890,
    avgResponseTime: '120ms'
  }
])

// 数据库信息
const dbInfo = ref({
  type: 'PostgreSQL',
  version: '14.5',
  connected: true,
  activeConnections: 12,
  idleConnections: 8,
  maxConnections: 100,
  size: '2.5 GB',
  tables: 45,
  slowQueries: 3
})

// 磁盘使用情况
const diskUsage = ref({
  percentage: 68,
  used: '340 GB',
  total: '500 GB'
})

// 系统日志
const logLevel = ref('all')
const logs = ref([
  {
    time: '2025-01-15 10:23:45',
    level: 'info',
    module: 'Web服务',
    message: '用户登录成功: admin'
  },
  {
    time: '2025-01-15 10:22:30',
    level: 'info',
    module: 'AI服务',
    message: '文档处理任务完成: task_12345'
  },
  {
    time: '2025-01-15 10:21:15',
    level: 'warning',
    module: '数据库',
    message: '慢查询检测: 查询耗时3.2秒'
  },
  {
    time: '2025-01-15 10:20:00',
    level: 'error',
    module: 'AI服务',
    message: 'API调用失败: 超时'
  },
  {
    time: '2025-01-15 10:18:45',
    level: 'info',
    module: '知识库',
    message: '文档索引更新完成'
  }
])

// 筛选后的日志
const filteredLogs = computed(() => {
  if (logLevel.value === 'all') {
    return logs.value
  }
  return logs.value.filter(log => log.level === logLevel.value)
})

// 刷新状态
const refreshStatus = () => {
  // 实际应该调用API刷新数据
  console.log('刷新状态')
}

// 获取进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage >= 80) return '#f56c6c'
  if (percentage >= 60) return '#e6a23c'
  return '#67c23a'
}

// 获取日志级别类型
const getLogLevelType = (level: string) => {
  const types: Record<string, any> = {
    error: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return types[level] || 'info'
}
</script>

<style scoped lang="scss">

.system-status {
  padding: 20px;

  .overview-card {
    .overview-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .overview-icon {
        font-size: 48px;

        &.icon-primary {
          color: var(--el-color-primary);
        }

        &.icon-success {
          color: var(--el-color-success);
        }

        &.icon-warning {
          color: var(--el-color-warning);
        }

        &.icon-info {
          color: var(--el-color-info);
        }
      }

      .overview-info {
        flex: 1;

        .overview-label {
          font-size: 14px;
          color: var(--el-text-color-secondary);
          margin-bottom: 8px;
        }

        .overview-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
      }
    }
  }

  :deep(.el-card__header) {
    padding: 16px 20px;
    background: var(--el-fill-color-light);
    font-weight: 600;
  }
}
</style>
