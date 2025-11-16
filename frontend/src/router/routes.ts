/**
 * 路由表定义
 *
 * 定义应用所有路由配置，采用Lazy Loading提升性能
 */

import type { RouteRecordRaw } from 'vue-router'

/**
 * 路由表
 */
export const routes: RouteRecordRaw[] = [
  // ==================== 登录页 ====================
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      requiresAuth: false,
      title: '登录',
      hideBreadcrumb: true,
      showInMenu: false
    }
  },

  // ==================== 主布局路由 ====================
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    redirect: { name: 'Home' },
    children: [
      // ========== 工作台 ==========
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home/Dashboard.vue'),
        meta: {
          title: '工作台',
          icon: 'bi-house',
          category: 'workspace',
          order: 1,
          affix: true,
          description: '项目总览和快捷入口'
        }
      },

      // ========== 项目管理 ==========
      {
        path: 'tender-management',
        name: 'TenderManagement',
        component: () => import('@/views/Tender/Management.vue'),
        meta: {
          title: '投标管理',
          icon: 'bi-file-earmark-text',
          category: 'project',
          order: 2,
          keepAlive: true,
          description: 'HITL人机协同系统'
        }
      },

      // 项目详情页
      {
        path: 'tender-management/:id',
        name: 'TenderManagementDetail',
        component: () => import('@/views/Tender/ManagementDetail.vue'),
        meta: {
          title: '项目详情',
          icon: 'bi-file-earmark-text',
          parent: 'TenderManagement',
          showInMenu: false,
          hideBreadcrumb: false,
          description: '查看项目详细信息和资格要求'
        }
      },

      // ========== AI核心工具 - 智能应答 ==========
      {
        path: 'business-response',
        name: 'BusinessResponse',
        component: () => import('@/views/Business/Response.vue'),
        meta: {
          title: '商务应答',
          icon: 'bi-briefcase',
          category: 'ai-tools',
          order: 3,
          description: '智能生成商务应答文档'
        }
      },

      {
        path: 'point-to-point',
        name: 'PointToPoint',
        component: () => import('@/views/Business/PointToPoint.vue'),
        meta: {
          title: '点对点应答',
          icon: 'bi-arrow-left-right',
          category: 'ai-tools',
          order: 4,
          description: '针对招标要求逐点响应'
        }
      },

      // ========== AI核心工具 - 方案生成 ==========
      {
        path: 'tech-proposal',
        name: 'TechProposal',
        component: () => import('@/views/Business/TechProposal.vue'),
        meta: {
          title: '技术方案',
          icon: 'bi-file-code',
          category: 'ai-tools',
          order: 5,
          description: 'AI生成技术方案大纲'
        }
      },

      // ========== AI核心工具 - 智能评审 ==========
      {
        path: 'tender-scoring',
        name: 'TenderScoring',
        component: () => import('@/views/Tender/Scoring.vue'),
        meta: {
          title: '标书评分',
          icon: 'bi-star',
          category: 'ai-tools',
          order: 6,
          description: 'AI辅助标书评分和风险分析'
        }
      },

      // ========== 知识中心 ==========
      {
        path: 'knowledge',
        name: 'Knowledge',
        redirect: { name: 'CompanyLibrary' },
        meta: {
          title: '知识中心',
          icon: 'bi-book',
          order: 7,
          description: 'AI系统的大脑和资料库'
        },
        children: [
          // 企业库
          {
            path: 'company-library',
            name: 'CompanyLibrary',
            component: () => import('@/views/Knowledge/CompanyLibrary.vue'),
            meta: {
              title: '企业库',
              icon: 'bi-building',
              order: 1,
              parent: 'Knowledge',
              keepAlive: true,
              description: '管理企业基本信息和资质证书'
            }
          },

          // 企业详情
          {
            path: 'company/:id',
            name: 'CompanyDetail',
            component: () => import('@/views/Knowledge/CompanyDetail.vue'),
            meta: {
              title: '企业详情',
              icon: 'bi-building',
              parent: 'Knowledge',
              showInMenu: false,
              hideBreadcrumb: false,
              description: '查看和编辑企业详细信息'
            }
          },

          // 案例库
          {
            path: 'case-library',
            name: 'CaseLibrary',
            component: () => import('@/views/Knowledge/CaseLibrary.vue'),
            meta: {
              title: '案例库',
              icon: 'bi-archive',
              order: 2,
              parent: 'Knowledge',
              keepAlive: true,
              description: '管理历史项目案例'
            }
          },

          // 案例详情
          {
            path: 'case/:id',
            name: 'CaseDetail',
            component: () => import('@/views/Knowledge/CaseDetail.vue'),
            meta: {
              title: '案例详情',
              icon: 'bi-archive',
              parent: 'Knowledge',
              showInMenu: false,
              hideBreadcrumb: false,
              description: '查看和编辑案例详细信息'
            }
          },

          // 文档库
          {
            path: 'document-library',
            name: 'DocumentLibrary',
            component: () => import('@/views/Knowledge/DocumentLibrary.vue'),
            meta: {
              title: '文档库',
              icon: 'bi-folder',
              order: 3,
              parent: 'Knowledge',
              keepAlive: true,
              description: '管理企业知识文档'
            }
          },

          // 简历库
          {
            path: 'resume-library',
            name: 'ResumeLibrary',
            component: () => import('@/views/Knowledge/ResumeLibrary.vue'),
            meta: {
              title: '简历库',
              icon: 'bi-person-badge',
              order: 4,
              parent: 'Knowledge',
              keepAlive: true,
              description: '管理人员简历信息'
            }
          },

          // 简历详情
          {
            path: 'resume/:id',
            name: 'ResumeDetail',
            component: () => import('@/views/Knowledge/ResumeDetail.vue'),
            meta: {
              title: '简历详情',
              icon: 'bi-person-badge',
              parent: 'Knowledge',
              showInMenu: false,
              hideBreadcrumb: false,
              description: '查看和编辑简历详细信息'
            }
          }
        ]
      },

      // ========== 开发工具 ==========
      {
        path: 'demo',
        name: 'Demo',
        component: () => import('@/views/Demo/index.vue'),
        meta: {
          title: '工具演示',
          icon: 'bi-tools',
          category: 'dev-tools',
          order: 8,
          keepAlive: true,
          description: '工具函数和组合式函数演示',
          showInMenu: import.meta.env.DEV // 仅在开发环境显示
        }
      },

      // ========== 编辑器测试 ==========
      {
        path: 'editor-test',
        name: 'EditorTest',
        component: () => import('@/views/EditorTest.vue'),
        meta: {
          title: '编辑器测试',
          icon: 'bi-pencil-square',
          category: 'dev-tools',
          order: 9,
          description: 'Umo Editor功能测试',
          showInMenu: import.meta.env.DEV // 仅在开发环境显示
        }
      },

      // ========== 解析方法对比工具 ==========
      {
        path: 'parser-comparison',
        name: 'ParserComparison',
        component: () => import('@/views/Debug/ParserComparison.vue'),
        meta: {
          title: '目录解析对比',
          icon: 'bi-file-earmark-diff',
          category: 'dev-tools',
          order: 10,
          description: '对比不同解析方法的准确率',
          showInMenu: import.meta.env.DEV // 仅在开发环境显示
        }
      }
    ]
  },

  // ==================== 投标处理页面(独立布局) ====================
  {
    path: '/tender-processing/:projectId?',
    name: 'TenderProcessing',
    component: () => import('@/views/Tender/Processing.vue'),
    meta: {
      requiresAuth: true,
      title: '投标处理',
      icon: 'bi-gear',
      showInMenu: false,
      hideBreadcrumb: false,
      customClass: 'tender-processing-page'
    }
  },

  // ==================== 系统页面 ====================
  {
    path: '/system-status',
    name: 'SystemStatus',
    component: () => import('@/views/System/Status.vue'),
    meta: {
      requiresAuth: true,
      title: '系统状态',
      icon: 'bi-hdd',
      showInMenu: false,
      permission: 'admin:view'
    }
  },

  {
    path: '/help',
    name: 'Help',
    component: () => import('@/views/System/Help.vue'),
    meta: {
      requiresAuth: false,
      title: '帮助中心',
      icon: 'bi-question-circle',
      showInMenu: false
    }
  },

  // ==================== 错误页面 ====================
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/Error/Forbidden.vue'),
    meta: {
      requiresAuth: false,
      title: '403 - 无权限访问',
      hideBreadcrumb: true,
      showInMenu: false
    }
  },

  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/Error/NotFound.vue'),
    meta: {
      requiresAuth: false,
      title: '404 - 页面未找到',
      hideBreadcrumb: true,
      showInMenu: false
    }
  },

  {
    path: '/500',
    name: 'ServerError',
    component: () => import('@/views/Error/ServerError.vue'),
    meta: {
      requiresAuth: false,
      title: '500 - 服务器错误',
      hideBreadcrumb: true,
      showInMenu: false
    }
  },

  // ==================== 捕获所有未匹配路由 ====================
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'NotFound' }
  }
]

/**
 * 旧路由重定向映射(兼容旧hash路由)
 */
export const legacyHashRoutes: Record<string, string> = {
  '#home': '/',
  '#project-overview': '/project-overview',
  '#tender-management': '/tender-management',
  '#business-response': '/business-response',
  '#point-to-point': '/point-to-point',
  '#tech-proposal': '/tech-proposal',
  '#check-export': '/check-export',
  '#tender-scoring': '/tender-scoring',
  '#knowledge-company-library': '/knowledge/company-library',
  '#knowledge-case-library': '/knowledge/case-library',
  '#knowledge-document-library': '/knowledge/document-library',
  '#knowledge-resume-library': '/knowledge/resume-library'
}

/**
 * 动态路由(需要权限加载)
 */
export const dynamicRoutes: RouteRecordRaw[] = [
  // 未来扩展: 管理员页面、用户设置页面等
]
