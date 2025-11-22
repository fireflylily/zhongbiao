import { e as apiClient } from "./index.js";
const knowledgeApi = {
  // ==================== 企业知识库 ====================
  /**
   * 获取知识文档列表
   */
  async getKnowledgeDocuments(params) {
    return apiClient.get("/knowledge/documents", params);
  },
  /**
   * 获取知识文档详情
   */
  async getKnowledgeDocument(documentId) {
    return apiClient.get(`/knowledge/documents/${documentId}`);
  },
  /**
   * 上传知识文档
   */
  async uploadKnowledgeDocument(data, onProgress) {
    const formData = new FormData();
    formData.append("file", data.file);
    formData.append("company_id", data.company_id.toString());
    formData.append("category", data.category);
    formData.append("title", data.title);
    if (data.description) {
      formData.append("description", data.description);
    }
    return apiClient.upload("/knowledge/documents/upload", formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 更新知识文档
   */
  async updateKnowledgeDocument(documentId, data) {
    return apiClient.put(`/knowledge/documents/${documentId}`, data);
  },
  /**
   * 删除知识文档
   */
  async deleteKnowledgeDocument(documentId) {
    return apiClient.delete(`/knowledge/documents/${documentId}`);
  },
  /**
   * 获取知识分类列表
   */
  async getKnowledgeCategories() {
    return apiClient.get("/knowledge/categories");
  },
  /**
   * 搜索知识库
   */
  async searchKnowledge(params) {
    return apiClient.post("/knowledge/search", params);
  },
  /**
   * RAG检索（向量搜索）
   */
  async ragRetrieval(params) {
    return apiClient.post("/knowledge/rag-retrieval", params);
  },
  // ==================== 案例库 ====================
  /**
   * 获取案例列表
   */
  async getCases(params) {
    return apiClient.get("/case_library/cases", params);
  },
  /**
   * 获取案例详情
   */
  async getCase(caseId) {
    return apiClient.get(`/case_library/cases/${caseId}`);
  },
  /**
   * 创建案例
   */
  async createCase(data) {
    return apiClient.post("/case_library/cases", data);
  },
  /**
   * 更新案例
   */
  async updateCase(caseId, data) {
    return apiClient.put(`/case_library/cases/${caseId}`, data);
  },
  /**
   * 删除案例
   */
  async deleteCase(caseId) {
    return apiClient.delete(`/case_library/cases/${caseId}`);
  },
  /**
   * 获取案例附件列表
   */
  async getCaseAttachments(caseId) {
    return apiClient.get(`/case_library/cases/${caseId}/attachments`);
  },
  /**
   * 上传案例附件
   */
  async uploadCaseAttachment(caseId, file, attachmentType, description, onProgress) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("attachment_type", attachmentType);
    if (description) {
      formData.append("description", description);
    }
    return apiClient.upload(`/case_library/cases/${caseId}/attachments`, formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 删除案例附件
   */
  async deleteCaseAttachment(attachmentId) {
    return apiClient.delete(`/case_library/attachments/${attachmentId}`);
  },
  /**
   * 下载案例附件
   */
  downloadCaseAttachment(attachmentId) {
    return `${apiClient.getInstance().defaults.baseURL}/case_library/attachments/${attachmentId}/download`;
  },
  /**
   * 搜索案例
   */
  async searchCases(query, companyId) {
    return apiClient.get("/case_library/search", { q: query, company_id: companyId });
  },
  /**
   * 获取案例统计信息
   */
  async getCaseStatistics(companyId) {
    return apiClient.get("/case_library/statistics", companyId ? { company_id: companyId } : void 0);
  },
  // ==================== 简历库 ====================
  /**
   * 获取简历列表
   */
  async getResumes(params) {
    return apiClient.get("/resume_library/list", params);
  },
  /**
   * 获取简历详情
   */
  async getResume(resumeId) {
    return apiClient.get(`/resume_library/detail/${resumeId}`);
  },
  /**
   * 创建简历
   */
  async createResume(data) {
    return apiClient.post("/resume_library/create", data);
  },
  /**
   * 更新简历
   */
  async updateResume(resumeId, data) {
    return apiClient.put(`/resume_library/update/${resumeId}`, data);
  },
  /**
   * 删除简历
   */
  async deleteResume(resumeId) {
    return apiClient.delete(`/resume_library/delete/${resumeId}`);
  },
  /**
   * 解析简历文件
   */
  async parseResumeFile(file, autoCreate = false, companyId, onProgress) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("auto_create", autoCreate.toString());
    if (companyId) {
      formData.append("company_id", companyId.toString());
    }
    return apiClient.upload("/resume_library/parse-resume", formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 上传简历附件
   */
  async uploadResumeAttachment(resumeId, file, category, description, onProgress) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("resume_id", resumeId.toString());
    formData.append("attachment_category", category);
    if (description) {
      formData.append("description", description);
    }
    return apiClient.upload("/resume_library/upload-attachment", formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 获取简历附件列表
   */
  async getResumeAttachments(resumeId, category) {
    return apiClient.get(`/resume_library/attachments/${resumeId}`, category ? { category } : void 0);
  },
  /**
   * 删除简历附件
   */
  async deleteResumeAttachment(attachmentId) {
    return apiClient.delete(`/resume_library/attachment/${attachmentId}`);
  },
  /**
   * 下载简历附件
   */
  downloadResumeAttachment(attachmentId) {
    return `${apiClient.getInstance().defaults.baseURL}/resume_library/attachment/${attachmentId}/download`;
  },
  /**
   * 搜索简历
   */
  async searchResumes(keyword, limit = 10) {
    return apiClient.get("/resume_library/search", { keyword, limit });
  },
  /**
   * 获取简历统计信息
   */
  async getResumeStatistics(companyId) {
    return apiClient.get("/resume_library/statistics", companyId ? { company_id: companyId } : void 0);
  },
  /**
   * 批量导出简历
   */
  async exportResumes(resumeIds, options) {
    return apiClient.post("/resume_library/export", { resume_ids: resumeIds, options });
  },
  /**
   * 获取附件类别列表
   */
  async getAttachmentCategories() {
    return apiClient.get("/resume_library/categories");
  },
  /**
   * 获取学历级别列表
   */
  async getEducationLevels() {
    return apiClient.get("/resume_library/education-levels");
  }
};
const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${Math.round(bytes / Math.pow(k, i) * 100) / 100} ${sizes[i]}`;
};
const formatDate = (dateStr, format = "datetime") => {
  if (!dateStr) return "";
  const date = typeof dateStr === "string" ? new Date(dateStr) : dateStr;
  if (isNaN(date.getTime())) return "";
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hour = String(date.getHours()).padStart(2, "0");
  const minute = String(date.getMinutes()).padStart(2, "0");
  const second = String(date.getSeconds()).padStart(2, "0");
  switch (format) {
    case "date":
      return `${year}-${month}-${day}`;
    case "time":
      return `${hour}:${minute}`;
    case "datetime-full":
      return `${year}年${month}月${day}日 ${hour}:${minute}:${second}`;
    case "datetime":
    default:
      return `${year}-${month}-${day} ${hour}:${minute}`;
  }
};
export {
  formatFileSize as a,
  formatDate as f,
  knowledgeApi as k
};
