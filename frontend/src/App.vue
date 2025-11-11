<template>
  <router-view />
  <!-- 全局反馈按钮 -->
  <FeedbackButton />
</template>

<script setup lang="ts">
// App根组件
// 所有页面通过router-view渲染
import FeedbackButton from '@/components/FeedbackButton.vue'
</script>

<style lang="scss">
// 全局样式已在main.ts中导入
// 这里可以添加App级别的覆盖样式
</style>
