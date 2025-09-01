#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
采购需求点对点应答系统 - 测试版本
不调用LLM API，使用模拟数据进行功能测试
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestRequirementProcessor:
    """测试版需求处理器"""
    
    def __init__(self):
        self.template_file = 'config/response_templates.json'
        self.patterns_file = 'config/requirement_patterns.json'
        self.load_templates()
        self.load_patterns()
    
    def load_templates(self):
        """加载应答模板"""
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
                logger.info("应答模板加载成功")
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
            self.templates = {"通用模板": "应答：满足。{具体方案}"}
    
    def load_patterns(self):
        """加载需求识别模式"""
        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
                logger.info("需求识别模式加载成功")
        except Exception as e:
            logger.error(f"加载模式失败: {e}")
            self.patterns = {"关键词": ["要求", "需求", "应", "必须"]}
    
    def extract_requirements_simple(self, content: str) -> List[Dict]:
        """
        简化版需求提取：使用正则表达式和关键词匹配
        """
        requirements = []
        lines = content.split('\n')
        current_id = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查编号格式
            has_number = False
            for pattern in self.patterns.get("编号模式", []):
                if re.match(pattern, line):
                    has_number = True
                    break
            
            # 检查关键词
            has_keyword = any(keyword in line for keyword in self.patterns.get("关键词", []))
            
            # 长度过滤
            if (has_number or has_keyword) and len(line) > 15:
                # 简单分类
                req_type = self.classify_requirement_simple(line)
                
                requirement = {
                    "id": str(current_id),
                    "content": line,
                    "type": req_type,
                    "keywords": [kw for kw in self.patterns.get("关键词", []) if kw in line]
                }
                requirements.append(requirement)
                current_id += 1
        
        logger.info(f"提取到 {len(requirements)} 个需求条目")
        return requirements
    
    def classify_requirement_simple(self, content: str) -> str:
        """
        简化版需求分类
        """
        content_lower = content.lower()
        
        # 获取分类关键词
        tech_keywords = self.patterns.get("技术分类关键词", {})
        
        for category, keywords in tech_keywords.items():
            if any(keyword.lower() in content_lower for keyword in keywords):
                return category
        
        return "通用模板"
    
    def generate_response_simple(self, requirement: Dict) -> str:
        """
        简化版应答生成
        """
        req_type = requirement["type"]
        template = self.templates.get(req_type, self.templates["通用模板"])
        
        # 简单的参数填充
        if "{" in template:
            # 根据需求类型填充不同的示例参数
            if req_type == "硬件配置":
                response = template.format(具体配置="Intel Xeon Gold 6248R 24核处理器、128GB DDR4内存、20TB SSD存储")
            elif req_type == "软件功能":  
                response = template.format(功能名称="数据采集处理", 技术方案="Apache Kafka + Apache Spark")
            elif req_type == "性能指标":
                response = template.format(具体指标="并发用户2000个，响应时间<1秒，系统可用性99.99%")
            elif req_type == "安全要求":
                response = template.format(安全措施="SSL/TLS加密、双因子认证、完整审计日志")
            elif req_type == "服务保障":
                response = template.format(服务内容="7*24小时技术支持、3个月实施周期、60小时专业培训")
            elif req_type == "资质证明":
                response = template.format(资质名称="软件企业认定证书、ISO9001质量管理体系认证")
            else:
                response = template.format(具体方案="采用业界主流技术方案，完全满足技术要求")
        else:
            response = template
        
        # 确保以"应答：满足。"开头
        if not response.startswith("应答：满足。"):
            response = f"应答：满足。{response}"
        
        return response
    
    def process_test_file(self, file_path: str) -> Dict:
        """
        处理测试文件
        """
        logger.info(f"开始处理测试文件: {file_path}")
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 模拟项目信息
            project_info = {
                "project_name": "智慧城市数据分析平台建设项目",
                "project_number": "ZH-2025-001",
                "tenderer": "某市政府",
                "agency": "某招标代理公司"
            }
            
            # 提取需求
            requirements = self.extract_requirements_simple(content)
            
            if not requirements:
                raise ValueError("未能提取到任何需求条目")
            
            # 生成应答
            responses = []
            for i, req in enumerate(requirements, 1):
                logger.info(f"正在处理第 {i}/{len(requirements)} 个需求...")
                response = self.generate_response_simple(req)
                
                responses.append({
                    "requirement": req,
                    "response": response
                })
            
            result = {
                "project_info": project_info,
                "requirements_count": len(requirements),
                "responses": responses,
                "processing_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"处理完成，共生成 {len(responses)} 条应答")
            return result
            
        except Exception as e:
            logger.error(f"处理失败: {e}")
            raise
    
    def export_to_text_simple(self, result: Dict, output_path: str = None) -> str:
        """
        导出结果到文本文件
        """
        try:
            project_name = result["project_info"].get("project_name", "测试项目")
            
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"采购需求应答书_{timestamp}.txt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"采购需求应答书 - {project_name}\n")
                f.write("=" * 80 + "\n\n")
                
                # 项目信息
                f.write("项目信息：\n")
                f.write("-" * 40 + "\n")
                f.write(f"项目名称：{result['project_info'].get('project_name', '未知')}\n")
                f.write(f"项目编号：{result['project_info'].get('project_number', '未知')}\n")
                f.write(f"需求条目数量：{result['requirements_count']}\n")
                f.write(f"生成时间：{result['processing_time']}\n\n")
                
                # 应答汇总表
                f.write("需求应答汇总：\n")
                f.write("-" * 40 + "\n")
                f.write(f"{'序号':<4} {'需求概要':<30} {'应答状态'}\n")
                f.write("-" * 80 + "\n")
                
                for i, resp in enumerate(result["responses"], 1):
                    req_summary = resp["requirement"]["content"][:25] + "..." if len(resp["requirement"]["content"]) > 25 else resp["requirement"]["content"]
                    f.write(f"{i:<4} {req_summary:<30} 满足\n")
                
                # 详细应答
                f.write("\n\n详细应答内容：\n")
                f.write("=" * 80 + "\n\n")
                
                for i, resp in enumerate(result["responses"], 1):
                    f.write(f"{i}. 需求条目\n")
                    f.write("原文需求：\n")
                    f.write(f"    {resp['requirement']['content']}\n\n")
                    f.write("供应商应答：\n")
                    f.write(f"    {resp['response']}\n\n")
                    f.write("─" * 80 + "\n\n")
            
            logger.info(f"测试文件已保存至: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"导出文件失败: {e}")
            raise

def main():
    """测试主函数"""
    try:
        processor = TestRequirementProcessor()
        
        # 测试文件路径
        test_file = "test_requirements.txt"
        
        if not os.path.exists(test_file):
            print(f"测试文件不存在: {test_file}")
            return
        
        print("开始测试采购需求点对点应答系统...")
        print("-" * 50)
        
        # 处理测试文件
        result = processor.process_test_file(test_file)
        
        print(f"✓ 处理完成!")
        print(f"项目名称: {result['project_info'].get('project_name')}")
        print(f"需求条目数量: {result['requirements_count']}")
        print(f"处理时间: {result['processing_time']}")
        
        # 导出结果
        output_file = processor.export_to_text_simple(result)
        print(f"✓ 应答文件已生成: {output_file}")
        
        # 显示前几条应答预览
        print(f"\n前3条应答预览:")
        print("-" * 50)
        for i, resp in enumerate(result['responses'][:3], 1):
            print(f"{i}. 需求: {resp['requirement']['content'][:60]}...")
            print(f"   应答: {resp['response'][:100]}...")
            print()
        
        print("测试完成! 📋✅")
        
    except Exception as e:
        print(f"测试失败: {e}")
        logger.error(f"测试失败: {e}")

if __name__ == "__main__":
    main()