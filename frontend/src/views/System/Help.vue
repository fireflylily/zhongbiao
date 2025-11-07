<template>
  <div class="help-center">
    <Card title="帮助文档">
      <Empty type="no-data" description="帮助文档正在编写中..." />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.help-center {
  padding: 20px;
}
</style>
