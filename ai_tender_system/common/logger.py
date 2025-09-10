#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一日志管理模块
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from .config import get_config

def setup_logging(log_dir: Optional[Path] = None) -> None:
    """设置日志系统"""
    config = get_config()
    log_config = config.get_logging_config()
    
    if log_dir is None:
        log_dir = config.get_path('data') / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, log_config['level']),
        format=log_config['format'],
        handlers=[
            # 控制台输出
            logging.StreamHandler(),
            # 文件输出（轮转）
            logging.handlers.RotatingFileHandler(
                log_dir / "ai_tender_system.log",
                maxBytes=log_config['max_bytes'],
                backupCount=log_config['backup_count'],
                encoding='utf-8'
            )
        ]
    )

def get_module_logger(module_name: str) -> logging.Logger:
    """获取模块专用日志器"""
    logger = logging.getLogger(f"ai_tender_system.{module_name}")
    
    # 如果还没有设置过处理器，为模块添加专用日志文件
    if not logger.handlers:
        config = get_config()
        log_config = config.get_logging_config()
        log_dir = config.get_path('data') / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 添加模块专用的文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{module_name}.log",
            maxBytes=log_config['max_bytes'],
            backupCount=log_config['backup_count'],
            encoding='utf-8'
        )
        file_handler.setFormatter(
            logging.Formatter(log_config['format'])
        )
        logger.addHandler(file_handler)
        logger.setLevel(getattr(logging, log_config['level']))
    
    return logger

def get_request_logger() -> logging.Logger:
    """获取请求日志器"""
    return get_module_logger("requests")

def get_error_logger() -> logging.Logger:
    """获取错误日志器"""
    return get_module_logger("errors")

def get_tender_logger() -> logging.Logger:
    """获取招标信息处理日志器"""
    return get_module_logger("tender_info")

def get_business_logger() -> logging.Logger:
    """获取商务应答日志器"""
    return get_module_logger("business_response")

def get_tech_logger() -> logging.Logger:
    """获取技术方案日志器"""
    return get_module_logger("tech_proposal")

if __name__ == "__main__":
    # 测试日志系统
    setup_logging()
    
    logger = get_module_logger("test")
    logger.info("日志系统测试")
    logger.warning("这是一个警告")
    logger.error("这是一个错误")
    
    print("日志系统测试完成")