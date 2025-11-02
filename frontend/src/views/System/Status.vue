<template>
  <div class="system-status">
    <PageHeader
      title="系统状态"
      description="查看系统运行状态和监控信息"
    />

    <Card title="系统信息">
      <Empty type="no-data" description="功能开发中..." />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.system-status {
  padding: 20px;
}
</style>
