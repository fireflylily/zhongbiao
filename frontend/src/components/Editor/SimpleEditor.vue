<template>
  <div class="simple-editor">
    <h3>简单编辑器测试</h3>
    <UmoEditor
      ref="editorRef"
      value="<h1>测试标题</h1><p>这是测试内容</p>"
      height="400px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UmoEditor } from '@umoteam/editor'

const editorRef = ref()
</script>

<style scoped>
.simple-editor {
  padding: 20px;
}
</style>
