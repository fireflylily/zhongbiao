import { e as apiClient } from "./index.js";
const tenderApi = {
  // ==================== 项目管理 ====================
  /**
   * 获取项目列表
   */
  async getProjects(params) {
    return apiClient.get("/tender-projects", params);
  },
  /**
   * 获取项目详情
   */
  async getProject(projectId) {
    return apiClient.get(`/tender-projects/${projectId}`);
  },
  /**
   * 创建新项目
   */
  async createProject(data) {
    return apiClient.post("/tender-projects", data);
  },
  /**
   * 更新项目信息
   */
  async updateProject(projectId, data) {
    return apiClient.put(`/tender-projects/${projectId}`, data);
  },
  /**
   * 删除项目
   */
  async deleteProject(projectId) {
    return apiClient.delete(`/tender-projects/${projectId}`);
  },
  // ==================== 文档管理 ====================
  /**
   * 上传招标文档
   */
  async uploadTenderDocument(projectId, file, onProgress) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("project_id", projectId.toString());
    return apiClient.upload("/upload/tender-document", formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 上传商务应答模板
   */
  async uploadBusinessTemplate(projectId, file, onProgress) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("project_id", projectId.toString());
    return apiClient.upload("/upload/business-template", formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 上传技术方案模板
   */
  async uploadTechnicalTemplate(projectId, file, onProgress) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("project_id", projectId.toString());
    return apiClient.upload("/upload/technical-template", formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 获取项目文档列表
   */
  async getProjectDocuments(projectId) {
    return apiClient.get(`/tender-projects/${projectId}/documents`);
  },
  /**
   * 删除文档
   */
  async deleteDocument(documentId) {
    return apiClient.delete(`/documents/${documentId}`);
  },
  /**
   * 下载文档
   */
  async downloadDocument(documentId, filename, onProgress) {
    return apiClient.download(`/documents/${documentId}/download`, filename, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  // ==================== 文档处理 ====================
  /**
   * 启动文档处理任务（Step 1 - 解析招标文档）
   */
  async startTenderProcessing(data) {
    return apiClient.post("/tender-processing/start", data);
  },
  /**
   * 获取任务状态
   */
  async getTaskStatus(taskId) {
    return apiClient.get(`/tasks/${taskId}/status`);
  },
  /**
   * 取消任务
   */
  async cancelTask(taskId) {
    return apiClient.post(`/tasks/${taskId}/cancel`);
  },
  /**
   * 获取任务结果
   */
  async getTaskResult(taskId) {
    return apiClient.get(`/tasks/${taskId}/result`);
  },
  /**
   * 解析文档结构（用于章节选择）
   */
  async parseDocumentStructure(formData) {
    return apiClient.post("/tender-processing/parse-structure", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
  },
  /**
   * 保存应答文件章节
   */
  async saveResponseFile(projectId, chapterIds) {
    return apiClient.post(`/tender-processing/save-response-file/${projectId}`, {
      chapter_ids: chapterIds
    });
  },
  /**
   * 保存技术需求章节
   */
  async saveTechnicalChapters(projectId, chapterIds) {
    return apiClient.post(`/tender-processing/save-technical-chapters/${projectId}`, {
      chapter_ids: chapterIds
    });
  },
  /**
   * AI提取基本信息
   */
  async extractBasicInfo(projectId) {
    return apiClient.post(`/tender-processing/extract-basic-info/${projectId}`, {});
  },
  /**
   * AI提取资格要求
   */
  async extractQualifications(projectId) {
    return apiClient.post(`/tender-processing/extract-qualifications/${projectId}`, {});
  },
  // ==================== 文档融合 ====================
  /**
   * 获取源文档列表（用于文档融合）
   */
  async getSourceDocuments(projectId) {
    return apiClient.get(`/document-merger/source-documents/${projectId}`);
  },
  /**
   * 启动文档融合任务
   */
  async startDocumentMerge(data) {
    return apiClient.post("/document-merger/merge", data);
  },
  /**
   * 获取文档融合结果
   */
  async getMergeTaskResult(taskId) {
    return apiClient.get(`/document-merger/tasks/${taskId}/result`);
  },
  /**
   * 下载融合后的文档
   */
  async downloadMergedDocument(taskId, filename, onProgress) {
    return apiClient.download(
      `/document-merger/tasks/${taskId}/download`,
      filename,
      (event) => {
        if (onProgress && event.total) {
          const progress = Math.round(event.loaded * 100 / event.total);
          onProgress(progress);
        }
      }
    );
  },
  // ==================== HITL工作流 ====================
  /**
   * 获取HITL任务详情
   */
  async getHITLTask(projectId) {
    return apiClient.get(`/tender-processing/hitl-tasks/${projectId}`);
  },
  /**
   * 更新HITL任务状态
   */
  async updateHITLTask(projectId, data) {
    return apiClient.put(`/tender-processing/hitl-tasks/${projectId}`, data);
  },
  /**
   * 提交HITL审核
   */
  async submitHITLReview(projectId, data) {
    return apiClient.post(`/tender-processing/hitl-tasks/${projectId}/submit`, data);
  },
  // ==================== 统计数据 ====================
  /**
   * 获取工作台全局统计数据
   */
  async getDashboardStatistics() {
    return apiClient.get("/tender-management/dashboard-stats");
  },
  /**
   * 获取项目统计数据
   */
  async getProjectStatistics(projectId) {
    return apiClient.get(`/tender-projects/${projectId}/statistics`);
  },
  // ==================== 提示词配置 ====================
  /**
   * 获取大纲生成提示词配置
   */
  async getOutlineGenerationPrompts() {
    return apiClient.get("/prompts/outline-generation");
  }
};
export {
  tenderApi as t
};
