# -*- coding: utf-8 -*-
"""
统一日志管理模块
解决分散日志配置问题
"""

import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Dict, Any

from .config import get_config


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self.config = get_config()
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志系统"""
        # 创建日志目录
        log_dir = Path(self.config.app.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置根日志级别
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.app.log_level.upper()))
        
        # 清除现有的处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config.app.log_level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器（按天轮转）
        main_log_file = log_dir / "ai_tender_system.log"
        file_handler = TimedRotatingFileHandler(
            filename=main_log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # 保留30天的日志
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别的日志
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # 错误日志文件处理器
        error_log_file = log_dir / "errors.log"
        error_handler = RotatingFileHandler(
            filename=error_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def get_module_logger(self, module_name: str) -> logging.Logger:
        """获取模块专用日志器"""
        logger = self.get_logger(f"modules.{module_name}")
        
        # 为模块创建专门的日志文件
        log_dir = Path(self.config.app.log_dir)
        module_log_file = log_dir / f"{module_name}.log"
        
        # 检查是否已经有文件处理器
        has_file_handler = any(
            isinstance(h, (RotatingFileHandler, TimedRotatingFileHandler))
            and getattr(h, 'baseFilename', '').endswith(f"{module_name}.log")
            for h in logger.handlers
        )
        
        if not has_file_handler:
            # 创建模块专用的文件处理器
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            module_handler = RotatingFileHandler(
                filename=module_log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            module_handler.setLevel(logging.DEBUG)
            module_handler.setFormatter(formatter)
            logger.addHandler(module_handler)
        
        return logger
    
    def set_level(self, level: str):
        """设置全局日志级别"""
        level_obj = getattr(logging, level.upper())
        root_logger = logging.getLogger()
        root_logger.setLevel(level_obj)
        
        # 更新所有控制台处理器的级别
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
                handler.setLevel(level_obj)
    
    def create_performance_logger(self) -> logging.Logger:
        """创建性能监控日志器"""
        perf_logger = self.get_logger("performance")
        
        # 创建性能日志文件处理器
        log_dir = Path(self.config.app.log_dir)
        perf_log_file = log_dir / "performance.log"
        
        # 检查是否已经有性能日志处理器
        has_perf_handler = any(
            getattr(h, 'baseFilename', '').endswith("performance.log")
            for h in perf_logger.handlers
        )
        
        if not has_perf_handler:
            formatter = logging.Formatter(
                '%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            perf_handler = RotatingFileHandler(
                filename=perf_log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=3,
                encoding='utf-8'
            )
            perf_handler.setLevel(logging.INFO)
            perf_handler.setFormatter(formatter)
            perf_logger.addHandler(perf_handler)
            
            # 性能日志不传播到根日志器
            perf_logger.propagate = False
        
        return perf_logger
    
    def cleanup_old_logs(self, days: int = 30):
        """清理旧日志文件"""
        log_dir = Path(self.config.app.log_dir)
        
        if not log_dir.exists():
            return
        
        import time
        cutoff = time.time() - (days * 24 * 60 * 60)
        
        for log_file in log_dir.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    print(f"已清理旧日志文件: {log_file}")
            except Exception as e:
                print(f"清理日志文件失败 {log_file}: {e}")


# 全局日志管理器实例
_logger_manager = None


def get_logger_manager() -> LoggerManager:
    """获取日志管理器实例"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def get_logger(name: str = __name__) -> logging.Logger:
    """获取日志器的便捷函数"""
    manager = get_logger_manager()
    return manager.get_logger(name)


def get_module_logger(module_name: str) -> logging.Logger:
    """获取模块日志器的便捷函数"""
    manager = get_logger_manager()
    return manager.get_module_logger(module_name)


def setup_logging():
    """初始化日志系统的便捷函数"""
    get_logger_manager()


class PerformanceLogger:
    """性能监控日志器"""
    
    def __init__(self):
        self.logger = get_logger_manager().create_performance_logger()
    
    def log_operation(self, operation: str, duration: float, **kwargs):
        """记录操作性能"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.info(f"PERF | {operation} | {duration:.3f}s | {extra_info}")
    
    def log_api_call(self, api_name: str, duration: float, status: str, **kwargs):
        """记录API调用性能"""
        self.log_operation(f"API_{api_name}", duration, status=status, **kwargs)
    
    def log_document_processing(self, file_path: str, duration: float, size: int):
        """记录文档处理性能"""
        self.log_operation("DOC_PROCESS", duration, file=file_path, size=size)


# 全局性能日志器
_perf_logger = None


def get_performance_logger() -> PerformanceLogger:
    """获取性能日志器"""
    global _perf_logger
    if _perf_logger is None:
        _perf_logger = PerformanceLogger()
    return _perf_logger


# 性能监控装饰器
def log_performance(operation_name: str = None):
    """性能监控装饰器"""
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                get_performance_logger().log_operation(op_name, duration, status="success")
                return result
            except Exception as e:
                duration = time.time() - start_time
                get_performance_logger().log_operation(op_name, duration, status="error", error=str(e))
                raise
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试日志系统
    setup_logging()
    
    # 测试不同类型的日志
    main_logger = get_logger("test_main")
    module_logger = get_module_logger("test_module")
    perf_logger = get_performance_logger()
    
    main_logger.info("这是主日志测试")
    main_logger.warning("这是警告日志")
    main_logger.error("这是错误日志")
    
    module_logger.info("这是模块日志测试")
    module_logger.debug("这是调试日志")
    
    perf_logger.log_operation("test_operation", 0.123, param1="value1")
    
    # 测试性能装饰器
    @log_performance("test_function")
    def test_function():
        import time
        time.sleep(0.1)
        return "测试完成"
    
    result = test_function()
    print(f"✅ 日志系统测试完成: {result}")