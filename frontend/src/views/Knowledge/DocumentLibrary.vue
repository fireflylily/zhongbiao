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
  padding: 20px;
}
</style>
