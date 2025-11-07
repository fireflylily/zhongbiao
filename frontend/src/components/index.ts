/**
 * 通用UI组件库统一导出
 *
 * 使用方式：
 * import { Loading, Empty, PageHeader, Card, UploadButton, IconButton, SSEStreamViewer, DocumentUploader, DocumentPreview } from '@/components'
 */

import Loading from './Loading.vue'
import Empty from './Empty.vue'
import PageHeader from './PageHeader.vue'
import Card from './Card.vue'
import UploadButton from './UploadButton.vue'
import IconButton from './IconButton.vue'
import SSEStreamViewer from './SSEStreamViewer.vue'
import DocumentUploader from './DocumentUploader.vue'
import DocumentPreview from './DocumentPreview.vue'

// 默认导出所有组件
export { Loading, Empty, PageHeader, Card, UploadButton, IconButton, SSEStreamViewer, DocumentUploader, DocumentPreview }

// 也可以作为对象导出
export default {
  Loading,
  Empty,
  PageHeader,
  Card,
  UploadButton,
  IconButton,
  SSEStreamViewer,
  DocumentUploader,
  DocumentPreview
}
