# -*- coding: utf-8 -*-
"""
招标信息提取模块
"""

from .extractor import TenderInfoExtractor
from .models import TenderInfo, QualificationRequirements

__all__ = ['TenderInfoExtractor', 'TenderInfo', 'QualificationRequirements']