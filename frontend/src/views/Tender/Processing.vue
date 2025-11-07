<template>
  <div class="tender-processing">
    <Card title="处理流程">
      <Empty type="no-data" description="请上传招标文档开始处理..." />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.tender-processing {
  padding: 20px;
}
</style>
