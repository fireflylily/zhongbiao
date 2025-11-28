#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 modules/document_parser/
包含对文档解析模块的全面单元测试
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_tender_system.modules.document_parser.parser_manager import (
    ParserManager, DocumentType, ParseStatus, ParseResult
)


class TestParserManager:
    """测试ParserManager类"""

    @pytest.fixture
    def mock_db(self):
        """Mock数据库"""
        with patch('ai_tender_system.modules.document_parser.parser_manager.get_knowledge_base_db') as mock:
            db = Mock()
            db.execute_query = Mock(return_value=None)
            mock.return_value = db
            yield db

    @pytest.fixture
    def mock_config(self):
        """Mock配置"""
        with patch('ai_tender_system.modules.document_parser.parser_manager.get_config') as mock:
            config = Mock()
            mock.return_value = config
            yield config

    @pytest.fixture
    def parser_manager(self, mock_db, mock_config):
        """创建ParserManager实例"""
        return ParserManager()

    def test_init(self, parser_manager):
        """测试初始化"""
        assert parser_manager is not None
        assert parser_manager._parsers == {}
        assert parser_manager._text_splitter is None
        assert parser_manager._content_cleaner is None

    def test_detect_document_type_pdf(self, parser_manager):
        """测试检测PDF文档类型"""
        doc_type = parser_manager._detect_document_type("/path/to/file.pdf")
        assert doc_type == DocumentType.PDF

    def test_detect_document_type_docx(self, parser_manager):
        """测试检测DOCX文档类型"""
        doc_type = parser_manager._detect_document_type("/path/to/file.docx")
        assert doc_type == DocumentType.WORD

    def test_detect_document_type_doc(self, parser_manager):
        """测试检测DOC文档类型"""
        doc_type = parser_manager._detect_document_type("/path/to/file.doc")
        assert doc_type == DocumentType.DOC

    def test_detect_document_type_txt(self, parser_manager):
        """测试检测TXT文档类型"""
        doc_type = parser_manager._detect_document_type("/path/to/file.txt")
        assert doc_type == DocumentType.TXT

    def test_detect_document_type_unknown(self, parser_manager):
        """测试检测未知文档类型"""
        doc_type = parser_manager._detect_document_type("/path/to/file.xyz")
        assert doc_type == DocumentType.UNKNOWN

    def test_get_parser_pdf(self, parser_manager):
        """测试获取PDF解析器"""
        with patch('ai_tender_system.modules.document_parser.parser_manager.PDFParser'):
            parser = parser_manager._get_parser(DocumentType.PDF)
            assert parser is not None
            assert DocumentType.PDF in parser_manager._parsers

    def test_get_parser_word(self, parser_manager):
        """测试获取Word解析器"""
        with patch('ai_tender_system.modules.document_parser.parser_manager.WordParser'):
            parser = parser_manager._get_parser(DocumentType.WORD)
            assert parser is not None
            assert DocumentType.WORD in parser_manager._parsers

    def test_get_parser_txt(self, parser_manager):
        """测试获取TXT解析器"""
        with patch('ai_tender_system.modules.document_parser.parser_manager.TXTParser'):
            parser = parser_manager._get_parser(DocumentType.TXT)
            assert parser is not None
            assert DocumentType.TXT in parser_manager._parsers

    def test_get_parser_unsupported(self, parser_manager):
        """测试获取不支持的解析器"""
        with pytest.raises(ValueError) as exc_info:
            parser_manager._get_parser(DocumentType.UNKNOWN)

        assert "不支持的文档类型" in str(exc_info.value)

    def test_get_text_splitter(self, parser_manager):
        """测试获取文本分块器"""
        with patch('ai_tender_system.modules.document_parser.parser_manager.IntelligentTextSplitter'):
            splitter = parser_manager._get_text_splitter()
            assert splitter is not None
            assert parser_manager._text_splitter is not None

            # 再次调用应返回同一实例
            splitter2 = parser_manager._get_text_splitter()
            assert splitter2 is splitter

    def test_get_content_cleaner(self, parser_manager):
        """测试获取内容清洗器"""
        with patch('ai_tender_system.modules.document_parser.parser_manager.ContentCleaner'):
            cleaner = parser_manager._get_content_cleaner()
            assert cleaner is not None
            assert parser_manager._content_cleaner is not None

            # 再次调用应返回同一实例
            cleaner2 = parser_manager._get_content_cleaner()
            assert cleaner2 is cleaner

    @pytest.mark.asyncio
    async def test_parse_document_success(self, parser_manager, mock_db):
        """测试解析文档成功"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w', encoding='utf-8') as f:
            f.write("测试文档内容")
            temp_file = f.name

        try:
            # Mock解析器
            with patch.object(parser_manager, '_get_parser') as mock_get_parser, \
                 patch.object(parser_manager, '_get_content_cleaner') as mock_get_cleaner, \
                 patch.object(parser_manager, '_get_text_splitter') as mock_get_splitter, \
                 patch.object(parser_manager, '_update_parse_status'), \
                 patch.object(parser_manager, '_save_parse_result', new_callable=AsyncMock):

                # Mock解析器
                mock_parser = Mock()
                mock_parser.parse = AsyncMock(return_value=("测试内容", {'page_count': 1}))
                mock_get_parser.return_value = mock_parser

                # Mock清洗器
                mock_cleaner = Mock()
                mock_cleaner.clean_content = Mock(return_value="清洗后内容")
                mock_get_cleaner.return_value = mock_cleaner

                # Mock分块器
                mock_splitter = Mock()
                mock_splitter.split_text = Mock(return_value=[
                    {'content': '块1', 'index': 0},
                    {'content': '块2', 'index': 1}
                ])
                mock_get_splitter.return_value = mock_splitter

                # 执行解析
                result = await parser_manager.parse_document(doc_id=1, file_path=temp_file)

                # 验证结果
                assert result.doc_id == 1
                assert result.status == ParseStatus.COMPLETED
                assert result.content == "清洗后内容"
                assert len(result.chunks) == 2
                assert result.parse_time > 0

        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)

    @pytest.mark.asyncio
    async def test_parse_document_unsupported_format(self, parser_manager):
        """测试解析不支持的文档格式"""
        with patch.object(parser_manager, '_update_parse_status'):
            result = await parser_manager.parse_document(doc_id=1, file_path="/path/to/file.xyz")

            assert result.status == ParseStatus.FAILED
            assert "不支持的文档格式" in result.error_message

    @pytest.mark.asyncio
    async def test_parse_document_parser_error(self, parser_manager):
        """测试解析器抛出异常"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name

        try:
            with patch.object(parser_manager, '_get_parser') as mock_get_parser, \
                 patch.object(parser_manager, '_update_parse_status'):

                # Mock解析器抛出异常
                mock_parser = Mock()
                mock_parser.parse = AsyncMock(side_effect=Exception("解析错误"))
                mock_get_parser.return_value = mock_parser

                result = await parser_manager.parse_document(doc_id=1, file_path=temp_file)

                assert result.status == ParseStatus.FAILED
                assert "解析错误" in result.error_message

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_parse_document_simple_success(self, parser_manager):
        """测试简化版本解析文档成功"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w', encoding='utf-8') as f:
            f.write("这是测试内容")
            temp_file = f.name

        try:
            with patch.object(parser_manager, '_get_parser') as mock_get_parser:
                # Mock解析器
                mock_parser = Mock()
                mock_parser.parse = AsyncMock(return_value=("测试文本内容", {}))
                mock_get_parser.return_value = mock_parser

                # 执行简化解析
                text = parser_manager.parse_document_simple(temp_file)

                assert text == "测试文本内容"
                assert isinstance(text, str)

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_parse_document_simple_unsupported_format(self, parser_manager):
        """测试简化解析不支持的格式"""
        with pytest.raises(ValueError) as exc_info:
            parser_manager.parse_document_simple("/path/to/file.xyz")

        assert "不支持的文档格式" in str(exc_info.value)

    def test_parse_document_simple_empty_content(self, parser_manager):
        """测试简化解析空内容"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name

        try:
            with patch.object(parser_manager, '_get_parser') as mock_get_parser:
                # Mock解析器返回空内容
                mock_parser = Mock()
                mock_parser.parse = AsyncMock(return_value=("", {}))
                mock_get_parser.return_value = mock_parser

                with pytest.raises(ValueError) as exc_info:
                    parser_manager.parse_document_simple(temp_file)

                assert "文档内容为空" in str(exc_info.value)

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_update_parse_status(self, parser_manager, mock_db):
        """测试更新解析状态"""
        parser_manager._update_parse_status(
            doc_id=1,
            status=ParseStatus.COMPLETED,
            error_message=""
        )

        # 验证数据库调用
        mock_db.execute_query.assert_called_once()
        call_args = mock_db.execute_query.call_args
        assert 'UPDATE documents' in call_args[0][0]
        assert 'completed' in call_args[0][1]

    @pytest.mark.asyncio
    async def test_get_parse_status(self, parser_manager, mock_db):
        """测试获取解析状态"""
        # Mock数据库查询结果
        mock_db.execute_query.return_value = [{
            'doc_id': 1,
            'parse_status': 'completed',
            'parse_error': '',
            'parse_time': '2025-01-01 12:00:00'
        }]

        status = await parser_manager.get_parse_status(doc_id=1)

        assert status['doc_id'] == 1
        assert status['status'] == 'completed'
        assert status['progress'] == 100

    @pytest.mark.asyncio
    async def test_get_parse_status_not_found(self, parser_manager, mock_db):
        """测试获取不存在文档的解析状态"""
        mock_db.execute_query.return_value = []

        status = await parser_manager.get_parse_status(doc_id=999)

        assert status['doc_id'] == 999
        assert status['status'] == 'not_found'
        assert status['progress'] == 0

    def test_calculate_progress(self, parser_manager):
        """测试计算解析进度"""
        assert parser_manager._calculate_progress('pending') == 0
        assert parser_manager._calculate_progress('processing') == 50
        assert parser_manager._calculate_progress('completed') == 100
        assert parser_manager._calculate_progress('failed') == 0
        assert parser_manager._calculate_progress('unknown') == 0

    @pytest.mark.asyncio
    async def test_batch_parse_documents(self, parser_manager, mock_db):
        """测试批量解析文档"""
        # Mock文档信息
        def mock_get_doc_info(doc_id):
            return {'doc_id': doc_id, 'file_path': f'/path/to/doc{doc_id}.txt'}

        with patch.object(parser_manager, '_get_document_info', side_effect=mock_get_doc_info), \
             patch.object(parser_manager, 'parse_document') as mock_parse:

            # Mock解析结果
            mock_parse.return_value = ParseResult(
                doc_id=1,
                status=ParseStatus.COMPLETED,
                content="内容",
                chunks=[],
                metadata={},
                parse_time=1.0
            )

            results = await parser_manager.batch_parse_documents([1, 2, 3])

            assert len(results) == 3
            assert mock_parse.call_count == 3

    def test_get_document_info(self, parser_manager, mock_db):
        """测试获取文档信息"""
        # Mock数据库查询
        mock_db.execute_query.return_value = [{
            'doc_id': 1,
            'filename': 'test.pdf',
            'file_path': '/path/to/test.pdf'
        }]

        doc_info = parser_manager._get_document_info(doc_id=1)

        assert doc_info is not None
        assert doc_info['doc_id'] == 1
        assert doc_info['filename'] == 'test.pdf'

    def test_get_document_info_not_found(self, parser_manager, mock_db):
        """测试获取不存在的文档信息"""
        mock_db.execute_query.return_value = []

        doc_info = parser_manager._get_document_info(doc_id=999)

        assert doc_info is None


class TestParseResult:
    """测试ParseResult数据类"""

    def test_parse_result_init(self):
        """测试ParseResult初始化"""
        result = ParseResult(
            doc_id=1,
            status=ParseStatus.COMPLETED,
            content="测试内容"
        )

        assert result.doc_id == 1
        assert result.status == ParseStatus.COMPLETED
        assert result.content == "测试内容"
        assert result.chunks == []
        assert result.metadata == {}
        assert result.error_message == ""
        assert result.parse_time == 0.0

    def test_parse_result_with_chunks(self):
        """测试ParseResult包含分块"""
        chunks = [
            {'content': '块1', 'index': 0},
            {'content': '块2', 'index': 1}
        ]

        result = ParseResult(
            doc_id=1,
            status=ParseStatus.COMPLETED,
            content="完整内容",
            chunks=chunks
        )

        assert len(result.chunks) == 2
        assert result.chunks[0]['content'] == '块1'

    def test_parse_result_with_metadata(self):
        """测试ParseResult包含元数据"""
        metadata = {
            'page_count': 10,
            'author': '测试作者',
            'created_date': '2025-01-01'
        }

        result = ParseResult(
            doc_id=1,
            status=ParseStatus.COMPLETED,
            metadata=metadata
        )

        assert result.metadata['page_count'] == 10
        assert result.metadata['author'] == '测试作者'

    def test_parse_result_failed(self):
        """测试ParseResult失败状态"""
        result = ParseResult(
            doc_id=1,
            status=ParseStatus.FAILED,
            error_message="解析失败：文件损坏"
        )

        assert result.status == ParseStatus.FAILED
        assert "文件损坏" in result.error_message


class TestDocumentType:
    """测试DocumentType枚举"""

    def test_document_type_values(self):
        """测试DocumentType枚举值"""
        assert DocumentType.PDF.value == "pdf"
        assert DocumentType.WORD.value == "docx"
        assert DocumentType.DOC.value == "doc"
        assert DocumentType.TXT.value == "txt"
        assert DocumentType.UNKNOWN.value == "unknown"


class TestParseStatus:
    """测试ParseStatus枚举"""

    def test_parse_status_values(self):
        """测试ParseStatus枚举值"""
        assert ParseStatus.PENDING.value == "pending"
        assert ParseStatus.PROCESSING.value == "processing"
        assert ParseStatus.COMPLETED.value == "completed"
        assert ParseStatus.FAILED.value == "failed"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
