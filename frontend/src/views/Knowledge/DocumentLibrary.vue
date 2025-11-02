<template>
  <div class="document-library">
    <PageHeader
      title="文档库"
      description="管理企业知识文档"
    >
      <template #actions>
        <UploadButton
          :auto-upload="false"
          accept=".pdf,.doc,.docx"
          @change="handleUpload"
        >
          <el-button type="primary" icon="Upload">上传文档</el-button>
        </UploadButton>
      </template>
    </PageHeader>

    <Card title="文档列表">
      <Empty type="no-data" description="暂无文档数据" />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { PageHeader, Card, Empty, UploadButton } from '@/components'
import { useNotification } from '@/composables'

const { success } = useNotification()

const handleUpload = (file: File) => {
  success('上传文档', `已选择文件: ${file.name}`)
}
</script>

<style scoped lang="scss">
.document-library {
  padding: 20px;
}
</style>
