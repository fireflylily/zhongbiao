-- 简历库数据库表结构
-- 用于存储人员简历信息和相关附件

-- 简历主表
CREATE TABLE IF NOT EXISTS resumes (
    resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,

    -- 基本信息
    name VARCHAR(50) NOT NULL,                -- 姓名
    gender VARCHAR(10),                       -- 性别
    birth_date DATE,                          -- 出生日期
    nationality VARCHAR(20),                  -- 民族
    native_place VARCHAR(100),                -- 籍贯
    political_status VARCHAR(50),             -- 政治面貌
    id_number VARCHAR(18),                    -- 身份证号

    -- 教育信息
    education_level VARCHAR(20),              -- 学历（本科/硕士/博士等）
    degree VARCHAR(20),                       -- 学位
    university VARCHAR(100),                  -- 毕业院校
    major VARCHAR(100),                       -- 专业
    graduation_date DATE,                     -- 毕业时间

    -- 工作信息
    current_position VARCHAR(100),            -- 当前职位
    professional_title VARCHAR(100),          -- 职称
    work_years INTEGER,                       -- 工作年限
    current_company VARCHAR(200),             -- 当前工作单位
    department VARCHAR(100),                  -- 所在部门

    -- 技能信息
    skills TEXT,                              -- 技能特长（JSON格式）
    certificates TEXT,                        -- 证书列表（JSON格式）
    languages TEXT,                           -- 语言能力（JSON格式）
    project_experience TEXT,                  -- 项目经验（JSON格式）

    -- 联系方式
    phone VARCHAR(20),                        -- 手机号码
    email VARCHAR(100),                       -- 邮箱
    address VARCHAR(200),                     -- 联系地址

    -- 其他信息
    salary_expectation VARCHAR(50),           -- 期望薪资
    work_location VARCHAR(100),               -- 工作地点
    introduction TEXT,                        -- 个人简介
    awards TEXT,                              -- 获奖情况

    -- 系统字段
    status VARCHAR(20) DEFAULT 'active',      -- 状态：active/inactive/archived
    tags VARCHAR(500),                        -- 标签（逗号分隔）
    created_by VARCHAR(50),                   -- 创建人
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- 外键
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL
);

-- 简历附件表
CREATE TABLE IF NOT EXISTS resume_attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,

    -- 文件信息
    file_name VARCHAR(255) NOT NULL,          -- 文件名（系统生成）
    original_filename VARCHAR(255) NOT NULL,   -- 原始文件名
    file_path VARCHAR(500) NOT NULL,          -- 文件路径
    file_type VARCHAR(20),                    -- 文件类型（pdf/jpg/png等）
    file_size INTEGER,                        -- 文件大小（字节）

    -- 附件分类（重要）
    attachment_category VARCHAR(50) NOT NULL,  -- 附件类别
    -- resume: 简历文件
    -- id_card: 身份证
    -- education: 学历证书
    -- degree: 学位证书
    -- qualification: 资质证书
    -- award: 获奖证书
    -- other: 其他

    attachment_description TEXT,              -- 附件说明

    -- 时间戳
    uploaded_by VARCHAR(50),                  -- 上传人
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- 外键
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_resumes_company ON resumes(company_id);
CREATE INDEX IF NOT EXISTS idx_resumes_name ON resumes(name);
CREATE INDEX IF NOT EXISTS idx_resumes_position ON resumes(current_position);
CREATE INDEX IF NOT EXISTS idx_resumes_education ON resumes(education_level);
CREATE INDEX IF NOT EXISTS idx_resumes_status ON resumes(status);
CREATE INDEX IF NOT EXISTS idx_resumes_created ON resumes(created_at);

-- 创建附件表索引
CREATE INDEX IF NOT EXISTS idx_resume_attachments ON resume_attachments(resume_id);
CREATE INDEX IF NOT EXISTS idx_attachment_category ON resume_attachments(attachment_category);

-- 创建全文搜索虚拟表（用于快速搜索）
CREATE VIRTUAL TABLE IF NOT EXISTS resumes_fts USING fts5(
    name,
    current_position,
    skills,
    university,
    major,
    introduction,
    content=resumes
);

-- 触发器：自动更新 updated_at 字段
CREATE TRIGGER IF NOT EXISTS update_resumes_timestamp
AFTER UPDATE ON resumes
FOR EACH ROW
BEGIN
    UPDATE resumes SET updated_at = CURRENT_TIMESTAMP WHERE resume_id = NEW.resume_id;
END;