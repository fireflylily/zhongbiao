/**
 * 路由工具函数
 *
 * 提供路由相关的辅助方法
 */

import type { RouteLocationNormalized, RouteRecordNormalized } from 'vue-router'
import type { Breadcrumb, MenuItem } from '@/types/router'
import { routes, legacyHashRoutes } from './routes'

/**
 * 获取路由元信息
 * @param route - 路由对象
 * @returns 路由元信息
 */
export function getRouteMeta(route: RouteLocationNormalized) {
  return route.meta || {}
}

/**
 * 生成面包屑导航
 * @param route - 当前路由
 * @returns 面包屑数组
 */
export function getBreadcrumbs(route: RouteLocationNormalized): Breadcrumb[] {
  const breadcrumbs: Breadcrumb[] = []

  // 过滤掉不需要显示的路由
  const matched = route.matched.filter((r) => {
    return r.meta?.title && !r.meta?.hideBreadcrumb
  })

  // 转换为面包屑格式
  matched.forEach((r, index) => {
    breadcrumbs.push({
      title: r.meta.title as string,
      path: index === matched.length - 1 ? undefined : r.path, // 最后一项不可点击
      icon: r.meta.icon as string,
      disabled: index === matched.length - 1
    })
  })

  return breadcrumbs
}

/**
 * 判断路由是否激活
 * @param routePath - 目标路由路径
 * @param currentPath - 当前路由路径
 * @returns 是否激活
 */
export function isActiveRoute(routePath: string, currentPath: string): boolean {
  if (routePath === '/') {
    return currentPath === '/'
  }
  return currentPath.startsWith(routePath)
}

/**
 * 从路由表生成菜单项
 * @param routes - 路由配置数组
 * @param parentPath - 父级路径
 * @returns 菜单项数组
 */
export function generateMenuFromRoutes(
  routes: RouteRecordNormalized[],
  parentPath: string = ''
): MenuItem[] {
  const menuItems: MenuItem[] = []

  routes.forEach((route) => {
    // 跳过不显示在菜单中的路由
    if (route.meta?.showInMenu === false) {
      return
    }

    // 跳过没有title的路由
    if (!route.meta?.title) {
      return
    }

    const fullPath = parentPath + (route.path.startsWith('/') ? route.path : `/${route.path}`)

    const menuItem: MenuItem = {
      name: route.name as string,
      path: fullPath,
      title: route.meta.title as string,
      icon: route.meta.icon as string,
      order: route.meta.order as number,
      meta: route.meta,
      children: []
    }

    // 递归处理子路由
    if (route.children && route.children.length > 0) {
      menuItem.children = generateMenuFromRoutes(route.children, fullPath)
    }

    menuItems.push(menuItem)
  })

  // 按order排序
  menuItems.sort((a, b) => (a.order || 999) - (b.order || 999))

  return menuItems
}

/**
 * 查找路由配置
 * @param routeName - 路由名称
 * @param routes - 路由配置数组
 * @returns 找到的路由配置
 */
export function findRouteByName(
  routeName: string,
  routes: RouteRecordNormalized[]
): RouteRecordNormalized | null {
  for (const route of routes) {
    if (route.name === routeName) {
      return route
    }
    if (route.children && route.children.length > 0) {
      const found = findRouteByName(routeName, route.children)
      if (found) return found
    }
  }
  return null
}

/**
 * 检查路由是否需要权限
 * @param route - 路由对象
 * @param userPermissions - 用户权限列表
 * @returns 是否有权限
 */
export function hasRoutePermission(
  route: RouteLocationNormalized,
  userPermissions: string[]
): boolean {
  const permission = route.meta?.permission

  // 没有设置权限要求，直接通过
  if (!permission) {
    return true
  }

  // 字符串权限
  if (typeof permission === 'string') {
    return userPermissions.includes(permission)
  }

  // 数组权限(任一满足即可)
  if (Array.isArray(permission)) {
    return permission.some((p) => userPermissions.includes(p))
  }

  return false
}

/**
 * 获取路由的完整路径(包括父级)
 * @param route - 路由对象
 * @returns 完整路径
 */
export function getFullPath(route: RouteLocationNormalized): string {
  return route.matched.map((r) => r.path).join('/')
}

/**
 * 格式化路由查询参数为URL字符串
 * @param query - 查询参数对象
 * @returns 格式化后的查询字符串
 */
export function formatQueryString(query: Record<string, any>): string {
  const params = new URLSearchParams()

  Object.entries(query).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params.append(key, String(value))
    }
  })

  const queryString = params.toString()
  return queryString ? `?${queryString}` : ''
}

/**
 * 解析URL查询字符串
 * @param queryString - 查询字符串
 * @returns 查询参数对象
 */
export function parseQueryString(queryString: string): Record<string, string> {
  const params = new URLSearchParams(queryString)
  const query: Record<string, string> = {}

  params.forEach((value, key) => {
    query[key] = value
  })

  return query
}

/**
 * 处理旧hash路由重定向
 * @param hash - URL hash值
 * @returns 新路由路径(如果需要重定向)
 */
export function handleLegacyHashRoute(hash: string): string | null {
  // 使用导入的旧路由映射
  if (hash && legacyHashRoutes[hash]) {
    return legacyHashRoutes[hash]
  }

  return null
}

/**
 * 获取路由页面标题
 * @param route - 路由对象
 * @param defaultTitle - 默认标题
 * @returns 页面标题
 */
export function getPageTitle(
  route: RouteLocationNormalized,
  defaultTitle: string = '元景AI智能标书生成平台'
): string {
  const routeTitle = route.meta?.title as string

  if (routeTitle) {
    return `${routeTitle} - ${defaultTitle}`
  }

  return defaultTitle
}

/**
 * 构建完整URL(包含baseURL)
 * @param path - 路径
 * @param baseURL - 基础URL
 * @returns 完整URL
 */
export function buildFullUrl(path: string, baseURL: string = ''): string {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }

  return `${baseURL}${path.startsWith('/') ? path : `/${path}`}`
}
