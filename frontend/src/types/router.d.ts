/**
 * Vue Router类型扩展
 *
 * 扩展Vue Router的RouteMeta接口，添加自定义元信息字段
 */

import 'vue-router'

declare module 'vue-router' {
  /**
   * 路由元信息接口扩展
   */
  interface RouteMeta {
    /**
     * 页面标题(用于document.title和面包屑)
     */
    title?: string

    /**
     * 图标类名(Bootstrap Icons)
     */
    icon?: string

    /**
     * 是否需要登录
     * @default true
     */
    requiresAuth?: boolean

    /**
     * 需要的权限(如: 'project:edit', 'admin:manage')
     */
    permission?: string | string[]

    /**
     * 是否缓存页面(用于<keep-alive>)
     * @default false
     */
    keepAlive?: boolean

    /**
     * 是否在菜单中显示
     * @default true
     */
    showInMenu?: boolean

    /**
     * 菜单分类(用于分组显示)
     * - workspace: 工作台
     * - project: 项目管理
     * - ai-tools: AI核心工具
     * - knowledge: 知识中心
     */
    category?: 'workspace' | 'project' | 'ai-tools' | 'knowledge' | string

    /**
     * 菜单排序(数字越小越靠前)
     */
    order?: number

    /**
     * 父级菜单(用于嵌套菜单)
     */
    parent?: string

    /**
     * 是否隐藏面包屑
     * @default false
     */
    hideBreadcrumb?: boolean

    /**
     * 自定义CSS类名(添加到页面容器)
     */
    customClass?: string

    /**
     * 页面描述(用于SEO)
     */
    description?: string

    /**
     * 页面关键词(用于SEO)
     */
    keywords?: string[]

    /**
     * 是否固定在标签页(Tabs)
     * @default false
     */
    affix?: boolean

    /**
     * 标签页激活颜色
     */
    activeColor?: string
  }
}

/**
 * 面包屑项
 */
export interface Breadcrumb {
  title: string
  path?: string
  icon?: string
  disabled?: boolean
}

/**
 * 菜单项(基于路由生成)
 */
export interface MenuItem {
  name: string
  path: string
  title: string
  icon?: string
  category?: string
  order?: number
  children?: MenuItem[]
  meta?: RouteMeta
}
