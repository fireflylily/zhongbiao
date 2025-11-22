import { C as defineStore, r as ref, c as computed } from "./vendor-MtO928VE.js";
import "./index.js";
import { t as tenderApi } from "./tender-DvsgeLWX.js";
const useProjectStore = defineStore("project", () => {
  const currentProject = ref(null);
  const projects = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0
  });
  const projectId = computed(
    () => {
      var _a, _b;
      return ((_a = currentProject.value) == null ? void 0 : _a.id) || ((_b = currentProject.value) == null ? void 0 : _b.project_id) || null;
    }
  );
  const projectName = computed(
    () => {
      var _a, _b;
      return ((_a = currentProject.value) == null ? void 0 : _a.name) || ((_b = currentProject.value) == null ? void 0 : _b.project_name) || "";
    }
  );
  const projectNumber = computed(
    () => {
      var _a, _b;
      return ((_a = currentProject.value) == null ? void 0 : _a.number) || ((_b = currentProject.value) == null ? void 0 : _b.project_number) || "";
    }
  );
  const projectStatus = computed(() => {
    var _a;
    return ((_a = currentProject.value) == null ? void 0 : _a.status) || null;
  });
  const hasCurrentProject = computed(() => !!currentProject.value);
  const projectsCount = computed(() => projects.value.length);
  const projectsOptions = computed(() => {
    return projects.value.map((project) => ({
      label: `${project.name} (${project.project_number})`,
      value: project.id
    }));
  });
  const totalPages = computed(() => {
    return Math.ceil(pagination.value.total / pagination.value.pageSize);
  });
  function setCurrentProject(project) {
    currentProject.value = project;
    saveToStorage();
  }
  async function setCurrentProjectById(projectId2) {
    loading.value = true;
    error.value = null;
    try {
      const response = await tenderApi.getProject(projectId2);
      if (response.success && response.data) {
        setCurrentProject(response.data);
        return true;
      }
      error.value = response.message || "获取项目详情失败";
      return false;
    } catch (err) {
      error.value = err.message || "获取项目详情失败";
      return false;
    } finally {
      loading.value = false;
    }
  }
  function clearCurrentProject() {
    currentProject.value = null;
    localStorage.removeItem("current_project");
  }
  async function fetchProjects(params) {
    loading.value = true;
    error.value = null;
    if (params == null ? void 0 : params.page) pagination.value.page = params.page;
    if (params == null ? void 0 : params.page_size) pagination.value.pageSize = params.page_size;
    try {
      const response = await tenderApi.getProjects({
        page: pagination.value.page,
        page_size: pagination.value.pageSize
      });
      if (response.success && response.data) {
        projects.value = response.data.items || response.data;
        pagination.value.total = response.data.total || projects.value.length;
      }
    } catch (err) {
      error.value = err.message || "获取项目列表失败";
      console.error("获取项目列表失败:", err);
    } finally {
      loading.value = false;
    }
  }
  async function fetchProject(projectId2) {
    loading.value = true;
    error.value = null;
    try {
      const response = await tenderApi.getProject(projectId2);
      if (response.success && response.data) {
        const index = projects.value.findIndex((p) => p.id === projectId2);
        if (index !== -1) {
          Object.assign(projects.value[index], {
            name: response.data.name,
            status: response.data.status,
            project_number: response.data.project_number
          });
        }
        return response.data;
      }
      error.value = response.message || "获取项目详情失败";
      return null;
    } catch (err) {
      error.value = err.message || "获取项目详情失败";
      return null;
    } finally {
      loading.value = false;
    }
  }
  async function createProject(data) {
    loading.value = true;
    error.value = null;
    try {
      const response = await tenderApi.createProject(data);
      if (response.success && response.data) {
        projects.value.unshift(response.data);
        pagination.value.total += 1;
        return response.data;
      }
      error.value = response.message || "创建项目失败";
      return null;
    } catch (err) {
      error.value = err.message || "创建项目失败";
      return null;
    } finally {
      loading.value = false;
    }
  }
  async function updateProject(projectId2, data) {
    var _a;
    loading.value = true;
    error.value = null;
    try {
      const response = await tenderApi.updateProject(projectId2, data);
      if (response.success && response.data) {
        const index = projects.value.findIndex((p) => p.id === projectId2);
        if (index !== -1) {
          Object.assign(projects.value[index], response.data);
        }
        if (((_a = currentProject.value) == null ? void 0 : _a.id) === projectId2) {
          Object.assign(currentProject.value, response.data);
          saveToStorage();
        }
        return true;
      }
      error.value = response.message || "更新项目失败";
      return false;
    } catch (err) {
      error.value = err.message || "更新项目失败";
      return false;
    } finally {
      loading.value = false;
    }
  }
  async function deleteProject(projectId2) {
    var _a;
    loading.value = true;
    error.value = null;
    try {
      const response = await tenderApi.deleteProject(projectId2);
      if (response.success) {
        projects.value = projects.value.filter((p) => p.id !== projectId2);
        pagination.value.total = Math.max(0, pagination.value.total - 1);
        if (((_a = currentProject.value) == null ? void 0 : _a.id) === projectId2) {
          clearCurrentProject();
        }
        return true;
      }
      error.value = response.message || "删除项目失败";
      return false;
    } catch (err) {
      error.value = err.message || "删除项目失败";
      return false;
    } finally {
      loading.value = false;
    }
  }
  async function refreshCurrentProject() {
    var _a;
    if (!((_a = currentProject.value) == null ? void 0 : _a.id)) {
      return;
    }
    const project = await fetchProject(currentProject.value.id);
    if (project) {
      currentProject.value = project;
      saveToStorage();
    }
  }
  function setPagination(page, pageSize) {
    pagination.value.page = page;
    pagination.value.pageSize = pageSize;
  }
  async function nextPage() {
    if (pagination.value.page < totalPages.value) {
      pagination.value.page += 1;
      await fetchProjects();
    }
  }
  async function prevPage() {
    if (pagination.value.page > 1) {
      pagination.value.page -= 1;
      await fetchProjects();
    }
  }
  function restoreFromStorage() {
    try {
      const savedProject = localStorage.getItem("current_project");
      if (savedProject) {
        currentProject.value = JSON.parse(savedProject);
      }
    } catch (err) {
      console.error("恢复项目状态失败:", err);
    }
  }
  function saveToStorage() {
    try {
      if (currentProject.value) {
        localStorage.setItem("current_project", JSON.stringify(currentProject.value));
      }
    } catch (err) {
      console.error("保存项目状态失败:", err);
    }
  }
  function $reset() {
    currentProject.value = null;
    projects.value = [];
    loading.value = false;
    error.value = null;
    pagination.value = {
      page: 1,
      pageSize: 10,
      total: 0
    };
    localStorage.removeItem("current_project");
  }
  return {
    // State
    currentProject,
    projects,
    loading,
    error,
    pagination,
    // Getters
    projectId,
    projectName,
    projectNumber,
    projectStatus,
    hasCurrentProject,
    projectsCount,
    projectsOptions,
    totalPages,
    // Actions
    setCurrentProject,
    setCurrentProjectById,
    clearCurrentProject,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
    refreshCurrentProject,
    setPagination,
    nextPage,
    prevPage,
    restoreFromStorage,
    saveToStorage,
    $reset
  };
});
export {
  useProjectStore as u
};
