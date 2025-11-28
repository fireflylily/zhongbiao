"""
测试modules/business_response/qualification_matcher.py
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.unit
class TestQualificationMatcher:
    """测试资质匹配器"""

    def test_qualification_mapping_exists(self):
        """测试资质映射表存在"""
        from ai_tender_system.modules.business_response.qualification_matcher import QUALIFICATION_MAPPING
        
        assert isinstance(QUALIFICATION_MAPPING, dict)
        assert len(QUALIFICATION_MAPPING) > 0

    def test_qualification_mapping_structure(self):
        """测试资质映射表结构"""
        from ai_tender_system.modules.business_response.qualification_matcher import QUALIFICATION_MAPPING
        
        for key, value in QUALIFICATION_MAPPING.items():
            assert 'keywords' in value, f"{key} 缺少 keywords"
            assert isinstance(value['keywords'], list), f"{key} keywords应为列表"
            assert 'priority' in value, f"{key} 缺少 priority"
            assert 'category' in value, f"{key} 缺少 category"

    def test_basic_qualification_keys(self):
        """测试基础资质类型是否存在"""
        from ai_tender_system.modules.business_response.qualification_matcher import QUALIFICATION_MAPPING

        # Check essential qualification types that should be present
        essential_quals = [
            'business_license',  # 营业执照
            'iso9001',           # 质量管理体系
            'iso27001',          # 信息安全管理体系
            'cmmi'               # 软件能力成熟度 (instead of software_capability)
        ]

        for qual in essential_quals:
            assert qual in QUALIFICATION_MAPPING, f"缺少基础资质类型: {qual}"


@pytest.mark.unit
@patch('ai_tender_system.common.database.get_knowledge_base_db')
class TestQualificationMatcherIntegration:
    """测试资质匹配器集成功能"""

    def test_match_qualifications_basic(self, mock_db, sample_tender_text):
        """测试基本资质匹配"""
        from ai_tender_system.modules.business_response.qualification_matcher import QualificationMatcher

        # Mock数据库 - not used for now since matcher doesn't need DB in __init__
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance

        # Create matcher (no company_id needed in constructor)
        matcher = QualificationMatcher()

        # Test extract_required_qualifications with mock data
        # Simulate tender requirements in the format the method expects
        qualifications_data = {
            'requirements': [
                {
                    'category': 'qualification',
                    'detail': '投标人须具有有效的营业执照',
                    'subcategory': '基本资质',
                    'constraint_type': 'mandatory'
                },
                {
                    'category': 'qualification',
                    'detail': '具有ISO9001质量管理体系认证',
                    'subcategory': '质量认证',
                    'constraint_type': 'mandatory'
                }
            ]
        }

        # Call the extraction method
        results = matcher.extract_required_qualifications(qualifications_data)

        # Verify results
        assert isinstance(results, list)
        # Should match business_license and iso9001
        assert len(results) >= 1  # At least one qualification should be matched
