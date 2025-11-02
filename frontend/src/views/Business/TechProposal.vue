<template>
  <div class="tech-proposal">
    <PageHeader
      title="技术方案"
      description="AI生成技术方案大纲"
    />

    <Card title="技术方案生成">
      <Empty type="no-data" description="功能开发中..." />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.tech-proposal {
  padding: 20px;
}
</style>
