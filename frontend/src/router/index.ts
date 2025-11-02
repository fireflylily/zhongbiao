/**
 * Vue Router配置
 *
 * 创建和配置Router实例
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationNormalized, RouterScrollBehavior } from 'vue-router'
import { routes } from './routes'
import { setupRouterGuards } from './guards'

/**
 * 滚动行为配置
 */
const scrollBehavior: RouterScrollBehavior = (to, from, savedPosition) => {
  // 如果有保存的滚动位置(浏览器前进/后退)
  if (savedPosition) {
    return savedPosition
  }

  // 如果有hash锚点
  if (to.hash) {
    return {
      el: to.hash,
      behavior: 'smooth',
      top: 80 // 偏移导航栏高度
    }
  }

  // 如果路由配置了保持滚动位置
  if (to.meta.keepScrollPosition) {
    return false
  }

  // 默认滚动到顶部
  return { top: 0, behavior: 'smooth' }
}

/**
 * 创建Router实例
 */
export const router = createRouter({
  // 使用HTML5 History模式
  history: createWebHistory(import.meta.env.BASE_URL),

  // 路由配置
  routes,

  // 滚动行为
  scrollBehavior,

  // 严格模式(路径末尾斜杠必须匹配)
  strict: false,

  // 大小写敏感
  sensitive: false
})

// 设置路由守卫
setupRouterGuards(router)

/**
 * 导出router实例
 */
export default router

/**
 * 重置路由(用于动态添加路由后的重置)
 */
export function resetRouter(): void {
  const newRouter = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
  })

  ;(router as any).matcher = (newRouter as any).matcher
}

/**
 * 动态添加路由
 * @param routes - 路由配置数组
 */
export function addDynamicRoutes(routes: any[]): void {
  routes.forEach((route) => {
    router.addRoute(route)
  })
}

/**
 * 判断路由是否存在
 * @param name - 路由名称
 * @returns 是否存在
 */
export function hasRoute(name: string): boolean {
  return router.hasRoute(name)
}

/**
 * 获取所有路由
 * @returns 路由数组
 */
export function getAllRoutes() {
  return router.getRoutes()
}

/**
 * 导航到指定路由(带错误处理)
 * @param to - 目标路由
 */
export async function navigateTo(to: any): Promise<void> {
  try {
    await router.push(to)
  } catch (error: any) {
    // 忽略重复导航错误
    if (error.name === 'NavigationDuplicated') {
      return
    }

    console.error('[Router] Navigation failed:', error)
    throw error
  }
}

/**
 * 替换当前路由(不会在历史记录中留下记录)
 * @param to - 目标路由
 */
export async function replaceTo(to: any): Promise<void> {
  try {
    await router.replace(to)
  } catch (error: any) {
    if (error.name === 'NavigationDuplicated') {
      return
    }

    console.error('[Router] Replace failed:', error)
    throw error
  }
}

/**
 * 返回上一页
 */
export function goBack(): void {
  router.back()
}

/**
 * 前进到下一页
 */
export function goForward(): void {
  router.forward()
}

/**
 * 跳转指定步数(-1为后退一步，1为前进一步)
 * @param delta - 步数
 */
export function go(delta: number): void {
  router.go(delta)
}
