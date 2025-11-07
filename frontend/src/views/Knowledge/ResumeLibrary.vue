<template>
  <div class="resume-library">
    <Card title="简历列表">
      <Empty type="no-data" description="暂无简历数据" />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.resume-library {
  padding: 20px;
}
</style>
