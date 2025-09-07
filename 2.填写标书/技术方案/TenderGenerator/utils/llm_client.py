"""
LLM客户端封装
支持始皇API和其他OpenAI兼容接口
"""

import requests
import json
import time
import logging
from typing import Optional, Dict, Any, List
try:
    from ..config import (
        SHIHUANG_API_KEY, SHIHUANG_BASE_URL, SHIHUANG_MODEL,
        REQUEST_TIMEOUT, MAX_CONCURRENT_REQUESTS
    )
except ImportError:
    # 当作为脚本运行时的fallback
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import (
        SHIHUANG_API_KEY, SHIHUANG_BASE_URL, SHIHUANG_MODEL,
        REQUEST_TIMEOUT, MAX_CONCURRENT_REQUESTS,
        MIN_QUALITY_SCORE, OPTIMIZATION_THRESHOLD, MAX_OPTIMIZATION_ROUNDS
    )

class LLMClient:
    """LLM客户端类，封装API调用逻辑"""
    
    def __init__(self, 
                 api_key: str = SHIHUANG_API_KEY,
                 base_url: str = SHIHUANG_BASE_URL,
                 model: str = SHIHUANG_MODEL):
        """
        初始化LLM客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        })
    
    def chat_completion(self, 
                       prompt: str,
                       max_tokens: int = 1500,
                       temperature: float = 0.7,
                       system_prompt: Optional[str] = None) -> Optional[str]:
        """
        调用聊天完成API
        
        Args:
            prompt: 用户提示词
            max_tokens: 最大tokens数
            temperature: 温度参数
            system_prompt: 系统提示词
            
        Returns:
            生成的文本内容，失败时返回None
        """
        try:
            # 构建消息列表
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # 构建请求数据
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # 发送请求
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                result = data['choices'][0]['message']['content'].strip()
                self.logger.info(f"LLM API调用成功，返回内容长度: {len(result)}")
                return result
            elif 'error' in data:
                self.logger.error(f"LLM API错误: {data['error'].get('message', '未知错误')}")
                return None
            else:
                self.logger.error(f"API响应格式异常: {data}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error(f"LLM API请求超时")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LLM API网络错误: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            self.logger.error(f"LLM API调用异常: {e}")
            return None
    
    def generate_outline(self, scoring_criteria: str, requirements: str) -> Optional[Dict[str, Any]]:
        """
        生成技术方案大纲
        
        Args:
            scoring_criteria: 评分标准
            requirements: 需求内容
            
        Returns:
            大纲数据（JSON格式），失败时返回None
        """
        try:
            from ..config import OUTLINE_PROMPT
        except ImportError:
            from config import OUTLINE_PROMPT
        
        prompt = OUTLINE_PROMPT.format(
            scoring_criteria=scoring_criteria,
            requirements=requirements
        )
        
        result = self.chat_completion(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.5
        )
        
        if result:
            try:
                # 尝试解析JSON
                outline_data = json.loads(result)
                return outline_data
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试提取JSON部分
                try:
                    start_idx = result.find('{')
                    end_idx = result.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = result[start_idx:end_idx]
                        outline_data = json.loads(json_str)
                        return outline_data
                except:
                    pass
                
                self.logger.error(f"无法解析大纲JSON: {result}")
        
        return None
    
    def generate_content(self, 
                        requirement: str,
                        product_features: str,
                        section_title: str) -> Optional[str]:
        """
        生成技术方案内容
        
        Args:
            requirement: 需求描述
            product_features: 产品功能
            section_title: 章节标题
            
        Returns:
            生成的内容文本，失败时返回None
        """
        try:
            from ..config import CONTENT_GENERATION_PROMPT
        except ImportError:
            from config import CONTENT_GENERATION_PROMPT
        
        prompt = CONTENT_GENERATION_PROMPT.format(
            requirement=requirement,
            product_features=product_features,
            section_title=section_title
        )
        
        return self.chat_completion(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        )
    
    def rewrite_content(self, 
                       original_content: str,
                       target_requirement: str,
                       section_title: str) -> Optional[str]:
        """
        改写现有内容
        
        Args:
            original_content: 原始内容
            target_requirement: 目标需求
            section_title: 章节标题
            
        Returns:
            改写后的内容，失败时返回None
        """
        try:
            from ..config import CONTENT_REWRITE_PROMPT
        except ImportError:
            from config import CONTENT_REWRITE_PROMPT
        
        prompt = CONTENT_REWRITE_PROMPT.format(
            original_content=original_content,
            target_requirement=target_requirement,
            section_title=section_title
        )
        
        return self.chat_completion(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.6
        )
    
    def batch_generate(self, tasks: List[Dict[str, Any]], 
                      delay: float = 1.0) -> List[Optional[str]]:
        """
        批量生成内容
        
        Args:
            tasks: 任务列表，每个任务包含type和参数
            delay: 请求间延迟（秒）
            
        Returns:
            生成结果列表
        """
        results = []
        
        for i, task in enumerate(tasks):
            try:
                task_type = task.get('type')
                
                if task_type == 'generate_content':
                    result = self.generate_content(
                        requirement=task.get('requirement', ''),
                        product_features=task.get('product_features', ''),
                        section_title=task.get('section_title', '')
                    )
                elif task_type == 'rewrite_content':
                    result = self.rewrite_content(
                        original_content=task.get('original_content', ''),
                        target_requirement=task.get('target_requirement', ''),
                        section_title=task.get('section_title', '')
                    )
                else:
                    self.logger.warning(f"未知任务类型: {task_type}")
                    result = None
                
                results.append(result)
                
                # 请求间延迟
                if i < len(tasks) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"批量任务执行失败: {e}")
                results.append(None)
        
        return results
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接状态
        """
        try:
            result = self.chat_completion(
                prompt="测试连接",
                max_tokens=10,
                temperature=0.1
            )
            return result is not None
        except:
            return False
    
    def generate_content_with_quality_control(self, 
                                            requirement: str,
                                            product_features: str,
                                            section_title: str) -> Dict[str, Any]:
        """
        带质量控制的内容生成
        
        Args:
            requirement: 需求描述
            product_features: 产品功能
            section_title: 章节标题
            
        Returns:
            包含内容和质量信息的字典
        """
        try:
            from ..config import CONTENT_QUALITY_PROMPT, CONTENT_OPTIMIZATION_PROMPT
        except ImportError:
            from config import CONTENT_QUALITY_PROMPT, CONTENT_OPTIMIZATION_PROMPT
        
        result = {
            'content': '',
            'quality_score': 0.0,
            'optimization_rounds': 0,
            'final_quality': 'unknown'
        }
        
        # 第一次生成内容
        initial_content = self.generate_content(requirement, product_features, section_title)
        if not initial_content:
            return result
        
        current_content = initial_content
        optimization_round = 0
        
        while optimization_round < MAX_OPTIMIZATION_ROUNDS:
            # 评估当前内容质量
            quality_assessment = self._assess_content_quality(
                current_content, requirement, section_title
            )
            
            if not quality_assessment:
                break
                
            overall_score = quality_assessment.get('overall_score', 0)
            result['quality_score'] = overall_score
            
            # 如果质量已经足够好，退出优化循环
            if overall_score >= OPTIMIZATION_THRESHOLD:
                result['final_quality'] = 'excellent'
                break
            
            # 如果质量太低且还有优化机会，进行优化
            if overall_score < MIN_QUALITY_SCORE and optimization_round < MAX_OPTIMIZATION_ROUNDS - 1:
                optimized_content = self._optimize_content(current_content, quality_assessment)
                if optimized_content and len(optimized_content) > len(current_content) * 0.8:
                    current_content = optimized_content
                    optimization_round += 1
                    result['optimization_rounds'] = optimization_round
                else:
                    break
            else:
                break
        
        result['content'] = current_content
        
        # 设置最终质量等级
        if result['quality_score'] >= OPTIMIZATION_THRESHOLD:
            result['final_quality'] = 'excellent'
        elif result['quality_score'] >= MIN_QUALITY_SCORE:
            result['final_quality'] = 'good'
        else:
            result['final_quality'] = 'average'
        
        self.logger.info(f"内容生成完成: 质量分数={result['quality_score']:.1f}, 优化轮次={result['optimization_rounds']}")
        return result
    
    def _assess_content_quality(self, content: str, requirement: str, section_title: str) -> Optional[Dict[str, Any]]:
        """评估内容质量"""
        try:
            from ..config import CONTENT_QUALITY_PROMPT
        except ImportError:
            from config import CONTENT_QUALITY_PROMPT
        
        prompt = CONTENT_QUALITY_PROMPT.format(
            content=content,
            requirement=requirement,
            section_title=section_title
        )
        
        result = self.chat_completion(
            prompt=prompt,
            max_tokens=800,
            temperature=0.3
        )
        
        if result:
            try:
                # 尝试解析JSON响应
                assessment_data = json.loads(result)
                return assessment_data
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试提取JSON部分
                try:
                    start_idx = result.find('{')
                    end_idx = result.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = result[start_idx:end_idx]
                        assessment_data = json.loads(json_str)
                        return assessment_data
                except:
                    pass
                
                self.logger.warning(f"无法解析质量评估结果: {result}")
        
        return None
    
    def _optimize_content(self, original_content: str, quality_assessment: Dict[str, Any]) -> Optional[str]:
        """优化内容"""
        try:
            from ..config import CONTENT_OPTIMIZATION_PROMPT
        except ImportError:
            from config import CONTENT_OPTIMIZATION_PROMPT
        
        prompt = CONTENT_OPTIMIZATION_PROMPT.format(
            original_content=original_content,
            quality_assessment=json.dumps(quality_assessment, ensure_ascii=False, indent=2)
        )
        
        result = self.chat_completion(
            prompt=prompt,
            max_tokens=2500,
            temperature=0.6
        )
        
        return result


# 全局LLM客户端实例
_llm_client = None

def get_llm_client() -> LLMClient:
    """获取全局LLM客户端实例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

def set_llm_client(client: LLMClient):
    """设置全局LLM客户端实例"""
    global _llm_client
    _llm_client = client