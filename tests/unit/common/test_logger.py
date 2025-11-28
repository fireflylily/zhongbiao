"""
测试common/logger.py日志模块
"""

import pytest
import logging


@pytest.mark.unit
class TestLogger:
    """测试日志模块"""

    def test_get_module_logger(self):
        """测试获取模块logger"""
        from ai_tender_system.common.logger import get_module_logger
        
        logger = get_module_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "ai_tender_system.test_module"

    def test_logger_different_modules(self):
        """测试不同模块的logger是独立的"""
        from ai_tender_system.common.logger import get_module_logger
        
        logger1 = get_module_logger("module1")
        logger2 = get_module_logger("module2")
        
        assert logger1.name != logger2.name

    def test_logger_basic_operations(self):
        """测试logger基本操作"""
        from ai_tender_system.common.logger import get_module_logger
        
        logger = get_module_logger("test")
        
        # 不应抛出异常
        logger.info("Info message")
        logger.error("Error message")
        logger.debug("Debug message")
        logger.warning("Warning message")
