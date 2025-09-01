"""
自动标书生成系统主程序
整合各个模块，提供完整的标书生成流程
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from parsers.tender_parser import get_tender_parser
from parsers.product_parser import get_product_parser
from matchers.exact_matcher import get_exact_matcher
from matchers.semantic_matcher import get_semantic_matcher
from generators.outline_generator import get_outline_generator
from generators.content_generator import get_content_generator
from generators.word_generator import get_word_generator
from utils.file_utils import get_file_utils
from utils.llm_client import get_llm_client
from config import (
    OUTPUT_DIR, DEFAULT_OUTLINE_FILE, DEFAULT_PROPOSAL_FILE, 
    DEFAULT_MATCH_REPORT, LOG_LEVEL, LOG_FILE
)

class TenderGenerator:
    """主要的标书生成器类"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个模块
        self.tender_parser = get_tender_parser()
        self.product_parser = get_product_parser()
        self.exact_matcher = get_exact_matcher()
        self.semantic_matcher = get_semantic_matcher()
        self.outline_generator = get_outline_generator()
        self.content_generator = get_content_generator()
        self.word_generator = get_word_generator()
        self.file_utils = get_file_utils()
        self.llm_client = get_llm_client()
        
        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        self.logger.info("标书生成系统初始化完成")
    
    def setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def generate_proposal(self, 
                         tender_file: str,
                         product_file: str,
                         output_prefix: str = "proposal") -> Dict[str, Any]:
        """
        生成完整的技术方案
        
        Args:
            tender_file: 招标文件路径
            product_file: 产品文档路径
            output_prefix: 输出文件前缀
            
        Returns:
            生成结果统计
        """
        self.logger.info(f"开始生成技术方案：招标文件={tender_file}, 产品文档={product_file}")
        
        try:
            # 第一步：解析招标文件
            self.logger.info("第一步：解析招标文件")
            tender_data = self.tender_parser.parse_tender_document(tender_file)
            if 'error' in tender_data:
                raise Exception(f"解析招标文件失败: {tender_data['error']}")
            
            requirements = tender_data['requirements']
            scoring_criteria = tender_data['scoring_details']
            
            self.logger.info(f"招标文件解析完成：{len(requirements)} 个需求，{len(scoring_criteria)} 个评分项")
            
            # 第二步：解析产品文档
            self.logger.info("第二步：解析产品文档")
            product_data = self.product_parser.parse_product_document(product_file)
            if 'error' in product_data:
                raise Exception(f"解析产品文档失败: {product_data['error']}")
            
            features = product_data['features']
            self.logger.info(f"产品文档解析完成：{len(features)} 个功能特性")
            
            # 第三步：需求功能匹配
            self.logger.info("第三步：进行需求功能匹配")
            exact_matches = self.exact_matcher.match_requirements_with_features(requirements, features)
            semantic_matches = self.semantic_matcher.semantic_match(requirements, features)
            
            # 合并匹配结果
            all_matches = self._merge_match_results(exact_matches, semantic_matches)
            self.logger.info(f"匹配完成：{len(all_matches)} 个匹配结果")
            
            # 第四步：生成技术方案大纲
            self.logger.info("第四步：生成技术方案大纲")
            outline = self.outline_generator.generate_outline(scoring_criteria, requirements)
            self.logger.info(f"大纲生成完成：{outline['total_sections']} 个章节")
            
            # 第五步：生成方案内容
            self.logger.info("第五步：生成技术方案内容")
            proposal = self.content_generator.generate_proposal_content(outline, all_matches, features)
            
            # 第六步：生成匹配度报告
            self.logger.info("第六步：生成匹配度报告")
            match_report = self.content_generator.generate_match_report(all_matches)
            
            # 第七步：保存结果文件
            self.logger.info("第七步：保存结果文件")
            output_files = self._save_results(
                proposal, outline, match_report, 
                tender_data, product_data, output_prefix
            )
            
            # 生成统计结果
            result_stats = {
                'success': True,
                'tender_file': tender_file,
                'product_file': product_file,
                'requirements_count': len(requirements),
                'features_count': len(features),
                'matches_count': len(all_matches),
                'sections_count': outline['total_sections'],
                'generation_stats': proposal['generation_stats'],
                'match_stats': {
                    'matched_requirements': match_report['matched_requirements'],
                    'unmatched_requirements': match_report['unmatched_requirements'],
                    'average_match_score': match_report['average_match_score']
                },
                'output_files': output_files
            }
            
            self.logger.info(f"技术方案生成完成：{result_stats}")
            return result_stats
            
        except Exception as e:
            self.logger.error(f"生成技术方案失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'tender_file': tender_file,
                'product_file': product_file
            }
    
    def _merge_match_results(self, exact_matches, semantic_matches):
        """合并精确匹配和语义匹配结果"""
        merged = {}
        
        # 添加精确匹配结果
        for match in exact_matches:
            req_id = match['requirement_id']
            feature_id = match.get('feature_id')
            
            key = f"{req_id}_{feature_id}" if feature_id else f"{req_id}_none"
            
            if key not in merged or match['match_score'] > merged[key].get('match_score', 0):
                merged[key] = match.copy()
                merged[key]['match_source'] = 'exact'
        
        # 添加语义匹配结果
        for match in semantic_matches:
            req_id = match['requirement_id']
            feature_id = match.get('feature_id')
            
            key = f"{req_id}_{feature_id}" if feature_id else f"{req_id}_none"
            
            if key not in merged:
                match_copy = match.copy()
                match_copy['match_score'] = match.get('semantic_score', 0)
                match_copy['match_source'] = 'semantic'
                merged[key] = match_copy
            else:
                # 如果已存在，比较分数并保留最佳的
                existing_score = merged[key].get('match_score', 0)
                semantic_score = match.get('semantic_score', 0)
                
                if semantic_score > existing_score:
                    match_copy = match.copy()
                    match_copy['match_score'] = semantic_score
                    match_copy['match_source'] = 'semantic'
                    merged[key] = match_copy
        
        return list(merged.values())
    
    def _save_results(self, proposal, outline, match_report, tender_data, product_data, prefix):
        """保存所有结果文件"""
        output_files = {}
        
        # 保存技术方案大纲 (JSON)
        outline_file = os.path.join(OUTPUT_DIR, f"{prefix}_outline.json")
        outline_export = self.outline_generator.export_outline_to_dict(outline)
        self.file_utils.save_json(outline_export, outline_file)
        output_files['outline'] = outline_file
        
        # 保存技术方案内容 (Word文档)
        proposal_file = os.path.join(OUTPUT_DIR, f"{prefix}_proposal.docx")
        try:
            # 尝试生成Word文档
            success = self.word_generator.export_proposal_to_word(
                proposal, outline_export, proposal_file
            )
            if success:
                output_files['proposal'] = proposal_file
            else:
                # 如果Word生成失败，fallback到文本文件
                self.logger.warning("Word文档生成失败，使用文本格式")
                proposal_txt_file = os.path.join(OUTPUT_DIR, f"{prefix}_proposal.txt")
                proposal_text = self.content_generator.export_to_text(proposal)
                with open(proposal_txt_file, 'w', encoding='utf-8') as f:
                    f.write(proposal_text)
                output_files['proposal'] = proposal_txt_file
        except Exception as e:
            self.logger.error(f"生成Word文档时出错: {e}")
            # fallback到文本文件
            proposal_txt_file = os.path.join(OUTPUT_DIR, f"{prefix}_proposal.txt")
            proposal_text = self.content_generator.export_to_text(proposal)
            with open(proposal_txt_file, 'w', encoding='utf-8') as f:
                f.write(proposal_text)
            output_files['proposal'] = proposal_txt_file
        
        # 保存匹配度报告 (JSON)
        match_report_file = os.path.join(OUTPUT_DIR, f"{prefix}_match_report.json")
        self.file_utils.save_json(match_report, match_report_file)
        output_files['match_report'] = match_report_file
        
        # 保存完整数据 (JSON)
        full_data_file = os.path.join(OUTPUT_DIR, f"{prefix}_full_data.json")
        full_data = {
            'tender_data': {
                'file_path': tender_data['file_path'],
                'requirements_count': len(tender_data['requirements']),
                'scoring_count': len(tender_data['scoring_details'])
            },
            'product_data': {
                'file_path': product_data['file_path'],
                'features_count': len(product_data['features']),
                'product_info': product_data['product_info']
            },
            'outline': outline_export,
            'proposal_stats': proposal['generation_stats'],
            'match_report': match_report
        }
        self.file_utils.save_json(full_data, full_data_file)
        output_files['full_data'] = full_data_file
        
        return output_files
    
    def test_api_connection(self) -> bool:
        """测试API连接"""
        self.logger.info("测试LLM API连接")
        return self.llm_client.test_connection()
    
    def analyze_tender_file(self, tender_file: str) -> Dict[str, Any]:
        """单独分析招标文件"""
        self.logger.info(f"分析招标文件: {tender_file}")
        return self.tender_parser.parse_tender_document(tender_file)
    
    def analyze_product_file(self, product_file: str) -> Dict[str, Any]:
        """单独分析产品文档"""
        self.logger.info(f"分析产品文档: {product_file}")
        return self.product_parser.parse_product_document(product_file)


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='自动标书生成系统')
    parser.add_argument('--tender', '-t', required=True, help='招标文件路径')
    parser.add_argument('--product', '-p', required=True, help='产品文档路径')
    parser.add_argument('--output', '-o', default='proposal', help='输出文件前缀')
    parser.add_argument('--test-api', action='store_true', help='测试API连接')
    parser.add_argument('--analyze-only', action='store_true', help='仅分析文件，不生成方案')
    
    args = parser.parse_args()
    
    # 创建标书生成器
    generator = TenderGenerator()
    
    # 测试API连接
    if args.test_api:
        if generator.test_api_connection():
            print("✅ API连接测试成功")
        else:
            print("❌ API连接测试失败")
            return
    
    # 检查文件是否存在
    if not os.path.exists(args.tender):
        print(f"❌ 招标文件不存在: {args.tender}")
        return
    
    if not os.path.exists(args.product):
        print(f"❌ 产品文档不存在: {args.product}")
        return
    
    try:
        if args.analyze_only:
            # 仅分析文件
            print("📋 分析招标文件...")
            tender_result = generator.analyze_tender_file(args.tender)
            if 'error' in tender_result:
                print(f"❌ 招标文件分析失败: {tender_result['error']}")
            else:
                print(f"✅ 找到 {len(tender_result['requirements'])} 个需求和 {len(tender_result['scoring_details'])} 个评分项")
            
            print("📋 分析产品文档...")
            product_result = generator.analyze_product_file(args.product)
            if 'error' in product_result:
                print(f"❌ 产品文档分析失败: {product_result['error']}")
            else:
                print(f"✅ 找到 {len(product_result['features'])} 个功能特性")
        
        else:
            # 生成完整方案
            print("🚀 开始生成技术方案...")
            result = generator.generate_proposal(args.tender, args.product, args.output)
            
            if result['success']:
                print("✅ 技术方案生成成功！")
                print(f"📊 统计信息:")
                print(f"  - 需求数量: {result['requirements_count']}")
                print(f"  - 功能数量: {result['features_count']}")
                print(f"  - 匹配数量: {result['matches_count']}")
                print(f"  - 章节数量: {result['sections_count']}")
                print(f"  - 匹配率: {result['match_stats']['matched_requirements']}/{result['requirements_count']}")
                print(f"📁 输出文件:")
                for file_type, file_path in result['output_files'].items():
                    print(f"  - {file_type}: {file_path}")
            else:
                print(f"❌ 生成失败: {result['error']}")
    
    except KeyboardInterrupt:
        print("\\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"💥 程序异常: {e}")
        logging.exception("程序异常")


if __name__ == "__main__":
    main()