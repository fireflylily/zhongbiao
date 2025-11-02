<template>
  <el-card class="demo-card">
    <template #header>
      <div class="card-header">
        <span>辅助函数演示</span>
        <el-tag type="success">helpers.ts</el-tag>
      </div>
    </template>

    <!-- 防抖与节流 -->
    <el-divider content-position="left">
      <el-icon><Timer /></el-icon>
      防抖与节流
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="debounce(防抖函数)">
          <el-space direction="vertical" style="width: 100%">
            <div>点击次数（不防抖）: {{ normalClickCount }}</div>
            <el-button @click="handleNormalClick" type="primary">普通点击</el-button>
            <div>点击次数（防抖500ms）: {{ debounceClickCount }}</div>
            <el-button @click="handleDebounceClick" type="success">防抖点击</el-button>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="throttle(节流函数)">
          <el-space direction="vertical" style="width: 100%">
            <div>点击次数（不节流）: {{ normalThrottleCount }}</div>
            <el-button @click="handleNormalThrottleClick" type="primary">普通点击</el-button>
            <div>点击次数（节流500ms）: {{ throttleClickCount }}</div>
            <el-button @click="handleThrottleClick" type="warning">节流点击</el-button>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- 深拷贝与合并 -->
    <el-divider content-position="left">
      <el-icon><CopyDocument /></el-icon>
      深拷贝与合并
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="deepClone(深拷贝)">
          <el-space direction="vertical">
            <div>原对象: {{ JSON.stringify(originalObj) }}</div>
            <div>深拷贝: {{ JSON.stringify(clonedObj) }}</div>
            <el-button @click="modifyClone" type="primary" size="small">修改拷贝对象</el-button>
            <el-tag v-if="cloneModified" type="success">修改后原对象未受影响！</el-tag>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="deepMerge(深度合并)">
          <el-space direction="vertical">
            <div>对象1: {{ JSON.stringify(mergeObj1) }}</div>
            <div>对象2: {{ JSON.stringify(mergeObj2) }}</div>
            <div>合并结果: {{ JSON.stringify(mergedObj) }}</div>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- 数组处理 -->
    <el-divider content-position="left">
      <el-icon><Grid /></el-icon>
      数组处理
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="unique(数组去重)">
          <el-space direction="vertical">
            <div>原数组: {{ JSON.stringify(duplicateArray) }}</div>
            <div>去重后: {{ JSON.stringify(uniqueArray) }}</div>
          </el-space>
        </demo-item>

        <demo-item label="groupBy(数组分组)">
          <el-space direction="vertical">
            <div>原数组: {{ JSON.stringify(groupArray) }}</div>
            <div>按type分组: {{ JSON.stringify(groupedArray) }}</div>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="unique(对象数组去重)">
          <el-space direction="vertical">
            <div>原数组: {{ JSON.stringify(duplicateObjArray) }}</div>
            <div>按id去重: {{ JSON.stringify(uniqueObjArray) }}</div>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- 树形数据处理 -->
    <el-divider content-position="left">
      <el-icon><List /></el-icon>
      树形数据处理
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="listToTree(列表转树)">
          <el-space direction="vertical">
            <div style="font-size: 12px">
              列表数据: {{ JSON.stringify(flatList) }}
            </div>
            <div style="font-size: 12px">
              树形结构: {{ JSON.stringify(treeData) }}
            </div>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="treeToList(树转列表)">
          <el-space direction="vertical">
            <div style="font-size: 12px">
              树形结构: {{ JSON.stringify(treeForFlat) }}
            </div>
            <div style="font-size: 12px">
              扁平列表: {{ JSON.stringify(flattenedList) }}
            </div>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- 本地存储 -->
    <el-divider content-position="left">
      <el-icon><FolderOpened /></el-icon>
      本地存储
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="storage(LocalStorage)">
          <el-space direction="vertical" style="width: 100%">
            <el-input v-model="storageKey" placeholder="键名" />
            <el-input v-model="storageValue" placeholder="值" />
            <el-space>
              <el-button @click="saveToStorage" type="primary" size="small">保存</el-button>
              <el-button @click="loadFromStorage" type="success" size="small">读取</el-button>
              <el-button @click="removeFromStorage" type="danger" size="small">删除</el-button>
            </el-space>
            <div v-if="loadedValue">读取的值: {{ loadedValue }}</div>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="其他工具函数">
          <el-space direction="vertical" style="width: 100%">
            <div>UUID: {{ generatedUUID }}</div>
            <el-button @click="generateNewUUID" type="primary" size="small">生成新UUID</el-button>
            <div>随机字符串(8位): {{ randomStr }}</div>
            <el-button @click="generateRandomStr" type="success" size="small">生成随机串</el-button>
            <div>浏览器信息: {{ browserInfo.name }} {{ browserInfo.version }}</div>
            <div>是否移动端: {{ mobileStatus }}</div>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>

    <!-- 文件操作 -->
    <el-divider content-position="left">
      <el-icon><Document /></el-icon>
      文件操作
    </el-divider>
    <el-row :gutter="20">
      <el-col :span="12">
        <demo-item label="文件名处理">
          <el-space direction="vertical">
            <div>文件名: document.report.pdf</div>
            <div>扩展名: {{ getFileExtension('document.report.pdf') }}</div>
            <div>不含扩展名: {{ getFileName('document.report.pdf') }}</div>
          </el-space>
        </demo-item>
      </el-col>

      <el-col :span="12">
        <demo-item label="剪贴板操作">
          <el-space direction="vertical" style="width: 100%">
            <el-input v-model="clipboardText" placeholder="输入要复制的文本" />
            <el-button @click="copyText" type="primary" size="small">复制到剪贴板</el-button>
            <el-tag v-if="copySuccess" type="success">复制成功！</el-tag>
          </el-space>
        </demo-item>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Timer, CopyDocument, Grid, List, FolderOpened, Document } from '@element-plus/icons-vue'
import {
  debounce,
  throttle,
  deepClone,
  deepMerge,
  unique,
  groupBy,
  listToTree,
  treeToList,
  storage,
  generateUUID,
  randomString,
  getBrowserInfo,
  isMobile,
  getFileExtension,
  getFileName,
  copyToClipboard
} from '@/utils'
import { ElMessage } from 'element-plus'

// ============ 防抖与节流 ============
const normalClickCount = ref(0)
const debounceClickCount = ref(0)
const normalThrottleCount = ref(0)
const throttleClickCount = ref(0)

function handleNormalClick() {
  normalClickCount.value++
}

const handleDebounceClick = debounce(() => {
  debounceClickCount.value++
}, 500)

function handleNormalThrottleClick() {
  normalThrottleCount.value++
}

const handleThrottleClick = throttle(() => {
  throttleClickCount.value++
}, 500)

// ============ 深拷贝与合并 ============
const originalObj = ref({ a: 1, b: { c: 2 } })
const clonedObj = ref(deepClone(originalObj.value))
const cloneModified = ref(false)

function modifyClone() {
  clonedObj.value.b.c = 999
  cloneModified.value = originalObj.value.b.c === 2
}

const mergeObj1 = { a: 1, b: { x: 1 } }
const mergeObj2 = { b: { y: 2 }, c: 3 }
const mergedObj = deepMerge({ ...mergeObj1 }, mergeObj2)

// ============ 数组处理 ============
const duplicateArray = [1, 2, 2, 3, 3, 4]
const uniqueArray = unique(duplicateArray)

const duplicateObjArray = [
  { id: 1, name: 'A' },
  { id: 2, name: 'B' },
  { id: 1, name: 'C' }
]
const uniqueObjArray = unique(duplicateObjArray, 'id')

const groupArray = [
  { type: 'A', value: 1 },
  { type: 'B', value: 2 },
  { type: 'A', value: 3 }
]
const groupedArray = groupBy(groupArray, 'type')

// ============ 树形数据处理 ============
const flatList = [
  { id: 1, name: '节点1', parent_id: null },
  { id: 2, name: '节点2', parent_id: 1 },
  { id: 3, name: '节点3', parent_id: 1 },
  { id: 4, name: '节点4', parent_id: 2 }
]
const treeData = listToTree(flatList)

const treeForFlat = [
  {
    id: 1,
    name: '根节点',
    children: [
      { id: 2, name: '子节点1', children: [] },
      { id: 3, name: '子节点2', children: [] }
    ]
  }
]
const flattenedList = treeToList(treeForFlat)

// ============ 本地存储 ============
const storageKey = ref('demo-key')
const storageValue = ref('demo-value')
const loadedValue = ref<any>(null)

function saveToStorage() {
  storage.set(storageKey.value, storageValue.value)
  ElMessage.success('保存成功')
}

function loadFromStorage() {
  loadedValue.value = storage.get(storageKey.value)
  if (loadedValue.value === null) {
    ElMessage.warning('未找到该键')
  }
}

function removeFromStorage() {
  storage.remove(storageKey.value)
  loadedValue.value = null
  ElMessage.success('删除成功')
}

// ============ 其他工具 ============
const generatedUUID = ref(generateUUID())
const randomStr = ref(randomString(8))
const browserInfo = getBrowserInfo()
const mobileStatus = isMobile() ? '是' : '否'

function generateNewUUID() {
  generatedUUID.value = generateUUID()
}

function generateRandomStr() {
  randomStr.value = randomString(8)
}

// ============ 剪贴板 ============
const clipboardText = ref('Hello, World!')
const copySuccess = ref(false)

async function copyText() {
  const success = await copyToClipboard(clipboardText.value)
  copySuccess.value = success
  if (success) {
    ElMessage.success('复制成功')
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } else {
    ElMessage.error('复制失败')
  }
}
</script>

<script lang="ts">
// DemoItem 组件
import { defineComponent, h } from 'vue'

const DemoItem = defineComponent({
  name: 'DemoItem',
  props: {
    label: String,
    code: String
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'demo-item' }, [
        h('div', { class: 'demo-label' }, props.label),
        h('div', { class: 'demo-result' }, slots.default?.()),
        props.code ? h('div', { class: 'demo-code' }, h('code', props.code)) : null
      ])
  }
})

export default {
  components: { DemoItem }
}
</script>

<style scoped lang="scss">
.demo-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.demo-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;

  .demo-label {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
    font-weight: 500;
  }

  .demo-result {
    font-size: 14px;
    color: #303133;
    padding: 8px;
    background: white;
    border-radius: 4px;
  }

  .demo-code {
    font-size: 12px;
    color: #909399;
    margin-top: 8px;

    code {
      background: #e9ecef;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }
  }
}

:deep(.el-divider) {
  margin: 24px 0;

  .el-divider__text {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #409eff;
  }
}
</style>
