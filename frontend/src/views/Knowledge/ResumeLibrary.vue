<template>
  <div class="resume-library">
    <PageHeader
      title="简历库"
      description="管理人员简历信息"
    >
      <template #actions>
        <el-button type="primary" icon="Plus">新增简历</el-button>
      </template>
    </PageHeader>

    <Card title="简历列表">
      <Empty type="no-data" description="暂无简历数据" />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty } from '@/components'
</script>

<style scoped lang="scss">
.resume-library {
  padding: 20px;
}
</style>
