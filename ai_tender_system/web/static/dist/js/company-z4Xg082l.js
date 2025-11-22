import { e as apiClient } from "./index.js";
const companyApi = {
  // ==================== 公司管理 ====================
  /**
   * 获取公司列表
   */
  async getCompanies(params) {
    return apiClient.get("/companies", params);
  },
  /**
   * 获取公司详情
   */
  async getCompany(companyId) {
    return apiClient.get(`/companies/${companyId}`);
  },
  /**
   * 创建新公司
   */
  async createCompany(data) {
    return apiClient.post("/companies", data);
  },
  /**
   * 更新公司信息
   */
  async updateCompany(companyId, data) {
    return apiClient.put(`/companies/${companyId}`, data);
  },
  /**
   * 删除公司
   */
  async deleteCompany(companyId) {
    return apiClient.delete(`/companies/${companyId}`);
  },
  // ==================== 资质管理 ====================
  /**
   * 获取公司资质列表
   * 返回格式：{ data: { id_card_front: {...}, business_license: {...}, ... } }
   */
  async getCompanyQualifications(companyId) {
    return apiClient.get(`/companies/${companyId}/qualifications`);
  },
  /**
   * 获取资质类型列表
   */
  async getQualificationTypes() {
    return apiClient.get("/qualification-types");
  },
  /**
   * 上传资质文件
   */
  async uploadQualification(companyId, typeKey, file, data, onProgress) {
    const formData = new FormData();
    formData.append(`qualifications[${typeKey}]`, file);
    const qualificationNames = {};
    formData.append("qualification_names", JSON.stringify(qualificationNames));
    const fileVersions = {};
    if (data.notes) {
      fileVersions[typeKey] = data.notes;
    }
    formData.append("file_versions", JSON.stringify(fileVersions));
    return apiClient.upload(`/companies/${companyId}/qualifications/upload`, formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 更新资质信息
   */
  async updateQualification(qualificationId, data) {
    return apiClient.put(`/qualifications/${qualificationId}`, data);
  },
  /**
   * 删除资质
   */
  async deleteQualification(qualificationId) {
    return apiClient.delete(`/qualifications/${qualificationId}`);
  },
  /**
   * 下载资质文件
   */
  async downloadQualification(qualificationId, filename, onProgress) {
    return apiClient.download(
      `/qualifications/${qualificationId}/download`,
      filename,
      (event) => {
        if (onProgress && event.total) {
          const progress = Math.round(event.loaded * 100 / event.total);
          onProgress(progress);
        }
      }
    );
  },
  /**
   * 批量上传资质
   */
  async batchUploadQualifications(companyId, files, onProgress) {
    const formData = new FormData();
    formData.append("company_id", companyId.toString());
    files.forEach((item, index) => {
      formData.append(`files[${index}]`, item.file);
      formData.append(`type_keys[${index}]`, item.typeKey);
    });
    return apiClient.upload("/qualifications/batch-upload", formData, (event) => {
      if (onProgress && event.total) {
        const progress = Math.round(event.loaded * 100 / event.total);
        onProgress(progress);
      }
    });
  },
  /**
   * 获取即将过期的资质
   */
  async getExpiringQualifications(companyId, days = 30) {
    return apiClient.get(`/companies/${companyId}/qualifications/expiring`, { days });
  },
  /**
   * 搜索公司
   */
  async searchCompanies(keyword) {
    return apiClient.get("/companies/search", { keyword });
  }
};
export {
  companyApi as c
};
