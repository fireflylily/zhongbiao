<template>
  <div class="case-library">
    <PageHeader
      title="案例库"
      description="管理历史项目案例"
    >
      <template #actions>
        <el-button type="primary" icon="Plus">新增案例</el-button>
      </template>
    </PageHeader>

    <Card title="案例列表">
      <Empty type="no-data" description="暂无案例数据" />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.case-library {
  padding: 20px;
}
</style>
