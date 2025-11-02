<template>
  <div class="company-library">
    <PageHeader
      title="企业库"
      description="管理企业基本信息和资质证书"
    >
      <template #actions>
        <el-button type="primary" icon="Plus">新增企业</el-button>
      </template>
    </PageHeader>

    <Card title="企业列表">
      <Empty type="no-data" description="暂无企业数据" />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.company-library {
  padding: 20px;
}
</style>
