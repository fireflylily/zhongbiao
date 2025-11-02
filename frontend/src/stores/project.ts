/**
 * 项目状态管理
 *
 * 管理当前项目和项目列表
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tenderApi } from '@/api'
import type { Project, ProjectDetail, ProjectState } from '@/types'

/**
 * 项目Store
 */
export const useProjectStore = defineStore('project', () => {
  // ==================== State ====================

  const currentProject = ref<ProjectDetail | null>(null)
  const projects = ref<Project[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0
  })

  // ==================== Getters ====================

  const projectId = computed(() => currentProject.value?.id || null)

  const projectName = computed(() => currentProject.value?.name || '')

  const projectNumber = computed(() => currentProject.value?.project_number || '')

  const projectStatus = computed(() => currentProject.value?.status || null)

  const hasCurrentProject = computed(() => !!currentProject.value)

  const projectsCount = computed(() => projects.value.length)

  const projectsOptions = computed(() => {
    return projects.value.map((project) => ({
      label: `${project.name} (${project.project_number})`,
      value: project.id
    }))
  })

  const totalPages = computed(() => {
    return Math.ceil(pagination.value.total / pagination.value.pageSize)
  })

  // ==================== Actions ====================

  /**
   * 设置当前项目
   */
  function setCurrentProject(project: ProjectDetail): void {
    currentProject.value = project
    saveToStorage()
  }

  /**
   * 通过ID设置当前项目
   */
  async function setCurrentProjectById(projectId: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await tenderApi.getProject(projectId)

      if (response.success && response.data) {
        setCurrentProject(response.data)
        return true
      }

      error.value = response.message || '获取项目详情失败'
      return false
    } catch (err: any) {
      error.value = err.message || '获取项目详情失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 清除当前项目
   */
  function clearCurrentProject(): void {
    currentProject.value = null
    localStorage.removeItem('current_project')
  }

  /**
   * 获取项目列表
   */
  async function fetchProjects(params?: {
    page?: number
    page_size?: number
  }): Promise<void> {
    loading.value = true
    error.value = null

    // 更新分页参数
    if (params?.page) pagination.value.page = params.page
    if (params?.page_size) pagination.value.pageSize = params.page_size

    try {
      const response = await tenderApi.getProjects({
        page: pagination.value.page,
        page_size: pagination.value.pageSize
      })

      if (response.success && response.data) {
        projects.value = response.data.items || response.data
        pagination.value.total = response.data.total || projects.value.length
      }
    } catch (err: any) {
      error.value = err.message || '获取项目列表失败'
      console.error('获取项目列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取项目详情
   */
  async function fetchProject(projectId: number): Promise<ProjectDetail | null> {
    loading.value = true
    error.value = null

    try {
      const response = await tenderApi.getProject(projectId)

      if (response.success && response.data) {
        // 更新列表中的项目信息
        const index = projects.value.findIndex((p) => p.id === projectId)
        if (index !== -1) {
          // 只更新基本信息
          Object.assign(projects.value[index], {
            name: response.data.name,
            status: response.data.status,
            project_number: response.data.project_number
          })
        }

        return response.data
      }

      error.value = response.message || '获取项目详情失败'
      return null
    } catch (err: any) {
      error.value = err.message || '获取项目详情失败'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建新项目
   */
  async function createProject(data: {
    name: string
    project_number: string
    company_id: number
    description?: string
  }): Promise<Project | null> {
    loading.value = true
    error.value = null

    try {
      const response = await tenderApi.createProject(data)

      if (response.success && response.data) {
        // 添加到列表开头
        projects.value.unshift(response.data)
        pagination.value.total += 1

        return response.data
      }

      error.value = response.message || '创建项目失败'
      return null
    } catch (err: any) {
      error.value = err.message || '创建项目失败'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新项目信息
   */
  async function updateProject(
    projectId: number,
    data: Partial<Project>
  ): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await tenderApi.updateProject(projectId, data)

      if (response.success && response.data) {
        // 更新列表中的项目
        const index = projects.value.findIndex((p) => p.id === projectId)
        if (index !== -1) {
          Object.assign(projects.value[index], response.data)
        }

        // 如果是当前项目，也更新
        if (currentProject.value?.id === projectId) {
          Object.assign(currentProject.value, response.data)
          saveToStorage()
        }

        return true
      }

      error.value = response.message || '更新项目失败'
      return false
    } catch (err: any) {
      error.value = err.message || '更新项目失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除项目
   */
  async function deleteProject(projectId: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await tenderApi.deleteProject(projectId)

      if (response.success) {
        // 从列表中移除
        projects.value = projects.value.filter((p) => p.id !== projectId)
        pagination.value.total = Math.max(0, pagination.value.total - 1)

        // 如果删除的是当前项目，清除当前项目
        if (currentProject.value?.id === projectId) {
          clearCurrentProject()
        }

        return true
      }

      error.value = response.message || '删除项目失败'
      return false
    } catch (err: any) {
      error.value = err.message || '删除项目失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 刷新当前项目
   */
  async function refreshCurrentProject(): Promise<void> {
    if (!currentProject.value?.id) {
      return
    }

    const project = await fetchProject(currentProject.value.id)
    if (project) {
      currentProject.value = project
      saveToStorage()
    }
  }

  /**
   * 设置分页
   */
  function setPagination(page: number, pageSize: number): void {
    pagination.value.page = page
    pagination.value.pageSize = pageSize
  }

  /**
   * 下一页
   */
  async function nextPage(): Promise<void> {
    if (pagination.value.page < totalPages.value) {
      pagination.value.page += 1
      await fetchProjects()
    }
  }

  /**
   * 上一页
   */
  async function prevPage(): Promise<void> {
    if (pagination.value.page > 1) {
      pagination.value.page -= 1
      await fetchProjects()
    }
  }

  /**
   * 从localStorage恢复状态
   */
  function restoreFromStorage(): void {
    try {
      const savedProject = localStorage.getItem('current_project')

      if (savedProject) {
        currentProject.value = JSON.parse(savedProject)
      }
    } catch (err) {
      console.error('恢复项目状态失败:', err)
    }
  }

  /**
   * 保存到localStorage
   */
  function saveToStorage(): void {
    try {
      if (currentProject.value) {
        localStorage.setItem('current_project', JSON.stringify(currentProject.value))
      }
    } catch (err) {
      console.error('保存项目状态失败:', err)
    }
  }

  /**
   * 重置状态
   */
  function $reset(): void {
    currentProject.value = null
    projects.value = []
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      pageSize: 10,
      total: 0
    }
    localStorage.removeItem('current_project')
  }

  // ==================== Return ====================

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
  }
})
