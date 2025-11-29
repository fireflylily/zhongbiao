<template>
  <div class="document-library">
    <Card title="文档列表">
      <Empty type="no-data" description="暂无文档数据" />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.document-library {
  // 移除padding，避免与page-content的padding叠加
}
</style>
