# -*- coding: utf-8 -*-
"""
招标信息数据模型
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class QualificationRequirement:
    """单个资质要求"""
    required: bool = False
    description: str = ""


@dataclass
class QualificationRequirements:
    """资质要求集合"""
    business_license: QualificationRequirement
    taxpayer_qualification: QualificationRequirement
    performance_requirements: QualificationRequirement
    authorization_requirements: QualificationRequirement
    credit_china: QualificationRequirement
    commitment_letter: QualificationRequirement
    audit_report: QualificationRequirement
    social_security: QualificationRequirement
    labor_contract: QualificationRequirement
    other_requirements: QualificationRequirement
    
    @classmethod
    def create_default(cls) -> 'QualificationRequirements':
        """创建默认资质要求"""
        return cls(
            business_license=QualificationRequirement(),
            taxpayer_qualification=QualificationRequirement(),
            performance_requirements=QualificationRequirement(),
            authorization_requirements=QualificationRequirement(),
            credit_china=QualificationRequirement(),
            commitment_letter=QualificationRequirement(required=True, description="承诺函（默认满足）"),
            audit_report=QualificationRequirement(),
            social_security=QualificationRequirement(),
            labor_contract=QualificationRequirement(),
            other_requirements=QualificationRequirement()
        )
    
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """转换为字典格式"""
        result = {}
        for field_name, field_value in asdict(self).items():
            result[field_name] = field_value
        return result


@dataclass
class TechnicalScoringItem:
    """技术评分项"""
    name: str = ""
    weight: str = ""
    criteria: str = ""
    source: str = ""


@dataclass
class TechnicalScoring:
    """技术评分信息"""
    technical_scoring_items: list[TechnicalScoringItem]
    total_technical_score: str = ""
    extraction_summary: str = ""
    raw_response: str = ""
    
    @classmethod
    def create_empty(cls) -> 'TechnicalScoring':
        """创建空的技术评分"""
        return cls(
            technical_scoring_items=[],
            total_technical_score="未提供",
            extraction_summary="未找到技术评分信息",
            raw_response=""
        )


@dataclass
class TenderInfo:
    """招标信息完整数据模型"""
    # 基本信息
    tenderer: str = ""                    # 招标人
    agency: str = ""                      # 招标代理
    bidding_method: str = ""              # 投标方式
    bidding_location: str = ""            # 投标地点
    bidding_time: str = ""                # 投标时间
    winner_count: str = ""                # 中标人数量
    project_name: str = ""                # 项目名称
    project_number: str = ""              # 项目编号
    
    # 资质要求
    qualification_requirements: Optional[QualificationRequirements] = None
    
    # 技术评分
    technical_scoring: Optional[TechnicalScoring] = None
    
    # 元数据
    extraction_time: Optional[datetime] = None
    source_file: str = ""
    
    def __post_init__(self):
        """初始化后处理"""
        if self.qualification_requirements is None:
            self.qualification_requirements = QualificationRequirements.create_default()
        
        if self.technical_scoring is None:
            self.technical_scoring = TechnicalScoring.create_empty()
        
        if self.extraction_time is None:
            self.extraction_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'tenderer': self.tenderer,
            'agency': self.agency,
            'bidding_method': self.bidding_method,
            'bidding_location': self.bidding_location,
            'bidding_time': self.bidding_time,
            'winner_count': self.winner_count,
            'project_name': self.project_name,
            'project_number': self.project_number,
            'source_file': self.source_file,
            'extraction_time': self.extraction_time.isoformat() if self.extraction_time else ""
        }
        
        if self.qualification_requirements:
            result['qualification_requirements'] = self.qualification_requirements.to_dict()
        
        if self.technical_scoring:
            result['technical_scoring'] = asdict(self.technical_scoring)
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TenderInfo':
        """从字典创建实例"""
        # 处理资质要求
        qual_req = None
        if 'qualification_requirements' in data:
            qual_data = data['qualification_requirements']
            qual_req = QualificationRequirements(
                business_license=QualificationRequirement(**qual_data.get('business_license', {})),
                taxpayer_qualification=QualificationRequirement(**qual_data.get('taxpayer_qualification', {})),
                performance_requirements=QualificationRequirement(**qual_data.get('performance_requirements', {})),
                authorization_requirements=QualificationRequirement(**qual_data.get('authorization_requirements', {})),
                credit_china=QualificationRequirement(**qual_data.get('credit_china', {})),
                commitment_letter=QualificationRequirement(**qual_data.get('commitment_letter', {})),
                audit_report=QualificationRequirement(**qual_data.get('audit_report', {})),
                social_security=QualificationRequirement(**qual_data.get('social_security', {})),
                labor_contract=QualificationRequirement(**qual_data.get('labor_contract', {})),
                other_requirements=QualificationRequirement(**qual_data.get('other_requirements', {}))
            )
        
        # 处理技术评分
        tech_scoring = None
        if 'technical_scoring' in data:
            tech_data = data['technical_scoring']
            scoring_items = [
                TechnicalScoringItem(**item) 
                for item in tech_data.get('technical_scoring_items', [])
            ]
            tech_scoring = TechnicalScoring(
                technical_scoring_items=scoring_items,
                total_technical_score=tech_data.get('total_technical_score', ''),
                extraction_summary=tech_data.get('extraction_summary', ''),
                raw_response=tech_data.get('raw_response', '')
            )
        
        # 处理提取时间
        extraction_time = None
        if 'extraction_time' in data and data['extraction_time']:
            try:
                extraction_time = datetime.fromisoformat(data['extraction_time'])
            except:
                extraction_time = datetime.now()
        
        return cls(
            tenderer=data.get('tenderer', ''),
            agency=data.get('agency', ''),
            bidding_method=data.get('bidding_method', ''),
            bidding_location=data.get('bidding_location', ''),
            bidding_time=data.get('bidding_time', ''),
            winner_count=data.get('winner_count', ''),
            project_name=data.get('project_name', ''),
            project_number=data.get('project_number', ''),
            qualification_requirements=qual_req,
            technical_scoring=tech_scoring,
            extraction_time=extraction_time,
            source_file=data.get('source_file', '')
        )
    
    def is_valid(self) -> bool:
        """验证数据是否有效"""
        # 至少要有项目名称或项目编号
        return bool(self.project_name.strip() or self.project_number.strip())
    
    def get_summary(self) -> str:
        """获取摘要信息"""
        summary_parts = []
        
        if self.project_name:
            summary_parts.append(f"项目: {self.project_name}")
        
        if self.project_number:
            summary_parts.append(f"编号: {self.project_number}")
        
        if self.tenderer:
            summary_parts.append(f"招标人: {self.tenderer}")
        
        if self.bidding_time:
            summary_parts.append(f"截止时间: {self.bidding_time}")
        
        return " | ".join(summary_parts) if summary_parts else "无有效信息"