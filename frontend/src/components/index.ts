/**
 * 通用UI组件库统一导出
 *
 * 使用方式：
 * import { Loading, Empty, PageHeader, Card, ListPageLayout, DetailPageLayout } from '@/components'
 */

// 基础组件
import Loading from './Loading.vue'
import Empty from './Empty.vue'
import PageHeader from './PageHeader.vue'
import Card from './Card.vue'
import UploadButton from './UploadButton.vue'
import IconButton from './IconButton.vue'
import SSEStreamViewer from './SSEStreamViewer.vue'
import DocumentUploader from './DocumentUploader.vue'
import DocumentPreview from './DocumentPreview.vue'

// 编辑器组件
import RichTextEditor from './Editor/RichTextEditor.vue'

// 布局组件
import ListPageLayout from './layouts/ListPageLayout.vue'
import DetailPageLayout from './layouts/DetailPageLayout.vue'
import FormTabLayout from './layouts/FormTabLayout.vue'

// 业务组件
import StatsCard from './business/StatsCard.vue'
import HitlFileAlert from './business/HitlFileAlert.vue'
import HistoryFilesPanel from './business/HistoryFilesPanel.vue'

// 全局组件
import FeedbackButton from './FeedbackButton.vue'

// 默认导出所有组件
export {
  // 基础组件
  Loading,
  Empty,
  PageHeader,
  Card,
  UploadButton,
  IconButton,
  SSEStreamViewer,
  DocumentUploader,
  DocumentPreview,
  // 编辑器组件
  RichTextEditor,
  // 布局组件
  ListPageLayout,
  DetailPageLayout,
  FormTabLayout,
  // 业务组件
  StatsCard,
  HitlFileAlert,
  HistoryFilesPanel,
  // 全局组件
  FeedbackButton
}

// 类型导出
export type { StatItem } from './business/StatsCard.vue'
export type { HitlFileAlertProps } from './business/HitlFileAlert.vue'
export type { HistoryFilesPanelProps } from './business/HistoryFilesPanel.vue'
export type { ListPageLayoutProps } from './layouts/ListPageLayout.vue'

// 也可以作为对象导出
export default {
  // 基础组件
  Loading,
  Empty,
  PageHeader,
  Card,
  UploadButton,
  IconButton,
  SSEStreamViewer,
  DocumentUploader,
  DocumentPreview,
  // 编辑器组件
  RichTextEditor,
  // 布局组件
  ListPageLayout,
  DetailPageLayout,
  FormTabLayout,
  // 业务组件
  StatsCard,
  HitlFileAlert,
  HistoryFilesPanel,
  // 全局组件
  FeedbackButton
}
