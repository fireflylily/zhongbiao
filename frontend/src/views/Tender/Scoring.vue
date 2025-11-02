<template>
  <div class="tender-scoring">
    <PageHeader
      title="标书评分"
      description="AI辅助标书评分和风险分析"
    />

    <Card title="评分功能">
      <Empty type="no-data" description="功能开发中，敬请期待..." />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.tender-scoring {
  padding: 20px;
}
</style>
