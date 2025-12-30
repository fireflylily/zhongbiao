"""
重试策略模块
提供智能体调用的自动重试机制，支持指数退避
"""

import time
import logging
import functools
from typing import Callable, Any, Optional, Type, Tuple, List
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3           # 最大重试次数
    base_delay: float = 2.0         # 基础延迟(秒)
    backoff_factor: float = 2.0     # 退避因子
    max_delay: float = 60.0         # 最大延迟(秒)

    # 不重试的异常类型
    non_retryable_exceptions: Tuple[Type[Exception], ...] = (
        ValueError,
        TypeError,
        FileNotFoundError,
        PermissionError,
    )


class RetryPolicy:
    """
    重试策略类

    支持:
    - 指数退避
    - 可配置的最大重试次数
    - 可配置的不重试异常类型
    - 重试回调通知
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.logger = logging.getLogger(f"{__name__}.RetryPolicy")

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """
        判断是否应该重试

        Args:
            attempt: 当前尝试次数(从1开始)
            error: 捕获的异常

        Returns:
            是否应该重试
        """
        # 超过最大重试次数
        if attempt >= self.config.max_attempts:
            return False

        # 不可重试的异常类型
        if isinstance(error, self.config.non_retryable_exceptions):
            self.logger.debug(f"异常类型 {type(error).__name__} 不可重试")
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """
        计算重试延迟(指数退避)

        Args:
            attempt: 当前尝试次数(从1开始)

        Returns:
            延迟秒数
        """
        delay = self.config.base_delay * (self.config.backoff_factor ** (attempt - 1))
        return min(delay, self.config.max_delay)

    def execute_with_retry(
        self,
        func: Callable,
        *args,
        on_retry: Optional[Callable[[int, Exception, float], None]] = None,
        **kwargs
    ) -> Any:
        """
        带重试的函数执行

        Args:
            func: 要执行的函数
            *args: 函数参数
            on_retry: 重试回调函数，参数为(attempt, error, delay)
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果

        Raises:
            Exception: 重试次数耗尽后抛出最后一次的异常
        """
        last_error = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e

                if not self.should_retry(attempt, e):
                    self.logger.error(
                        f"函数 {func.__name__} 执行失败，不再重试: {e}"
                    )
                    raise

                delay = self.get_delay(attempt)

                self.logger.warning(
                    f"函数 {func.__name__} 第{attempt}次执行失败，"
                    f"将在{delay:.1f}秒后重试 ({attempt}/{self.config.max_attempts}): {e}"
                )

                # 调用重试回调
                if on_retry:
                    try:
                        on_retry(attempt, e, delay)
                    except Exception as callback_error:
                        self.logger.warning(f"重试回调执行失败: {callback_error}")

                time.sleep(delay)

        # 所有重试都失败
        self.logger.error(
            f"函数 {func.__name__} 重试{self.config.max_attempts}次后仍失败"
        )
        raise last_error

    async def execute_with_retry_async(
        self,
        func: Callable,
        *args,
        on_retry: Optional[Callable[[int, Exception, float], None]] = None,
        **kwargs
    ) -> Any:
        """
        带重试的异步函数执行

        Args:
            func: 要执行的异步函数
            *args: 函数参数
            on_retry: 重试回调函数
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果
        """
        import asyncio

        last_error = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e

                if not self.should_retry(attempt, e):
                    self.logger.error(
                        f"异步函数 {func.__name__} 执行失败，不再重试: {e}"
                    )
                    raise

                delay = self.get_delay(attempt)

                self.logger.warning(
                    f"异步函数 {func.__name__} 第{attempt}次执行失败，"
                    f"将在{delay:.1f}秒后重试 ({attempt}/{self.config.max_attempts}): {e}"
                )

                if on_retry:
                    try:
                        on_retry(attempt, e, delay)
                    except Exception as callback_error:
                        self.logger.warning(f"重试回调执行失败: {callback_error}")

                await asyncio.sleep(delay)

        raise last_error


def retry(
    max_attempts: int = 3,
    base_delay: float = 2.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    non_retryable: Tuple[Type[Exception], ...] = ()
):
    """
    重试装饰器

    用法:
        @retry(max_attempts=3, base_delay=2)
        def my_function():
            ...

    Args:
        max_attempts: 最大重试次数
        base_delay: 基础延迟
        backoff_factor: 退避因子
        max_delay: 最大延迟
        non_retryable: 不重试的异常类型
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        backoff_factor=backoff_factor,
        max_delay=max_delay,
        non_retryable_exceptions=non_retryable + RetryConfig.non_retryable_exceptions
    )
    policy = RetryPolicy(config)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return policy.execute_with_retry(func, *args, **kwargs)
        return wrapper

    return decorator


class RetryContext:
    """
    重试上下文，用于跟踪单次执行的重试状态
    """

    def __init__(self, policy: RetryPolicy, operation_name: str = ""):
        self.policy = policy
        self.operation_name = operation_name
        self.attempts: List[dict] = []
        self.start_time: float = 0
        self.end_time: float = 0
        self.success: bool = False
        self.final_error: Optional[Exception] = None

    def record_attempt(
        self,
        attempt: int,
        success: bool,
        duration_ms: float,
        error: Optional[Exception] = None
    ):
        """记录一次尝试"""
        self.attempts.append({
            "attempt": attempt,
            "success": success,
            "duration_ms": duration_ms,
            "error": str(error) if error else None,
            "error_type": type(error).__name__ if error else None
        })

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "operation_name": self.operation_name,
            "total_attempts": len(self.attempts),
            "success": self.success,
            "attempts": self.attempts,
            "total_duration_ms": (self.end_time - self.start_time) * 1000 if self.end_time else 0,
            "final_error": str(self.final_error) if self.final_error else None
        }


# 默认重试策略实例
default_retry_policy = RetryPolicy()
