# MCP处理架构说明

## 概述
系统已全面升级为使用MCP（Model Context Protocol）处理方法，所有传统处理器已弃用。

## 核心处理器
- **主处理器**: `mcp_bidder_name_processor_enhanced.py`
- **功能**: 智能识别并填写投标人名称、公司地址、项目编号等字段

## 支持的格式（共22种）
### 方式1：替换内容（replace_content）
1. `（请填写供应商名称）`
2. `（请填写投标人名称）`
3. `（请填写公司名称）`
4. `（公司名称）` ✨ 新增
5. `（单位名称）` ✨ 新增
6. `（供应商全称）`
7. `（供应商名称）`
8. `（供应商名称、地址）` ✨ 新增 - 自动填写公司名称和地址

### 方式2：空格填写（fill_space）
9. `公司名称（全称、盖章）：________________`
10. `公司名称（全称、盖章）：`
11. `公司名称（盖章）：`
12. `供应商名称(盖章) ：         ` ✨ 新增
13. `供应商全称及公章：  `
14. `供应商名称：________________（公章）`
15. `供应商名称：                                （加盖公章）`
16. `供应商名称：                                        ` (长空格)
17. `供应商名称：               ` (中等空格)
18. `供应商名称：___________________`
19. `供应商名称                                    ` ✨ 新增 (无冒号)
20. `供应商名称：                          采购编号：                ` ✨ 新增 (双字段)
21. `供应商名称：` (通用)
22. `投标人名称相关填写`

## 核心功能
- ✅ **智能模式识别**: 自动识别22种不同格式
- ✅ **格式保留**: 保持原始字体、大小、颜色等格式
- ✅ **占位符清理**: 自动清理公司名称后的多余占位符
- ✅ **地址支持**: 支持公司名称和地址组合填写
- ✅ **项目编号**: 从配置文件自动读取项目编号
- ✅ **跨run处理**: 处理Word文档中的复杂格式分割

## 配置信息
- **公司地址**: 北京市东城区王府井大街200号七层711室
- **项目编号**: 从 `tender_config.ini` 读取
- **日志记录**: 详细的处理过程日志

## 弃用的处理器
以下文件已移至 `deprecated/` 目录：
- `business_response_processor.py` - 传统商务应答处理器
- `enhanced_business_response_processor.py` - 增强商务应答处理器
- `enhanced_inline_reply.py` - 增强内联回复处理器
- `mcp_bidder_name_processor.py` - 原版MCP处理器

## Web接口
- **主上传**: `/upload` - 使用MCP处理器处理文档
- **商务应答**: `/process-business-response` - 专用商务应答处理
- **API测试**: `/api/test` - MCP处理器初始化测试

## 使用示例
```python
from mcp_bidder_name_processor_enhanced import MCPBidderNameProcessor

processor = MCPBidderNameProcessor()
result = processor.process_bidder_name(
    input_file="template.docx",
    output_file="output.docx", 
    company_name="智慧足迹数据科技有限公司"
)
```

## 性能优势
- 🚀 **单次遍历**: O(n) 时间复杂度
- 🎯 **精确匹配**: 避免误识别
- 🛡️ **原子操作**: 要么全部成功，要么全部失败
- 🔧 **易维护**: 单一职责原则