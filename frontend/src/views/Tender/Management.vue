<template>
  <div class="tender-management">
    <PageHeader
      title="投标管理"
      description="HITL人机协同系统"
    >
      <template #actions>
        <el-button type="primary" icon="Plus">新建项目</el-button>
      </template>
    </PageHeader>

    <Card title="项目列表">
      <Loading v-if="loading" text="加载中..." />
      <Empty v-else-if="!projects.length" type="no-data" description="暂无项目" />
      <el-table v-else :data="projects" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { PageHeader, Card, Loading, Empty } from '@/components'
import { useNotification } from '@/composables'

// 状态
const loading = ref(false)
const projects = ref<any[]>([])

// Hooks
const { success, error } = useNotification()

// 方法
const loadProjects = async () => {
  loading.value = true
  try {
    // TODO: 调用API加载项目列表
    // const data = await tenderApi.getProjects()
    // projects.value = data

    // 临时模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))
    projects.value = []
  } catch (err) {
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loading.value = false
  }
}

const handleEdit = (row: any) => {
  success('编辑功能', '待实现')
}

const handleDelete = (row: any) => {
  success('删除功能', '待实现')
}

// 生命周期
onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.tender-management {
  padding: 20px;
}
</style>
