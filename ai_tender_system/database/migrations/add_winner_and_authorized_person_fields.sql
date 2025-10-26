-- =====================================================
-- 迁移: 添加中标人数量和被授权人信息字段到 tender_projects 表
-- 创建时间: 2025-10-26
-- 描述: 添加前端表单中使用但数据库缺失的字段
-- =====================================================

-- 添加中标人数量字段
ALTER TABLE tender_projects ADD COLUMN winner_count VARCHAR(50);

-- 添加被授权人信息字段
ALTER TABLE tender_projects ADD COLUMN authorized_person_name VARCHAR(100);
ALTER TABLE tender_projects ADD COLUMN authorized_person_id VARCHAR(18);
ALTER TABLE tender_projects ADD COLUMN authorized_person_position VARCHAR(100);
