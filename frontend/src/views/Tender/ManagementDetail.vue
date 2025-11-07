<template>
  <div class="tender-management-detail">
    <!-- 页面头部 -->
    <PageHeader :title="pageTitle" :show-back="true">
      <template #actions>
        <template v-if="!isEditing">
          <el-button @click="handleRefresh">
            <i class="bi bi-arrow-clockwise"></i> 刷新
          </el-button>
          <el-button type="primary" @click="handleEdit">
            <i class="bi bi-pencil"></i> 编辑项目
          </el-button>
        </template>
        <template v-else>
          <el-button @click="handleCancel">
            <i class="bi bi-x-lg"></i> 取消
          </el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">
            <i class="bi bi-check-lg"></i> 保存
          </el-button>
        </template>
      </template>
    </PageHeader>

    <!-- 加载状态 -->
    <Loading v-if="loading" text="加载项目详情..." />

    <!-- 项目详情 -->
    <template v-else-if="projectDetail">
      <!-- 招标文档处理（页面上方总览） -->
      <TenderDocumentProcessor
        :project-id="projectId"
        :company-id="projectDetail.company_id"
        :project-detail="projectDetail"
        @success="handleProcessSuccess"
        @refresh="loadProjectDetail"
        @task-id-update="handleTaskIdUpdate"
        @preview="handlePreview"
      />

      <!-- Tab 导航 -->
      <el-card class="tabs-card" shadow="never">
        <el-tabs v-model="activeTab" class="detail-tabs">
          <!-- ==================== Tab 1: 基本信息 ==================== -->
          <el-tab-pane name="basic">
            <template #label>
              <span class="tab-label">
                <i class="bi bi-info-circle"></i> 基本信息
              </span>
            </template>

            <div class="tab-content">
              <!-- 项目基本信息 -->
              <section class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-folder"></i> 项目基本信息</h3>
                  <el-tag :type="getStatusType(projectDetail.status)">
                    {{ getStatusText(projectDetail.status) }}
                  </el-tag>
                </div>

                <!-- 编辑模式 -->
                <el-form v-if="isEditing" :model="formData" :rules="formRules" label-width="120px" class="edit-form">
                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item label="项目名称" prop="name">
                        <el-input v-model="formData.name" placeholder="请输入项目名称" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="项目编号" prop="number">
                        <el-input v-model="formData.number" placeholder="请输入项目编号" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="公司名称" prop="company_id">
                        <el-select v-model="formData.company_id" placeholder="请选择公司" style="width: 100%">
                          <el-option
                            v-for="company in companies"
                            :key="company.company_id"
                            :label="company.name"
                            :value="company.company_id"
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="被授权人">
                        <el-input v-model="formData.authorized_person_name" placeholder="请输入被授权人姓名" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="授权人身份证">
                        <el-input v-model="formData.authorized_person_id" placeholder="请输入身份证号" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="24">
                      <el-form-item label="项目描述">
                        <el-input
                          v-model="formData.description"
                          type="textarea"
                          :rows="4"
                          placeholder="请输入项目描述"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>

                <!-- 查看模式 -->
                <el-descriptions v-else :column="2" border size="large">
                  <el-descriptions-item label="项目名称" :span="2">
                    <strong>{{ projectDetail.name }}</strong>
                  </el-descriptions-item>
                  <el-descriptions-item label="项目编号">
                    {{ projectDetail.number || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="公司名称">
                    {{ projectDetail.company_name }}
                  </el-descriptions-item>
                  <el-descriptions-item label="创建时间">
                    {{ projectDetail.created_at }}
                  </el-descriptions-item>
                  <el-descriptions-item label="最后更新">
                    {{ projectDetail.updated_at || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="被授权人">
                    {{ projectDetail.authorized_person_name || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="授权人身份证">
                    {{ projectDetail.authorized_person_id || '-' }}
                  </el-descriptions-item>
                </el-descriptions>
              </section>

              <!-- 招标信息 -->
              <section class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-megaphone"></i> 招标信息</h3>
                  <el-button
                    size="small"
                    type="primary"
                    :loading="extractingBasicInfo"
                    :disabled="!latestTaskId"
                    @click="handleExtractBasicInfo"
                  >
                    <i v-if="!extractingBasicInfo" class="bi bi-magic me-1"></i>
                    {{ extractingBasicInfo ? 'AI提取中...' : 'AI提取基本信息' }}
                  </el-button>
                </div>

                <!-- 编辑模式 -->
                <el-form v-if="isEditing" :model="formData" label-width="120px" class="edit-form">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="招标单位">
                        <el-input v-model="formData.tender_unit" placeholder="请输入招标单位" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="招标代理">
                        <el-input v-model="formData.tender_agency" placeholder="请输入招标代理" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="预算金额">
                        <el-input-number
                          v-model="formData.budget_amount"
                          :controls="false"
                          :precision="2"
                          placeholder="请输入预算金额"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="项目类型">
                        <el-input v-model="formData.project_type" placeholder="请输入项目类型" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="报名截止时间">
                        <el-date-picker
                          v-model="formData.registration_deadline"
                          type="datetime"
                          placeholder="选择报名截止时间"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="投标截止时间">
                        <el-date-picker
                          v-model="formData.bid_deadline"
                          type="datetime"
                          placeholder="选择投标截止时间"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="开标时间">
                        <el-date-picker
                          v-model="formData.bid_opening_time"
                          type="datetime"
                          placeholder="选择开标时间"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="开标地点">
                        <el-input v-model="formData.bid_opening_location" placeholder="请输入开标地点" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>

                <!-- 查看模式 -->
                <el-descriptions v-else :column="2" border size="large">
                  <el-descriptions-item label="招标单位">
                    {{ projectDetail.tender_unit || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="招标代理">
                    {{ projectDetail.tender_agency || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="预算金额">
                    <span v-if="projectDetail.budget_amount" class="amount">
                      ¥ {{ formatAmount(projectDetail.budget_amount) }}
                    </span>
                    <span v-else>-</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="项目类型">
                    {{ projectDetail.project_type || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="报名截止时间">
                    <span v-if="projectDetail.registration_deadline" class="deadline">
                      <i class="bi bi-calendar-event"></i>
                      {{ projectDetail.registration_deadline }}
                    </span>
                    <span v-else>-</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="投标截止时间">
                    <span v-if="projectDetail.bid_deadline" class="deadline">
                      <i class="bi bi-calendar-event"></i>
                      {{ projectDetail.bid_deadline }}
                    </span>
                    <span v-else>-</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="开标时间">
                    <span v-if="projectDetail.bid_opening_time" class="deadline">
                      <i class="bi bi-calendar-event"></i>
                      {{ projectDetail.bid_opening_time }}
                    </span>
                    <span v-else>-</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="开标地点">
                    {{ projectDetail.bid_opening_location || '-' }}
                  </el-descriptions-item>
                </el-descriptions>
              </section>

              <!-- 联系人信息 -->
              <section class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-person-lines-fill"></i> 联系人信息</h3>
                </div>

                <!-- 编辑模式 -->
                <el-form v-if="isEditing" :model="formData" label-width="120px" class="edit-form">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="项目经理">
                        <el-input v-model="formData.project_manager_name" placeholder="请输入项目经理姓名" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="联系电话">
                        <el-input v-model="formData.project_manager_phone" placeholder="请输入联系电话" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="技术负责人">
                        <el-input v-model="formData.tech_lead_name" placeholder="请输入技术负责人姓名" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="联系电话">
                        <el-input v-model="formData.tech_lead_phone" placeholder="请输入联系电话" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="商务联系人">
                        <el-input v-model="formData.business_contact_name" placeholder="请输入商务联系人姓名" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="联系电话">
                        <el-input v-model="formData.business_contact_phone" placeholder="请输入联系电话" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>

                <!-- 查看模式 -->
                <el-descriptions v-else :column="2" border size="large">
                  <el-descriptions-item label="项目经理">
                    {{ projectDetail.project_manager_name || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="联系电话">
                    {{ projectDetail.project_manager_phone || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="技术负责人">
                    {{ projectDetail.tech_lead_name || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="联系电话">
                    {{ projectDetail.tech_lead_phone || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="商务联系人">
                    {{ projectDetail.business_contact_name || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="联系电话">
                    {{ projectDetail.business_contact_phone || '-' }}
                  </el-descriptions-item>
                </el-descriptions>
              </section>
            </div>
          </el-tab-pane>

          <!-- ==================== Tab 2: 资格要求 ==================== -->
          <el-tab-pane name="qualifications">
            <template #label>
              <span class="tab-label">
                <i class="bi bi-award"></i> 资格要求
              </span>
            </template>

            <div class="tab-content">
              <!-- 资质要求 -->
              <section class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-patch-check"></i> 资质要求</h3>
                  <el-button
                    size="small"
                    type="primary"
                    :loading="extractingQualifications"
                    :disabled="!latestTaskId"
                    @click="handleExtractQualifications"
                  >
                    <i v-if="!extractingQualifications" class="bi bi-magic me-1"></i>
                    {{ extractingQualifications ? 'AI提取中...' : 'AI提取资格要求' }}
                  </el-button>
                </div>
                <div v-if="qualifications.certifications.length > 0" class="requirements-list">
                  <el-card
                    v-for="(cert, index) in qualifications.certifications"
                    :key="index"
                    shadow="never"
                    class="requirement-item"
                  >
                    <div class="requirement-content">
                      <div class="requirement-icon">
                        <i class="bi bi-shield-check"></i>
                      </div>
                      <div class="requirement-text">
                        <h4>{{ getQualificationDisplayName(cert.name) }}</h4>
                        <p v-if="cert.level">等级要求: {{ cert.level }}</p>
                        <p v-if="cert.note">{{ cert.note }}</p>
                      </div>
                      <div class="requirement-status">
                        <el-tag v-if="cert.required" type="danger" size="small">
                          必需
                        </el-tag>
                        <el-tag v-else type="info" size="small">可选</el-tag>
                      </div>
                    </div>
                  </el-card>
                </div>
                <el-empty v-else description="暂无资质要求" :image-size="80" />
              </section>

              <!-- 业绩要求 -->
              <section class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-graph-up-arrow"></i> 业绩要求</h3>
                </div>
                <div v-if="qualifications.performance.length > 0" class="requirements-list">
                  <el-card
                    v-for="(perf, index) in qualifications.performance"
                    :key="index"
                    shadow="never"
                    class="requirement-item"
                  >
                    <div class="requirement-content">
                      <div class="requirement-icon">
                        <i class="bi bi-briefcase"></i>
                      </div>
                      <div class="requirement-text">
                        <h4>{{ perf.description }}</h4>
                        <p v-if="perf.amount">金额要求: ≥ ¥{{ formatAmount(perf.amount) }}</p>
                        <p v-if="perf.time_range">时间范围: {{ perf.time_range }}</p>
                        <p v-if="perf.count">数量要求: {{ perf.count }} 个</p>
                      </div>
                      <div class="requirement-status">
                        <el-tag v-if="perf.required" type="danger" size="small">
                          必需
                        </el-tag>
                        <el-tag v-else type="info" size="small">可选</el-tag>
                      </div>
                    </div>
                  </el-card>
                </div>
                <el-empty v-else description="暂无业绩要求" :image-size="80" />
              </section>

              <!-- 人员配置要求 -->
              <section class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-people"></i> 人员配置要求</h3>
                </div>
                <div v-if="qualifications.personnel.length > 0" class="requirements-list">
                  <el-card
                    v-for="(person, index) in qualifications.personnel"
                    :key="index"
                    shadow="never"
                    class="requirement-item"
                  >
                    <div class="requirement-content">
                      <div class="requirement-icon">
                        <i class="bi bi-person-badge"></i>
                      </div>
                      <div class="requirement-text">
                        <h4>{{ person.position }}</h4>
                        <p v-if="person.count">人数: {{ person.count }} 人</p>
                        <p v-if="person.qualification">资格要求: {{ person.qualification }}</p>
                        <p v-if="person.experience">经验要求: {{ person.experience }}</p>
                      </div>
                      <div class="requirement-status">
                        <el-tag v-if="person.required" type="danger" size="small">
                          必需
                        </el-tag>
                        <el-tag v-else type="info" size="small">可选</el-tag>
                      </div>
                    </div>
                  </el-card>
                </div>
                <el-empty v-else description="暂无人员配置要求" :image-size="80" />
              </section>

              <!-- 财务要求 -->
              <section class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-cash-stack"></i> 财务要求</h3>
                </div>
                <div v-if="qualifications.financial" class="financial-requirements">
                  <el-card shadow="never" class="requirement-item">
                    <div class="requirement-content">
                      <div class="requirement-icon">
                        <i class="bi bi-cash-stack"></i>
                      </div>
                      <div class="requirement-text">
                        <h4>财务相关要求</h4>
                        <p>{{ qualifications.financial.description }}</p>
                      </div>
                    </div>
                  </el-card>
                </div>
                <el-empty v-else description="暂无财务要求" :image-size="80" />
              </section>
            </div>
          </el-tab-pane>

          <!-- ==================== Tab 3: 商务应答 ==================== -->
          <el-tab-pane name="business">
            <template #label>
              <span class="tab-label">
                <i class="bi bi-briefcase"></i> 商务应答
                <el-badge
                  v-if="projectDetail.step1_data?.business_response_file"
                  is-dot
                  type="success"
                />
              </span>
            </template>

            <div class="tab-content">
              <!-- 应答文件模板 -->
              <section class="file-section">
                <div class="section-header">
                  <h3><i class="bi bi-file-earmark-text"></i> 应答文件模板</h3>
                  <el-tag type="info" size="small">AI 自动提取</el-tag>
                </div>
                <FileCard
                  v-if="responseFileInfo"
                  :file-url="responseFileInfo.fileUrl"
                  :file-name="responseFileInfo.fileName"
                  :file-size="responseFileInfo.fileSize"
                  :show-actions="true"
                  @preview="handlePreview"
                />
                <el-empty v-else description="暂未提取到应答文件模板" :image-size="80">
                  <template #extra>
                    <el-text type="info" size="small">
                      请先上传招标文件并进行 AI 解析
                    </el-text>
                  </template>
                </el-empty>
              </section>

              <el-divider />

              <!-- 商务应答完成文件 -->
              <section class="file-section">
                <div class="section-header">
                  <h3><i class="bi bi-file-earmark-check"></i> 商务应答完成文件</h3>
                  <el-tag
                    v-if="businessResponseFileInfo"
                    type="success"
                    size="small"
                  >
                    <i class="bi bi-check-circle-fill"></i> 已生成
                  </el-tag>
                  <el-tag v-else type="info" size="small">未生成</el-tag>
                </div>
                <FileCard
                  v-if="businessResponseFileInfo"
                  :file-url="businessResponseFileInfo.fileUrl"
                  :file-name="businessResponseFileInfo.fileName"
                  :file-size="businessResponseFileInfo.fileSize"
                  :show-actions="true"
                  type="success"
                  @preview="handlePreview"
                />
                <el-empty v-else description="暂未生成商务应答文件" :image-size="80">
                  <template #extra>
                    <el-text type="info" size="small">
                      点击下方按钮开始生成商务应答
                    </el-text>
                  </template>
                </el-empty>
              </section>

              <!-- 操作按钮 -->
              <div class="action-area">
                <el-button
                  type="primary"
                  size="large"
                  :disabled="!responseFileInfo"
                  @click="handleStartBusiness"
                >
                  <i class="bi bi-rocket-takeoff"></i>
                  {{ businessResponseFileInfo ? '重新生成' : '开始' }}商务应答
                </el-button>
                <el-text v-if="!responseFileInfo" type="warning" size="small">
                  <i class="bi bi-exclamation-triangle"></i>
                  请先上传招标文件并进行 AI 解析
                </el-text>
              </div>
            </div>
          </el-tab-pane>

          <!-- ==================== Tab 4: 文档与章节 ==================== -->
          <el-tab-pane name="documents">
            <template #label>
              <span class="tab-label">
                <i class="bi bi-files"></i> 文档与章节
                <el-badge
                  v-if="projectDocuments.length > 0 || parsedChapters.length > 0"
                  :value="projectDocuments.length"
                  type="success"
                />
              </span>
            </template>

            <div class="tab-content">
              <!-- 文档列表 -->
              <section class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-file-earmark-text"></i> 项目文档</h3>
                  <el-tag v-if="projectDocuments.length > 0" type="success" size="small">
                    共 {{ projectDocuments.length }} 个文件
                  </el-tag>
                </div>

                <div v-if="projectDocuments.length > 0" class="documents-grid">
                  <FileCard
                    v-for="doc in projectDocuments"
                    :key="doc.id"
                    :file-url="doc.file_url || doc.file_path"
                    :file-name="doc.original_filename"
                    :file-size="doc.file_size"
                    :upload-time="doc.uploaded_at"
                    :show-actions="true"
                    @preview="handlePreview"
                  />
                </div>
                <el-empty v-else description="暂无文档" :image-size="80">
                  <template #extra>
                    <el-text type="info" size="small">
                      请在页面顶部上传招标文档
                    </el-text>
                  </template>
                </el-empty>
              </section>

              <el-divider v-if="parsedChapters.length > 0" />

              <!-- 已识别章节 -->
              <section v-if="parsedChapters.length > 0" class="info-section">
                <div class="section-header">
                  <h3><i class="bi bi-list-nested"></i> 已识别章节</h3>
                  <el-tag type="success" size="small">
                    共 {{ totalParsedChapters }} 个章节
                  </el-tag>
                </div>

                <ChapterTree
                  :chapters="parsedChapters"
                  :show-checkbox="false"
                  :show-search="true"
                />
              </section>
            </div>
          </el-tab-pane>

          <!-- ==================== Tab 5: 技术需求 ==================== -->
          <el-tab-pane name="technical">
            <template #label>
              <span class="tab-label">
                <i class="bi bi-cpu"></i> 技术需求
                <el-badge
                  v-if="projectDetail.step1_data?.technical_point_to_point_file ||
                        projectDetail.step1_data?.technical_proposal_file"
                  is-dot
                  type="success"
                />
              </span>
            </template>

            <div class="tab-content">
              <!-- 技术需求文件 -->
              <section class="file-section">
                <div class="section-header">
                  <h3><i class="bi bi-file-earmark-text"></i> 技术需求文件</h3>
                  <el-tag type="info" size="small">AI 自动提取</el-tag>
                </div>
                <FileCard
                  v-if="technicalFileInfo"
                  :file-url="technicalFileInfo.fileUrl"
                  :file-name="technicalFileInfo.fileName"
                  :file-size="technicalFileInfo.fileSize"
                  :show-actions="true"
                  @preview="handlePreview"
                />
                <el-empty v-else description="暂未提取到技术需求文件" :image-size="80" />
              </section>

              <el-divider />

              <!-- 点对点应答完成文件 -->
              <section class="file-section">
                <div class="section-header">
                  <h3><i class="bi bi-arrow-left-right"></i> 点对点应答完成文件</h3>
                  <el-tag
                    v-if="technicalP2PFileInfo"
                    type="success"
                    size="small"
                  >
                    <i class="bi bi-check-circle-fill"></i> 已生成
                  </el-tag>
                  <el-tag v-else type="info" size="small">未生成</el-tag>
                </div>
                <FileCard
                  v-if="technicalP2PFileInfo"
                  :file-url="technicalP2PFileInfo.fileUrl"
                  :file-name="technicalP2PFileInfo.fileName"
                  :file-size="technicalP2PFileInfo.fileSize"
                  :show-actions="true"
                  type="success"
                  @preview="handlePreview"
                />
                <el-empty v-else description="暂未生成点对点应答文件" :image-size="80" />
              </section>

              <el-divider />

              <!-- 技术方案完成文件 -->
              <section class="file-section">
                <div class="section-header">
                  <h3><i class="bi bi-file-code"></i> 技术方案完成文件</h3>
                  <el-tag
                    v-if="technicalProposalFileInfo"
                    type="success"
                    size="small"
                  >
                    <i class="bi bi-check-circle-fill"></i> 已生成
                  </el-tag>
                  <el-tag v-else type="info" size="small">未生成</el-tag>
                </div>
                <FileCard
                  v-if="technicalProposalFileInfo"
                  :file-url="technicalProposalFileInfo.fileUrl"
                  :file-name="technicalProposalFileInfo.fileName"
                  :file-size="technicalProposalFileInfo.fileSize"
                  :show-actions="true"
                  type="success"
                  @preview="handlePreview"
                />
                <el-empty v-else description="暂未生成技术方案文件" :image-size="80" />
              </section>

              <!-- 操作按钮 -->
              <div class="action-area">
                <el-space :size="16">
                  <el-button
                    type="primary"
                    size="large"
                    :disabled="!technicalFileInfo"
                    @click="handleStartPointToPoint"
                  >
                    <i class="bi bi-arrow-left-right"></i>
                    {{ technicalP2PFileInfo ? '重新生成' : '开始' }}点对点应答
                  </el-button>
                  <el-button
                    type="primary"
                    size="large"
                    :disabled="!technicalFileInfo"
                    @click="handleStartProposal"
                  >
                    <i class="bi bi-file-code"></i>
                    {{ technicalProposalFileInfo ? '重新生成' : '开始' }}技术方案编写
                  </el-button>
                </el-space>
                <el-text v-if="!technicalFileInfo" type="warning" size="small">
                  <i class="bi bi-exclamation-triangle"></i>
                  请先上传招标文件并进行 AI 解析
                </el-text>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </template>

    <!-- 错误状态 -->
    <el-empty v-else description="项目不存在或加载失败" />

    <!-- 文档预览对话框 -->
    <DocumentPreview
      v-model="previewVisible"
      :file-url="previewFileUrl"
      :file-name="previewFileName"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { PageHeader, Loading, DocumentPreview } from '@/components'
import FileCard from '@/components/FileCard.vue'
import ChapterTree from '@/components/ChapterTree.vue'
import TenderDocumentProcessor from '@/components/TenderDocumentProcessor.vue'
import { tenderApi } from '@/api/endpoints/tender'
import { companyApi } from '@/api/endpoints/company'
import { useProjectStore } from '@/stores/project'
import type { ProjectDetail } from '@/types'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

// 状态
const loading = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const projectDetail = ref<ProjectDetail | null>(null)
const activeTab = ref('basic') // 默认显示基本信息
const companies = ref<any[]>([]) // 公司列表
const latestTaskId = ref<string | null>(null) // 最新的文档解析task_id
const extractingBasicInfo = ref(false) // AI提取基本信息loading状态
const extractingQualifications = ref(false) // AI提取资格要求loading状态
const projectDocuments = ref<any[]>([]) // 项目文档列表
const parsedChapters = ref<any[]>([]) // 已解析的章节

// 预览相关状态
const previewVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')

// 表单数据
const formData = reactive({
  name: '',
  number: '',
  company_id: null as number | null,
  description: '',
  tender_unit: '',
  tender_agency: '',
  budget_amount: null as number | null,
  project_type: '',
  registration_deadline: '',
  bid_deadline: '',
  bid_opening_time: '',
  bid_opening_location: '',
  project_manager_name: '',
  project_manager_phone: '',
  tech_lead_name: '',
  tech_lead_phone: '',
  business_contact_name: '',
  business_contact_phone: '',
  authorized_person_name: '',
  authorized_person_id: ''
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  number: [{ required: true, message: '请输入项目编号', trigger: 'blur' }],
  company_id: [{ required: true, message: '请选择公司', trigger: 'change' }]
}

// 项目 ID
const projectId = computed(() => Number(route.params.id))

// 页面标题
const pageTitle = computed(() => {
  return projectDetail.value?.name || '项目详情'
})

// 计算章节总数
const totalParsedChapters = computed(() => {
  const countChapters = (chapters: any[]): number => {
    let count = chapters.length
    chapters.forEach(chapter => {
      if (chapter.children && chapter.children.length > 0) {
        count += countChapters(chapter.children)
      }
    })
    return count
  }
  return countChapters(parsedChapters.value)
})

// 辅助函数：安全提取文件路径
const getFileUrl = (fileData: any): string | null => {
  if (!fileData) return null
  if (typeof fileData === 'string') return fileData
  return fileData.file_url || fileData.file_path || null
}

// 辅助函数：安全提取文件信息
const getFileInfo = (fileData: any) => {
  if (!fileData) return null
  if (typeof fileData === 'string') {
    return {
      fileUrl: fileData,
      fileName: undefined,
      fileSize: undefined
    }
  }
  return {
    fileUrl: fileData.file_url || fileData.file_path || '',
    fileName: fileData.filename || fileData.file_name,
    fileSize: fileData.file_size
  }
}

// 提取各个文件的信息
const responseFileInfo = computed(() => {
  return getFileInfo(projectDetail.value?.step1_data?.response_file_path)
})

const businessResponseFileInfo = computed(() => {
  return getFileInfo(projectDetail.value?.step1_data?.business_response_file)
})

const technicalFileInfo = computed(() => {
  return getFileInfo(projectDetail.value?.step1_data?.technical_file_path)
})

const technicalP2PFileInfo = computed(() => {
  return getFileInfo(projectDetail.value?.step1_data?.technical_point_to_point_file)
})

const technicalProposalFileInfo = computed(() => {
  return getFileInfo(projectDetail.value?.step1_data?.technical_proposal_file)
})

// 资质名称中英文映射字典（基于后端extractor.py的定义）
const qualificationNameMapping: Record<string, string> = {
  // 基础资质类
  'business_license': '营业执照信息',
  'legal_id_front': '法人身份证正面',
  'legal_id_back': '法人身份证反面',
  'auth_id_front': '被授权人身份证正面',
  'auth_id_back': '被授权人身份证反面',
  'authorization_letter': '法人授权委托书',

  // 认证证书类
  'iso9001': 'ISO9001质量管理体系认证',
  'iso20000': 'ISO20000信息技术服务管理体系认证',
  'iso27001': 'ISO27001信息安全管理体系认证',
  'cmmi': 'CMMI能力成熟度认证',
  'itss': 'ITSS信息技术服务标准认证',

  // 行业资质类
  'telecom_license': '电信业务许可证',
  'value_added_telecom_license': '增值电信业务许可证',
  'basic_telecom_license': '基础电信业务许可证',
  'level_protection': '等级保护认证',
  'software_copyright': '软件著作权',
  'patent_certificate': '专利证书',
  'audit_report': '财务要求',
  'project_performance': '项目业绩要求',

  // 社保和信用资质类
  'social_security': '社会保险证明',
  'dishonest_executor': '失信被执行人',
  'tax_violation_check': '重大税收违法',
  'gov_procurement_creditchina': '政府采购严重违法失信记录（信用中国）',
  'gov_procurement_ccgp': '政府采购严重违法失信记录（政府采购网）',
  'tax_compliance': '依法纳税',
  'commitment_letter': '承诺函',
  'property_certificate': '营业办公场所房产证明',
  'deposit_requirement': '保证金要求',
  'purchaser_blacklist': '采购人黑名单'
}

// 获取资质的中文名称
const getQualificationDisplayName = (nameOrKey: string): string => {
  // 如果在映射字典中找到，返回中文名称
  if (qualificationNameMapping[nameOrKey]) {
    return qualificationNameMapping[nameOrKey]
  }
  // 否则返回原值（可能已经是中文名称）
  return nameOrKey
}

// 资格要求数据转换辅助函数
const convertQualificationsData = (rawData: Record<string, any>) => {
  const certifications: any[] = []
  const performance: any[] = []
  const personnel: any[] = []
  let financial: any = null

  // 定义分类映射
  const certKeywords = ['ISO', '认证', '资质', '许可证', '证书', '等保', '著作权', '专利', '信用']
  const perfKeywords = ['业绩', '项目', '案例', '合同']
  const personnelKeywords = ['人员', '项目经理', '技术负责人', '工程师']
  const financialKeywords = ['财务', '资本', '资产', '审计', '银行', '注册资金', '营业额']

  Object.entries(rawData).forEach(([key, value]: [string, any]) => {
    const isRequired = value.constraint_type === 'mandatory'
    const detail = value.detail || ''
    const summary = value.summary || key

    // 分类到对应类别
    if (financialKeywords.some(kw => key.includes(kw))) {
      // 财务要求 - 合并到financial对象
      if (!financial) {
        financial = {
          description: []
        }
      }
      financial.description.push(`${summary}: ${detail}`)
    } else if (perfKeywords.some(kw => key.includes(kw))) {
      // 业绩要求
      performance.push({
        description: summary,
        detail,
        required: isRequired
      })
    } else if (personnelKeywords.some(kw => key.includes(kw))) {
      // 人员配置
      personnel.push({
        position: summary,
        detail,
        required: isRequired
      })
    } else if (certKeywords.some(kw => key.includes(kw))) {
      // 资质证书
      certifications.push({
        name: summary,
        note: detail,
        required: isRequired
      })
    } else {
      // 默认归类到资质证书
      certifications.push({
        name: summary,
        note: detail,
        required: isRequired
      })
    }
  })

  // 格式化financial描述
  if (financial && financial.description) {
    financial.description = financial.description.join('；')
  }

  return {
    certifications,
    performance,
    personnel,
    financial
  }
}

// 资格要求数据（从 qualifications_data 读取并转换）
const qualifications = computed(() => {
  // 从 projectDetail 读取 qualifications_data
  const rawData = projectDetail.value?.qualifications_data

  if (rawData && typeof rawData === 'object' && Object.keys(rawData).length > 0) {
    return convertQualificationsData(rawData)
  }

  // 空数据回退
  return {
    certifications: [],
    performance: [],
    personnel: [],
    financial: null
  }
})

// 加载项目详情
const loadProjectDetail = async () => {
  if (!projectId.value) return

  loading.value = true
  try {
    const response = await tenderApi.getProject(projectId.value)
    const rawData = response.data

    // 映射字段名以匹配前端
    projectDetail.value = {
      id: rawData.project_id,
      name: rawData.project_name,
      number: rawData.project_number,
      company_id: rawData.company_id,
      company_name: rawData.company_name,
      status: rawData.status,
      created_at: rawData.created_at,
      updated_at: rawData.updated_at,
      authorized_person_name: rawData.authorized_person_name,
      authorized_person_id: rawData.authorized_person_id,
      // 招标信息
      tender_unit: rawData.tender_unit,
      tender_agency: rawData.tender_agency,
      budget_amount: rawData.budget_amount,
      project_type: rawData.project_type,
      registration_deadline: rawData.registration_deadline,
      bid_deadline: rawData.bid_deadline,
      bid_opening_time: rawData.bid_opening_time,
      bid_opening_location: rawData.bid_opening_location,
      // 联系人信息
      project_manager_name: rawData.project_manager_name,
      project_manager_phone: rawData.project_manager_phone,
      tech_lead_name: rawData.tech_lead_name,
      tech_lead_phone: rawData.tech_lead_phone,
      business_contact_name: rawData.business_contact_name,
      business_contact_phone: rawData.business_contact_phone,
      // 项目描述
      description: rawData.description,
      // step1_data 包含 AI 提取的文件路径
      step1_data: rawData.step1_data,
      // 保留原始数据
      ...rawData
    }

    // 填充表单数据
    formData.name = projectDetail.value.name || ''
    formData.number = projectDetail.value.number || ''
    formData.company_id = projectDetail.value.company_id || null
    formData.description = projectDetail.value.description || ''
    formData.tender_unit = projectDetail.value.tender_unit || ''
    formData.tender_agency = projectDetail.value.tender_agency || ''
    formData.budget_amount = projectDetail.value.budget_amount || null
    formData.project_type = projectDetail.value.project_type || ''
    formData.registration_deadline = projectDetail.value.registration_deadline || ''
    formData.bid_deadline = projectDetail.value.bid_deadline || ''
    formData.bid_opening_time = projectDetail.value.bid_opening_time || ''
    formData.bid_opening_location = projectDetail.value.bid_opening_location || ''
    formData.project_manager_name = projectDetail.value.project_manager_name || ''
    formData.project_manager_phone = projectDetail.value.project_manager_phone || ''
    formData.tech_lead_name = projectDetail.value.tech_lead_name || ''
    formData.tech_lead_phone = projectDetail.value.tech_lead_phone || ''
    formData.business_contact_name = projectDetail.value.business_contact_name || ''
    formData.business_contact_phone = projectDetail.value.business_contact_phone || ''
    formData.authorized_person_name = projectDetail.value.authorized_person_name || ''
    formData.authorized_person_id = projectDetail.value.authorized_person_id || ''

    // 解析章节数据和文档信息
    if (rawData.step1_data) {
      try {
        const step1Data = typeof rawData.step1_data === 'string'
          ? JSON.parse(rawData.step1_data)
          : rawData.step1_data

        // 提取章节信息
        if (step1Data.chapters && Array.isArray(step1Data.chapters)) {
          parsedChapters.value = step1Data.chapters
        }

        // 从step1_data中提取文档信息
        const docs: any[] = []
        let docId = 1

        // 原始招标文档
        if (rawData.tender_document_path) {
          docs.push({
            id: docId++,
            file_path: rawData.tender_document_path,
            file_url: rawData.tender_document_path,
            original_filename: '招标文档',
            document_type: 'tender',
            uploaded_at: rawData.created_at
          })
        }

        // 应答文件模板
        if (step1Data.response_file_path) {
          docs.push({
            id: docId++,
            file_path: step1Data.response_file_path,
            file_url: step1Data.response_file_path,
            original_filename: step1Data.response_filename || '应答文件模板',
            document_type: 'response_template',
            file_size: step1Data.response_file_size,
            uploaded_at: rawData.updated_at
          })
        }

        // 技术需求文件
        if (step1Data.technical_file_path) {
          docs.push({
            id: docId++,
            file_path: step1Data.technical_file_path,
            file_url: step1Data.technical_file_path,
            original_filename: step1Data.technical_filename || '技术需求文件',
            document_type: 'technical',
            file_size: step1Data.technical_file_size,
            uploaded_at: rawData.updated_at
          })
        }

        // 商务应答完成文件
        if (step1Data.business_response_file) {
          const businessFile = typeof step1Data.business_response_file === 'string'
            ? { file_path: step1Data.business_response_file }
            : step1Data.business_response_file

          docs.push({
            id: docId++,
            file_path: businessFile.file_path || businessFile.file_url,
            file_url: businessFile.file_url || businessFile.file_path,
            original_filename: businessFile.file_name || '商务应答完成文件',
            document_type: 'business_response',
            file_size: businessFile.file_size,
            uploaded_at: rawData.updated_at
          })
        }

        // 技术点对点应答文件
        if (step1Data.technical_point_to_point_file) {
          const techP2PFile = typeof step1Data.technical_point_to_point_file === 'string'
            ? { file_path: step1Data.technical_point_to_point_file }
            : step1Data.technical_point_to_point_file

          docs.push({
            id: docId++,
            file_path: techP2PFile.file_path || techP2PFile.file_url,
            file_url: techP2PFile.file_url || techP2PFile.file_path,
            original_filename: techP2PFile.file_name || '技术点对点应答文件',
            document_type: 'technical_p2p',
            file_size: techP2PFile.file_size,
            uploaded_at: rawData.updated_at
          })
        }

        // 技术方案文件
        if (step1Data.technical_proposal_file) {
          const techProposalFile = typeof step1Data.technical_proposal_file === 'string'
            ? { file_path: step1Data.technical_proposal_file }
            : step1Data.technical_proposal_file

          docs.push({
            id: docId++,
            file_path: techProposalFile.file_path || techProposalFile.file_url,
            file_url: techProposalFile.file_url || techProposalFile.file_path,
            original_filename: techProposalFile.file_name || '技术方案文件',
            document_type: 'technical_proposal',
            file_size: techProposalFile.file_size,
            uploaded_at: rawData.updated_at
          })
        }

        projectDocuments.value = docs
      } catch (e) {
        console.warn('解析文档和章节数据失败:', e)
      }
    }

    // 如果是新建的项目（名称为"新项目"），自动进入编辑模式
    if (projectDetail.value.name === '新项目' || projectDetail.value.status === 'draft') {
      isEditing.value = true
    }
  } catch (error) {
    console.error('加载项目详情失败:', error)
    ElMessage.error('加载项目详情失败')
  } finally {
    loading.value = false
  }
}

// 加载公司列表
const loadCompanies = async () => {
  try {
    const response = await companyApi.getCompanies()
    companies.value = response.data || []
  } catch (error) {
    console.error('加载公司列表失败:', error)
  }
}

// 格式化金额
const formatAmount = (amount: number) => {
  return amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 状态相关
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    active: 'success',
    completed: 'primary',
    draft: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: '进行中',
    completed: '已完成',
    draft: '草稿'
  }
  return map[status] || status
}

// 操作方法
const handleRefresh = () => {
  loadProjectDetail()
}

// 进入编辑模式
const handleEdit = () => {
  isEditing.value = true
}

// 取消编辑
const handleCancel = () => {
  ElMessageBox.confirm('确定要取消编辑吗？未保存的更改将丢失', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 重新加载项目数据
    loadProjectDetail()
    isEditing.value = false
  }).catch(() => {
    // 用户取消
  })
}

// 保存项目
const handleSave = async () => {
  saving.value = true
  try {
    // 准备更新数据
    const updateData = {
      project_name: formData.name,
      project_number: formData.number,
      company_id: formData.company_id,
      description: formData.description,
      tender_unit: formData.tender_unit,
      tender_agency: formData.tender_agency,
      budget_amount: formData.budget_amount,
      project_type: formData.project_type,
      registration_deadline: formData.registration_deadline,
      bid_deadline: formData.bid_deadline,
      bid_opening_time: formData.bid_opening_time,
      bid_opening_location: formData.bid_opening_location,
      project_manager_name: formData.project_manager_name,
      project_manager_phone: formData.project_manager_phone,
      tech_lead_name: formData.tech_lead_name,
      tech_lead_phone: formData.tech_lead_phone,
      business_contact_name: formData.business_contact_name,
      business_contact_phone: formData.business_contact_phone,
      authorized_person_name: formData.authorized_person_name,
      authorized_person_id: formData.authorized_person_id,
      status: 'active' // 保存后更新为活跃状态
    }

    await tenderApi.updateProject(projectId.value, updateData)
    ElMessage.success('保存成功')
    isEditing.value = false
    // 重新加载项目数据
    await loadProjectDetail()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 跳转到商务应答
const handleStartBusiness = async () => {
  if (!projectDetail.value) return

  const responseFileUrl = projectDetail.value.step1_data?.response_file_path

  if (!responseFileUrl) {
    ElMessage.warning('未找到应答文件模板')
    return
  }

  // 将当前项目保存到 Pinia Store，以便商务应答页面可以读取
  projectStore.setCurrentProject(projectDetail.value)

  await router.push({
    name: 'BusinessResponse'
  })
}

// 跳转到点对点应答
const handleStartPointToPoint = async () => {
  if (!projectDetail.value) return

  const technicalFileUrl = projectDetail.value.step1_data?.technical_file_path

  if (!technicalFileUrl) {
    ElMessage.warning('未找到技术需求文件')
    return
  }

  await router.push({
    name: 'PointToPoint',
    query: {
      projectId: projectId.value.toString(),
      technicalFileUrl,
      fromHitl: 'true'
    }
  })
}

// 跳转到技术方案
const handleStartProposal = async () => {
  if (!projectDetail.value) return

  const technicalFileUrl = projectDetail.value.step1_data?.technical_file_path

  if (!technicalFileUrl) {
    ElMessage.warning('未找到技术需求文件')
    return
  }

  await router.push({
    name: 'TechProposal',
    query: {
      projectId: projectId.value.toString(),
      technicalFileUrl,
      fromHitl: 'true'
    }
  })
}

// 处理文档处理成功事件
const handleProcessSuccess = async (type: 'response' | 'technical') => {
  // 重新加载项目详情以获取最新的step1_data和章节信息
  await loadProjectDetail()

  if (type === 'response') {
    // 保存应答文件成功，自动切换到商务应答Tab
    ElMessage.success('应答文件已保存，可以开始商务应答处理')
    activeTab.value = 'business'
  } else if (type === 'technical') {
    // 保存技术需求成功，自动切换到技术需求Tab
    ElMessage.success('技术需求已保存，可以开始技术方案编写')
    activeTab.value = 'technical'
  }
}

// 处理任务ID更新事件
const handleTaskIdUpdate = (taskId: string) => {
  latestTaskId.value = taskId
  console.log('收到task_id:', taskId)
}

// AI提取基本信息
const handleExtractBasicInfo = async () => {
  if (!projectId.value) {
    ElMessage.warning('请先上传并解析招标文档')
    return
  }

  extractingBasicInfo.value = true
  try {
    const response = await tenderApi.extractBasicInfo(projectId.value)

    if (response.success && response.data) {
      const info = response.data

      // 填充表单字段
      if (info.project_name) formData.name = info.project_name
      if (info.project_number) formData.number = info.project_number
      if (info.tender_party) formData.tender_unit = info.tender_party
      if (info.tender_agent) formData.tender_agency = info.tender_agent
      if (info.tender_location) formData.bid_opening_location = info.tender_location
      if (info.tender_deadline) formData.bid_deadline = info.tender_deadline

      ElMessage.success('AI提取基本信息成功')

      // 如果不在编辑模式，自动进入编辑模式
      if (!isEditing.value) {
        isEditing.value = true
      }
    } else {
      throw new Error((response as any).error || 'AI提取失败')
    }
  } catch (error) {
    console.error('AI提取基本信息失败:', error)
    ElMessage.error(`AI提取失败: ${error instanceof Error ? error.message : '未知错误'}`)
  } finally {
    extractingBasicInfo.value = false
  }
}

// AI提取资格要求
const handleExtractQualifications = async () => {
  if (!projectId.value) {
    ElMessage.warning('请先上传并解析招标文档')
    return
  }

  extractingQualifications.value = true
  try {
    const response = await tenderApi.extractQualifications(projectId.value)

    if (response.success) {
      ElMessage.success('AI提取资格要求成功，正在刷新数据...')

      // 重新加载项目详情以获取最新的资格要求数据
      await loadProjectDetail()

      ElMessage.success('资格要求已更新')
    } else {
      throw new Error((response as any).error || 'AI提取失败')
    }
  } catch (error) {
    console.error('AI提取资格要求失败:', error)
    ElMessage.error(`AI提取失败: ${error instanceof Error ? error.message : '未知错误'}`)
  } finally {
    extractingQualifications.value = false
  }
}

// 处理文档预览
const handlePreview = (fileUrl: string, fileName: string) => {
  previewFileUrl.value = fileUrl
  previewFileName.value = fileName
  previewVisible.value = true
}

// 监听路由变化
watch(() => route.params.id, () => {
  loadProjectDetail()
})

onMounted(() => {
  loadCompanies()
  loadProjectDetail()
})
</script>

<style scoped lang="scss">
.tender-management-detail {
  padding: 20px;

  .tabs-card {
    :deep(.el-card__body) {
      padding: 0;
    }

    .detail-tabs {
      :deep(.el-tabs__header) {
        padding: 0 20px;
        margin-bottom: 0;
      }

      :deep(.el-tabs__content) {
        padding: 30px 20px;
      }

      .tab-label {
        display: flex;
        align-items: center;
        gap: 6px;

        i {
          font-size: 16px;
        }
      }
    }
  }

  .tab-content {
    // 统一所有 el-descriptions 的标签列宽度
    :deep(.el-descriptions__label) {
      width: 120px !important;
      min-width: 120px;
    }

    .info-section {
      margin-bottom: 30px;

      &:last-child {
        margin-bottom: 0;
      }

      .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;

        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--el-text-color-primary);

          i {
            margin-right: 8px;
            color: var(--el-color-primary);
          }
        }
      }

      .description-box {
        padding: 20px;
        background: var(--el-fill-color-light);
        border-radius: 8px;
        border: 1px solid var(--el-border-color-lighter);
        line-height: 1.8;
        white-space: pre-wrap;
      }

      // 编辑表单样式
      .edit-form {
        padding: 20px;
        background: var(--el-fill-color-lighter);
        border-radius: 8px;
        border: 1px solid var(--el-border-color-lighter);

        :deep(.el-form-item) {
          margin-bottom: 18px;
        }

        :deep(.el-input__inner),
        :deep(.el-textarea__inner) {
          background: var(--bg-white, #ffffff);
        }
      }
    }

    .file-section {
      margin-bottom: 30px;

      &:last-of-type {
        margin-bottom: 0;
      }

      .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;

        h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);

          i {
            margin-right: 8px;
            color: var(--el-color-primary);
          }
        }
      }
    }

    .documents-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }

    .requirements-list {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .requirement-item {
        :deep(.el-card__body) {
          padding: 16px;
        }

        .requirement-content {
          display: flex;
          align-items: flex-start;
          gap: 16px;

          .requirement-icon {
            font-size: 32px;
            color: var(--el-color-primary);
          }

          .requirement-text {
            flex: 1;

            h4 {
              margin: 0 0 8px 0;
              font-size: 15px;
              font-weight: 600;
              color: var(--el-text-color-primary);
            }

            p {
              margin: 4px 0;
              font-size: 13px;
              color: var(--el-text-color-secondary);
            }
          }

          .requirement-status {
            flex-shrink: 0;
          }
        }
      }
    }

    .action-area {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      margin-top: 40px;
      padding-top: 30px;
      border-top: 1px solid var(--el-border-color-lighter);
    }
  }

  // 金额样式
  .amount {
    font-weight: 600;
    color: var(--el-color-danger);
    font-size: 15px;
  }

  // 截止日期样式
  .deadline {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--el-color-warning);

    i {
      font-size: 14px;
    }
  }
}
</style>
