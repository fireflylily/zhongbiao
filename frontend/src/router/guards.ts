/**
 * 路由守卫配置
 *
 * 处理路由鉴权、权限检查、页面切换等逻辑
 */

import type { Router, RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { useNotification } from '@/composables/useNotification'
import { getPageTitle, handleLegacyHashRoute } from './utils'

// Token验证缓存（5分钟有效）
let tokenValidationCache: {
  lastValidated: number | null
  isValid: boolean
} = {
  lastValidated: null,
  isValid: false
}

const TOKEN_VALIDATION_CACHE_DURATION = 5 * 60 * 1000 // 5分钟

/**
 * 设置路由守卫
 * @param router - Router实例
 */
export function setupRouterGuards(router: Router): void {
  setupBeforeEachGuard(router)
  setupAfterEachGuard(router)
  setupErrorHandler(router)
}

/**
 * 全局前置守卫（简化版 - 只保留登录检查）
 */
function setupBeforeEachGuard(router: Router): void {
  router.beforeEach(async (to, from, next) => {
    // 开始加载进度条
    startProgress()

    // 处理旧hash路由重定向
    if (handleOldHashRoute(to, next)) {
      return
    }

    // 鉴权检查（只检查登录状态）
    const authResult = await checkAuthentication(to, from, next)
    if (!authResult) {
      stopProgress()
      return
    }

    // 设置页面标题
    setPageTitle(to)

    // 继续导航
    next()
  })
}

/**
 * 全局后置守卫
 */
function setupAfterEachGuard(router: Router): void {
  router.afterEach((to, from) => {
    // 停止加载进度条
    stopProgress()

    // 记录路由跳转日志
    logNavigation(to, from)

    // 页面加载完成事件(可用于埋点统计)
    emitPageViewEvent(to)
  })
}

/**
 * 路由错误处理
 */
function setupErrorHandler(router: Router): void {
  router.onError((error) => {
    console.error('[Router] Navigation error:', error)

    const { error: showError } = useNotification()
    stopProgress()

    // 处理不同类型的错误
    if (error.message.includes('Failed to fetch dynamically imported module')) {
      showError('页面加载失败，请刷新页面重试')
    } else if (error.message.includes('Redirected when going from')) {
      // 重定向循环错误
      showError('路由配置错误，请联系管理员')
    } else {
      showError('页面加载失败')
    }
  })
}

// ==================== 辅助函数 ====================

/**
 * 开始加载进度条
 */
function startProgress(): void {
  const settingsStore = useSettingsStore()

  if (settingsStore.showProgress) {
    // 使用NProgress或自定义进度条
    if (typeof window !== 'undefined' && (window as any).NProgress) {
      ;(window as any).NProgress.start()
    }
  }
}

/**
 * 停止加载进度条
 */
function stopProgress(): void {
  if (typeof window !== 'undefined' && (window as any).NProgress) {
    ;(window as any).NProgress.done()
  }
}

/**
 * 处理旧hash路由重定向
 * @returns true表示已处理，不再继续导航
 */
function handleOldHashRoute(
  to: RouteLocationNormalized,
  next: NavigationGuardNext
): boolean {
  // 检查URL中是否有旧hash
  const hash = window.location.hash
  const newPath = handleLegacyHashRoute(hash)

  if (newPath) {
    console.log(`[Router] 重定向旧hash路由: ${hash} → ${newPath}`)
    next({ path: newPath, replace: true })
    return true
  }

  return false
}

/**
 * 鉴权检查
 * @returns true表示通过，false表示已处理(不再继续导航)
 */
async function checkAuthentication(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): Promise<boolean> {
  const userStore = useUserStore()

  // 如果页面不需要登录，直接通过
  if (to.meta.requiresAuth === false) {
    return true
  }

  // 检查是否已登录
  if (!userStore.isLoggedIn) {
    // 先静默尝试从localStorage恢复登录状态
    userStore.restoreFromStorage()

    // 如果有token，静默验证其有效性
    if (userStore.hasToken) {
      try {
        const isValid = await userStore.verifyToken()

        if (isValid) {
          // 静默恢复成功，直接放行
          console.log('[Router] 静默恢复登录状态成功')
          return true
        }
      } catch (error) {
        console.error('[Router] 静默Token验证失败:', error)
      }
    }

    // 确认无法恢复，静默重定向到登录页
    if (!userStore.isLoggedIn) {
      console.log(`[Router] 未登录，静默重定向到登录页: ${to.path}`)

      next({
        name: 'Login',
        query: { redirect: to.fullPath }, // 记录目标页面，登录后跳转
        replace: true
      })

      return false
    }
  }

  // ✅ 优化：使用缓存减少Token验证频率（5分钟内不重复验证）
  const now = Date.now()
  const cacheValid =
    tokenValidationCache.lastValidated !== null &&
    now - tokenValidationCache.lastValidated < TOKEN_VALIDATION_CACHE_DURATION &&
    tokenValidationCache.isValid

  if (cacheValid) {
    // 使用缓存结果，跳过API调用
    console.log('[Router] 使用缓存的Token验证结果（5分钟内）')
    return true
  }

  // 验证Token是否有效（调用API）
  try {
    const isValid = await userStore.verifyToken()

    // 更新缓存
    tokenValidationCache.lastValidated = now
    tokenValidationCache.isValid = isValid

    if (!isValid) {
      console.log('[Router] Token失效，静默重定向到登录页')

      // 清除登录状态和缓存
      await userStore.logout()
      tokenValidationCache.lastValidated = null
      tokenValidationCache.isValid = false

      next({
        name: 'Login',
        query: { redirect: to.fullPath },
        replace: true
      })

      return false
    }
  } catch (error) {
    console.error('[Router] Token验证失败:', error)

    // Token验证失败，清除缓存
    tokenValidationCache.lastValidated = null
    tokenValidationCache.isValid = false

    // Token验证失败，静默跳转到登录页
    await userStore.logout()

    next({
      name: 'Login',
      query: { redirect: to.fullPath },
      replace: true
    })

    return false
  }

  return true
}

/**
 * 权限检查（已移除 - 简化权限系统）
 * 现在只需要登录即可访问所有页面
 */

/**
 * 设置页面标题
 */
function setPageTitle(to: RouteLocationNormalized): void {
  const title = getPageTitle(to)
  document.title = title

  // 设置meta description(SEO)
  if (to.meta.description) {
    setMetaTag('description', to.meta.description as string)
  }

  // 设置meta keywords(SEO)
  if (to.meta.keywords && Array.isArray(to.meta.keywords)) {
    setMetaTag('keywords', (to.meta.keywords as string[]).join(', '))
  }
}

/**
 * 设置Meta标签
 */
function setMetaTag(name: string, content: string): void {
  let metaTag = document.querySelector(`meta[name="${name}"]`)

  if (!metaTag) {
    metaTag = document.createElement('meta')
    metaTag.setAttribute('name', name)
    document.head.appendChild(metaTag)
  }

  metaTag.setAttribute('content', content)
}

/**
 * 记录路由跳转日志
 */
function logNavigation(to: RouteLocationNormalized, from: RouteLocationNormalized): void {
  const fromName = from.name || 'unknown'
  const toName = to.name || 'unknown'

  console.log(`[Router] ${String(fromName)} → ${String(toName)}`, {
    from: from.path,
    to: to.path,
    params: to.params,
    query: to.query
  })
}

/**
 * 触发页面浏览事件(用于统计)
 */
function emitPageViewEvent(to: RouteLocationNormalized): void {
  // 可以在这里集成Google Analytics、百度统计等

  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new CustomEvent('pageview', {
        detail: {
          path: to.path,
          name: to.name,
          title: to.meta.title
        }
      })
    )
  }
}
