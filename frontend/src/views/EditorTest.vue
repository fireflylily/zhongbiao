<template>
  <div class="editor-test">
    <el-card>
      <template #header>
        <h2>Umo Editor 测试页面</h2>
      </template>

      <el-alert type="info" :closable="false" style="margin-bottom: 20px">
        这是一个最简单的Umo Editor测试。如果这里能正常显示，说明编辑器本身没问题。
      </el-alert>

      <!-- 最简单的编辑器 -->
      <div class="editor-container">
        <UmoEditor
          ref="editorRef"
        />
      </div>

      <div style="margin-top: 20px;">
        <el-button @click="getEditorContent">获取内容</el-button>
        <el-button @click="setTestContent">设置测试内容</el-button>
        <el-button @click="clearContent">清空</el-button>
      </div>

      <el-card v-if="outputContent" style="margin-top: 20px;" shadow="never">
        <template #header>输出内容</template>
        <div v-html="outputContent"></div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UmoEditor } from '@umoteam/editor'
import { ElMessage } from 'element-plus'

const editorRef = ref<any>(null)
const content = ref('<h1>测试文档</h1><h2>第一章</h2><p>这是测试内容...</p><h2>第二章</h2><p>更多内容...</p>')
const outputContent = ref('')

const getEditorContent = () => {
  if (!editorRef.value) {
    ElMessage.error('编辑器未就绪')
    return
  }

  try {
    console.log('编辑器ref:', editorRef.value)
    console.log('可用方法:', Object.keys(editorRef.value))

    // 尝试多种方法获取内容
    let html = ''

    // 方法1: 直接获取
    if (typeof editorRef.value.getHTML === 'function') {
      html = editorRef.value.getHTML()
      console.log('方法1成功: getHTML()')
    }
    // 方法2: 通过getEditor
    else if (typeof editorRef.value.getEditor === 'function') {
      const editor = editorRef.value.getEditor()
      console.log('editor实例:', editor)
      console.log('editor方法:', Object.keys(editor))

      if (typeof editor.getHTML === 'function') {
        html = editor.getHTML()
        console.log('方法2成功: getEditor().getHTML()')
      }
    }
    // 方法3: 通过getContent
    else if (typeof editorRef.value.getContent === 'function') {
      html = editorRef.value.getContent()
      console.log('方法3成功: getContent()')
    }

    if (html) {
      outputContent.value = html
      ElMessage.success('内容获取成功')
      console.log('编辑器内容:', html)
    } else {
      ElMessage.warning('无法获取内容，查看控制台')
    }
  } catch (error) {
    console.error('获取内容失败:', error)
    ElMessage.error('获取内容失败: ' + error)
  }
}

const setTestContent = () => {
  content.value = `
    <h1>新内容 - ${new Date().toLocaleTimeString()}</h1>
    <h2>章节1</h2>
    <p>这是动态设置的内容</p>
    <h2>章节2</h2>
    <p>包含多个标题用于测试目录功能</p>
  `
  ElMessage.success('内容已设置')
}

const clearContent = () => {
  content.value = '<p></p>'
  ElMessage.info('内容已清空')
}
</script>

<style scoped lang="scss">
.editor-test {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;

  .editor-container {
    border: 1px solid var(--el-border-color);
    border-radius: 4px;
    overflow: hidden;
  }
}
</style>
