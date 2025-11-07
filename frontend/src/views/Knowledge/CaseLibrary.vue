<template>
  <div class="case-library">
    <Card title="案例列表">
      <Empty type="no-data" description="暂无案例数据" />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.case-library {
  padding: 20px;
}
</style>
