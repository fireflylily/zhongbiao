<template>
  <div class="resume-library">
    <!-- 统计信息 -->
    <div class="stats-bar">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#409eff"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">总简历数</div>
            <div class="stat-value">{{ allResumes.length }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#67c23a"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">活跃简历</div>
            <div class="stat-value">{{ activeResumesCount }}</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="32" color="#e6a23c"><TrophyBase /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">平均工龄</div>
            <div class="stat-value">{{ averageWorkYears }}年</div>
          </div>
        </div>
      </el-card>
    </div>

    <Card title="简历列表">
      <template #actions>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建简历
        </el-button>
        <el-button type="success" @click="handleUploadResume">
          <el-icon><Upload /></el-icon>
          智能导入
        </el-button>
      </template>

      <!-- 搜索和筛选区域 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filters">
          <el-form-item label="搜索">
            <el-input
              v-model="filters.keyword"
              placeholder="搜索姓名、职位、技能..."
              clearable
              style="width: 300px"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="学历">
            <el-select
              v-model="filters.educationLevel"
              placeholder="全部学历"
              clearable
              style="width: 120px"
              @change="handleSearch"
            >
              <el-option label="全部学历" value="" />
              <el-option label="博士" value="博士" />
              <el-option label="硕士" value="硕士" />
              <el-option label="本科" value="本科" />
              <el-option label="大专" value="大专" />
              <el-option label="高中" value="高中" />
            </el-select>
          </el-form-item>
          <el-form-item label="职位">
            <el-input
              v-model="filters.position"
              placeholder="职位关键词"
              clearable
              style="width: 150px"
              @input="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="filters.status"
              placeholder="全部状态"
              clearable
              style="width: 120px"
              @change="handleSearch"
            >
              <el-option label="全部状态" value="" />
              <el-option label="活跃" value="active" />
              <el-option label="离职" value="inactive" />
              <el-option label="已归档" value="archived" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="handleResetFilters">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <Loading v-if="loading" text="加载中..." />
      <Empty v-else-if="!filteredResumes.length" type="no-data" description="暂无简历数据" />
      <el-table v-else :data="filteredResumes" stripe style="width: 100%">
        <el-table-column prop="resume_id" label="ID" width="70" fixed />
        <el-table-column prop="name" label="姓名" width="100" fixed />
        <el-table-column prop="gender" label="性别" width="60" align="center">
          <template #default="{ row }">
            {{ row.gender || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="education_level" label="学历" width="80">
          <template #default="{ row }">
            <el-tag :type="getEducationTagType(row.education_level)" size="small">
              {{ row.education_level || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="university" label="毕业院校" width="140" show-overflow-tooltip />
        <el-table-column prop="major" label="专业" width="120" show-overflow-tooltip />
        <el-table-column prop="current_position" label="当前职位" width="140" show-overflow-tooltip />
        <el-table-column prop="professional_title" label="职称" width="100" />
        <el-table-column prop="work_years" label="工作年限" width="90" align="center">
          <template #default="{ row }">
            {{ row.work_years ? `${row.work_years}年` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="current_company" label="当前单位" width="160" show-overflow-tooltip />
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" show-overflow-tooltip />

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="handleView(row)">
              查看详情
            </el-button>
            <el-button text type="warning" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </Card>

    <!-- 新建简历对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建简历"
      width="700px"
      @close="handleDialogClose"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="120px"
      >
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="createForm.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="createForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="createForm.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="createForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">教育信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历" prop="education_level">
              <el-select v-model="createForm.education_level" placeholder="请选择学历" style="width: 100%">
                <el-option label="博士" value="博士" />
                <el-option label="硕士" value="硕士" />
                <el-option label="本科" value="本科" />
                <el-option label="大专" value="大专" />
                <el-option label="高中" value="高中" />
                <el-option label="中专" value="中专" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学位" prop="degree">
              <el-select v-model="createForm.degree" placeholder="请选择学位" style="width: 100%">
                <el-option label="博士学位" value="博士" />
                <el-option label="硕士学位" value="硕士" />
                <el-option label="学士学位" value="学士" />
                <el-option label="无学位" value="无" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="毕业院校" prop="university">
              <el-input v-model="createForm.university" placeholder="请输入毕业院校" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-input v-model="createForm.major" placeholder="请输入专业" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">工作信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="当前职位" prop="current_position">
              <el-input v-model="createForm.current_position" placeholder="如：项目经理" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="professional_title">
              <el-input v-model="createForm.professional_title" placeholder="如：高级工程师" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工作年限" prop="work_years">
              <el-input-number
                v-model="createForm.work_years"
                :min="0"
                :max="50"
                placeholder="年"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="当前单位" prop="current_company">
              <el-input v-model="createForm.current_company" placeholder="请输入当前工作单位" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="个人简介" prop="introduction">
          <el-input
            v-model="createForm.introduction"
            type="textarea"
            :rows="3"
            placeholder="请简要介绍个人经历、专长等"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleConfirmCreate">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 智能导入简历对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="智能导入简历"
      width="500px"
      @close="handleUploadDialogClose"
    >
      <el-alert
        title="智能解析"
        type="info"
        description="上传PDF/DOC/DOCX格式的简历文件，系统将自动提取信息并创建简历记录"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-upload
        ref="uploadRef"
        v-model:file-list="uploadFileList"
        :auto-upload="false"
        :limit="1"
        accept=".pdf,.doc,.docx"
        drag
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到这里 或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持PDF、DOC、DOCX格式，文件大小不超过10MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="parsing" @click="handleConfirmUpload">
          开始解析
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, Loading, Empty } from '@/components'
import { useNotification } from '@/composables'
import { knowledgeApi } from '@/api/endpoints/knowledge'
import { formatDate } from '@/utils/formatters'
import { validatePhone, validateEmail } from '@/utils/validators'
import {
  User,
  CircleCheck,
  TrophyBase,
  Plus,
  Upload,
  UploadFilled,
  Search,
  RefreshLeft
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadInstance, UploadFile } from 'element-plus'
import type { Resume } from '@/types'

// Router
const router = useRouter()

// Hooks
const { success, error } = useNotification()

// 状态
const loading = ref(false)
const allResumes = ref<Resume[]>([])
const filters = ref({
  keyword: '',
  educationLevel: '',
  position: '',
  status: ''
})

// 新建简历相关
const createDialogVisible = ref(false)
const creating = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = ref({
  name: '',
  gender: '',
  phone: '',
  email: '',
  education_level: '',
  degree: '',
  university: '',
  major: '',
  current_position: '',
  professional_title: '',
  work_years: undefined as number | undefined,
  current_company: '',
  introduction: ''
})

const createFormRules: FormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' }
  ]
}

// 智能导入相关
const uploadDialogVisible = ref(false)
const parsing = ref(false)
const uploadRef = ref<UploadInstance>()
const uploadFileList = ref<UploadFile[]>([])
const currentUploadFile = ref<File | null>(null)

// 计算属性
const filteredResumes = computed(() => {
  let result = [...allResumes.value]

  // 关键词搜索
  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    result = result.filter((r) => {
      return (
        r.name?.toLowerCase().includes(keyword) ||
        r.current_position?.toLowerCase().includes(keyword) ||
        r.skills?.toLowerCase().includes(keyword) ||
        r.major?.toLowerCase().includes(keyword)
      )
    })
  }

  // 学历筛选
  if (filters.value.educationLevel) {
    result = result.filter((r) => r.education_level === filters.value.educationLevel)
  }

  // 职位筛选
  if (filters.value.position) {
    const position = filters.value.position.toLowerCase()
    result = result.filter((r) => r.current_position?.toLowerCase().includes(position))
  }

  // 状态筛选
  if (filters.value.status) {
    result = result.filter((r) => r.status === filters.value.status)
  }

  return result
})

const activeResumesCount = computed(() => {
  return allResumes.value.filter(r => r.status === 'active').length
})

const averageWorkYears = computed(() => {
  const resumes = allResumes.value.filter(r => r.work_years && r.work_years > 0)
  if (resumes.length === 0) return 0
  const total = resumes.reduce((sum, r) => sum + (r.work_years || 0), 0)
  return (total / resumes.length).toFixed(1)
})

// 方法
const loadResumes = async () => {
  loading.value = true
  try {
    const response = await knowledgeApi.getResumes()
    if (response.success && response.data) {
      // 后端返回的是 { resumes: [], total: n } 格式
      const resumeList = response.data.resumes || response.data
      allResumes.value = resumeList.map((r: any) => ({
        ...r,
        created_at: r.created_at ? formatDate(r.created_at) : '-',
        updated_at: r.updated_at ? formatDate(r.updated_at) : '-'
      }))
    }
  } catch (err) {
    console.error('加载简历列表失败:', err)
    error('加载失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  // 筛选逻辑由 computed 自动处理
}

// 重置筛选
const handleResetFilters = () => {
  filters.value.keyword = ''
  filters.value.educationLevel = ''
  filters.value.position = ''
  filters.value.status = ''
}

// 学历标签类型
const getEducationTagType = (education: string | undefined) => {
  if (!education) return 'info'
  if (education === '博士') return 'danger'
  if (education === '硕士') return 'warning'
  if (education === '本科') return 'success'
  return 'info'
}

// 状态标签类型
const getStatusTagType = (status: string | undefined) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'warning'
    case 'archived': return 'info'
    default: return 'info'
  }
}

// 状态标签文本
const getStatusLabel = (status: string | undefined) => {
  switch (status) {
    case 'active': return '活跃'
    case 'inactive': return '离职'
    case 'archived': return '已归档'
    default: return '-'
  }
}

// 新建简历
const handleCreate = () => {
  createDialogVisible.value = true
}

// 确认创建简历
const handleConfirmCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    creating.value = true
    try {
      const response = await knowledgeApi.createResume({
        name: createForm.value.name,
        gender: createForm.value.gender || undefined,
        phone: createForm.value.phone || undefined,
        email: createForm.value.email || undefined,
        education_level: createForm.value.education_level || undefined,
        degree: createForm.value.degree || undefined,
        university: createForm.value.university || undefined,
        major: createForm.value.major || undefined,
        current_position: createForm.value.current_position || undefined,
        professional_title: createForm.value.professional_title || undefined,
        work_years: createForm.value.work_years,
        current_company: createForm.value.current_company || undefined,
        introduction: createForm.value.introduction || undefined,
        status: 'active'
      })

      if (response.success) {
        success('创建成功', '简历创建成功')
        createDialogVisible.value = false
        await loadResumes()
      } else {
        error('创建失败', response.error || '未知错误')
      }
    } catch (err) {
      console.error('创建简历失败:', err)
      error('创建失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      creating.value = false
    }
  })
}

// 智能导入简历
const handleUploadResume = () => {
  uploadDialogVisible.value = true
}

// 文件变化处理
const handleFileChange = (uploadFile: UploadFile) => {
  console.log('文件变化:', uploadFile)
  if (uploadFile.raw) {
    // 验证文件大小（10MB限制）
    const maxSize = 10 * 1024 * 1024
    if (uploadFile.raw.size > maxSize) {
      error('文件过大', '文件大小不能超过10MB')
      uploadFileList.value = []
      currentUploadFile.value = null
      return
    }
    currentUploadFile.value = uploadFile.raw
  }
}

// 文件移除处理
const handleFileRemove = () => {
  currentUploadFile.value = null
}

// 确认上传并解析
const handleConfirmUpload = async () => {
  // 验证是否有文件
  if (!currentUploadFile.value) {
    error('请选择文件', '请先选择要上传的简历文件')
    return
  }

  parsing.value = true
  try {
    const response = await knowledgeApi.parseResumeFile(currentUploadFile.value, true)
    if (response.success) {
      success('导入成功', '简历已自动解析并创建')
      uploadDialogVisible.value = false
      await loadResumes()
    } else {
      error('导入失败', response.error || '解析失败')
    }
  } catch (err) {
    console.error('智能导入失败:', err)
    error('导入失败', err instanceof Error ? err.message : '未知错误')
  } finally {
    parsing.value = false
  }
}

// 关闭上传对话框
const handleUploadDialogClose = () => {
  uploadFileList.value = []
  currentUploadFile.value = null
}

// 关闭对话框
const handleDialogClose = () => {
  createForm.value = {
    name: '',
    gender: '',
    phone: '',
    email: '',
    education_level: '',
    degree: '',
    university: '',
    major: '',
    current_position: '',
    professional_title: '',
    work_years: undefined,
    current_company: '',
    introduction: ''
  }
  createFormRef.value?.resetFields()
}

// 查看详情
const handleView = (row: Resume) => {
  // TODO: 跳转到详情页
  router.push(`/knowledge/resume/${row.resume_id}`)
}

// 编辑简历
const handleEdit = (row: Resume) => {
  // TODO: 跳转到编辑页（与详情页相同）
  router.push(`/knowledge/resume/${row.resume_id}`)
}

// 删除简历
const handleDelete = async (row: Resume) => {
  try {
    // 确认删除
    if (!confirm(`确定要删除简历 "${row.name}" 吗？此操作不可恢复。`)) {
      return
    }

    const response = await knowledgeApi.deleteResume(row.resume_id)
    if (response.success) {
      success('删除成功', `已删除简历: ${row.name}`)
      await loadResumes()
    } else {
      error('删除失败', response.error || '未知错误')
    }
  } catch (err) {
    console.error('删除简历失败:', err)
    error('删除失败', err instanceof Error ? err.message : '未知错误')
  }
}

// 生命周期
onMounted(() => {
  loadResumes()
})
</script>

<style scoped lang="scss">
.resume-library {
  // 移除padding，避免与page-content的padding叠加
}

.stats-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;

  .stat-card {
    flex: 1;
    cursor: default;

    :deep(.el-card__body) {
      padding: 16px;
    }

    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .stat-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        background: #f0f9ff;
        border-radius: 12px;
      }

      .stat-info {
        flex: 1;

        .stat-label {
          font-size: 14px;
          color: #909399;
          margin-bottom: 4px;
        }

        .stat-value {
          font-size: 28px;
          font-weight: bold;
          color: #303133;
        }
      }
    }
  }
}

.filter-section {
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;

  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}
</style>
