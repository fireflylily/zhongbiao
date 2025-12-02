<template>
  <div class="basic-info-tab">
    <Card title="基础信息">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="140px"
        class="basic-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="企业名称" prop="company_name">
              <el-input v-model="formData.company_name" placeholder="请输入企业名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成立日期" prop="establish_date">
              <el-date-picker
                v-model="formData.establish_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="法定代表人" prop="legal_representative">
              <el-input v-model="formData.legal_representative" placeholder="请输入法定代表人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="法定代表人职务" prop="legal_representative_position">
              <el-input v-model="formData.legal_representative_position" placeholder="请输入职务" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="法定代表人性别" prop="legal_representative_gender">
              <el-select v-model="formData.legal_representative_gender" placeholder="请选择性别" style="width: 100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="法定代表人年龄" prop="legal_representative_age">
              <el-input-number
                v-model="formData.legal_representative_age"
                :min="18"
                :max="100"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="统一社会信用代码" prop="social_credit_code">
              <el-input v-model="formData.social_credit_code" placeholder="请输入统一社会信用代码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="注册资本" prop="registered_capital">
              <el-input v-model="formData.registered_capital" placeholder="如：1000万元" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="企业类型" prop="company_type">
              <el-input v-model="formData.company_type" placeholder="如：有限责任公司" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="注册地址" prop="registered_address">
              <el-input v-model="formData.registered_address" placeholder="请输入注册地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话" prop="fixed_phone">
              <el-input v-model="formData.fixed_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="传真" prop="fax">
              <el-input v-model="formData.fax" placeholder="请输入传真" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮政编码" prop="postal_code">
              <el-input v-model="formData.postal_code" placeholder="请输入邮政编码" maxlength="6" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入电子邮箱" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="经营范围" prop="business_scope">
              <el-input
                v-model="formData.business_scope"
                type="textarea"
                :rows="5"
                placeholder="请输入经营范围"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="企业简介" prop="description">
              <el-input
                v-model="formData.description"
                type="textarea"
                :rows="5"
                placeholder="请输入企业简介"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSave">
                <el-icon><Select /></el-icon>
                {{ isNewMode ? '创建企业' : '保存基础信息' }}
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { Card } from '@/components'
import { useNotification } from '@/composables'
import { companyApi } from '@/api/endpoints/company'
import { Select } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

// Props
const props = defineProps<{
  companyId: number
  companyData: any
  isNewMode?: boolean
}>()

// Emits
const emit = defineEmits<{
  (e: 'update'): void
  (e: 'created', companyId: number): void
}>()

// Hooks
const { success, error } = useNotification()

// 计算属性
const isNewMode = computed(() => props.isNewMode || false)

// 状态
const formRef = ref<FormInstance>()
const saving = ref(false)
const formData = ref({
  company_name: '',
  establish_date: '',
  legal_representative: '',
  legal_representative_position: '',
  legal_representative_gender: '',
  legal_representative_age: undefined as number | undefined,
  social_credit_code: '',
  registered_capital: '',
  company_type: '',
  registered_address: '',
  fixed_phone: '',
  fax: '',
  postal_code: '',
  email: '',
  business_scope: '',
  description: ''
})

// 表单验证规则
const formRules: FormRules = {
  company_name: [
    { required: true, message: '请输入企业名称', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  postal_code: [
    { pattern: /^\d{6}$/, message: '邮政编码必须是6位数字', trigger: 'blur' }
  ]
}

// 监听companyData变化，更新表单数据
watch(
  () => props.companyData,
  (newData) => {
    if (newData) {
      formData.value = {
        company_name: newData.company_name || '',
        establish_date: newData.establish_date || '',
        legal_representative: newData.legal_representative || '',
        legal_representative_position: newData.legal_representative_position || '',
        legal_representative_gender: newData.legal_representative_gender || '',
        legal_representative_age: newData.legal_representative_age || undefined,
        social_credit_code: newData.social_credit_code || '',
        registered_capital: newData.registered_capital || '',
        company_type: newData.company_type || '',
        registered_address: newData.registered_address || '',
        fixed_phone: newData.fixed_phone || '',
        fax: newData.fax || '',
        postal_code: newData.postal_code || '',
        email: newData.email || '',
        business_scope: newData.business_scope || '',
        description: newData.description || ''
      }
    }
  },
  { immediate: true, deep: true }
)

// 保存
const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      if (isNewMode.value) {
        // 新建模式 - 调用创建API
        const response = await companyApi.createCompany({
          companyName: formData.value.company_name,
          // 其他字段根据API要求传递
          registeredAddress: formData.value.registered_address,
          fixedPhone: formData.value.fixed_phone,
          email: formData.value.email,
          companyDescription: formData.value.description
        })

        if (response.success && response.data) {
          success('创建成功', '企业创建成功')
          // 触发created事件，传递新创建的企业ID
          emit('created', response.data.company_id)
        }
      } else {
        // 编辑模式 - 调用更新API
        const response = await companyApi.updateCompany(props.companyId, {
          companyName: formData.value.company_name,
          establishDate: formData.value.establish_date,
          legalRepresentative: formData.value.legal_representative,
          legalRepresentativePosition: formData.value.legal_representative_position,
          legalRepresentativeGender: formData.value.legal_representative_gender,
          legalRepresentativeAge: formData.value.legal_representative_age,
          socialCreditCode: formData.value.social_credit_code,
          registeredCapital: formData.value.registered_capital,
          companyType: formData.value.company_type,
          registeredAddress: formData.value.registered_address,
          fixedPhone: formData.value.fixed_phone,
          fax: formData.value.fax,
          postalCode: formData.value.postal_code,
          email: formData.value.email,
          businessScope: formData.value.business_scope,
          companyDescription: formData.value.description
        })

        if (response.success) {
          success('保存成功', '基础信息已更新')
          emit('update')
        }
      }
    } catch (err) {
      console.error(isNewMode.value ? '创建企业失败:' : '保存基础信息失败:', err)
      error(isNewMode.value ? '创建失败' : '保存失败', err instanceof Error ? err.message : '未知错误')
    } finally {
      saving.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.basic-info-tab {
  .basic-form {
    // 移除 max-width 限制，让表单占满整个容器宽度
  }
}
</style>
