<template>
  <div class="point-to-point">
    <PageHeader
      title="点对点应答"
      description="针对招标要求逐点响应"
    />

    <Card title="点对点应答生成">
      <Empty type="no-data" description="功能开发中..." />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.point-to-point {
  padding: 20px;
}
</style>
