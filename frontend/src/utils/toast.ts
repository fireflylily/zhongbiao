/**
 * Toast 提示工具
 * 封装 Element Plus 的 ElMessage
 */
import { ElMessage } from 'element-plus'

export const showToast = {
  /**
   * 成功提示
   */
  success(message: string, duration: number = 3000) {
    ElMessage.success({
      message,
      duration
    })
  },

  /**
   * 错误提示
   */
  error(message: string, duration: number = 3000) {
    ElMessage.error({
      message,
      duration
    })
  },

  /**
   * 警告提示
   */
  warning(message: string, duration: number = 3000) {
    ElMessage.warning({
      message,
      duration
    })
  },

  /**
   * 信息提示
   */
  info(message: string, duration: number = 3000) {
    ElMessage.info({
      message,
      duration
    })
  }
}
