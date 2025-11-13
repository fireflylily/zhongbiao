<template>
  <div class="editor-test-page">
    <h1>Editor Pagination Test</h1>
    <p>This page tests the RichTextEditor's pagination functionality in isolation.</p>
    <div class="editor-container">
      <RichTextEditor
        ref="editorRef"
        v-model="editorContent"
        title="Test Document"
        :height="800"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RichTextEditor } from '@/components';

const editorRef = ref<any>(null);

// Some long content to force pagination
const longContent = `
  <h1>Chapter 1</h1>
  <p>${'This is a paragraph. '.repeat(100)}</p>
  <p>${'This is another paragraph. '.repeat(100)}</p>
  <h1>Chapter 2</h1>
  <p>${'This is a paragraph in chapter 2. '.repeat(100)}</p>
  <p>${'This is another paragraph in chapter 2. '.repeat(100)}</p>
  <h1>Chapter 3</h1>
  <p>${'This is a paragraph in chapter 3. '.repeat(100)}</p>
  <p>${'This is another paragraph in chapter 3. '.repeat(100)}</p>
  <h1>Chapter 4</h1>
  <p>${'This is a paragraph in chapter 4. '.repeat(100)}</p>
  <p>${'This is another paragraph in chapter 4. '.repeat(100)}</p>
`;

const editorContent = ref(longContent);
</script>

<style scoped>
.editor-test-page {
  padding: 20px;
}
.editor-container {
  margin-top: 20px;
  border: 2px solid #ccc;
  /* No fixed height or overflow:hidden here */
}
</style>