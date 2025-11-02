<template>
  <div class="business-response">
    <PageHeader
      title="商务应答"
      description="智能生成商务应答文档"
    />

    <Card title="商务应答生成">
      <Empty type="no-data" description="功能开发中..." />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.business-response {
  padding: 20px;
}
</style>
