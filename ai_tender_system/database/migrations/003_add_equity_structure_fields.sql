-- 为 companies 表添加股权结构字段
-- 创建时间: 2025-10-27
-- 描述: 在财务信息模块中添加实际控制人、控股股东和股东信息（JSON格式）

-- 1. 实际控制人（实际控制公司经营决策的个人或组织）
ALTER TABLE companies ADD COLUMN actual_controller TEXT;

-- 2. 控股股东（持股比例最大或有实际控制权的股东）
ALTER TABLE companies ADD COLUMN controlling_shareholder TEXT;

-- 3. 股东信息（JSON格式存储，包含：股东名称、类型（企业/自然人）、出资比例）
-- JSON示例: [{"name":"张三","type":"自然人","ratio":"40%"},{"name":"XX公司","type":"企业","ratio":"60%"}]
ALTER TABLE companies ADD COLUMN shareholders_info TEXT;
