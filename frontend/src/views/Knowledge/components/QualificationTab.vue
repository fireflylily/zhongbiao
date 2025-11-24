<template>
  <div class="qualification-tab">
    <Card title="资质信息管理">
      <!-- 加载状态 -->
      <Loading v-if="loading" text="加载资质信息..." />

      <!-- 资质列表 -->
      <div v-else>
        <!-- 四个资质分类 -->
        <div v-for="category in categories" :key="category.key" class="qualification-category">
          <h6 class="category-title" :class="`text-${category.color}`">
            <el-icon><Folder /></el-icon>
            {{ category.name }}
          </h6>

          <el-row :gutter="16">
            <el-col
              v-for="qual in getQualificationsByCategory(category.key)"
              :key="qual.key"
              :span="12"
            >
              <QualificationCard
                :qualification="qual"
                :file-info="qualificationFiles[qual.key]"
                :company-name="companyData?.company_name"
                :on-upload="createUploadHandler(qual.key)"
                @download="handleDownload"
                @delete="handleDelete"
              />
            </el-col>
          </el-row>
        </div>

        <!-- 自定义资质 -->
        <div class="qualification-category">
          <h6 class="category-title text-secondary">
            <el-icon><Plus /></el-icon>
            自定义资质
          </h6>

          <el-button type="primary" @click="showAddCustomDialog">
            <el-icon><Plus /></el-icon>
            添加自定义资质
          </el-button>

          <!-- 自定义资质列表 -->
          <el-row v-if="customQualifications.length > 0" :gutter="16" class="mt-3">
            <el-col
              v-for="(qual, index) in customQualifications"
              :key="qual.key"
              :span="12"
            >
              <QualificationCard
                :qualification="qual"
                :file-info="qualificationFiles[qual.key]"
                :is-custom="true"
                :on-upload="createUploadHandler(qual.key)"
                @download="handleDownload"
                @delete="handleDelete"
                @remove-custom="removeCustomQualification(index)"
              />
            </el-col>
          </el-row>
        </div>
      </div>
    </Card>

    <!-- 添加自定义资质对话框 -->
    <el-dialog
      v-model="customDialogVisible"
      title="添加自定义资质"
      width="400px"
    >
      <el-form :model="customForm" label-width="100px">
        <el-form-item label="资质名称">
          <el-input
            v-model="customForm.name"
            placeholder="请输入资质名称"
            maxlength="50"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="customDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddCustom">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Card, Loading } from '@/components'
import { useNotification } from '@/composables'
import { companyApi } from '@/api/endpoints/company'
import { Folder, Plus } from '@element-plus/icons-vue'
import QualificationCard from './QualificationCard.vue'

// Props
const props = defineProps<{
  companyId: number
  companyData: any
}>()

// Emits
const emit = defineEmits<{
  (e: 'update'): void
}>()

// Hooks
const { success, error } = useNotification()

// 状态
const loading = ref(false)
const qualificationFiles = ref<Record<string, any>>({})
const customQualifications = ref<any[]>([])
const customDialogVisible = ref(false)
const customForm = ref({ name: '' })

// 资质分类
const categories = [
  { key: 'basic', name: '基本证件资质', color: 'primary' },
  { key: 'iso', name: 'ISO体系认证', color: 'success' },
  { key: 'credit', name: '信用资质证明', color: 'info' },
  { key: 'industry', name: '行业专业资质', color: 'danger' }
]

// 标准资质类型（19种）
const standardQualifications = [
  // 基本证件 (3项)
  { key: 'business_license', name: '营业执照', icon: 'Document', category: 'basic', required: true },
  { key: 'legal_id_front', name: '法人身份证(正面)', icon: 'CreditCard', category: 'basic', required: true },
  { key: 'legal_id_back', name: '法人身份证(反面)', icon: 'CreditCard', category: 'basic', required: true },

  // ISO认证 (4项)
  { key: 'iso9001', name: 'ISO 9001质量管理体系认证', icon: 'Medal', category: 'iso' },
  { key: 'iso14001', name: 'ISO 14001环境管理体系认证', icon: 'Medal', category: 'iso' },
  { key: 'iso27001', name: 'ISO 27001信息安全管理体系认证', icon: 'Lock', category: 'iso' },
  { key: 'iso20000', name: 'ISO 20000 IT服务管理体系认证', icon: 'Monitor', category: 'iso' },

  // 信用资质 (7项)
  { key: 'dishonest_executor', name: '失信被执行人名单（信用中国）', icon: 'WarningFilled', category: 'credit' },
  { key: 'tax_violation_check', name: '重大税收违法失信主体（信用中国）', icon: 'WarningFilled', category: 'credit' },
  { key: 'gov_procurement_creditchina', name: '政府采购严重违法失信行为（信用中国）', icon: 'Flag', category: 'credit' },
  { key: 'creditchina_blacklist', name: '严重失信主体（信用中国）', icon: 'WarnTriangleFilled', category: 'credit' },
  { key: 'creditchina_credit_report', name: '信用报告（信用中国）', icon: 'DocumentChecked', category: 'credit' },
  { key: 'enterprise_credit_report', name: '国家企业信用信息公示系统信息报告', icon: 'Tickets', category: 'credit' },
  { key: 'gov_procurement_ccgp', name: '政府采购严重违法失信行为信息记录（政府采购网）', icon: 'CircleCheck', category: 'credit' },

  // 行业资质 (7项)
  { key: 'basic_telecom_permit', name: '基础电信业务许可证', icon: 'PhoneFilled', category: 'industry' },
  { key: 'value_added_telecom_permit', name: '增值电信业务许可证', icon: 'PhoneFilled', category: 'industry' },
  { key: 'software_copyright', name: '软件著作权登记证书', icon: 'Document', category: 'industry', allowMultiple: true },
  { key: 'patent_certificate', name: '专利证书', icon: 'TrophyBase', category: 'industry', allowMultiple: true },
  { key: 'high_tech', name: '高新技术企业证书', icon: 'Star', category: 'industry' },
  { key: 'software_enterprise', name: '软件企业认定证书', icon: 'Monitor', category: 'industry' },
  { key: 'cmmi', name: 'CMMI成熟度等级证书', icon: 'Trophy', category: 'industry' },
  { key: 'level_protection', name: '等保三级认证', icon: 'Lock', category: 'industry' }
]

// 根据分类获取资质列表
const getQualificationsByCategory = (categoryKey: string) => {
  return standardQualifications.filter(q => q.category === categoryKey)
}

// 加载资质文件
const loadQualifications = async () => {
  loading.value = true
  try {
    const response = await companyApi.getCompanyQualifications(props.companyId)
    if (response.success && response.data) {
      qualificationFiles.value = response.data
      console.log('加载资质文件:', qualificationFiles.value)
    }
  } catch (err) {
    console.error('加载资质文件失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loading.value = false
  }
}

// 处理文件上传（返回Promise以配合DocumentUploader）
const handleUpload = async (qualKey: string, file: File): Promise<void> => {
  // 查找资质信息
  const qual = standardQualifications.find(q => q.key === qualKey) ||
               customQualifications.value.find(q => q.key === qualKey)

  try {
    const response = await companyApi.uploadQualification(
      props.companyId,
      qualKey,
      file,
      {}
    )

    if (response.success) {
      success('上传成功', `${qual?.name || '资质文件'}上传成功`)
      await loadQualifications()
      emit('update')
    } else {
      throw new Error(response.message || '上传失败')
    }
  } catch (err) {
    console.error('上传资质文件失败:', err)
    const errorMsg = err instanceof Error ? err.message : '未知错误'
    error('上传失败', errorMsg)
    throw err  // 重新抛出错误以便DocumentUploader处理
  }
}

// 为每个资质创建上传处理函数
const createUploadHandler = (qualKey: string) => {
  return (file: File) => handleUpload(qualKey, file)
}

// 处理文件下载
const handleDownload = async (qualKey: string, qualId?: number) => {
  try {
    if (qualId) {
      // 通过ID下载（多文件资质）
      await companyApi.downloadQualification(qualId, '')
    } else {
      // 通过key下载（单文件资质）
      window.open(`/api/companies/${props.companyId}/qualifications/${qualKey}/download`)
    }
  } catch (err) {
    console.error('下载资质文件失败:', err)
    error('下载失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 处理文件删除
const handleDelete = async (qualKey: string, qualId?: number) => {
  try {
    if (!confirm('确定要删除此资质文件吗？')) {
      return
    }

    if (qualId) {
      // 通过ID删除（多文件资质）
      await companyApi.deleteQualification(qualId)
    } else {
      // 通过key删除（单文件资质）
      const response = await fetch(`/api/companies/${props.companyId}/qualifications/${qualKey}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('删除失败')
    }

    success('删除成功', '资质文件已删除')
    await loadQualifications()
    emit('update')
  } catch (err) {
    console.error('删除资质文件失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 显示添加自定义资质对话框
const showAddCustomDialog = () => {
  customForm.value.name = ''
  customDialogVisible.value = true
}

// 添加自定义资质
const handleAddCustom = () => {
  if (!customForm.value.name.trim()) {
    error('错误', '请输入资质名称')
    return
  }

  const customKey = `custom_${Date.now()}`
  customQualifications.value.push({
    key: customKey,
    name: customForm.value.name.trim(),
    icon: 'Document',
    category: 'custom'
  })

  customDialogVisible.value = false
  success('添加成功', '自定义资质已添加')
}

// 移除自定义资质
const removeCustomQualification = (index: number) => {
  if (confirm('确定要移除此自定义资质吗？')) {
    customQualifications.value.splice(index, 1)
    success('移除成功', '自定义资质已移除')
  }
}

// 生命周期
onMounted(() => {
  loadQualifications()
})
</script>

<style scoped lang="scss">
.qualification-tab {
  .qualification-category {
    margin-bottom: 32px;

    .category-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e4e7ed;
    }
  }
}
</style>
