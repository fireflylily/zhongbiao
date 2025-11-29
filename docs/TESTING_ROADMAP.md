# 测试覆盖率提升路线图 (Week4-7详细计划)

**当前状态**: Week3完成，覆盖率19.91%
**最终目标**: Week7完成，覆盖率60%
**剩余时间**: 4周
**剩余提升**: +40.09%

---

## 📊 整体进度预览

```
Week1-3: ████████░░░░░░░░░░░░░░░ 19.91% ✅
Week4:   ████████████████░░░░░░░░ 35%    🎯
Week5:   ████████████████████░░░░ 45%    🎯
Week6:   ██████████████████████░░ 52%    🎯
Week7:   ████████████████████████ 60%    🏆

当前: [████░░░░░░] 33% (19.91/60)
```

---

## 📅 Week4详细计划：商务应答深度集成测试

### 🎯 目标

- **覆盖率**: 19.91% → **35%** (+15.09%)
- **时间**: 3-4天
- **新增测试**: 30个集成测试

### 📋 Day-by-Day计划

#### **Day 1**: 修复和优化 (3-4小时)

**任务1: 修复当前失败的集成测试**
```python
# 修复10个失败测试
- test_fill_simple_document_with_smart_filler
- test_fill_bracket_fields
- test_fill_combo_fields
...

# 调整断言匹配实际API返回值
# 确保20个集成测试100%通过
```

**任务2: 创建真实测试文档**
```bash
# 准备测试fixtures
tests/fixtures/
├── sample_template.docx      # 商务应答模板（简化版）
└── sample_company_quals.json # 资质文件路径
```

**预期产出**:
- ✅ 20个集成测试全部通过
- ✅ fixtures准备完成

---

#### **Day 2**: 图片插入流程测试 (6-8小时)

**创建**: `test_image_insertion_integration.py`

```python
# 测试1-3: 营业执照插入
def test_insert_business_license_to_placeholder()
def test_insert_business_license_without_placeholder()
def test_business_license_image_sizing()

# 测试4-7: 身份证插入
def test_insert_legal_id_cards_front_back()
def test_insert_auth_id_cards_to_table()
def test_id_card_table_creation()
def test_id_card_positioning()

# 测试8-12: 资质证书插入
def test_insert_single_qualification()
def test_insert_multiple_qualifications()
def test_qualification_with_insert_hint()
def test_qualification_without_placeholder_appends()
def test_multi_page_pdf_qualification()

# 测试13-14: 批量插入
def test_insert_all_images_flow()
def test_image_insertion_statistics()
```

**预期覆盖提升**:
- image_handler.py: 10.92% → 40-45%
- id_card_inserter.py: 4.10% → 30-35%

---

#### **Day 3**: 完整文档处理流程 (6-8小时)

**创建**: `test_document_processing_flow.py`

```python
# 端到端流程测试（8个）
def test_complete_business_response_generation():
    """
    测试完整流程:
    1. 加载模板
    2. 扫描字段
    3. 填充文字
    4. 插入图片
    5. 保存输出
    6. 验证结果
    """

def test_template_with_tables()
def test_template_with_complex_layout()
def test_multiple_companies_processing()
def test_concurrent_generation()
def test_large_document_processing()
def test_memory_efficient_processing()
def test_output_file_validation()
```

**预期覆盖提升**:
- processor.py: 25.40% → 55-60%
- smart_filler.py: 10.53% → 35-40%

---

#### **Day 4**: 异常场景和总结 (2-3小时)

**创建**: `test_error_handling_integration.py`

```python
# 异常场景测试（6个）
def test_missing_template_file()
def test_corrupted_word_document()
def test_missing_qualification_files()
def test_invalid_company_data()
def test_out_of_memory_handling()
def test_concurrent_access_safety()
```

**生成**: Week4总结报告

**验证**: 运行所有测试，确认覆盖率≥35%

---

### 📊 Week4预期成果

| 指标 | 目标 |
|------|------|
| 新增测试文件 | 3个 |
| 新增测试用例 | 30个 |
| 覆盖率提升 | +15% |
| 测试通过率 | >95% |
| processor.py覆盖 | >55% |
| image_handler.py覆盖 | >40% |

---

## 📅 Week5详细计划：文档解析模块

### 🎯 目标

- **覆盖率**: 35% → **45%** (+10%)
- **时间**: 3-4天
- **新增测试**: 25个

### 📋 工作内容

#### **文件1**: `test_pdf_parsing_flow.py` (9个测试)

```python
class TestPDFParsingFlow:
    def test_parse_simple_pdf()
    def test_parse_pdf_with_images()
    def test_parse_scanned_pdf()
    def test_extract_pdf_toc()
    def test_extract_pdf_tables()
    def test_pdf_text_cleaning()
    def test_pdf_encoding_handling()
    def test_large_pdf_processing()
    def test_corrupted_pdf_handling()
```

#### **文件2**: `test_word_parsing_flow.py` (9个测试)

```python
class TestWordParsingFlow:
    def test_parse_docx()
    def test_parse_doc()
    def test_extract_word_toc()
    def test_extract_word_tables()
    def test_preserve_formatting()
    def test_extract_word_images()
    def test_word_with_complex_layout()
    def test_password_protected_word()
    def test_word_encoding_issues()
```

#### **文件3**: `test_structure_parsing_flow.py` (7个测试)

```python
class TestStructureParsingFlow:
    def test_identify_document_structure()
    def test_extract_chapters()
    def test_extract_requirements()
    def test_extract_technical_specs()
    def test_multi_level_toc()
    def test_requirement_classification()
    def test_complex_document_structure()
```

### 📊 Week5预期成果

**关键模块提升**:
- structure_parser.py: 3.5% → 35%（+31.5%）
- pdf_parser.py: 7.51% → 40%（+32.5%）
- word_parser.py: 10.99% → 40%（+29%）
- parser_manager.py: 52.70% → 70%（+17.3%）

---

## 📅 Week6详细计划：知识库模块

### 🎯 目标

- **覆盖率**: 45% → **52%** (+7%)
- **时间**: 2-3天
- **新增测试**: 20个

### 📋 工作内容

#### **文件1**: `test_knowledge_base_flow.py` (8个)

```python
def test_add_document_to_kb()
def test_search_documents()
def test_update_document_metadata()
def test_delete_document()
def test_batch_import_documents()
def test_kb_with_categories()
def test_kb_concurrent_access()
def test_kb_backup_restore()
```

#### **文件2**: `test_vector_search_flow.py` (7个)

```python
def test_generate_embeddings()
def test_store_vectors()
def test_semantic_search()
def test_similarity_search()
def test_hybrid_search()
def test_vector_index_rebuild()
def test_search_performance()
```

#### **文件3**: `test_rag_engine_flow.py` (5个)

```python
def test_rag_question_answering()
def test_rag_context_retrieval()
def test_rag_with_filters()
def test_rag_response_quality()
def test_rag_error_handling()
```

---

## 📅 Week7详细计划：Web API测试

### 🎯 目标

- **覆盖率**: 52% → **60%** (+8%)
- **时间**: 2-3天
- **新增测试**: 15个

### 📋 工作内容

#### **文件1**: `test_business_api_flow.py` (7个)

```python
def test_upload_tender_file_api()
def test_create_project_api()
def test_generate_business_response_api()
def test_download_result_api()
def test_api_error_handling()
def test_api_concurrent_requests()
def test_api_rate_limiting()
```

#### **文件2**: `test_project_api_flow.py` (5个)

```python
def test_project_crud_operations()
def test_project_status_transitions()
def test_project_file_management()
def test_project_search_filter()
def test_project_batch_operations()
```

#### **文件3**: `test_complete_e2e_flow.py` (3个)

```python
def test_complete_tender_submission_flow():
    """
    完整的端到端测试:
    1. 用户登录
    2. 上传招标文件
    3. 创建项目
    4. 生成商务应答
    5. 生成技术方案
    6. 下载最终标书
    """

def test_multi_user_collaboration()
def test_error_recovery_flow()
```

---

## 🎯 覆盖率提升预测

### 按周预测

| Week | 覆盖率 | 本周提升 | 累计提升 | 主要贡献模块 |
|------|--------|---------|----------|-------------|
| 1-3 ✅ | 19.91% | +19.91% | +19.91% | field_recognizer, processor |
| 4 | 35% | +15.09% | +35% | image_handler, id_card |
| 5 | 45% | +10% | +45% | parsers, structure_parser |
| 6 | 52% | +7% | +52% | knowledge_base, vector |
| 7 | 60% | +8% | +60% | Web APIs |

### 按模块预测

**到Week7结束时各模块预期覆盖率**:

| 模块类别 | 代表模块 | 当前 | Week7目标 |
|---------|---------|------|----------|
| **字段处理** | field_recognizer | 86% | 90% |
| **核心处理器** | processor | 25.40% | 60% |
| **图片处理** | image_handler | 10.92% | 50% |
| **文档解析** | structure_parser | 3.5% | 40% |
| **知识库** | kb/manager | 42.37% | 65% |
| **Web API** | api_business_bp | 5.3% | 50% |
| **数据库** | database | 40.94% | 60% |
| **AI客户端** | llm_client | 45.59% | 60% |

---

## 🛠️ 工具和资源

### 需要准备的测试数据

**Week4需要**:
- [ ] sample_template.docx - 商务应答模板（简化版，100页以内）
- [ ] sample_license.jpg - 测试用营业执照图片
- [ ] sample_id_front.jpg - 测试用身份证正面
- [ ] sample_id_back.jpg - 测试用身份证反面
- [ ] sample_qual.pdf - 测试用资质证书

**Week5需要**:
- [ ] sample_tender.pdf - 测试用招标文件（PDF）
- [ ] sample_tender.docx - 测试用招标文件（Word）

**Week6需要**:
- [ ] sample_knowledge_docs/ - 测试用知识库文档（10个）

---

## ⚠️ 风险和应对

### 可能的风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|---------|
| 测试数据准备耗时 | 中 | 中 | 使用自动生成的测试数据 |
| Mock配置复杂 | 高 | 低 | 简化测试，使用真实对象 |
| 覆盖率提升不及预期 | 低 | 高 | 调整测试策略，增加集成测试 |
| 测试执行时间过长 | 中 | 低 | 使用pytest-xdist并行执行 |

### 应急预案

**如果Week4未达35%**:
- 方案A: 延长1周，确保质量
- 方案B: 降低目标到30%，后续补齐
- 方案C: 增加投入，加快进度

---

## 📈 成功指标

### 每周检查点

**Week4结束检查**:
- [ ] 覆盖率≥35%
- [ ] 新增测试≥25个
- [ ] 测试通过率≥95%
- [ ] processor.py覆盖率≥55%

**Week5结束检查**:
- [ ] 覆盖率≥45%
- [ ] structure_parser.py覆盖率≥35%

**Week6结束检查**:
- [ ] 覆盖率≥52%
- [ ] knowledge_base/manager.py覆盖率≥65%

**Week7结束检查**:
- [ ] 覆盖率≥60%
- [ ] 所有Web API覆盖率≥50%
- [ ] 测试文档完整
- [ ] CI/CD集成完善

---

## 🎯 最终交付清单

### 代码交付

- [ ] 270个高质量测试用例
- [ ] tests/integration/ 完整目录
- [ ] tests/fixtures/ 完整测试数据
- [ ] 前端测试完善（30个用例）

### 文档交付

- [x] TESTING_FINAL_SUMMARY.md - 总结报告
- [x] TESTING_REVIEW_AND_PLAN.md - Review报告
- [x] TESTING_ROADMAP.md - 本路线图
- [x] TESTING_DASHBOARD_GUIDE.md - 监控指南
- [ ] TESTING_WEEK4_SUMMARY.md - Week4总结
- [ ] TESTING_WEEK5_SUMMARY.md - Week5总结
- [ ] TESTING_WEEK6_SUMMARY.md - Week6总结
- [ ] TESTING_WEEK7_SUMMARY.md - Week7总结

### 基础设施交付

- [x] 测试框架配置完整
- [x] Web监控页面完成
- [x] GitHub Actions集成
- [ ] 测试数据完整
- [ ] CI/CD优化

---

## 📞 执行建议

### 推荐节奏

**全职投入**:
- Week4-7: 每周3天投入
- 总投入: 12天
- 完成日期: 约3周后

**兼职投入**:
- Week4-7: 每周2-3小时
- 总投入: 8-12小时/周
- 完成日期: 约4-5周后

### 优先级调整

**如果时间紧张**，可以调整目标:

**最小目标**: 40%覆盖率
- 只完成Week4-5
- 关键模块覆盖完整
- 工作量减半

**理想目标**: 60%覆盖率
- 完成Week4-7
- 全面覆盖
- 按本路线图执行

---

## 📊 附录：测试用例模板

### 集成测试模板

```python
@pytest.mark.integration
@pytest.mark.business_response
class TestXXXIntegration:
    """XXX模块集成测试"""

    def test_complete_flow(self, fixtures):
        """测试完整流程"""
        # 1. 准备数据
        # 2. 执行操作
        # 3. 验证结果
        # 4. 清理资源
        pass

    def test_error_scenario(self):
        """测试异常场景"""
        pass
```

### API测试模板

```python
@pytest.mark.integration
def test_api_endpoint(client):
    """测试API端点"""
    response = client.post('/api/xxx', json={...})
    assert response.status_code == 200
    assert response.json['success'] == True
```

---

**文档版本**: v1.0
**最后更新**: 2025-11-29
