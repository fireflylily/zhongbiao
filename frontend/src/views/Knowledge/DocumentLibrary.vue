<template>
  <div class="document-library">
    <Card title="文档列表">
      <Empty type="no-data" description="暂无文档数据" />
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, Empty, UploadButton } from '@/components'
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
