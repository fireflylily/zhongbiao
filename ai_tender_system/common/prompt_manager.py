#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词管理器 - 统一管理所有LLM提示词
提供集中化的提示词加载、获取和缓存功能
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from threading import Lock

logger = logging.getLogger(__name__)


class PromptManager:
    """提示词管理器 - 单例模式"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._prompts_cache: Dict[str, Dict] = {}
        self._prompts_dir = Path(__file__).parent.parent / "prompts"

        # 确保 prompts 目录存在
        if not self._prompts_dir.exists():
            logger.warning(f"提示词目录不存在: {self._prompts_dir}")
            self._prompts_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"提示词管理器初始化完成，提示词目录: {self._prompts_dir}")

    def load_prompts(self, module_name: str) -> Dict[str, Any]:
        """
        加载指定模块的提示词配置

        Args:
            module_name: 模块名称，如 'point_to_point', 'business_response', 'common'

        Returns:
            提示词配置字典
        """
        # 检查缓存
        if module_name in self._prompts_cache:
            return self._prompts_cache[module_name]

        # 加载 JSON 文件
        prompts_file = self._prompts_dir / f"{module_name}.json"

        if not prompts_file.exists():
            logger.warning(f"提示词文件不存在: {prompts_file}")
            return {}

        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)

            # 缓存加载的提示词
            self._prompts_cache[module_name] = prompts_data

            logger.info(f"成功加载提示词配置: {module_name}")
            return prompts_data

        except json.JSONDecodeError as e:
            logger.error(f"提示词文件 JSON 解析失败: {prompts_file}, 错误: {e}")
            return {}
        except Exception as e:
            logger.error(f"加载提示词文件失败: {prompts_file}, 错误: {e}")
            return {}

    def get_prompt(self, module_name: str, prompt_key: str, default: Optional[str] = None) -> str:
        """
        获取指定模块的指定提示词

        Args:
            module_name: 模块名称
            prompt_key: 提示词键名
            default: 默认值，如果找不到提示词则返回此值

        Returns:
            提示词文本
        """
        prompts_data = self.load_prompts(module_name)

        if not prompts_data:
            logger.warning(f"模块 {module_name} 没有提示词配置")
            return default or ""

        prompts = prompts_data.get('prompts', {})
        prompt = prompts.get(prompt_key)

        if prompt is None:
            logger.warning(f"提示词键 {prompt_key} 在模块 {module_name} 中不存在")
            # 尝试从 common 模块获取默认提示词
            if module_name != 'common' and default is None:
                return self.get_prompt('common', 'default', default="")
            return default or ""

        return prompt

    def get_all_prompts(self, module_name: str) -> Dict[str, str]:
        """
        获取指定模块的所有提示词

        Args:
            module_name: 模块名称

        Returns:
            提示词字典
        """
        prompts_data = self.load_prompts(module_name)
        return prompts_data.get('prompts', {})

    def reload_prompts(self, module_name: Optional[str] = None):
        """
        重新加载提示词（清除缓存）

        Args:
            module_name: 模块名称，如果为 None 则重新加载所有模块
        """
        if module_name:
            if module_name in self._prompts_cache:
                del self._prompts_cache[module_name]
                logger.info(f"已清除模块 {module_name} 的提示词缓存")
        else:
            self._prompts_cache.clear()
            logger.info("已清除所有提示词缓存")

    def list_modules(self) -> list:
        """
        列出所有可用的提示词模块

        Returns:
            模块名称列表
        """
        if not self._prompts_dir.exists():
            return []

        modules = []
        for file in self._prompts_dir.glob("*.json"):
            modules.append(file.stem)

        return sorted(modules)

    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """
        获取模块的元信息

        Args:
            module_name: 模块名称

        Returns:
            包含 description, version, updated_at 等信息的字典
        """
        prompts_data = self.load_prompts(module_name)
        return {
            'module': prompts_data.get('module', module_name),
            'description': prompts_data.get('description', ''),
            'version': prompts_data.get('version', ''),
            'updated_at': prompts_data.get('updated_at', '')
        }


# 全局单例实例
_prompt_manager_instance = None


def get_prompt_manager() -> PromptManager:
    """
    获取提示词管理器的全局单例实例

    Returns:
        PromptManager 实例
    """
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance


# 便捷函数
def get_prompt(module_name: str, prompt_key: str, default: Optional[str] = None) -> str:
    """
    快捷方式：获取提示词

    Args:
        module_name: 模块名称
        prompt_key: 提示词键名
        default: 默认值

    Returns:
        提示词文本
    """
    return get_prompt_manager().get_prompt(module_name, prompt_key, default)


def reload_prompts(module_name: Optional[str] = None):
    """
    快捷方式：重新加载提示词

    Args:
        module_name: 模块名称，如果为 None 则重新加载所有模块
    """
    get_prompt_manager().reload_prompts(module_name)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    pm = get_prompt_manager()

    # 列出所有模块
    print("可用模块:", pm.list_modules())

    # 测试获取提示词
    prompt = pm.get_prompt('point_to_point', 'answer')
    print(f"\n点对点应答提示词（前100字符）: {prompt[:100]}...")

    # 测试获取模块信息
    info = pm.get_module_info('point_to_point')
    print(f"\n模块信息: {info}")
