import { t as tenderApi } from "./tender-DvsgeLWX.js";
import { u as useProjectStore } from "./project-X4Kuz_iO.js";
import { r as ref, c as computed, A as ElMessage } from "./vendor-MtO928VE.js";
function useProjectDocuments() {
  const projectStore = useProjectStore();
  const projects = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const currentDocuments = ref({
    tenderFile: null,
    templateFile: null,
    technicalFile: null,
    businessResponseFile: null,
    p2pResponseFile: null,
    techProposalFile: null
  });
  const selectedProject = computed(
    () => projects.value.find((p) => p.id === projectStore.projectId)
  );
  const hasProjects = computed(() => projects.value.length > 0);
  const hasTenderFile = computed(() => currentDocuments.value.tenderFile !== null);
  const hasTemplateFile = computed(() => currentDocuments.value.templateFile !== null);
  const hasTechnicalFile = computed(() => currentDocuments.value.technicalFile !== null);
  const loadProjects = async (filters) => {
    var _a;
    loading.value = true;
    error.value = null;
    try {
      const response = await tenderApi.getProjects({
        page: 1,
        page_size: 100,
        ...filters
      });
      projects.value = ((_a = response.data) == null ? void 0 : _a.items) || [];
      if (projects.value.length === 0) {
        ElMessage.warning("暂无项目数据");
      }
    } catch (err) {
      error.value = "加载项目列表失败";
      ElMessage.error(error.value);
      console.error("Load projects error:", err);
    } finally {
      loading.value = false;
    }
  };
  const handleProjectChange = async (projectId, callbacks) => {
    clearDocuments();
    if (callbacks == null ? void 0 : callbacks.onClear) {
      callbacks.onClear();
    }
    if (projectId) {
      try {
        const response = await tenderApi.getProject(projectId);
        if (response.data) {
          projectStore.setCurrentProject(response.data);
        }
      } catch (err) {
        console.error("获取项目详情失败:", err);
        ElMessage.error("获取项目详情失败");
      }
      await loadProjectDocuments(projectId, callbacks);
    } else {
      projectStore.clearCurrentProject();
    }
  };
  const loadProjectDocuments = async (projectId, callbacks) => {
    var _a, _b, _c, _d, _e, _f, _g, _h, _i;
    loading.value = true;
    try {
      const response = await tenderApi.getProject(projectId);
      const projectData = response.data;
      if (!projectData) {
        ElMessage.warning("未找到项目数据");
        return;
      }
      const step1Data = projectData.step1_data;
      const docs = {
        tenderFile: null,
        templateFile: null,
        technicalFile: null,
        businessResponseFile: null,
        p2pResponseFile: null,
        techProposalFile: null
      };
      if (step1Data == null ? void 0 : step1Data.file_path) {
        const fileName = step1Data.file_name || step1Data.file_path.split("/").pop() || "招标文档";
        const fileExt = ((_a = fileName.split(".").pop()) == null ? void 0 : _a.toLowerCase()) || "doc";
        const isWordDoc = ["doc", "docx"].includes(fileExt);
        docs.tenderFile = {
          name: step1Data.file_name || "招标文档",
          url: step1Data.file_path,
          status: "success",
          uid: Date.now() + Math.random(),
          size: step1Data.file_size || 0
        };
        console.log(`✅ 招标文档: ${fileName} (${isWordDoc ? "Word" : fileExt})`);
      }
      if (step1Data == null ? void 0 : step1Data.response_file_path) {
        const fileName = step1Data.response_file_path.split("/").pop() || "应答模板";
        const fileExt = ((_b = fileName.split(".").pop()) == null ? void 0 : _b.toLowerCase()) || "doc";
        const isWordDoc = ["doc", "docx"].includes(fileExt);
        docs.templateFile = {
          name: fileName,
          url: step1Data.response_file_path,
          status: "success",
          uid: Date.now() + Math.random() + 1,
          size: 0
        };
        console.log(`✅ 应答模板: ${fileName} (${isWordDoc ? "Word" : fileExt})`);
      }
      if (step1Data == null ? void 0 : step1Data.technical_file_path) {
        const fileName = step1Data.technical_file_path.split("/").pop() || "技术需求文档";
        const fileExt = ((_c = fileName.split(".").pop()) == null ? void 0 : _c.toLowerCase()) || "doc";
        const isWordDoc = ["doc", "docx"].includes(fileExt);
        docs.technicalFile = {
          name: fileName,
          url: step1Data.technical_file_path,
          status: "success",
          uid: Date.now() + Math.random() + 2,
          size: 0
        };
        console.log(`✅ 技术需求文档: ${fileName} (${isWordDoc ? "Word" : fileExt})`);
      }
      if (step1Data == null ? void 0 : step1Data.business_response_file) {
        const businessFile = step1Data.business_response_file;
        const fileName = ((_d = businessFile.file_path) == null ? void 0 : _d.split("/").pop()) || "商务应答文件";
        const fileExt = ((_e = fileName.split(".").pop()) == null ? void 0 : _e.toLowerCase()) || "docx";
        const isWordDoc = ["doc", "docx"].includes(fileExt);
        docs.businessResponseFile = {
          success: true,
          outputFile: businessFile.file_path,
          downloadUrl: getDownloadUrl(businessFile.file_path),
          previewUrl: isWordDoc ? `/api/business-response/preview/${projectId}` : void 0,
          stats: businessFile.stats || {},
          message: "该项目已有商务应答文件",
          isHistory: true,
          generated_at: businessFile.generated_at || step1Data.updated_at
        };
        console.log(`✅ 历史商务应答: ${fileName}`);
      }
      if (step1Data == null ? void 0 : step1Data.technical_point_to_point_file) {
        const p2pFile = step1Data.technical_point_to_point_file;
        const fileName = ((_f = p2pFile.file_path) == null ? void 0 : _f.split("/").pop()) || "点对点应答文件";
        const fileExt = ((_g = fileName.split(".").pop()) == null ? void 0 : _g.toLowerCase()) || "docx";
        const isWordDoc = ["doc", "docx"].includes(fileExt);
        docs.p2pResponseFile = {
          success: true,
          outputFile: p2pFile.file_path,
          downloadUrl: getDownloadUrl(p2pFile.file_path),
          previewUrl: isWordDoc ? `/api/point-to-point/preview/${projectId}` : void 0,
          stats: p2pFile.stats || {},
          message: "该项目已有点对点应答文件",
          isHistory: true,
          generated_at: p2pFile.generated_at || step1Data.updated_at
        };
        console.log(`✅ 历史点对点应答: ${fileName}`);
      }
      if (step1Data == null ? void 0 : step1Data.technical_proposal_file) {
        const proposalFile = step1Data.technical_proposal_file;
        const fileName = ((_h = proposalFile.file_path) == null ? void 0 : _h.split("/").pop()) || "技术方案文件";
        const fileExt = ((_i = fileName.split(".").pop()) == null ? void 0 : _i.toLowerCase()) || "docx";
        const isWordDoc = ["doc", "docx"].includes(fileExt);
        docs.techProposalFile = {
          success: true,
          outputFile: proposalFile.file_path,
          downloadUrl: getDownloadUrl(proposalFile.file_path),
          previewUrl: isWordDoc ? `/api/tech-proposal/preview/${projectId}` : void 0,
          stats: proposalFile.stats || {},
          message: "该项目已有技术方案文件",
          isHistory: true,
          generated_at: proposalFile.generated_at || step1Data.updated_at
        };
        console.log(`✅ 历史技术方案: ${fileName}`);
      }
      currentDocuments.value = docs;
      if (callbacks == null ? void 0 : callbacks.onDocumentsLoaded) {
        callbacks.onDocumentsLoaded(docs);
      }
    } catch (err) {
      error.value = "加载项目文档失败";
      ElMessage.error(error.value);
      console.error("Load project documents error:", err);
    } finally {
      loading.value = false;
    }
  };
  const clearDocuments = () => {
    currentDocuments.value = {
      tenderFile: null,
      templateFile: null,
      technicalFile: null,
      businessResponseFile: null,
      p2pResponseFile: null,
      techProposalFile: null
    };
  };
  const restoreProjectFromStore = async (callbacks) => {
    if (projectStore.projectId) {
      console.log(`🔄 从Store恢复项目: ${projectStore.projectId}`);
      await handleProjectChange(projectStore.projectId, callbacks);
      return projectStore.projectId;
    }
    return null;
  };
  const filePathToUploadFile = (filePath, fileName) => {
    const name = fileName || filePath.split("/").pop() || "文件";
    return {
      name,
      url: filePath,
      status: "success",
      uid: Date.now() + Math.random(),
      size: 0
    };
  };
  const getDownloadUrl = (filePath) => {
    if (filePath.startsWith("/api/")) {
      return filePath.includes("?") ? `${filePath}&download=true` : `${filePath}?download=true`;
    }
    let apiPath = filePath;
    const absolutePrefix = "/Users/lvhe/Downloads/zhongbiao/zhongbiao/";
    if (apiPath.startsWith(absolutePrefix)) {
      apiPath = apiPath.substring(absolutePrefix.length);
    }
    if (apiPath.startsWith("ai_tender_system/data/")) {
      apiPath = apiPath.substring("ai_tender_system/data/".length);
    } else if (apiPath.startsWith("data/")) {
      apiPath = apiPath.substring("data/".length);
    }
    return `/api/files/serve/${apiPath}?download=true`;
  };
  return {
    // 状态
    projects,
    loading,
    error,
    currentDocuments,
    // 计算属性
    selectedProject,
    hasProjects,
    hasTenderFile,
    hasTemplateFile,
    hasTechnicalFile,
    // 核心函数
    loadProjects,
    handleProjectChange,
    loadProjectDocuments,
    // 辅助函数
    clearDocuments,
    restoreProjectFromStore,
    filePathToUploadFile,
    getDownloadUrl
  };
}
export {
  useProjectDocuments as u
};
