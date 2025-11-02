<template>
  <div class="help-center">
    <PageHeader
      title="帮助中心"
      description="使用文档和常见问题"
    />

    <Card title="帮助文档">
      <Empty type="no-data" description="帮助文档正在编写中..." />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.help-center {
  padding: 20px;
}
</style>
