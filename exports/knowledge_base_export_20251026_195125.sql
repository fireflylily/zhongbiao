-- Database export: knowledge_base
-- Export date: 2025-10-26T19:51:25.695356
-- Source: /Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/knowledge_base.db

-- Disable foreign key checks during import
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE access_audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100), -- 用户标识
    user_role VARCHAR(50), -- 用户角色
    action_type VARCHAR(50) NOT NULL, -- view/download/upload/delete/modify
    resource_type VARCHAR(50) NOT NULL, -- document/library/profile
    resource_id INTEGER NOT NULL,
    privacy_level INTEGER,
    access_granted BOOLEAN,
    access_reason TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE case_attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,

    -- 文件信息
    file_name VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20),  -- pdf/doc/docx/jpg/png
    file_size INTEGER,

    -- 附件类型
    attachment_type VARCHAR(50),  -- contract:合同 acceptance:验收证明 testimony:客户证明 photo:项目照片 other:其他
    attachment_description TEXT,  -- 附件说明

    -- 时间戳
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (case_id) REFERENCES case_studies(case_id) ON DELETE CASCADE
);
CREATE TABLE case_studies (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    product_id INTEGER,  -- 关联产品(可选)

    -- 基本信息
    case_title VARCHAR(255) NOT NULL,  -- 案例标题/合同名称（统一字段）
    case_number VARCHAR(100),  -- 案例编号/合同编号（统一字段）
    customer_name VARCHAR(255) NOT NULL,  -- 甲方客户名称（统一字段）
    industry VARCHAR(100),  -- 所属行业

    -- 合同信息
    contract_name VARCHAR(255),  -- 合同名称（等同于case_title）
    contract_type VARCHAR(50) NOT NULL,  -- 合同类型: 订单/合同
    final_customer_name VARCHAR(255),  -- 最终客户名称(订单类型时填写)
    contract_amount VARCHAR(100),  -- 合同金额（支持数字或文字描述，如"100万元"、"百万级"）
    contract_start_date DATE,  -- 合同开始日期
    contract_end_date DATE,  -- 合同结束日期
    party_a_customer_name VARCHAR(255),  -- 甲方客户名称（等同于customer_name）
    party_b_company_name VARCHAR(255),  -- 乙方公司名称（可从company表获取）

    -- 甲方客户详细信息
    party_a_name VARCHAR(255),  -- 甲方名称（等同于customer_name）
    party_a_address TEXT,  -- 甲方地址
    party_a_contact_name VARCHAR(100),  -- 甲方联系人姓名
    party_a_contact_phone VARCHAR(50),  -- 甲方联系电话
    party_a_contact_email VARCHAR(100),  -- 甲方联系邮箱

    -- 乙方公司详细信息
    party_b_name VARCHAR(255),  -- 乙方名称（可从company表获取）
    party_b_address TEXT,  -- 乙方地址
    party_b_contact_name VARCHAR(100),  -- 乙方联系人姓名
    party_b_contact_phone VARCHAR(50),  -- 乙方联系电话
    party_b_contact_email VARCHAR(100),  -- 乙方联系邮箱

    -- 案例状态
    case_status VARCHAR(50) DEFAULT 'success',  -- 成功/进行中/待验收

    -- 时间戳
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
INSERT INTO "case_studies" VALUES(1,1,NULL,'光大银行手机信息核查服务','','光大银行股份有限公司','金融','光大银行手机信息核查服务','合同','','百万级','','','光大银行股份有限公司','','光大银行股份有限公司','','','','','','','','','','success','system','2025-10-23 16:46:19.526985','2025-10-23 16:46:19.526987');
CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    company_code VARCHAR(50) UNIQUE,
    industry_type VARCHAR(100),
    description TEXT,

    -- 基本信息
    establish_date DATE, -- 成立日期
    legal_representative VARCHAR(100), -- 法定代表人
    legal_representative_position VARCHAR(100), -- 法定代表人职务
    social_credit_code VARCHAR(50), -- 统一社会信用代码
    registered_capital VARCHAR(100), -- 注册资本
    company_type VARCHAR(100), -- 公司类型
    registered_address TEXT, -- 注册地址
    business_scope TEXT, -- 经营范围

    -- 联系信息
    fixed_phone VARCHAR(50), -- 固定电话
    fax VARCHAR(50), -- 传真
    postal_code VARCHAR(20), -- 邮编
    email VARCHAR(255), -- 电子邮箱
    office_address TEXT, -- 办公地址

    -- 规模信息
    employee_count INTEGER, -- 员工人数规模

    security_level INTEGER DEFAULT 1, -- 1:普通 2:保密 3:机密
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
, legal_representative_gender VARCHAR(10), legal_representative_age INTEGER, authorized_person_name VARCHAR(100), authorized_person_id VARCHAR(18), authorized_person_gender VARCHAR(10), authorized_person_position VARCHAR(100), authorized_person_title VARCHAR(100), authorized_person_age INTEGER, bank_name VARCHAR(255), bank_account VARCHAR(100));
INSERT INTO "companies" VALUES(1,'中国联合网络通信有限公司','UNICOM','telecommunications','中国联合通信有限公司成立于1994年7月19日，以13.4亿元资本金艰难起步。2009年01月07日，经国务院同意，中国联合通信有限公司与中国网络通信集团公司重组合并，新公司名称为中国联合网络通信集团有限公司。','2000-04-21','陈忠岳','董事长','91110000710939135P','22539208.432769万元','有限责任公司（台港澳法人独资）','北京市西城区金融大街21号','基础电信业务（具体经营范围以许可证为准）；增值电信业务（具体经营范围以许可证为准）；经营与通信及信息业务相关的系统集成、设备生产销售、设计施工业务；技术开发、技术服务、技术咨询、技术培训；寻呼机、手机及其配件的销售、维修；电信卡的制作、销售；客户服务；房屋租赁；编辑、出版、发行电话号码簿；设计、制作、发布、代理国内外各类广告。（涉及许可证或国家专项规定的，须凭许可证经营或按专项规定办理相关手续）。（市场主体依法自主选择经营项目，开展经营活动；依法须经批准的项目，经相关部门批准后依批准的内容开展经营活动；不得从事国家和本市产业政策禁止和限制类项目的经营活动。）','010-66169571','010-66169572','100033','info@chinaunicom.cn',NULL,NULL,1,'2025-10-23 01:43:59','2025-10-25 22:04:47.268487','男',58,'黄岿','110101199001011234','男','客户经理','高级工程师',35,'中国工商银行北京分行','1234567890123456');
CREATE TABLE company_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    profile_type VARCHAR(50) NOT NULL, -- basic/qualification/personnel/financial
    profile_name VARCHAR(255) NOT NULL,
    description TEXT,
    privacy_level INTEGER DEFAULT 1, -- 1:公开 2:内部 3:机密 4:绝密
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
INSERT INTO "company_profiles" VALUES(1,1,'basic','基础信息','公司基本信息和对外资料',1,1,'2025-10-23 01:43:59','2025-10-23 01:43:59');
INSERT INTO "company_profiles" VALUES(2,1,'qualification','资质证书','各类业务资质和认证证书',2,1,'2025-10-23 01:43:59','2025-10-23 01:43:59');
INSERT INTO "company_profiles" VALUES(3,1,'personnel','人员信息','员工信息和人力资源资料',3,1,'2025-10-23 01:43:59','2025-10-23 01:43:59');
INSERT INTO "company_profiles" VALUES(4,1,'financial','财务文档','财务报告和审计资料',4,1,'2025-10-23 01:43:59','2025-10-23 01:43:59');
CREATE TABLE "company_qualifications" (
    qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- 资质类型和名称
    qualification_key VARCHAR(50) NOT NULL,  -- 资质标识键
    qualification_name VARCHAR(255) NOT NULL,
    custom_name VARCHAR(255),                 -- 用户自定义名称

    -- 文件信息
    original_filename VARCHAR(500) NOT NULL,
    safe_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),

    -- 资质有效期
    issue_date DATE,
    expire_date DATE,
    is_valid BOOLEAN DEFAULT TRUE,

    -- 审核状态
    verify_status VARCHAR(20) DEFAULT 'pending',
    verify_time TIMESTAMP,
    verify_by VARCHAR(100),
    verify_note TEXT,

    -- 元数据
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_version VARCHAR(50),          -- 文件版本(如年份:2023)
    file_sequence INTEGER DEFAULT 1,    -- 文件序号
    is_primary BOOLEAN DEFAULT TRUE,    -- 是否为主文件

    -- 外键约束
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,

    -- 新的UNIQUE约束: 同一公司、同一资质类型、不同序号可以共存
    UNIQUE (company_id, qualification_key, file_sequence)
);
INSERT INTO "company_qualifications" VALUES(1,1,'credit_tax','credit_tax',NULL,'采购严重违法失信行为记录名单.png','20251023_164401_采购严重违法失信行为记录名单_e0fbfa33.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251023_164401_采购严重违法失信行为记录名单_e0fbfa33.png',218719,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-23 08:44:01',NULL,'2025-10-23 08:44:01',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(2,1,'credit_dishonest','credit_dishonest',NULL,'失信被执行人.png','20251023_164413_失信被执行人_9de8cda2.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251023_164413_失信被执行人_9de8cda2.png',188928,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-23 08:44:13',NULL,'2025-10-23 08:44:13',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(3,1,'credit_corruption','credit_corruption',NULL,'未列入严重失信违法名单（黑名单）信息.png','20251023_164427_未列入严重失信违法名单（黑名单）信息_47f0d68a.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251023_164427_未列入严重失信违法名单（黑名单）信息_47f0d68a.png',531958,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-23 08:44:27',NULL,'2025-10-23 08:44:27',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(4,1,'credit_procurement','credit_procurement',NULL,'中国政府采购网（www.ccgp.gov.cn:search:cr:）中未被纳入政府采购严重违法失信行为信息记录.png','20251023_164433_中国政府采购网（www.ccgp.gov.cn_search_cr_）中未被纳入政府采购严重违法失信行为信息记录_e6bc54db.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251023_164433_中国政府采购网（www.ccgp.gov.cn_search_cr_）中未被纳入政府采购严重违法失信行为信息记录_e6bc54db.png',717269,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-23 08:44:33',NULL,'2025-10-23 08:44:33',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(5,1,'auth_id','auth_id',NULL,'被授权人身份证_反面_吕贺.png','20251024_111558_被授权人身份证_反面_吕贺_ac8668da.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_111558_被授权人身份证_反面_吕贺_ac8668da.png',734770,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-24 03:15:52',NULL,'2025-10-24 03:15:58',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(6,1,'basic_telecom_permit','basic_telecom_permit',NULL,'基础电信业务经营许可证1.png','20251024_111742_基础电信业务经营许可证1_7dfb1cc5.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_111742_基础电信业务经营许可证1_7dfb1cc5.png',612596,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-24 03:16:35',NULL,'2025-10-24 03:17:42',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(7,1,'value_added_telecom_permit','value_added_telecom_permit',NULL,'增值电信业务经营许可证2024.pdf','20251024_111729_增值电信业务经营许可证2024_8c3a36a6.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_111729_增值电信业务经营许可证2024_8c3a36a6.pdf',1225287,'pdf',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-24 03:17:30',NULL,'2025-10-24 03:17:30',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(11,1,'financial_audit','financial_audit',NULL,'2023年联通审计报告.pdf','20251024_215510_2023年联通审计报告_193a252e.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_215510_2023年联通审计报告_193a252e.pdf',15589931,'pdf',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-24 13:55:10',NULL,'2025-10-24 13:55:10',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(12,1,'audit_report','audit_report',NULL,'2024年联通审计报告.pdf','20251024_215527_2024年联通审计报告_50207c10.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_215527_2024年联通审计报告_50207c10.pdf',28961462,'pdf',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-24 13:55:27',NULL,'2025-10-24 13:55:27','2024',1,1);
INSERT INTO "company_qualifications" VALUES(13,1,'audit_report','audit_report',NULL,'2022年联通审计报告.pdf','20251025_211106_2022年联通审计报告_4f9405ff.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_211106_2022年联通审计报告_4f9405ff.pdf',15032868,'pdf',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-25 13:11:06',NULL,'2025-10-25 13:11:06','2022',2,0);
INSERT INTO "company_qualifications" VALUES(14,1,'audit_report','audit_report',NULL,'2023年联通审计报告.pdf','20251025_211118_2023年联通审计报告_5476266b.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_211118_2023年联通审计报告_5476266b.pdf',15589931,'pdf',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-25 13:11:18',NULL,'2025-10-25 13:11:18','2023',3,0);
INSERT INTO "company_qualifications" VALUES(15,1,'legal_id_front','legal_id_front',NULL,'法人身份证_正面_智慧足迹.png','20251026_114157_法人身份证_正面_智慧足迹_9bc1bb36.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_114157_法人身份证_正面_智慧足迹_9bc1bb36.png',927087,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-26 03:41:57',NULL,'2025-10-26 03:41:57',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(16,1,'legal_id_back','legal_id_back',NULL,'法人身份证_反面_智慧足迹.png','20251026_114204_法人身份证_反面_智慧足迹_3f01bed9.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_114204_法人身份证_反面_智慧足迹_3f01bed9.png',956485,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-26 03:42:04',NULL,'2025-10-26 03:42:04',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(17,1,'business_license','business_license',NULL,'营业执照_智慧足迹.png','20251026_114211_营业执照_智慧足迹_b62554d6.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_114211_营业执照_智慧足迹_b62554d6.png',972130,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-26 03:42:11',NULL,'2025-10-26 03:42:11',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(18,1,'auth_id_front','auth_id_front',NULL,'被授权人身份证_正面_吕贺.png','20251026_141830_被授权人身份证_正面_吕贺_c3cc4e66.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_141830_被授权人身份证_正面_吕贺_c3cc4e66.png',691480,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-26 06:18:30',NULL,'2025-10-26 06:18:30',NULL,1,1);
INSERT INTO "company_qualifications" VALUES(19,1,'auth_id_back','auth_id_back',NULL,'被授权人身份证_反面_吕贺.png','20251026_141836_被授权人身份证_反面_吕贺_d155bb40.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_141836_被授权人身份证_反面_吕贺_d155bb40.png',734770,'png',NULL,NULL,1,'pending',NULL,NULL,NULL,'2025-10-26 06:18:36',NULL,'2025-10-26 06:18:36',NULL,1,1);
CREATE TABLE document_chunks (
    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50), -- text/table/image
    page_number INTEGER,
    position_info TEXT, -- JSON: 在文档中的位置信息
    vector_embedding BLOB, -- 向量嵌入 (序列化后的numpy数组)
    metadata TEXT, -- JSON: 分块元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id),
    UNIQUE(doc_id, chunk_index)
);
CREATE TABLE document_libraries (
    library_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_type VARCHAR(20) NOT NULL, -- product/company_profile
    owner_id INTEGER NOT NULL, -- product_id 或 profile_id
    library_name VARCHAR(255) NOT NULL,
    library_type VARCHAR(50) NOT NULL, -- tech/impl/service/qualification/personnel/financial
    privacy_level INTEGER DEFAULT 1, -- 1:公开🌐 2:内部🏢 3:机密🔒 4:绝密🚫
    is_shared BOOLEAN DEFAULT FALSE,
    share_scope VARCHAR(50), -- company/category/custom
    share_products TEXT, -- JSON数组: 共享的产品ID列表
    access_control_enabled BOOLEAN DEFAULT TRUE, -- 是否启用访问控制
    auto_classification BOOLEAN DEFAULT TRUE, -- 是否自动分类文档
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE document_permissions (
    permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    user_id INTEGER,
    role_id INTEGER,
    permission_type VARCHAR(20) NOT NULL, -- read/download/modify/delete
    granted_by INTEGER, -- 授权人user_id
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id),
    FOREIGN KEY (granted_by) REFERENCES users(user_id)
);
CREATE TABLE document_toc (
    toc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,                    -- 关联文档ID
    heading_level INTEGER NOT NULL,             -- 标题级别(1/2/3/4)
    heading_text TEXT NOT NULL,                 -- 标题完整文本
    section_number VARCHAR(50),                 -- 章节号(如"3.1.101"、"第一章")
    keywords TEXT,                              -- JSON数组:提取的关键词(接口编号、产品名等)
    page_number INTEGER,                        -- 页码
    parent_toc_id INTEGER,                      -- 父级目录ID(构建树形结构)
    sequence_order INTEGER,                     -- 在文档中的顺序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_toc_id) REFERENCES document_toc(toc_id) ON DELETE SET NULL
);
CREATE TABLE documents (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL, -- pdf/doc/docx
    file_size INTEGER,
    privacy_classification INTEGER DEFAULT 1, -- 1:公开🌐 2:内部🏢 3:机密🔒 4:绝密🚫
    access_roles TEXT, -- JSON数组: 访问角色列表
    tags TEXT, -- JSON数组: 文档标签
    metadata TEXT, -- JSON: 文档元数据
    document_category VARCHAR(50) DEFAULT 'tech', -- tech:技术🔧 impl:实施📋 service:服务🛠️
    applicable_products TEXT, -- JSON数组: 适用产品ID列表
    security_classification VARCHAR(20) DEFAULT 'normal', -- normal/confidential/secret/top_secret

    -- 处理状态
    upload_status VARCHAR(20) DEFAULT 'uploaded', -- uploaded/processing/completed/failed
    parse_status VARCHAR(20) DEFAULT 'pending', -- pending/parsing/completed/failed
    vector_status VARCHAR(20) DEFAULT 'pending', -- pending/processing/completed/failed

    -- 加密和安全
    encryption_required BOOLEAN DEFAULT FALSE,
    encryption_status VARCHAR(20) DEFAULT 'none', -- none/encrypted
    audit_required BOOLEAN DEFAULT FALSE,

    -- 时间戳
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP NULL,
    vectorized_at TIMESTAMP NULL,
    last_accessed TIMESTAMP NULL,

    FOREIGN KEY (library_id) REFERENCES document_libraries(library_id)
);
CREATE TABLE file_storage (
                    file_id TEXT PRIMARY KEY,
                    original_name TEXT NOT NULL,
                    safe_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    business_type TEXT NOT NULL,
                    upload_time TIMESTAMP NOT NULL,
                    user_id TEXT,
                    company_id INTEGER,
                    description TEXT,
                    tags TEXT,
                    checksum TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
INSERT INTO "file_storage" VALUES('ed005266-f3da-4e63-b916-2f5cee7149d6','单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx','20251023_095047_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_ed005266.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_095047_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_ed005266.docx',198927,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-23 09:50:47.694259',NULL,NULL,NULL,NULL,'dc998973c91f5658ad637beadcf062efc65fea8cbc337f99e1ee11a435861f52','2025-10-23 01:50:47');
INSERT INTO "file_storage" VALUES('bd910418-c603-409d-aa89-eece7c26057a','单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx','20251023_095849_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_bd910418.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_095849_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_bd910418.docx',198927,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-23 09:58:49.353296',NULL,NULL,NULL,NULL,'dc998973c91f5658ad637beadcf062efc65fea8cbc337f99e1ee11a435861f52','2025-10-23 01:58:49');
INSERT INTO "file_storage" VALUES('1b9b345c-ba0f-4e1b-b4e6-4700f1a17eda','单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx','20251023_095904_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_1b9b345c.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_095904_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_1b9b345c.docx',198927,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-23 09:59:04.655775',NULL,NULL,NULL,NULL,'dc998973c91f5658ad637beadcf062efc65fea8cbc337f99e1ee11a435861f52','2025-10-23 01:59:04');
INSERT INTO "file_storage" VALUES('78653e00-c8f2-46a8-9ab4-b3c332db91d1','单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx','20251023_100600_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_78653e00.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_100600_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_78653e00.docx',198927,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-23 10:06:00.425307',NULL,NULL,NULL,NULL,'dc998973c91f5658ad637beadcf062efc65fea8cbc337f99e1ee11a435861f52','2025-10-23 02:06:00');
INSERT INTO "file_storage" VALUES('072bbb07-c7db-4c8b-b28d-3e4768eb5715','单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx','20251023_102422_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_072bbb07.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_102422_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_072bbb07.docx',198927,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-23 10:24:22.290194',NULL,NULL,NULL,NULL,'dc998973c91f5658ad637beadcf062efc65fea8cbc337f99e1ee11a435861f52','2025-10-23 02:24:22');
INSERT INTO "file_storage" VALUES('64797a35-4ae2-47e8-a99c-870ab741964c','单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx','20251023_112129_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_64797a35.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_112129_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_64797a35.docx',198927,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-23 11:21:29.012311',NULL,NULL,NULL,NULL,'dc998973c91f5658ad637beadcf062efc65fea8cbc337f99e1ee11a435861f52','2025-10-23 03:21:29');
INSERT INTO "file_storage" VALUES('6a251827-be44-4b8a-b753-268ae0f824e8','单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx','20251023_154118_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_6a251827.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_154118_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_6a251827.docx',198927,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-23 15:41:18.168872',NULL,NULL,NULL,NULL,'dc998973c91f5658ad637beadcf062efc65fea8cbc337f99e1ee11a435861f52','2025-10-23 07:41:18');
INSERT INTO "file_storage" VALUES('e0fbfa33-4dc1-4c3a-887a-f0d71c13ee4c','采购严重违法失信行为记录名单.png','20251023_164401_采购严重违法失信行为记录名单_e0fbfa33.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251023_164401_采购严重违法失信行为记录名单_e0fbfa33.png',218719,'image/png','qualifications','credit_tax','2025-10-23 16:44:01.971162',NULL,1,NULL,'credit_tax,company_1','995593a1d831f78951e6b9faafa0ec83b5e64e4cdb066d97e33f888a6a3393f7','2025-10-23 08:44:01');
INSERT INTO "file_storage" VALUES('9de8cda2-6792-452a-8dc0-fdd38cf385a5','失信被执行人.png','20251023_164413_失信被执行人_9de8cda2.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251023_164413_失信被执行人_9de8cda2.png',188928,'image/png','qualifications','credit_dishonest','2025-10-23 16:44:13.357709',NULL,1,NULL,'credit_dishonest,company_1','2f4e6b7b11b86c268f41690903d2ea77a2368bf1c57e1c55d4db8a16ed4098bb','2025-10-23 08:44:13');
INSERT INTO "file_storage" VALUES('47f0d68a-22a0-4218-be7f-f4af4f761880','未列入严重失信违法名单（黑名单）信息.png','20251023_164427_未列入严重失信违法名单（黑名单）信息_47f0d68a.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251023_164427_未列入严重失信违法名单（黑名单）信息_47f0d68a.png',531958,'image/png','qualifications','credit_corruption','2025-10-23 16:44:27.916925',NULL,1,NULL,'credit_corruption,company_1','d4dd2ac774ffaec5007d67adecc6dcfedc22f1b14870874424460a0f5bd8069a','2025-10-23 08:44:27');
INSERT INTO "file_storage" VALUES('e6bc54db-2cdb-498a-bed0-b8c1bf773316','中国政府采购网（www.ccgp.gov.cn:search:cr:）中未被纳入政府采购严重违法失信行为信息记录.png','20251023_164433_中国政府采购网（www.ccgp.gov.cn_search_cr_）中未被纳入政府采购严重违法失信行为信息记录_e6bc54db.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251023_164433_中国政府采购网（www.ccgp.gov.cn_search_cr_）中未被纳入政府采购严重违法失信行为信息记录_e6bc54db.png',717269,'image/png','qualifications','credit_procurement','2025-10-23 16:44:33.956610',NULL,1,NULL,'credit_procurement,company_1','07283bd69371b81bc44b67eeaf824ae8a3a133f4df42e006ac12b5f95d2e40b0','2025-10-23 08:44:33');
INSERT INTO "file_storage" VALUES('e904aac4-386d-43f0-870e-1b9bee05f15d','被授权人身份证_正面_吕贺.png','20251024_111552_被授权人身份证_正面_吕贺_e904aac4.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_111552_被授权人身份证_正面_吕贺_e904aac4.png',691480,'image/png','qualifications','auth_id','2025-10-24 11:15:52.366532',NULL,1,NULL,'auth_id,company_1','0258c00ae4cfd654fc1632a34e08ab7ef8ddd17d607e103ccc8efa10839c3e14','2025-10-24 03:15:52');
INSERT INTO "file_storage" VALUES('ac8668da-8f46-4783-ab71-29a1a01239df','被授权人身份证_反面_吕贺.png','20251024_111558_被授权人身份证_反面_吕贺_ac8668da.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_111558_被授权人身份证_反面_吕贺_ac8668da.png',734770,'image/png','qualifications','auth_id','2025-10-24 11:15:58.514967',NULL,1,NULL,'auth_id,company_1','3614c6c94db494b3f0c77d948a3a9d65c811555cf721219b8f83b7701f871be4','2025-10-24 03:15:58');
INSERT INTO "file_storage" VALUES('a2e55bad-0417-4dec-80f5-f422962f9a5f','增值电信业务经营许可证件.png','20251024_111635_增值电信业务经营许可证件_a2e55bad.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_111635_增值电信业务经营许可证件_a2e55bad.png',352197,'image/png','qualifications','basic_telecom_permit','2025-10-24 11:16:35.124219',NULL,1,NULL,'basic_telecom_permit,company_1','f7323672dc1e7db5e248cbd62e778c080421d6066007d75dc268394bb8301229','2025-10-24 03:16:35');
INSERT INTO "file_storage" VALUES('8c3a36a6-412a-4f4c-83c6-c57cd541c6b7','增值电信业务经营许可证2024.pdf','20251024_111729_增值电信业务经营许可证2024_8c3a36a6.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_111729_增值电信业务经营许可证2024_8c3a36a6.pdf',1225287,'application/pdf','qualifications','value_added_telecom_permit','2025-10-24 11:17:29.999603',NULL,1,NULL,'value_added_telecom_permit,company_1','eeddc72cafb076b8e21ac44145a430839897625531e2c5de4dd3b1d65506d009','2025-10-24 03:17:30');
INSERT INTO "file_storage" VALUES('7dfb1cc5-825d-41b4-8f85-1ad9fe94b291','基础电信业务经营许可证1.png','20251024_111742_基础电信业务经营许可证1_7dfb1cc5.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_111742_基础电信业务经营许可证1_7dfb1cc5.png',612596,'image/png','qualifications','basic_telecom_permit','2025-10-24 11:17:42.878760',NULL,1,NULL,'basic_telecom_permit,company_1','83157e2f3f31e0b26d84fc7c9f592d71e91cfc095e4c58ae5e29fb1b554dfa11','2025-10-24 03:17:42');
INSERT INTO "file_storage" VALUES('6cfefcaf-6ea2-40db-9d77-c6cac08046f8','招标文件.docx','20251024_151438_招标文件_6cfefcaf.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_151438_招标文件_6cfefcaf.docx',1426257,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-24 15:14:38.206047',NULL,NULL,NULL,NULL,'80b15e50e5584fdb44d9832dc65c6b0599387f8b8f05f515da554ac128e3b8b2','2025-10-24 07:14:38');
INSERT INTO "file_storage" VALUES('19abf575-6b92-47e1-8901-ce1baf1c561a','2024年联通审计报告.pdf','20251024_173523_2024年联通审计报告_19abf575.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_173523_2024年联通审计报告_19abf575.pdf',28961462,'application/pdf','qualifications','financial_audit','2025-10-24 17:35:23.729072',NULL,1,NULL,'financial_audit,company_1','03d04c94dc71c6fb00924585cc63c071998a238a8c27b8c4b7b30d1e0462301d','2025-10-24 09:35:23');
INSERT INTO "file_storage" VALUES('4f9b3e07-f769-4d1a-9d7d-1aab0773f225','2023年联通审计报告.pdf','20251024_173537_2023年联通审计报告_4f9b3e07.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_173537_2023年联通审计报告_4f9b3e07.pdf',15589931,'application/pdf','qualifications','financial_audit','2025-10-24 17:35:37.739948',NULL,1,NULL,'financial_audit,company_1','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-24 09:35:37');
INSERT INTO "file_storage" VALUES('a34ddba1-f91d-4c9d-8a3d-db5c152efb57','2024年联通审计报告.pdf','20251024_173851_2024年联通审计报告_a34ddba1.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_173851_2024年联通审计报告_a34ddba1.pdf',28961462,'application/pdf','qualifications','financial_audit','2025-10-24 17:38:51.485329',NULL,1,NULL,'financial_audit,company_1','03d04c94dc71c6fb00924585cc63c071998a238a8c27b8c4b7b30d1e0462301d','2025-10-24 09:38:51');
INSERT INTO "file_storage" VALUES('920204d0-9e64-4718-9ceb-c87ca3cda745','招标文件-哈银消金.docx','20251024_175323_招标文件-哈银消金_920204d0.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_175323_招标文件-哈银消金_920204d0.docx',1426257,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-24 17:53:23.965305',NULL,NULL,NULL,NULL,'80b15e50e5584fdb44d9832dc65c6b0599387f8b8f05f515da554ac128e3b8b2','2025-10-24 09:53:23');
INSERT INTO "file_storage" VALUES('193a252e-fbd9-431d-8437-b44de30f857c','2023年联通审计报告.pdf','20251024_215510_2023年联通审计报告_193a252e.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_215510_2023年联通审计报告_193a252e.pdf',15589931,'application/pdf','qualifications','financial_audit','2025-10-24 21:55:10.466140',NULL,1,NULL,'financial_audit,company_1','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-24 13:55:10');
INSERT INTO "file_storage" VALUES('50207c10-27b6-46cf-9d4a-1e97580c962c','2024年联通审计报告.pdf','20251024_215527_2024年联通审计报告_50207c10.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_215527_2024年联通审计报告_50207c10.pdf',28961462,'application/pdf','qualifications','audit_report','2025-10-24 21:55:27.648032',NULL,1,NULL,'audit_report,company_1,version_2024','03d04c94dc71c6fb00924585cc63c071998a238a8c27b8c4b7b30d1e0462301d','2025-10-24 13:55:27');
INSERT INTO "file_storage" VALUES('9356a3ef-a4b1-40ee-a025-1a1dd7b4643d','2023年联通审计报告.pdf','20251024_215536_2023年联通审计报告_9356a3ef.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_215536_2023年联通审计报告_9356a3ef.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-24 21:55:36.284962',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-24 13:55:36');
INSERT INTO "file_storage" VALUES('0bf04edc-0284-49a0-a99b-83d7b84d9a21','2023年联通审计报告.pdf','20251024_215549_2023年联通审计报告_0bf04edc.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_215549_2023年联通审计报告_0bf04edc.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-24 21:55:49.096138',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-24 13:55:49');
INSERT INTO "file_storage" VALUES('ac8fc9e8-4b39-4131-8d75-080b69d404c8','2023年联通审计报告.pdf','20251024_215930_2023年联通审计报告_ac8fc9e8.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_215930_2023年联通审计报告_ac8fc9e8.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-24 21:59:30.135578',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-24 13:59:30');
INSERT INTO "file_storage" VALUES('10ed162c-50f3-4895-ad4b-a6a2e581c79b','2024年联通审计报告.pdf','20251024_215933_2024年联通审计报告_10ed162c.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_215933_2024年联通审计报告_10ed162c.pdf',28961462,'application/pdf','qualifications','audit_report','2025-10-24 21:59:33.796804',NULL,1,NULL,'audit_report,company_1,version_2024','03d04c94dc71c6fb00924585cc63c071998a238a8c27b8c4b7b30d1e0462301d','2025-10-24 13:59:33');
INSERT INTO "file_storage" VALUES('13ffc6be-9315-4453-96c1-f2dd2bba2baf','2024年联通审计报告.pdf','20251024_220207_2024年联通审计报告_13ffc6be.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_220207_2024年联通审计报告_13ffc6be.pdf',28961462,'application/pdf','qualifications','audit_report','2025-10-24 22:02:07.984038',NULL,1,NULL,'audit_report,company_1,version_2024','03d04c94dc71c6fb00924585cc63c071998a238a8c27b8c4b7b30d1e0462301d','2025-10-24 14:02:07');
INSERT INTO "file_storage" VALUES('8e2866d0-af56-4c82-a644-cf1900fdcb5b','2023年联通审计报告.pdf','20251024_220211_2023年联通审计报告_8e2866d0.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_220211_2023年联通审计报告_8e2866d0.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-24 22:02:11.666015',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-24 14:02:11');
INSERT INTO "file_storage" VALUES('d8d0f6b8-2db8-4c1f-800c-7280e0011ba7','2023年联通审计报告.pdf','20251024_221013_2023年联通审计报告_d8d0f6b8.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_221013_2023年联通审计报告_d8d0f6b8.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-24 22:10:13.831973',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-24 14:10:13');
INSERT INTO "file_storage" VALUES('e36b2927-4188-4c81-a9a8-e5f175db97b6','2024年联通审计报告.pdf','20251024_221017_2024年联通审计报告_e36b2927.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251024_221017_2024年联通审计报告_e36b2927.pdf',28961462,'application/pdf','qualifications','audit_report','2025-10-24 22:10:17.144604',NULL,1,NULL,'audit_report,company_1,version_2024','03d04c94dc71c6fb00924585cc63c071998a238a8c27b8c4b7b30d1e0462301d','2025-10-24 14:10:17');
INSERT INTO "file_storage" VALUES('8c8829a1-fd42-4753-80b8-683c1d85b310','招标文件-哈银消金.docx','20251025_095402_招标文件-哈银消金_8c8829a1.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251025_095402_招标文件-哈银消金_8c8829a1.docx',1426257,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','tender_processing','tender_hitl_document','2025-10-25 09:54:02.856431',NULL,NULL,NULL,NULL,'80b15e50e5584fdb44d9832dc65c6b0599387f8b8f05f515da554ac128e3b8b2','2025-10-25 01:54:02');
INSERT INTO "file_storage" VALUES('0ba13945-5c5a-438b-a2a6-3a2a0a2f75d4','2024年联通审计报告.pdf','20251025_202630_2024年联通审计报告_0ba13945.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_202630_2024年联通审计报告_0ba13945.pdf',28961462,'application/pdf','qualifications','audit_report','2025-10-25 20:26:30.957742',NULL,1,NULL,'audit_report,company_1,version_2024','03d04c94dc71c6fb00924585cc63c071998a238a8c27b8c4b7b30d1e0462301d','2025-10-25 12:26:30');
INSERT INTO "file_storage" VALUES('f3c8d627-84f3-42ce-ab13-9adf55870e44','2023年联通审计报告.pdf','20251025_202633_2023年联通审计报告_f3c8d627.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_202633_2023年联通审计报告_f3c8d627.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-25 20:26:33.866001',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-25 12:26:33');
INSERT INTO "file_storage" VALUES('36c4c4dc-b4b1-4b73-935d-73c69aeb732e','2023年联通审计报告.pdf','20251025_203519_2023年联通审计报告_36c4c4dc.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_203519_2023年联通审计报告_36c4c4dc.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-25 20:35:19.822118',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-25 12:35:19');
INSERT INTO "file_storage" VALUES('000a83a9-171e-45d8-b69c-8cbb2a1bfee5','2023年联通审计报告.pdf','20251025_204129_2023年联通审计报告_000a83a9.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_204129_2023年联通审计报告_000a83a9.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-25 20:41:29.543176',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-25 12:41:29');
INSERT INTO "file_storage" VALUES('f023918b-3936-480e-bb40-9a264854bd97','2023年联通审计报告.pdf','20251025_204309_2023年联通审计报告_f023918b.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_204309_2023年联通审计报告_f023918b.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-25 20:43:09.435120',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-25 12:43:09');
INSERT INTO "file_storage" VALUES('946e0fee-53e5-4ca1-90bf-807455f70f26','2022年联通审计报告.pdf','20251025_204446_2022年联通审计报告_946e0fee.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_204446_2022年联通审计报告_946e0fee.pdf',15032868,'application/pdf','qualifications','audit_report','2025-10-25 20:44:46.179129',NULL,1,NULL,'audit_report,company_1,version_2022','0a7b156e5893b84c6ddd3ef0cf5c0c3991bc01fbfee8ccfaf777363e52502ede','2025-10-25 12:44:46');
INSERT INTO "file_storage" VALUES('4fca65ff-1a1b-4552-acd2-bb898a4f85f3','2022年联通审计报告.pdf','20251025_204612_2022年联通审计报告_4fca65ff.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_204612_2022年联通审计报告_4fca65ff.pdf',15032868,'application/pdf','qualifications','audit_report','2025-10-25 20:46:12.279799',NULL,1,NULL,'audit_report,company_1,version_2022','0a7b156e5893b84c6ddd3ef0cf5c0c3991bc01fbfee8ccfaf777363e52502ede','2025-10-25 12:46:12');
INSERT INTO "file_storage" VALUES('aa3bd57c-3b4f-4064-8685-04d0d1cabeab','2023年联通审计报告.pdf','20251025_204615_2023年联通审计报告_aa3bd57c.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_204615_2023年联通审计报告_aa3bd57c.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-25 20:46:15.080595',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-25 12:46:15');
INSERT INTO "file_storage" VALUES('a58a0058-73ce-4eb3-8dff-dd4b6f131f79','偏离表.docx','20251025_210820_偏离表_a58a0058.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/business_templates/2025/10/20251025_210820_偏离表_a58a0058.docx',12289,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','business_templates','business_response','2025-10-25 21:08:20.111229',NULL,1,NULL,NULL,'1d0c0488c86630fdca4be63ef171681c48b78d5e26600be4e6d4a05c5b06ce94','2025-10-25 13:08:20');
INSERT INTO "file_storage" VALUES('4f9405ff-7924-4347-9af5-d63cd0d54c27','2022年联通审计报告.pdf','20251025_211106_2022年联通审计报告_4f9405ff.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_211106_2022年联通审计报告_4f9405ff.pdf',15032868,'application/pdf','qualifications','audit_report','2025-10-25 21:11:06.170132',NULL,1,NULL,'audit_report,company_1,version_2022','0a7b156e5893b84c6ddd3ef0cf5c0c3991bc01fbfee8ccfaf777363e52502ede','2025-10-25 13:11:06');
INSERT INTO "file_storage" VALUES('5476266b-b820-4381-8783-0a0ed5438d0a','2023年联通审计报告.pdf','20251025_211118_2023年联通审计报告_5476266b.pdf','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251025_211118_2023年联通审计报告_5476266b.pdf',15589931,'application/pdf','qualifications','audit_report','2025-10-25 21:11:18.190951',NULL,1,NULL,'audit_report,company_1,version_2023','c6ebd50c418ec14f60a831959c34250212623d9aca392880ef126b973f3075cc','2025-10-25 13:11:18');
INSERT INTO "file_storage" VALUES('db902921-659c-4d93-a6c2-9d05e3d7a81c','供应商名称空格（加盖公章）.docx','20251025_215929_供应商名称空格（加盖公章）_db902921.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/business_templates/2025/10/20251025_215929_供应商名称空格（加盖公章）_db902921.docx',16972,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','business_templates','business_response','2025-10-25 21:59:29.352457',NULL,1,NULL,NULL,'9b366aef1696f77dde6ebf34a022ae20e8087be6e4ba89b2acb1c149f3b2966d','2025-10-25 13:59:29');
INSERT INTO "file_storage" VALUES('c8ae2a59-69a8-4f2f-8f3c-57f6e3c6df19','公司名称（全称、盖章）、法人姓名、职务、邮编、地址、电话、传真、日期.docx','20251025_220010_公司名称（全称、盖章）、法人姓名、职务、邮编、地址、电话、传真、日期_c8ae2a59.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/business_templates/2025/10/20251025_220010_公司名称（全称、盖章）、法人姓名、职务、邮编、地址、电话、传真、日期_c8ae2a59.docx',11895,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','business_templates','business_response','2025-10-25 22:00:10.679102',NULL,1,NULL,NULL,'33723101b853e293b58eda656c0a931a1d6a4e4485e1186bad3f0dec29645b18','2025-10-25 14:00:10');
INSERT INTO "file_storage" VALUES('0218654b-84d3-45d7-a8e4-6f098328faed','公司名称（全称、盖章）、法人姓名、职务、邮编、地址、电话、传真、日期.docx','20251025_220632_公司名称（全称、盖章）、法人姓名、职务、邮编、地址、电话、传真、日期_0218654b.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/business_templates/2025/10/20251025_220632_公司名称（全称、盖章）、法人姓名、职务、邮编、地址、电话、传真、日期_0218654b.docx',11895,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','business_templates','business_response','2025-10-25 22:06:32.701520',NULL,1,NULL,NULL,'33723101b853e293b58eda656c0a931a1d6a4e4485e1186bad3f0dec29645b18','2025-10-25 14:06:32');
INSERT INTO "file_storage" VALUES('621c0fd3-fbcb-4440-8a82-f5be4cd5d1ae','采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期.docx','20251025_220704_采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期_621c0fd3.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/business_templates/2025/10/20251025_220704_采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期_621c0fd3.docx',12038,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','business_templates','business_response','2025-10-25 22:07:04.411556',NULL,1,NULL,NULL,'cc6e23a78247f81da11b72656bcab75948e359f47f2a282f2448827e545b5774','2025-10-25 14:07:04');
INSERT INTO "file_storage" VALUES('b3e3cddc-0e3a-4a46-8377-d41dcd61ea7e','采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期.docx','20251025_221650_采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期_b3e3cddc.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/business_templates/2025/10/20251025_221650_采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期_b3e3cddc.docx',12038,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','business_templates','business_response','2025-10-25 22:16:50.083901',NULL,1,NULL,NULL,'cc6e23a78247f81da11b72656bcab75948e359f47f2a282f2448827e545b5774','2025-10-25 14:16:50');
INSERT INTO "file_storage" VALUES('c5398b61-e4e5-4a13-923b-80f5a7eca322','采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期.docx','20251025_230101_采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期_c5398b61.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/business_templates/2025/10/20251025_230101_采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期_c5398b61.docx',12038,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','business_templates','business_response','2025-10-25 23:01:01.962691',NULL,1,NULL,NULL,'cc6e23a78247f81da11b72656bcab75948e359f47f2a282f2448827e545b5774','2025-10-25 15:01:01');
INSERT INTO "file_storage" VALUES('5510e946-2fd7-4678-a12b-65f66c935d18','法人身份、供应商名称、成立时间、经营范围、姓名、性别、年龄、职位、（请填写供应商名称）、公章、日期.docx','20251026_091235_法人身份、供应商名称、成立时间、经营范围、姓名、性别、年龄、职位、（请填写供应商名称）、公章、日期_5510e946.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/business_templates/2025/10/20251026_091235_法人身份、供应商名称、成立时间、经营范围、姓名、性别、年龄、职位、（请填写供应商名称）、公章、日期_5510e946.docx',11718,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','business_templates','business_response','2025-10-26 09:12:35.592428',NULL,1,NULL,NULL,'4ed42548f6338c7efb15f784a0da5847077765b3ec8dfea7d3c6cc6489d9aab8','2025-10-26 01:12:35');
INSERT INTO "file_storage" VALUES('9bc1bb36-fed3-479d-861c-2a4263ca5c1d','法人身份证_正面_智慧足迹.png','20251026_114157_法人身份证_正面_智慧足迹_9bc1bb36.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_114157_法人身份证_正面_智慧足迹_9bc1bb36.png',927087,'image/png','qualifications','legal_id_front','2025-10-26 11:41:57.546092',NULL,1,NULL,'legal_id_front,company_1','7004eee053211747381b7bd2311c792eeb8534c13b1b19617b3f0e7fcd5d92ae','2025-10-26 03:41:57');
INSERT INTO "file_storage" VALUES('3f01bed9-7fad-4f30-8d6f-8a4c938546ef','法人身份证_反面_智慧足迹.png','20251026_114204_法人身份证_反面_智慧足迹_3f01bed9.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_114204_法人身份证_反面_智慧足迹_3f01bed9.png',956485,'image/png','qualifications','legal_id_back','2025-10-26 11:42:04.395736',NULL,1,NULL,'legal_id_back,company_1','a0b6799adc7d907d8d2b1be6098b27f5118b02fca18c6f8f403aec18761c5669','2025-10-26 03:42:04');
INSERT INTO "file_storage" VALUES('b62554d6-8922-4e62-98c9-89476d1660e1','营业执照_智慧足迹.png','20251026_114211_营业执照_智慧足迹_b62554d6.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_114211_营业执照_智慧足迹_b62554d6.png',972130,'image/png','qualifications','business_license','2025-10-26 11:42:11.374831',NULL,1,NULL,'business_license,company_1','2767a8be029808dac0f61317952f0982ce2ef1c40ac064742f48d4d273baf9c5','2025-10-26 03:42:11');
INSERT INTO "file_storage" VALUES('c3cc4e66-8197-46ff-9741-74c5aa7c0ae1','被授权人身份证_正面_吕贺.png','20251026_141830_被授权人身份证_正面_吕贺_c3cc4e66.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_141830_被授权人身份证_正面_吕贺_c3cc4e66.png',691480,'image/png','qualifications','auth_id_front','2025-10-26 14:18:30.168768',NULL,1,NULL,'auth_id_front,company_1','0258c00ae4cfd654fc1632a34e08ab7ef8ddd17d607e103ccc8efa10839c3e14','2025-10-26 06:18:30');
INSERT INTO "file_storage" VALUES('d155bb40-1d58-41b0-8115-fc91c2091be5','被授权人身份证_反面_吕贺.png','20251026_141836_被授权人身份证_反面_吕贺_d155bb40.png','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/qualifications/2025/10/20251026_141836_被授权人身份证_反面_吕贺_d155bb40.png',734770,'image/png','qualifications','auth_id_back','2025-10-26 14:18:36.876581',NULL,1,NULL,'auth_id_back,company_1','3614c6c94db494b3f0c77d948a3a9d65c811555cf721219b8f83b7701f871be4','2025-10-26 06:18:36');
CREATE TABLE knowledge_base_configs (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    config_type VARCHAR(20) DEFAULT 'string', -- string/json/integer/boolean
    description TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO "knowledge_base_configs" VALUES(1,'max_file_size','100','integer','文档上传最大大小(MB)',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(2,'supported_file_types','["pdf", "doc", "docx", "txt", "xls", "xlsx", "ppt", "pptx"]','json','支持的文件类型',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(3,'vector_model_name','sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2','string','向量化模型名称',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(4,'chunk_size','1000','integer','文档分块大小',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(5,'chunk_overlap','200','integer','分块重叠大小',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(6,'privacy_retention_days','2555','integer','隐私文档保留天数(7年)',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(7,'audit_log_retention_days','2555','integer','审计日志保留天数(7年)',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(8,'auto_encrypt_level','3','integer','自动加密的隐私级别阈值',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(9,'session_timeout','7200','integer','会话超时时间(秒)',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(10,'max_concurrent_uploads','5','integer','最大并发上传数',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(11,'enable_document_watermark','true','boolean','是否启用文档水印',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(12,'db_initialized','true','boolean','数据库是否已完成初始化',0,'2025-10-23 01:43:59');
INSERT INTO "knowledge_base_configs" VALUES(13,'initial_data_loaded','true','boolean','初始数据是否已加载完成',0,'2025-10-23 01:43:59');
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_code VARCHAR(50),
    product_category VARCHAR(100), -- communication/cloud/bigdata
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, product_code)
);
INSERT INTO "products" VALUES(1,1,'5G核心网产品','5G_CORE','communication','5G核心网解决方案',1,'2025-10-23 01:43:59','2025-10-23 01:43:59');
INSERT INTO "products" VALUES(2,1,'云计算平台','CLOUD_PLATFORM','cloud','企业级云计算服务平台',1,'2025-10-23 01:43:59','2025-10-23 01:43:59');
INSERT INTO "products" VALUES(3,1,'大数据平台','BIG_DATA','bigdata','大数据分析和处理平台',1,'2025-10-23 01:43:59','2025-10-23 01:43:59');
CREATE TABLE qualification_access_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    qualification_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    action_type VARCHAR(50) NOT NULL,         -- upload/download/view/update/delete
    user_id VARCHAR(100),
    user_role VARCHAR(50),
    ip_address VARCHAR(50),
    user_agent TEXT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (qualification_id) REFERENCES company_qualifications(qualification_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
CREATE TABLE qualification_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_key VARCHAR(50) NOT NULL UNIQUE,     -- 资质标识键
    type_name VARCHAR(255) NOT NULL,          -- 资质类型名称
    category VARCHAR(50),                     -- 分类：基础资质/行业资质/认证证书/其他
    is_required BOOLEAN DEFAULT FALSE,        -- 是否必需
    description TEXT,                          -- 描述
    sort_order INTEGER DEFAULT 0,             -- 排序
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
, allow_multiple_files BOOLEAN DEFAULT FALSE, version_label VARCHAR(50));
INSERT INTO "qualification_types" VALUES(1,'business_license','营业执照','基础资质',1,NULL,1,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(2,'bank_permit','开户许可证','基础资质',0,NULL,4,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(3,'legal_id_front','法人身份证正面','基础资质',0,NULL,5,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(4,'legal_id_back','法人身份证反面','基础资质',0,NULL,6,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(5,'iso9001','ISO9001质量管理体系认证','认证证书',0,NULL,10,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(7,'iso20000','ISO20000信息技术服务管理体系认证','认证证书',0,NULL,12,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(8,'iso27001','ISO27001信息安全管理体系认证','认证证书',0,NULL,13,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(9,'cmmi','CMMI认证','认证证书',0,NULL,14,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(10,'itss','ITSS信息技术服务标准认证','认证证书',0,NULL,15,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(11,'safety_production','安全生产许可证','行业资质',0,NULL,16,1,'2025-10-23 02:07:47',0,NULL);
INSERT INTO "qualification_types" VALUES(12,'software_copyright','软件著作权登记证书','行业资质',0,NULL,17,1,'2025-10-23 02:07:47',1,'软著名称');
INSERT INTO "qualification_types" VALUES(13,'patent_certificate','专利证书','行业资质',0,NULL,18,1,'2025-10-23 02:07:47',1,'专利号');
INSERT INTO "qualification_types" VALUES(14,'audit_report','财务审计报告','财务资质',0,NULL,19,1,'2025-10-23 02:07:47',1,'年份');
INSERT INTO "qualification_types" VALUES(505,'basic_telecom_permit','基础电信业务许可证','行业资质',0,NULL,7,1,'2025-10-24 02:23:47',0,NULL);
INSERT INTO "qualification_types" VALUES(506,'value_added_telecom_permit','增值电信业务许可证','行业资质',0,NULL,8,1,'2025-10-24 02:23:47',0,NULL);
INSERT INTO "qualification_types" VALUES(3028,'auth_id_front','被授权人身份证正面','基础资质',0,NULL,7,1,'2025-10-26 05:35:56',0,NULL);
INSERT INTO "qualification_types" VALUES(3029,'auth_id_back','被授权人身份证反面','基础资质',0,NULL,8,1,'2025-10-26 05:35:56',0,NULL);
INSERT INTO "qualification_types" VALUES(3166,'credit_china_check','信用中国查询证明','信用证明',0,NULL,20,1,'2025-10-26 06:36:53',0,NULL);
INSERT INTO "qualification_types" VALUES(3167,'tax_violation_check','重大税收违法案件查询证明','信用证明',0,NULL,21,1,'2025-10-26 06:36:53',0,NULL);
INSERT INTO "qualification_types" VALUES(3168,'gov_procurement_check','政府采购严重违法失信查询证明','信用证明',0,NULL,22,1,'2025-10-26 06:36:53',0,NULL);
CREATE TABLE resume_attachments (
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
INSERT INTO "resume_attachments" VALUES(4,1,'resume_1_id_card_20251023_144140.docx','董勇身份证正反面.docx','/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/resume_attachments/resume_1_id_card_20251023_144140.docx','docx',695333,'id_card',NULL,NULL,'2025-10-23 06:41:40');
CREATE TABLE resumes (
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, work_experience TEXT,

    -- 外键
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL
);
INSERT INTO "resumes" VALUES(1,NULL,'董勇','男','','汉族','山东省','群众','37110219861102381','本科','本科','北京外国语大学','计算机应用技术','','项目经理','高级',19,'智慧足迹数据科技有限公司','金融事业部',NULL,NULL,NULL,NULL,'19861102381','','西单大悦城','','','','','active',NULL,NULL,'2025-10-23 03:08:06','2025-10-23 03:30:15',NULL);
INSERT INTO sqlite_master(type,name,tbl_name,rootpage,sql)VALUES('table','resumes_fts','resumes_fts',0,'CREATE VIRTUAL TABLE resumes_fts USING fts5(
    name,
    current_position,
    skills,
    university,
    major,
    introduction,
    content=resumes
)');
INSERT INTO "resumes_fts" VALUES('董勇','项目经理',NULL,'北京外国语大学','计算机应用技术','');
CREATE TABLE 'resumes_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
INSERT INTO "resumes_fts_config" VALUES('version',4);
CREATE TABLE 'resumes_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
INSERT INTO "resumes_fts_data" VALUES(1,X'');
INSERT INTO "resumes_fts_data" VALUES(10,X'00000000000000');
CREATE TABLE 'resumes_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'resumes_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE tender_document_chapters (
    chapter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) NOT NULL,

    -- 章节信息
    chapter_node_id VARCHAR(50) NOT NULL,  -- 如 "ch_1_2_3"
    level INTEGER NOT NULL,  -- 1-3 层级
    title VARCHAR(500) NOT NULL,
    para_start_idx INTEGER NOT NULL,  -- 起始段落索引
    para_end_idx INTEGER,  -- 结束段落索引
    word_count INTEGER DEFAULT 0,
    preview_text TEXT,  -- 预览文本

    -- 选择状态
    is_selected BOOLEAN DEFAULT FALSE,  -- 用户是否选中
    auto_selected BOOLEAN DEFAULT FALSE,  -- 自动推荐选中
    skip_recommended BOOLEAN DEFAULT FALSE,  -- 推荐跳过

    -- 父子关系
    parent_chapter_id INTEGER,  -- 父章节ID

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_chapter_id) REFERENCES tender_document_chapters(chapter_id) ON DELETE CASCADE
);
INSERT INTO "tender_document_chapters" VALUES(1,5,'task_09c43b5a2130','ch_0',1,'第一部分    单一来源采购谈判邀请',54,144,3860,'中国联合网络通信有限公司：
中招国际招标有限公司受中国光大银行股份有限公司（采购人）的委托，对中国联通手机信息核验类外部数据服务采购项目组织单一来源采购，具体事项通知如下：
项目编号：TC25090CL
项目名称：中国联通手机信息核验类外部数据服务采购项目',1,1,0,NULL,'2025-10-23 02:24:25','2025-10-23 02:24:34');
INSERT INTO "tender_document_chapters" VALUES(2,5,'task_09c43b5a2130','ch_1',1,'第二部分    供应商须知',145,297,4933,'A. 说明
1.适用范围
本商务谈判文件是中国联通手机信息核验类外部数据服务采购项目商务谈判的规范性文件，适用于本项目所涉及的供应商、设备（货物）及服务采购等方面，是供应商编制商务谈判文件的依据。
2.法律适用
本商务谈判文件及由本次商务谈判产生的合同适用中华人民共和国法律。',0,1,0,NULL,'2025-10-23 02:24:25','2025-10-23 02:24:25');
INSERT INTO "tender_document_chapters" VALUES(3,5,'task_09c43b5a2130','ch_2',1,'第三部分    合同条款',298,915,24578,'（如对合同条款有偏离，需在商务条款偏离表中体现，
具体合同条款以最终生效的合同为准）',0,0,1,NULL,'2025-10-23 02:24:25','2025-10-23 02:24:25');
INSERT INTO "tender_document_chapters" VALUES(4,5,'task_09c43b5a2130','ch_3',1,'第四部分    技术需求书',916,967,1507,'一、项目背景
为增强账户实名制管理能力，进一步保障采购人业务的持续稳定运行。本次采购人拟采购的中国联通手机信息核验类外部数据服务内容包括简版三要素、在网时长、手机号状态、工作地验证、居住地验证等24项服务。
总体目标
本次采购的项目为中国联通手机信息核验类外部数据服务采购项目，拟采购中国联通手机核验类24项服务，拟引入一家供应商（联通），合作期限三年。',0,1,0,NULL,'2025-10-23 02:24:25','2025-10-23 02:24:25');
INSERT INTO "tender_document_chapters" VALUES(5,5,'task_09c43b5a2130','ch_4',1,'第五部分    谈判响应文件格式',968,1443,5059,'1报价
1.1报价函
致： 中国光大银行
根据贵方中国联通手机信息核验类外部数据服务采购项目（项目编号：TC25090CL）商务谈判的邀请，签字人    （全名）经正式授权并代表供应商            （供应商名称、地址）提交按商务谈判...',0,0,1,NULL,'2025-10-23 02:24:25','2025-10-23 02:24:25');
INSERT INTO "tender_document_chapters" VALUES(6,6,'task_b25667a09a85','ch_0',1,'第一部分    单一来源采购谈判邀请',54,144,3860,'中国联合网络通信有限公司：
中招国际招标有限公司受中国光大银行股份有限公司（采购人）的委托，对中国联通手机信息核验类外部数据服务采购项目组织单一来源采购，具体事项通知如下：
项目编号：TC25090CL
项目名称：中国联通手机信息核验类外部数据服务采购项目',1,1,0,NULL,'2025-10-23 03:21:32','2025-10-23 03:21:38');
INSERT INTO "tender_document_chapters" VALUES(7,6,'task_b25667a09a85','ch_1',1,'第二部分    供应商须知',145,297,4933,'A. 说明
1.适用范围
本商务谈判文件是中国联通手机信息核验类外部数据服务采购项目商务谈判的规范性文件，适用于本项目所涉及的供应商、设备（货物）及服务采购等方面，是供应商编制商务谈判文件的依据。
2.法律适用
本商务谈判文件及由本次商务谈判产生的合同适用中华人民共和国法律。',0,1,0,NULL,'2025-10-23 03:21:32','2025-10-23 03:21:32');
INSERT INTO "tender_document_chapters" VALUES(8,6,'task_b25667a09a85','ch_2',1,'第三部分    合同条款',298,915,24578,'（如对合同条款有偏离，需在商务条款偏离表中体现，
具体合同条款以最终生效的合同为准）',0,0,1,NULL,'2025-10-23 03:21:32','2025-10-23 03:21:32');
INSERT INTO "tender_document_chapters" VALUES(9,6,'task_b25667a09a85','ch_3',1,'第四部分    技术需求书',916,967,1507,'一、项目背景
为增强账户实名制管理能力，进一步保障采购人业务的持续稳定运行。本次采购人拟采购的中国联通手机信息核验类外部数据服务内容包括简版三要素、在网时长、手机号状态、工作地验证、居住地验证等24项服务。
总体目标
本次采购的项目为中国联通手机信息核验类外部数据服务采购项目，拟采购中国联通手机核验类24项服务，拟引入一家供应商（联通），合作期限三年。',0,1,0,NULL,'2025-10-23 03:21:32','2025-10-23 03:21:32');
INSERT INTO "tender_document_chapters" VALUES(10,6,'task_b25667a09a85','ch_4',1,'第五部分    谈判响应文件格式',968,1443,5059,'1报价
1.1报价函
致： 中国光大银行
根据贵方中国联通手机信息核验类外部数据服务采购项目（项目编号：TC25090CL）商务谈判的邀请，签字人    （全名）经正式授权并代表供应商            （供应商名称、地址）提交按商务谈判...',0,0,1,NULL,'2025-10-23 03:21:32','2025-10-23 03:21:32');
INSERT INTO "tender_document_chapters" VALUES(11,7,'task_1000f90f89ea','ch_0',1,'第一部分    单一来源采购谈判邀请',54,144,3860,'中国联合网络通信有限公司：
中招国际招标有限公司受中国光大银行股份有限公司（采购人）的委托，对中国联通手机信息核验类外部数据服务采购项目组织单一来源采购，具体事项通知如下：
项目编号：TC25090CL
项目名称：中国联通手机信息核验类外部数据服务采购项目',1,1,0,NULL,'2025-10-23 07:41:21','2025-10-23 07:41:28');
INSERT INTO "tender_document_chapters" VALUES(12,7,'task_1000f90f89ea','ch_1',1,'第二部分    供应商须知',145,297,4933,'A. 说明
1.适用范围
本商务谈判文件是中国联通手机信息核验类外部数据服务采购项目商务谈判的规范性文件，适用于本项目所涉及的供应商、设备（货物）及服务采购等方面，是供应商编制商务谈判文件的依据。
2.法律适用
本商务谈判文件及由本次商务谈判产生的合同适用中华人民共和国法律。',0,1,0,NULL,'2025-10-23 07:41:21','2025-10-23 07:41:21');
INSERT INTO "tender_document_chapters" VALUES(13,7,'task_1000f90f89ea','ch_2',1,'第三部分    合同条款',298,915,24578,'（如对合同条款有偏离，需在商务条款偏离表中体现，
具体合同条款以最终生效的合同为准）',0,0,1,NULL,'2025-10-23 07:41:21','2025-10-23 07:41:21');
INSERT INTO "tender_document_chapters" VALUES(14,7,'task_1000f90f89ea','ch_3',1,'第四部分    技术需求书',916,967,1507,'一、项目背景
为增强账户实名制管理能力，进一步保障采购人业务的持续稳定运行。本次采购人拟采购的中国联通手机信息核验类外部数据服务内容包括简版三要素、在网时长、手机号状态、工作地验证、居住地验证等24项服务。
总体目标
本次采购的项目为中国联通手机信息核验类外部数据服务采购项目，拟采购中国联通手机核验类24项服务，拟引入一家供应商（联通），合作期限三年。',0,1,0,NULL,'2025-10-23 07:41:21','2025-10-23 07:41:21');
INSERT INTO "tender_document_chapters" VALUES(15,7,'task_1000f90f89ea','ch_4',1,'第五部分    谈判响应文件格式',968,1443,5059,'1报价
1.1报价函
致： 中国光大银行
根据贵方中国联通手机信息核验类外部数据服务采购项目（项目编号：TC25090CL）商务谈判的邀请，签字人    （全名）经正式授权并代表供应商            （供应商名称、地址）提交按商务谈判...',0,0,1,NULL,'2025-10-23 07:41:21','2025-10-23 07:41:21');
INSERT INTO "tender_document_chapters" VALUES(16,8,'task_d1b8cba6db44','ch_0',1,'第一部分    单一来源采购谈判邀请',54,144,3860,'中国联合网络通信有限公司：
中招国际招标有限公司受中国光大银行股份有限公司（采购人）的委托，对中国联通手机信息核验类外部数据服务采购项目组织单一来源采购，具体事项通知如下：
项目编号：TC25090CL
项目名称：中国联通手机信息核验类外部数据服务采购项目',1,1,0,NULL,'2025-10-24 01:03:07','2025-10-26 02:53:32');
INSERT INTO "tender_document_chapters" VALUES(17,8,'task_d1b8cba6db44','ch_1',1,'第二部分    供应商须知',145,297,4933,'A. 说明
1.适用范围
本商务谈判文件是中国联通手机信息核验类外部数据服务采购项目商务谈判的规范性文件，适用于本项目所涉及的供应商、设备（货物）及服务采购等方面，是供应商编制商务谈判文件的依据。
2.法律适用
本商务谈判文件及由本次商务谈判产生的合同适用中华人民共和国法律。',0,1,0,NULL,'2025-10-24 01:03:07','2025-10-24 01:03:07');
INSERT INTO "tender_document_chapters" VALUES(18,8,'task_d1b8cba6db44','ch_2',1,'第三部分    合同条款',298,915,24578,'（如对合同条款有偏离，需在商务条款偏离表中体现，
具体合同条款以最终生效的合同为准）',0,0,1,NULL,'2025-10-24 01:03:07','2025-10-24 01:03:07');
INSERT INTO "tender_document_chapters" VALUES(19,8,'task_d1b8cba6db44','ch_3',1,'第四部分    技术需求书',916,967,1507,'一、项目背景
为增强账户实名制管理能力，进一步保障采购人业务的持续稳定运行。本次采购人拟采购的中国联通手机信息核验类外部数据服务内容包括简版三要素、在网时长、手机号状态、工作地验证、居住地验证等24项服务。
总体目标
本次采购的项目为中国联通手机信息核验类外部数据服务采购项目，拟采购中国联通手机核验类24项服务，拟引入一家供应商（联通），合作期限三年。',0,1,0,NULL,'2025-10-24 01:03:07','2025-10-24 01:03:07');
INSERT INTO "tender_document_chapters" VALUES(20,8,'task_d1b8cba6db44','ch_4',1,'第五部分    谈判响应文件格式',968,1443,5059,'1报价
1.1报价函
致： 中国光大银行
根据贵方中国联通手机信息核验类外部数据服务采购项目（项目编号：TC25090CL）商务谈判的邀请，签字人    （全名）经正式授权并代表供应商            （供应商名称、地址）提交按商务谈判...',0,0,1,NULL,'2025-10-24 01:03:07','2025-10-24 01:03:07');
INSERT INTO "tender_document_chapters" VALUES(21,9,'task_fcafea9ebcda','ch_0',1,'第一部分 招标公告',119,119,0,'(无内容)',0,1,0,NULL,'2025-10-24 07:14:39','2025-10-24 07:14:39');
INSERT INTO "tender_document_chapters" VALUES(22,9,'task_fcafea9ebcda','ch_1',1,'第二部分 投标人须知前附表及投标人须知',120,120,0,'(无内容)',0,0,1,NULL,'2025-10-24 07:14:39','2025-10-24 07:14:39');
INSERT INTO "tender_document_chapters" VALUES(23,9,'task_fcafea9ebcda','ch_2',1,'第三部分 评标办法',121,121,0,'(无内容)',0,1,0,NULL,'2025-10-24 07:14:39','2025-10-24 07:14:39');
INSERT INTO "tender_document_chapters" VALUES(24,9,'task_fcafea9ebcda','ch_3',1,'第四部分 合同主要条款及格式',122,122,0,'(无内容)',0,0,1,NULL,'2025-10-24 07:14:39','2025-10-24 07:14:39');
INSERT INTO "tender_document_chapters" VALUES(25,9,'task_fcafea9ebcda','ch_4',1,'第五部分 采购需求书',123,123,0,'(无内容)',0,1,0,NULL,'2025-10-24 07:14:39','2025-10-24 07:14:39');
INSERT INTO "tender_document_chapters" VALUES(26,9,'task_fcafea9ebcda','ch_5',1,'第六部分 附  件',124,666,18134,'投标人应认真阅读招标文件中所有的事项、格式、条款和技术规范等。投标人没有按照招标文件要求提交全部资料，或者投标文件没有对招标文件在各方面都作出实质性响应是投标人的风险，并可能导致其投标文件被拒绝。
招标文件的澄清
4.1 任何要求对招标文件进行澄清的投标人，均应按第13条规定的递交投标文件截止期十五（15）天前以书面形式通知招标人。招标人认为有必要的，在投标文件递交截止期日前以书面形式答复每一投标人（答复中不包...
招标文件的修改
为使投标人准备投标文件时有充分时间对招标文件的修改部分进行研究，招标人可自行决定是否延长递交投标文件截止时间。',0,0,0,NULL,'2025-10-24 07:14:39','2025-10-24 07:14:39');
INSERT INTO "tender_document_chapters" VALUES(27,9,'task_a80075c84665','ch_0',1,'第一部分 招标公告',119,119,0,'(无内容)',0,1,0,NULL,'2025-10-24 07:29:25','2025-10-24 07:29:25');
INSERT INTO "tender_document_chapters" VALUES(28,9,'task_a80075c84665','ch_1',1,'第二部分 投标人须知前附表及投标人须知',120,120,0,'(无内容)',0,0,1,NULL,'2025-10-24 07:29:25','2025-10-24 07:29:25');
INSERT INTO "tender_document_chapters" VALUES(29,9,'task_a80075c84665','ch_2',1,'第三部分 评标办法',121,121,0,'(无内容)',0,1,0,NULL,'2025-10-24 07:29:25','2025-10-24 07:29:25');
INSERT INTO "tender_document_chapters" VALUES(30,9,'task_a80075c84665','ch_3',1,'第四部分 合同主要条款及格式',122,122,0,'(无内容)',0,0,1,NULL,'2025-10-24 07:29:25','2025-10-24 07:29:25');
INSERT INTO "tender_document_chapters" VALUES(31,9,'task_a80075c84665','ch_4',1,'第五部分 采购需求书',123,123,0,'(无内容)',0,1,0,NULL,'2025-10-24 07:29:25','2025-10-24 07:29:25');
INSERT INTO "tender_document_chapters" VALUES(32,9,'task_a80075c84665','ch_5',1,'第六部分 附  件',124,666,18134,'投标人应认真阅读招标文件中所有的事项、格式、条款和技术规范等。投标人没有按照招标文件要求提交全部资料，或者投标文件没有对招标文件在各方面都作出实质性响应是投标人的风险，并可能导致其投标文件被拒绝。
招标文件的澄清
4.1 任何要求对招标文件进行澄清的投标人，均应按第13条规定的递交投标文件截止期十五（15）天前以书面形式通知招标人。招标人认为有必要的，在投标文件递交截止期日前以书面形式答复每一投标人（答复中不包...
招标文件的修改
为使投标人准备投标文件时有充分时间对招标文件的修改部分进行研究，招标人可自行决定是否延长递交投标文件截止时间。',0,0,0,NULL,'2025-10-24 07:29:25','2025-10-24 07:29:25');
INSERT INTO "tender_document_chapters" VALUES(33,9,'task_346a245051bd','ch_0',1,'第一部分 招标公告',119,119,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:30:59','2025-10-24 09:30:59');
INSERT INTO "tender_document_chapters" VALUES(34,9,'task_346a245051bd','ch_1',1,'第二部分 投标人须知前附表及投标人须知',120,120,0,'(无内容)',0,0,1,NULL,'2025-10-24 09:30:59','2025-10-24 09:30:59');
INSERT INTO "tender_document_chapters" VALUES(35,9,'task_346a245051bd','ch_2',1,'第三部分 评标办法',121,121,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:30:59','2025-10-24 09:30:59');
INSERT INTO "tender_document_chapters" VALUES(36,9,'task_346a245051bd','ch_3',1,'第四部分 合同主要条款及格式',122,122,0,'(无内容)',0,0,1,NULL,'2025-10-24 09:30:59','2025-10-24 09:30:59');
INSERT INTO "tender_document_chapters" VALUES(37,9,'task_346a245051bd','ch_4',1,'第五部分 采购需求书',123,123,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:30:59','2025-10-24 09:30:59');
INSERT INTO "tender_document_chapters" VALUES(38,9,'task_346a245051bd','ch_5',1,'第六部分 附  件',124,666,18134,'投标人应认真阅读招标文件中所有的事项、格式、条款和技术规范等。投标人没有按照招标文件要求提交全部资料，或者投标文件没有对招标文件在各方面都作出实质性响应是投标人的风险，并可能导致其投标文件被拒绝。
招标文件的澄清
4.1 任何要求对招标文件进行澄清的投标人，均应按第13条规定的递交投标文件截止期十五（15）天前以书面形式通知招标人。招标人认为有必要的，在投标文件递交截止期日前以书面形式答复每一投标人（答复中不包...
招标文件的修改
为使投标人准备投标文件时有充分时间对招标文件的修改部分进行研究，招标人可自行决定是否延长递交投标文件截止时间。',0,0,0,NULL,'2025-10-24 09:30:59','2025-10-24 09:30:59');
INSERT INTO "tender_document_chapters" VALUES(39,9,'task_17b3a1f25e95','ch_0',1,'第一部分 招标公告',119,119,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:32:52','2025-10-24 09:32:52');
INSERT INTO "tender_document_chapters" VALUES(40,9,'task_17b3a1f25e95','ch_1',1,'第二部分 投标人须知前附表及投标人须知',120,120,0,'(无内容)',0,0,1,NULL,'2025-10-24 09:32:52','2025-10-24 09:32:52');
INSERT INTO "tender_document_chapters" VALUES(41,9,'task_17b3a1f25e95','ch_2',1,'第三部分 评标办法',121,121,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:32:52','2025-10-24 09:32:52');
INSERT INTO "tender_document_chapters" VALUES(42,9,'task_17b3a1f25e95','ch_3',1,'第四部分 合同主要条款及格式',122,122,0,'(无内容)',0,0,1,NULL,'2025-10-24 09:32:52','2025-10-24 09:32:52');
INSERT INTO "tender_document_chapters" VALUES(43,9,'task_17b3a1f25e95','ch_4',1,'第五部分 采购需求书',123,123,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:32:52','2025-10-24 09:32:52');
INSERT INTO "tender_document_chapters" VALUES(44,9,'task_17b3a1f25e95','ch_5',1,'第六部分 附  件',124,666,18134,'投标人应认真阅读招标文件中所有的事项、格式、条款和技术规范等。投标人没有按照招标文件要求提交全部资料，或者投标文件没有对招标文件在各方面都作出实质性响应是投标人的风险，并可能导致其投标文件被拒绝。
招标文件的澄清
4.1 任何要求对招标文件进行澄清的投标人，均应按第13条规定的递交投标文件截止期十五（15）天前以书面形式通知招标人。招标人认为有必要的，在投标文件递交截止期日前以书面形式答复每一投标人（答复中不包...
招标文件的修改
为使投标人准备投标文件时有充分时间对招标文件的修改部分进行研究，招标人可自行决定是否延长递交投标文件截止时间。',0,0,0,NULL,'2025-10-24 09:32:52','2025-10-24 09:32:52');
INSERT INTO "tender_document_chapters" VALUES(45,9,'task_4b87c8de5bd7','ch_0',1,'第一部分 招标公告',119,119,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:49:41','2025-10-24 09:49:41');
INSERT INTO "tender_document_chapters" VALUES(46,9,'task_4b87c8de5bd7','ch_1',1,'第二部分 投标人须知前附表及投标人须知',120,120,0,'(无内容)',0,0,1,NULL,'2025-10-24 09:49:41','2025-10-24 09:49:41');
INSERT INTO "tender_document_chapters" VALUES(47,9,'task_4b87c8de5bd7','ch_2',1,'第三部分 评标办法',121,121,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:49:41','2025-10-24 09:49:41');
INSERT INTO "tender_document_chapters" VALUES(48,9,'task_4b87c8de5bd7','ch_3',1,'第四部分 合同主要条款及格式',122,122,0,'(无内容)',0,0,1,NULL,'2025-10-24 09:49:41','2025-10-24 09:49:41');
INSERT INTO "tender_document_chapters" VALUES(49,9,'task_4b87c8de5bd7','ch_4',1,'第五部分 采购需求书',123,123,0,'(无内容)',0,1,0,NULL,'2025-10-24 09:49:41','2025-10-24 09:49:41');
INSERT INTO "tender_document_chapters" VALUES(50,9,'task_4b87c8de5bd7','ch_5',1,'第六部分 附  件',124,666,18134,'投标人应认真阅读招标文件中所有的事项、格式、条款和技术规范等。投标人没有按照招标文件要求提交全部资料，或者投标文件没有对招标文件在各方面都作出实质性响应是投标人的风险，并可能导致其投标文件被拒绝。
招标文件的澄清
4.1 任何要求对招标文件进行澄清的投标人，均应按第13条规定的递交投标文件截止期十五（15）天前以书面形式通知招标人。招标人认为有必要的，在投标文件递交截止期日前以书面形式答复每一投标人（答复中不包...
招标文件的修改
为使投标人准备投标文件时有充分时间对招标文件的修改部分进行研究，招标人可自行决定是否延长递交投标文件截止时间。',0,0,0,NULL,'2025-10-24 09:49:41','2025-10-24 09:49:41');
INSERT INTO "tender_document_chapters" VALUES(51,10,'task_f7298ac1d510','ch_1',1,'第二部分 投标人须知前附表及投标人须知',104,258,6743,'投标人须知前附表
本表是对投标人须知的具体补充和修改，如有矛盾，均以本资料表为准。标记“■”的选项意为适用于本项目，标记“□”的选项意为不适用于本项目。
投标人须知
一、说  明
招标人及合格的投标人',1,0,1,NULL,'2025-10-24 09:53:25','2025-10-24 09:55:14');
INSERT INTO "tender_document_chapters" VALUES(52,10,'task_f7298ac1d510','ch_2',1,'第三部分 评标办法',259,266,254,'注：
计算得分应四舍五入，精确到小数点后两位。
如投标人开具可抵扣的增值税专用发票，按不含增值税报价计算评标价格，否则按含增值税报价计算评标价格。
在评标过程中，评标委员会发现投标人的报价明显低于其他投标报价，使得其投标报价可能低于其个别成本的，将可能要求要求该投标人作出书面说明并提供相关证明材料。投标人不能合理说明或者不能提供相关证明材料的，由...',0,1,0,NULL,'2025-10-24 09:53:25','2025-10-24 09:53:25');
INSERT INTO "tender_document_chapters" VALUES(53,10,'task_f7298ac1d510','ch_3',1,'第四部分 合同主要条款及格式',267,378,4487,'提示：本协议内容为本次招投标项目公示版，不具备法律效力，细则信息以中标后双方实际签约为准。
哈尔滨哈银消费金融有限责任公司数据服务协议
甲方：',0,0,1,NULL,'2025-10-24 09:53:25','2025-10-24 09:53:25');
INSERT INTO "tender_document_chapters" VALUES(54,10,'task_f7298ac1d510','ch_4',1,'第五部分 采购需求书',379,426,1471,'采购需求书
（一）服务名称及周期
1、项目服务名称：2025年-2027年运营商数据采购项目。
2、服务周期：3年。
（二）服务工作范围及内容',0,1,0,NULL,'2025-10-24 09:53:25','2025-10-24 09:53:25');
INSERT INTO "tender_document_chapters" VALUES(55,10,'task_f7298ac1d510','ch_5',1,'第六部分 附  件',427,666,5594,'附件1 投标函
哈尔滨哈银消费金融有限责任公司：
（投标人全称）授权             （全权代表姓名、职务、职称）                   为全权代表，参加贵方组织的        （招标编号、招标项目名称）招标的有关活动，为此：
提供投标人须知规定的全部投标文件（正本[ 1 ]份，副本[    ]份、电子版[ 1 ]份）。
满足招标文件全部需求的投标报价为：见附件2：开标一览表。',0,0,0,NULL,'2025-10-24 09:53:25','2025-10-24 09:53:25');
INSERT INTO "tender_document_chapters" VALUES(56,10,'task_94a67139022c','ch_0',1,'第一部分 招标公告',38,103,2669,'国信招标集团股份有限公司（招标代理机构）受哈尔滨哈银消费金融有限责任公司（招标人）委托，就哈银消金2025年-2027年运营商数据采购项目进行公开招标。
项目名称：
哈银消金2025年-2027年运营商数据采购项目
招标编号：',1,1,0,NULL,'2025-10-24 13:32:30','2025-10-24 13:42:39');
INSERT INTO "tender_document_chapters" VALUES(57,10,'task_94a67139022c','ch_1',1,'第二部分 投标人须知前附表及投标人须知',104,258,6743,'投标人须知前附表
本表是对投标人须知的具体补充和修改，如有矛盾，均以本资料表为准。标记“■”的选项意为适用于本项目，标记“□”的选项意为不适用于本项目。
投标人须知
一、说  明
招标人及合格的投标人',0,0,1,NULL,'2025-10-24 13:32:30','2025-10-24 13:32:30');
INSERT INTO "tender_document_chapters" VALUES(58,10,'task_94a67139022c','ch_2',1,'第三部分 评标办法',259,266,254,'注：
计算得分应四舍五入，精确到小数点后两位。
如投标人开具可抵扣的增值税专用发票，按不含增值税报价计算评标价格，否则按含增值税报价计算评标价格。
在评标过程中，评标委员会发现投标人的报价明显低于其他投标报价，使得其投标报价可能低于其个别成本的，将可能要求要求该投标人作出书面说明并提供相关证明材料。投标人不能合理说明或者不能提供相关证明材料的，由...',1,1,0,NULL,'2025-10-24 13:32:30','2025-10-24 13:42:39');
INSERT INTO "tender_document_chapters" VALUES(59,10,'task_94a67139022c','ch_3',1,'第四部分 合同主要条款及格式',267,378,4487,'提示：本协议内容为本次招投标项目公示版，不具备法律效力，细则信息以中标后双方实际签约为准。
哈尔滨哈银消费金融有限责任公司数据服务协议
甲方：',0,0,1,NULL,'2025-10-24 13:32:30','2025-10-24 13:32:30');
INSERT INTO "tender_document_chapters" VALUES(60,10,'task_94a67139022c','ch_4',1,'第五部分 采购需求书',379,426,1471,'采购需求书
（一）服务名称及周期
1、项目服务名称：2025年-2027年运营商数据采购项目。
2、服务周期：3年。
（二）服务工作范围及内容',0,1,0,NULL,'2025-10-24 13:32:30','2025-10-24 13:32:30');
INSERT INTO "tender_document_chapters" VALUES(61,10,'task_94a67139022c','ch_5',1,'第六部分 附  件',427,666,5594,'附件1 投标函
哈尔滨哈银消费金融有限责任公司：
（投标人全称）授权             （全权代表姓名、职务、职称）                   为全权代表，参加贵方组织的        （招标编号、招标项目名称）招标的有关活动，为此：
提供投标人须知规定的全部投标文件（正本[ 1 ]份，副本[    ]份、电子版[ 1 ]份）。
满足招标文件全部需求的投标报价为：见附件2：开标一览表。',0,0,0,NULL,'2025-10-24 13:32:30','2025-10-24 13:32:30');
INSERT INTO "tender_document_chapters" VALUES(62,10,'task_33c4a4c40b8e','ch_0',1,'第一部分 招标公告',38,103,2669,'国信招标集团股份有限公司（招标代理机构）受哈尔滨哈银消费金融有限责任公司（招标人）委托，就哈银消金2025年-2027年运营商数据采购项目进行公开招标。
项目名称：
哈银消金2025年-2027年运营商数据采购项目
招标编号：',1,1,0,NULL,'2025-10-24 13:49:50','2025-10-25 01:52:27');
INSERT INTO "tender_document_chapters" VALUES(63,10,'task_33c4a4c40b8e','ch_1',1,'第二部分 投标人须知前附表及投标人须知',104,258,6743,'投标人须知前附表
本表是对投标人须知的具体补充和修改，如有矛盾，均以本资料表为准。标记“■”的选项意为适用于本项目，标记“□”的选项意为不适用于本项目。
投标人须知
一、说  明
招标人及合格的投标人',0,0,1,NULL,'2025-10-24 13:49:50','2025-10-24 13:49:50');
INSERT INTO "tender_document_chapters" VALUES(64,10,'task_33c4a4c40b8e','ch_2',1,'第三部分 评标办法',259,266,254,'注：
计算得分应四舍五入，精确到小数点后两位。
如投标人开具可抵扣的增值税专用发票，按不含增值税报价计算评标价格，否则按含增值税报价计算评标价格。
在评标过程中，评标委员会发现投标人的报价明显低于其他投标报价，使得其投标报价可能低于其个别成本的，将可能要求要求该投标人作出书面说明并提供相关证明材料。投标人不能合理说明或者不能提供相关证明材料的，由...',0,1,0,NULL,'2025-10-24 13:49:50','2025-10-24 13:49:50');
INSERT INTO "tender_document_chapters" VALUES(65,10,'task_33c4a4c40b8e','ch_3',1,'第四部分 合同主要条款及格式',267,378,4487,'提示：本协议内容为本次招投标项目公示版，不具备法律效力，细则信息以中标后双方实际签约为准。
哈尔滨哈银消费金融有限责任公司数据服务协议
甲方：',0,0,1,NULL,'2025-10-24 13:49:50','2025-10-24 13:49:50');
INSERT INTO "tender_document_chapters" VALUES(66,10,'task_33c4a4c40b8e','ch_4',1,'第五部分 采购需求书',379,426,1471,'采购需求书
（一）服务名称及周期
1、项目服务名称：2025年-2027年运营商数据采购项目。
2、服务周期：3年。
（二）服务工作范围及内容',0,1,0,NULL,'2025-10-24 13:49:50','2025-10-24 13:49:50');
INSERT INTO "tender_document_chapters" VALUES(67,10,'task_33c4a4c40b8e','ch_5',1,'第六部分 附  件',427,666,5594,'附件1 投标函
哈尔滨哈银消费金融有限责任公司：
（投标人全称）授权             （全权代表姓名、职务、职称）                   为全权代表，参加贵方组织的        （招标编号、招标项目名称）招标的有关活动，为此：
提供投标人须知规定的全部投标文件（正本[ 1 ]份，副本[    ]份、电子版[ 1 ]份）。
满足招标文件全部需求的投标报价为：见附件2：开标一览表。',0,0,0,NULL,'2025-10-24 13:49:50','2025-10-24 13:49:50');
INSERT INTO "tender_document_chapters" VALUES(68,11,'task_85c9f85b5feb','ch_0',1,'第一部分 招标公告',38,103,2669,'国信招标集团股份有限公司（招标代理机构）受哈尔滨哈银消费金融有限责任公司（招标人）委托，就哈银消金2025年-2027年运营商数据采购项目进行公开招标。
项目名称：
哈银消金2025年-2027年运营商数据采购项目
招标编号：',1,1,0,NULL,'2025-10-25 01:54:04','2025-10-25 01:54:10');
INSERT INTO "tender_document_chapters" VALUES(69,11,'task_85c9f85b5feb','ch_1',1,'第二部分 投标人须知前附表及投标人须知',104,258,6743,'投标人须知前附表
本表是对投标人须知的具体补充和修改，如有矛盾，均以本资料表为准。标记“■”的选项意为适用于本项目，标记“□”的选项意为不适用于本项目。
投标人须知
一、说  明
招标人及合格的投标人',0,0,1,NULL,'2025-10-25 01:54:04','2025-10-25 01:54:04');
INSERT INTO "tender_document_chapters" VALUES(70,11,'task_85c9f85b5feb','ch_2',1,'第三部分 评标办法',259,266,254,'注：
计算得分应四舍五入，精确到小数点后两位。
如投标人开具可抵扣的增值税专用发票，按不含增值税报价计算评标价格，否则按含增值税报价计算评标价格。
在评标过程中，评标委员会发现投标人的报价明显低于其他投标报价，使得其投标报价可能低于其个别成本的，将可能要求要求该投标人作出书面说明并提供相关证明材料。投标人不能合理说明或者不能提供相关证明材料的，由...',0,1,0,NULL,'2025-10-25 01:54:04','2025-10-25 01:54:04');
INSERT INTO "tender_document_chapters" VALUES(71,11,'task_85c9f85b5feb','ch_3',1,'第四部分 合同主要条款及格式',267,378,4487,'提示：本协议内容为本次招投标项目公示版，不具备法律效力，细则信息以中标后双方实际签约为准。
哈尔滨哈银消费金融有限责任公司数据服务协议
甲方：',0,0,1,NULL,'2025-10-25 01:54:04','2025-10-25 01:54:04');
INSERT INTO "tender_document_chapters" VALUES(72,11,'task_85c9f85b5feb','ch_4',1,'第五部分 采购需求书',379,426,1471,'采购需求书
（一）服务名称及周期
1、项目服务名称：2025年-2027年运营商数据采购项目。
2、服务周期：3年。
（二）服务工作范围及内容',0,1,0,NULL,'2025-10-25 01:54:04','2025-10-25 01:54:04');
INSERT INTO "tender_document_chapters" VALUES(73,11,'task_85c9f85b5feb','ch_5',1,'第六部分 附  件',427,666,5594,'附件1 投标函
哈尔滨哈银消费金融有限责任公司：
（投标人全称）授权             （全权代表姓名、职务、职称）                   为全权代表，参加贵方组织的        （招标编号、招标项目名称）招标的有关活动，为此：
提供投标人须知规定的全部投标文件（正本[ 1 ]份，副本[    ]份、电子版[ 1 ]份）。
满足招标文件全部需求的投标报价为：见附件2：开标一览表。',0,0,0,NULL,'2025-10-25 01:54:04','2025-10-25 01:54:04');
CREATE TABLE tender_document_chunks (
    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,  -- 块的顺序索引
    chunk_type VARCHAR(50) NOT NULL,  -- title/paragraph/table/list
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON格式: {section_title, page_number, token_count, parent_section}

    -- 筛选字段
    is_valuable BOOLEAN DEFAULT NULL,  -- NULL=未筛选, TRUE=高价值, FALSE=低价值
    filter_confidence FLOAT DEFAULT NULL,  -- 筛选置信度 0.0-1.0
    filtered_at TIMESTAMP DEFAULT NULL,
    filter_model VARCHAR(50) DEFAULT NULL,  -- 使用的筛选模型

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, hitl_task_id VARCHAR(100),

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);
CREATE TABLE tender_filter_review (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) NOT NULL,

    -- 原始筛选结果
    ai_decision VARCHAR(20) NOT NULL,  -- 'REQUIREMENT' 或 'NON-REQUIREMENT'
    ai_confidence FLOAT,  -- AI 置信度 0.0-1.0
    ai_reasoning TEXT,  -- AI 判断理由

    -- 人工复核
    user_decision VARCHAR(20),  -- 用户决策: 'keep', 'restore', 'discard'
    reviewed_by VARCHAR(100),  -- 复核人
    reviewed_at TIMESTAMP,
    review_notes TEXT,  -- 复核备注

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id) REFERENCES tender_document_chunks(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);
CREATE TABLE tender_hitl_tasks (
    hitl_task_id VARCHAR(100) PRIMARY KEY,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) NOT NULL,  -- 关联主处理任务

    -- 步骤状态
    step1_status VARCHAR(20) DEFAULT 'pending',  -- pending/in_progress/completed/skipped
    step1_completed_at TIMESTAMP,
    step1_data TEXT,  -- JSON: 步骤1的选择结果

    step2_status VARCHAR(20) DEFAULT 'pending',
    step2_completed_at TIMESTAMP,
    step2_data TEXT,  -- JSON: 步骤2的复核结果

    step3_status VARCHAR(20) DEFAULT 'pending',
    step3_completed_at TIMESTAMP,
    step3_data TEXT,  -- JSON: 步骤3的编辑结果

    -- 全局状态
    current_step INTEGER DEFAULT 1,  -- 1, 2, 3
    overall_status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress/completed/cancelled

    -- 成本预估
    estimated_cost FLOAT DEFAULT 0.0,
    estimated_words INTEGER DEFAULT 0,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tender_processing_tasks(task_id) ON DELETE CASCADE
);
INSERT INTO "tender_hitl_tasks" VALUES('hitl_25f04ef24f1a',5,'task_09c43b5a2130','completed','2025-10-23 02:24:34','{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_102422_\u5355\u4e00\u8c08\u5224\u6587\u4ef6-\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee-9-22(1)_072bbb07.docx", "file_name": "\u5355\u4e00\u8c08\u5224\u6587\u4ef6-\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee-9-22(1).docx", "selected_ids": ["ch_0"], "selected_count": 1}','in_progress',NULL,NULL,'pending',NULL,NULL,2,'in_progress',0.00772,3860,'2025-10-23 02:24:25','2025-10-23 02:24:34');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_1ffd461aca66',6,'task_b25667a09a85','completed','2025-10-23 03:21:38','{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_112129_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_64797a35.docx", "file_name": "单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx", "selected_ids": ["ch_0"], "selected_count": 1, "response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/response_files/2025/10/hitl_1ffd461aca66/第五部分    谈判响应文件格式_应答模板_20251023_112212.docx", "filename": "第五部分    谈判响应文件格式_应答模板_20251023_112212.docx", "file_size": 70798, "saved_at": "2025-10-23T11:22:12.016502"}, "technical_file": {"filename": "第四部分    技术需求书_技术需求_20251023_112220.docx", "file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/technical_files/2025/10/hitl_1ffd461aca66/第四部分    技术需求书_技术需求_20251023_112220.docx", "file_size": 54761, "saved_at": "2025-10-23T11:22:20.667983", "chapter_ids": ["ch_3"]}}','in_progress',NULL,NULL,'pending',NULL,NULL,2,'in_progress',0.00772,3860,'2025-10-23 03:21:32','2025-10-23 03:22:20');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_30a773ad71c5',7,'task_1000f90f89ea','completed','2025-10-23 07:41:28','{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_154118_单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1)_6a251827.docx", "file_name": "单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx", "selected_ids": ["ch_0"], "selected_count": 1, "response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/response_files/2025/10/hitl_30a773ad71c5/第五部分    谈判响应文件格式_应答模板_20251023_154159.docx", "filename": "第五部分    谈判响应文件格式_应答模板_20251023_154159.docx", "file_size": 70798, "saved_at": "2025-10-23T15:41:59.658734"}, "technical_file": {"filename": "第四部分    技术需求书_技术需求_20251023_154209.docx", "file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/technical_files/2025/10/hitl_30a773ad71c5/第四部分    技术需求书_技术需求_20251023_154209.docx", "file_size": 54761, "saved_at": "2025-10-23T15:42:09.604344", "chapter_ids": ["ch_3"]}}','in_progress',NULL,NULL,'pending',NULL,NULL,2,'in_progress',0.00772,3860,'2025-10-23 07:41:21','2025-10-23 07:42:09');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_5a00b2b7e859',8,'task_d1b8cba6db44','completed','2025-10-26 02:53:32','{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251023_154118_\u5355\u4e00\u8c08\u5224\u6587\u4ef6-\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee-9-22(1)_6a251827.docx", "file_name": "20251023_154118_\u5355\u4e00\u8c08\u5224\u6587\u4ef6-\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee-9-22(1)_6a251827.docx", "selected_ids": ["ch_0"], "selected_count": 1, "response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/response_files/2025/10/hitl_5a00b2b7e859/\u7b2c\u4e94\u90e8\u5206    \u8c08\u5224\u54cd\u5e94\u6587\u4ef6\u683c\u5f0f_\u5e94\u7b54\u6a21\u677f_20251024_090346.docx", "filename": "\u7b2c\u4e94\u90e8\u5206    \u8c08\u5224\u54cd\u5e94\u6587\u4ef6\u683c\u5f0f_\u5e94\u7b54\u6a21\u677f_20251024_090346.docx", "file_size": 70798, "saved_at": "2025-10-24T09:03:46.188289"}, "technical_file": {"filename": "\u7b2c\u56db\u90e8\u5206    \u6280\u672f\u9700\u6c42\u4e66_\u6280\u672f\u9700\u6c42_20251024_090401.docx", "file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/technical_files/2025/10/hitl_5a00b2b7e859/\u7b2c\u56db\u90e8\u5206    \u6280\u672f\u9700\u6c42\u4e66_\u6280\u672f\u9700\u6c42_20251024_090401.docx", "file_size": 54761, "saved_at": "2025-10-24T09:04:01.922434", "chapter_ids": ["ch_3"]}, "business_response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/completed_response_files/2025/10/hitl_5a00b2b7e859/\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251024_095408_\u5e94\u7b54\u5b8c\u6210.docx", "filename": "\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251024_095408_\u5e94\u7b54\u5b8c\u6210.docx", "file_size": 70882, "saved_at": "2025-10-24T09:54:10.204926", "source_file": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/outputs/\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251024_095408.docx"}, "technical_point_to_point_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/point_to_point_files/2025/10/hitl_5a00b2b7e859/\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee_\u70b9\u5bf9\u70b9\u5e94\u7b54_20251024_101857_\u70b9\u5bf9\u70b9\u5e94\u7b54.docx", "filename": "\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee_\u70b9\u5bf9\u70b9\u5e94\u7b54_20251024_101857_\u70b9\u5bf9\u70b9\u5e94\u7b54.docx", "file_size": 55212, "saved_at": "2025-10-24T10:18:59.710780", "source_file": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/outputs/\u4e2d\u56fd\u8054\u901a\u624b\u673a\u4fe1\u606f\u6838\u9a8c\u7c7b\u5916\u90e8\u6570\u636e\u670d\u52a1\u91c7\u8d2d\u9879\u76ee_\u70b9\u5bf9\u70b9\u5e94\u7b54_20251024_101857.docx"}}','in_progress',NULL,NULL,'pending',NULL,NULL,2,'in_progress',0.00772,3860,'2025-10-24 01:03:07','2025-10-26 02:53:32');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_3a1657758896',9,'task_fcafea9ebcda','in_progress',NULL,'{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx", "file_name": "\u62db\u6807\u6587\u4ef6.docx"}','pending',NULL,NULL,'pending',NULL,NULL,1,'in_progress',0.036268,18134,'2025-10-24 07:14:39','2025-10-24 07:14:39');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_7f5e067e3d2c',9,'task_a80075c84665','in_progress',NULL,'{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx", "file_name": "20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx"}','pending',NULL,NULL,'pending',NULL,NULL,1,'in_progress',0.036268,18134,'2025-10-24 07:29:25','2025-10-24 07:29:25');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_e8c1d0adc8f2',9,'task_346a245051bd','in_progress',NULL,'{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx", "file_name": "20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx"}','pending',NULL,NULL,'pending',NULL,NULL,1,'in_progress',0.036268,18134,'2025-10-24 09:30:59','2025-10-24 09:30:59');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_25aa90be5c36',9,'task_17b3a1f25e95','in_progress',NULL,'{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx", "file_name": "20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx"}','pending',NULL,NULL,'pending',NULL,NULL,1,'in_progress',0.036268,18134,'2025-10-24 09:32:52','2025-10-24 09:32:52');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_dc86d1244fbb',9,'task_4b87c8de5bd7','in_progress',NULL,'{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx", "file_name": "20251024_151438_\u62db\u6807\u6587\u4ef6_6cfefcaf.docx"}','pending',NULL,NULL,'pending',NULL,NULL,1,'in_progress',0.036268,18134,'2025-10-24 09:49:41','2025-10-24 09:49:41');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_f771fdaddab5',10,'task_f7298ac1d510','completed','2025-10-24 09:55:14','{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_175323_\u62db\u6807\u6587\u4ef6-\u54c8\u94f6\u6d88\u91d1_920204d0.docx", "file_name": "\u62db\u6807\u6587\u4ef6-\u54c8\u94f6\u6d88\u91d1.docx", "response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/response_files/2025/10/hitl_f771fdaddab5/\u7b2c\u516d\u90e8\u5206 \u9644  \u4ef6_\u5e94\u7b54\u6a21\u677f_20251024_175454.docx", "filename": "\u7b2c\u516d\u90e8\u5206 \u9644  \u4ef6_\u5e94\u7b54\u6a21\u677f_20251024_175454.docx", "file_size": 1344118, "saved_at": "2025-10-24T17:54:54.737228"}, "selected_ids": ["ch_1"], "selected_count": 1}','in_progress',NULL,NULL,'pending',NULL,NULL,2,'in_progress',1.348600000000000146e-02,6743,'2025-10-24 09:53:25','2025-10-24 09:55:14');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_2c9dd1cf72a4',10,'task_94a67139022c','completed','2025-10-24 13:42:39','{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_175323_招标文件-哈银消金_920204d0.docx", "file_name": "20251024_175323_招标文件-哈银消金_920204d0.docx", "selected_ids": ["ch_2", "ch_0"], "selected_count": 2, "response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/response_files/2025/10/hitl_2c9dd1cf72a4/第六部分 附  件_应答模板_20251024_214300.docx", "filename": "第六部分 附  件_应答模板_20251024_214300.docx", "file_size": 1344118, "saved_at": "2025-10-24T21:43:00.808400"}, "technical_file": {"filename": "第五部分 采购需求书_技术需求_20251024_214309.docx", "file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/technical_files/2025/10/hitl_2c9dd1cf72a4/第五部分 采购需求书_技术需求_20251024_214309.docx", "file_size": 1331127, "saved_at": "2025-10-24T21:43:09.963453", "chapter_ids": ["ch_4"]}}','in_progress',NULL,NULL,'pending',NULL,NULL,2,'in_progress',5.846000000000000501e-03,2923,'2025-10-24 13:32:30','2025-10-24 13:43:09');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_7955013df7a4',10,'task_33c4a4c40b8e','completed','2025-10-25 01:52:27','{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251024_175323_\u62db\u6807\u6587\u4ef6-\u54c8\u94f6\u6d88\u91d1_920204d0.docx", "file_name": "20251024_175323_\u62db\u6807\u6587\u4ef6-\u54c8\u94f6\u6d88\u91d1_920204d0.docx", "response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/response_files/2025/10/hitl_7955013df7a4/\u7b2c\u4e00\u90e8\u5206 \u62db\u6807\u516c\u544a_\u5e94\u7b54\u6a21\u677f_20251024_224751.docx", "filename": "\u7b2c\u4e00\u90e8\u5206 \u62db\u6807\u516c\u544a_\u5e94\u7b54\u6a21\u677f_20251024_224751.docx", "file_size": 1320995, "saved_at": "2025-10-24T22:47:51.053503"}, "technical_file": {"filename": "\u7b2c\u4e94\u90e8\u5206 \u91c7\u8d2d\u9700\u6c42\u4e66_\u6280\u672f\u9700\u6c42_20251024_224524.docx", "file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/technical_files/2025/10/hitl_7955013df7a4/\u7b2c\u4e94\u90e8\u5206 \u91c7\u8d2d\u9700\u6c42\u4e66_\u6280\u672f\u9700\u6c42_20251024_224524.docx", "file_size": 1331127, "saved_at": "2025-10-24T22:45:24.239055", "chapter_ids": ["ch_4"]}, "business_response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/completed_response_files/2025/10/hitl_7955013df7a4/\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251024_224601_\u5e94\u7b54\u5b8c\u6210.docx", "filename": "\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251024_224601_\u5e94\u7b54\u5b8c\u6210.docx", "file_size": 1344403, "saved_at": "2025-10-24T22:46:03.744936", "source_file": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/outputs/\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251024_224601.docx"}, "selected_ids": ["ch_0"], "selected_count": 1}','in_progress',NULL,NULL,'pending',NULL,NULL,2,'in_progress',0.005338,2669,'2025-10-24 13:49:50','2025-10-25 01:52:27');
INSERT INTO "tender_hitl_tasks" VALUES('hitl_3abc8818b9d7',11,'task_85c9f85b5feb','completed','2025-10-25 01:54:10','{"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tender_processing/2025/10/20251025_095402_\u62db\u6807\u6587\u4ef6-\u54c8\u94f6\u6d88\u91d1_8c8829a1.docx", "file_name": "\u62db\u6807\u6587\u4ef6-\u54c8\u94f6\u6d88\u91d1.docx", "selected_ids": ["ch_0"], "selected_count": 1, "technical_file": {"filename": "\u7b2c\u4e94\u90e8\u5206 \u91c7\u8d2d\u9700\u6c42\u4e66_\u6280\u672f\u9700\u6c42_20251025_095732.docx", "file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/technical_files/2025/10/hitl_3abc8818b9d7/\u7b2c\u4e94\u90e8\u5206 \u91c7\u8d2d\u9700\u6c42\u4e66_\u6280\u672f\u9700\u6c42_20251025_095732.docx", "file_size": 1331127, "saved_at": "2025-10-25T09:57:32.674991", "chapter_ids": ["ch_4"]}, "response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/response_files/2025/10/hitl_3abc8818b9d7/\u7b2c\u516d\u90e8\u5206 \u9644  \u4ef6_\u5e94\u7b54\u6a21\u677f_20251025_104039.docx", "filename": "\u7b2c\u516d\u90e8\u5206 \u9644  \u4ef6_\u5e94\u7b54\u6a21\u677f_20251025_104039.docx", "file_size": 1344118, "saved_at": "2025-10-25T10:40:39.330449"}, "business_response_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/completed_response_files/2025/10/hitl_3abc8818b9d7/\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251026_111444_\u5e94\u7b54\u5b8c\u6210.docx", "filename": "\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251026_111444_\u5e94\u7b54\u5b8c\u6210.docx", "file_size": 1344489, "saved_at": "2025-10-26T11:15:00.004201", "source_file": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/outputs/\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u5546\u52a1\u5e94\u7b54_20251026_111444.docx"}, "technical_proposal_file": {"file_path": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/uploads/tech_proposal_files/2025/10/hitl_3abc8818b9d7/\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u6280\u672f\u65b9\u6848_20251026_185209_\u6280\u672f\u65b9\u6848.docx", "filename": "\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u6280\u672f\u65b9\u6848_20251026_185209_\u6280\u672f\u65b9\u6848.docx", "file_size": 57244, "saved_at": "2025-10-26T19:02:39.731896", "source_file": "/Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/outputs/\u54c8\u94f6\u6d88\u91d12025\u5e74-2027\u5e74\u8fd0\u8425\u5546\u6570\u636e\u91c7\u8d2d\u9879\u76ee_\u6280\u672f\u65b9\u6848_20251026_185209.docx"}}','in_progress',NULL,NULL,'pending',NULL,NULL,2,'in_progress',0.005338,2669,'2025-10-25 01:54:04','2025-10-26 11:02:39');
CREATE TABLE tender_processing_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) UNIQUE,  -- 唯一任务ID（用于前端查询进度）

    -- 流程步骤
    step VARCHAR(20) NOT NULL,  -- chunking/filtering/extraction/completed/failed
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/processing/completed/failed/cancelled

    -- 进度信息
    total_items INTEGER DEFAULT 0,  -- 总项目数
    processed_items INTEGER DEFAULT 0,  -- 已处理项目数
    success_items INTEGER DEFAULT 0,  -- 成功项目数
    failed_items INTEGER DEFAULT 0,  -- 失败项目数

    -- 成本统计
    cost_estimation FLOAT DEFAULT 0.0,  -- 预估成本（美元）
    actual_cost FLOAT DEFAULT 0.0,  -- 实际成本（美元）
    api_calls INTEGER DEFAULT 0,  -- API调用次数
    total_tokens INTEGER DEFAULT 0,  -- 总token消耗

    -- 时间统计
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration INTEGER,  -- 预估耗时（秒）
    actual_duration INTEGER,  -- 实际耗时（秒）

    -- 错误信息
    error_message TEXT,
    error_details TEXT,  -- JSON格式的详细错误信息

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);
CREATE TABLE tender_processing_tasks (
    task_id VARCHAR(100) PRIMARY KEY,
    project_id INTEGER NOT NULL,

    -- 任务配置
    pipeline_config TEXT,  -- JSON格式的流程配置
    options TEXT,  -- JSON格式的处理选项

    -- 任务状态
    overall_status VARCHAR(20) DEFAULT 'pending',  -- pending/running/completed/failed/cancelled
    current_step VARCHAR(20),  -- 当前执行的步骤
    progress_percentage FLOAT DEFAULT 0.0,  -- 总体进度百分比

    -- 结果摘要
    total_chunks INTEGER DEFAULT 0,
    valuable_chunks INTEGER DEFAULT 0,
    total_requirements INTEGER DEFAULT 0,

    -- 时间信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);
CREATE TABLE tender_projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(255),
    project_number VARCHAR(100),
    tenderer VARCHAR(255), -- 招标方
    agency VARCHAR(255), -- 代理机构
    bidding_method VARCHAR(100), -- 招标方式
    bidding_location VARCHAR(255), -- 招标地点
    bidding_time VARCHAR(100), -- 招标时间
    tender_document_path VARCHAR(500), -- 标书文件路径
    original_filename VARCHAR(255), -- 原始文件名
    company_id INTEGER, -- 关联公司ID
    qualifications_data TEXT, -- 资质要求数据(JSON格式)
    scoring_data TEXT, -- 评分信息数据(JSON格式)
    status VARCHAR(20) DEFAULT 'draft', -- draft/active/completed
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, authorized_person_name VARCHAR(100), authorized_person_id VARCHAR(18), authorized_person_position VARCHAR(100), winner_count VARCHAR(50),
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, project_name, project_number) -- 防止同一公司创建重复项目
);
INSERT INTO "tender_projects" VALUES(8,'中国联通手机信息核验类外部数据服务采购项目','TC25090CL','中国光大银行股份有限公司','中招国际招标有限公司','单一来源采购','中关村资本大厦九层907C会议室（北京市海淀区学院南路62号中关村资本大厦九层）','2025年10月13日下午14:00（北京时间）','','',1,'{"营业执照信息": {"requirement_id": 27, "constraint_type": "mandatory", "detail": "供应商必须是在中华人民共和国境内注册或开办的具有独立法人资格的企业，或事业单位，或特殊普通合伙单位等；\n供应商资格要求：\n供应商具有独立承担民事责任的能力；\n供应商企业注册成立时间不少于3年（含）；", "summary": "需要提供营业执照信息", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "财务要求": {"requirement_id": 28, "constraint_type": "mandatory", "detail": "供应商具有良好的商业信誉和健全的财务会计制度（供应商提供近1年的经第三方机构审计的财务审计报告（每份报告应至少包含1）审计报告正文，2）资产负债表，3）利润表或收入费用表（事业单位提供），4）现金流量表。\n）的复印件加盖供应商公章）或近三个月银行出具的资信证明原件）；", "summary": "需要提供财务要求", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "依法纳税": {"requirement_id": 29, "constraint_type": "mandatory", "detail": "提供以下资料：①供应商提供谈判截止日前6个月任意1个月的增值税缴纳证明文件；", "summary": "需要提供依法纳税", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "缴纳社保": {"requirement_id": 30, "constraint_type": "mandatory", "detail": "②供应商企业社保直接缴纳人数不得低于10人（含）（须近一年在本公司（含分公司）直接缴纳且连续缴费月数大于等于12个月（且截止月至少包括2025年6月）的“社会保险权益记录（必须体现缴费单位名称、缴费个人姓名、社会保障号码（至少保留社会保障号码后6位）、缴费起止年月，以及提供鉴定真伪的查询方式）”）；\n被授权人近3个月在本公司（含分公司）直接缴纳且连续缴费月数大于等于3个月的（且截止月至少包括2025年6月）“社会保险权益记录（必须体现缴费单位名称、缴费个人姓名、社会保障号码（至少保留社会保障号码后6位）、缴费起止年月，以及提供鉴定真伪的查询方式）”）的证明资料并加盖公章。\n供应商有依法缴纳税收和社会保障资金的良好记录。", "summary": "需要提供缴纳社保", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "失信被执行人": {"requirement_id": 31, "constraint_type": "mandatory", "detail": "供应商不得被列入“失信被执行人”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。\n供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。", "summary": "需要提供失信被执行人", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "信用中国严重违法失信": {"requirement_id": 32, "constraint_type": "mandatory", "detail": "供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。", "summary": "需要提供信用中国严重违法失信", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "严重违法失信行为记录名单": {"requirement_id": 33, "constraint_type": "mandatory", "detail": "供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。", "summary": "需要提供严重违法失信行为记录名单", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "信用中国重大税收违法": {"requirement_id": 34, "constraint_type": "mandatory", "detail": "供应商不得被列入“重大税收违法案件当事人名单（即：重大税收违法失信主体名单）”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。", "summary": "需要提供信用中国重大税收违法", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "采购人黑名单": {"requirement_id": 35, "constraint_type": "mandatory", "detail": "供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。", "summary": "需要提供采购人黑名单", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "承诺函": {"requirement_id": 36, "constraint_type": "mandatory", "detail": "供应商具有履行合同所必需的设备和专业技术能力（供应商提供承诺函）；", "summary": "需要提供承诺函", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "营业办公场所房产证明": {"requirement_id": 37, "constraint_type": "mandatory", "detail": "供应商提供以下相关证明文件之一：①供应商自有房产的，须提供房产证明文件；\n供应商应依法取得营业办公场所的房产证明文件，或营业办公场所房产证明和在有效期内的房屋租赁合同。", "summary": "需要提供营业办公场所房产证明", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "业绩案例要求": {"requirement_id": 38, "constraint_type": "mandatory", "detail": "供应商具备至少1个手机核验信息核验类领域同类项目案例（须提供合同复印件（包括合同首页、服务内容页、双方盖章页复印件）加盖公章，若供应商存在名称变更，且本次谈判文件中案例的合同主体为变更前公司名称，应提供工商行政管理局等政府单位的批复/通知复印件加盖公章）。", "summary": "需要提供业绩案例要求", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}, "保证金要求": {"requirement_id": 39, "constraint_type": "mandatory", "detail": "人民币伍仟万元（不含）以上的，保证金为人民币肆万元）。", "summary": "需要提供保证金要求", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": false, "created_at": "2025-10-24 01:03:33"}}',NULL,'draft','system','2025-10-24 01:03:03','2025-10-26 02:55:21','黄岿','110101199001011234','客户经理','未提供');
INSERT INTO "tender_projects" VALUES(11,'哈银消金2025年-2027年运营商数据采购项目','GXTC-C-251590031','哈尔滨哈银消费金融有限责任公司','国信招标集团股份有限公司','公开招标','北京市海淀区西四环北路158-1号慧科大厦东区6层6E办公室','2025年08月27日下午14:30整（北京时间）','','',1,'{"营业执照信息": {"requirement_id": 76, "constraint_type": "mandatory", "detail": "营业执照副本复印件；\n其他必须满足的要求：\n1.在中华人民共和国境内注册的独立法人或者其他组织，具备有效的营业执照。\n合格投标人的基本资质要求（须同时满足）：\n投标人的资质要求如下：\n1.投标人须具有独立承担民事责任的能力，遵守法律、法规，具有良好的商业信誉和健全的财务会计制度。", "summary": "需要提供营业执照信息", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "财务要求": {"requirement_id": 77, "constraint_type": "mandatory", "detail": "具有良好的商业信誉和健全的财务会计制度；\n6.参加本项目的投标人近三年来企业财务状况良好，企业财产没有处于被接管、全部资金被冻结以及破产状态；", "summary": "需要提供财务要求", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "依法纳税": {"requirement_id": 78, "constraint_type": "mandatory", "detail": "9.投标人须能够提供增值税合法抵扣凭证（即增值税专用发票）。", "summary": "需要提供依法纳税", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "缴纳社保": {"requirement_id": 79, "constraint_type": "mandatory", "detail": "有依法缴纳税收和社会保障资金的良好记录。", "summary": "需要提供缴纳社保", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "失信被执行人": {"requirement_id": 80, "constraint_type": "mandatory", "detail": "3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。", "summary": "需要提供失信被执行人", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "信用中国严重违法失信": {"requirement_id": 81, "constraint_type": "mandatory", "detail": "3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。", "summary": "需要提供信用中国严重违法失信", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "严重违法失信行为记录名单": {"requirement_id": 82, "constraint_type": "mandatory", "detail": "3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。", "summary": "需要提供严重违法失信行为记录名单", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "信用中国重大税收违法": {"requirement_id": 83, "constraint_type": "mandatory", "detail": "3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。", "summary": "需要提供信用中国重大税收违法", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "采购人黑名单": {"requirement_id": 84, "constraint_type": "mandatory", "detail": "未被列入《哈银消金不良行为供应商禁用名单》和《哈银消金不良行为供应商黑名单》。", "summary": "需要提供采购人黑名单", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}, "业绩案例要求": {"requirement_id": 85, "constraint_type": "mandatory", "detail": "2.投标人近五年内至少承接过2个与招标人需求相近（运营商类数据，至少包含三要素验证、在网时长和在网状态三个产品）的成功案例，所提供的案例要求出具合同复印件首末及内容页(首页即项目名称页，末页即签字盖章页并能清楚体现最终用户名称、时间，内容页即项目主要内容), 需提供发票，不能清楚提供的视为无效案例，须注明案例范围。", "summary": "需要提供业绩案例要求", "source_location": "", "priority": "high", "extraction_confidence": 0.8, "is_verified": 0, "created_at": "2025-10-25 01:54:25"}}',NULL,'draft','system','2025-10-25 01:54:02','2025-10-25 01:54:25','黄岿','110101199001011234','客户经理',NULL);
CREATE TABLE tender_requirements (
    requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    chunk_id INTEGER,  -- 来源分块ID，可为NULL（合并多个块的要求）

    -- 要求分类
    constraint_type VARCHAR(20) NOT NULL,  -- mandatory（强制性）/optional（可选）/scoring（加分项）
    category VARCHAR(50) NOT NULL,  -- qualification（资质）/technical（技术）/commercial（商务）/service（服务）
    subcategory VARCHAR(100),  -- 子类别，如：证书类型、技术指标类型

    -- 要求内容
    detail TEXT NOT NULL,  -- 具体要求描述
    summary VARCHAR(200),  -- 简洁摘要（60字以内），方便快速浏览
    source_location VARCHAR(255),  -- 来源位置（章节标题、页码）
    priority VARCHAR(10) DEFAULT 'medium',  -- high/medium/low

    -- AI提取元数据
    extraction_confidence FLOAT DEFAULT NULL,  -- 提取置信度
    extraction_model VARCHAR(50) DEFAULT NULL,  -- 使用的提取模型
    extracted_at TIMESTAMP DEFAULT NULL,

    -- 验证和审核
    is_verified BOOLEAN DEFAULT FALSE,  -- 人工验证标记
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,
    notes TEXT,  -- 审核备注

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, hitl_task_id VARCHAR(100),

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (chunk_id) REFERENCES tender_document_chunks(chunk_id) ON DELETE SET NULL
);
INSERT INTO "tender_requirements" VALUES(1,6,NULL,'mandatory','qualification','营业执照信息','供应商必须是在中华人民共和国境内注册或开办的具有独立法人资格的企业，或事业单位，或特殊普通合伙单位等；
供应商资格要求：
供应商具有独立承担民事责任的能力；
供应商企业注册成立时间不少于3年（含）；','需要提供营业执照信息','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(2,6,NULL,'mandatory','qualification','财务要求','供应商具有良好的商业信誉和健全的财务会计制度（供应商提供近1年的经第三方机构审计的财务审计报告（每份报告应至少包含1）审计报告正文，2）资产负债表，3）利润表或收入费用表（事业单位提供），4）现金流量表。
）的复印件加盖供应商公章）或近三个月银行出具的资信证明原件）；','需要提供财务要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(3,6,NULL,'mandatory','qualification','依法纳税','提供以下资料：①供应商提供谈判截止日前6个月任意1个月的增值税缴纳证明文件；','需要提供依法纳税','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(4,6,NULL,'mandatory','qualification','缴纳社保','②供应商企业社保直接缴纳人数不得低于10人（含）（须近一年在本公司（含分公司）直接缴纳且连续缴费月数大于等于12个月（且截止月至少包括2025年6月）的“社会保险权益记录（必须体现缴费单位名称、缴费个人姓名、社会保障号码（至少保留社会保障号码后6位）、缴费起止年月，以及提供鉴定真伪的查询方式）”）；
被授权人近3个月在本公司（含分公司）直接缴纳且连续缴费月数大于等于3个月的（且截止月至少包括2025年6月）“社会保险权益记录（必须体现缴费单位名称、缴费个人姓名、社会保障号码（至少保留社会保障号码后6位）、缴费起止年月，以及提供鉴定真伪的查询方式）”）的证明资料并加盖公章。
供应商有依法缴纳税收和社会保障资金的良好记录。','需要提供缴纳社保','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(5,6,NULL,'mandatory','qualification','失信被执行人','供应商不得被列入“失信被执行人”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。
供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供失信被执行人','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(6,6,NULL,'mandatory','qualification','信用中国严重违法失信','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供信用中国严重违法失信','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(7,6,NULL,'mandatory','qualification','严重违法失信行为记录名单','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供严重违法失信行为记录名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(8,6,NULL,'mandatory','qualification','信用中国重大税收违法','供应商不得被列入“重大税收违法案件当事人名单（即：重大税收违法失信主体名单）”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供信用中国重大税收违法','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(9,6,NULL,'mandatory','qualification','采购人黑名单','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供采购人黑名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(10,6,NULL,'mandatory','qualification','承诺函','供应商具有履行合同所必需的设备和专业技术能力（供应商提供承诺函）；','需要提供承诺函','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(11,6,NULL,'mandatory','qualification','营业办公场所房产证明','供应商提供以下相关证明文件之一：①供应商自有房产的，须提供房产证明文件；
供应商应依法取得营业办公场所的房产证明文件，或营业办公场所房产证明和在有效期内的房屋租赁合同。','需要提供营业办公场所房产证明','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(12,6,NULL,'mandatory','qualification','业绩案例要求','供应商具备至少1个手机核验信息核验类领域同类项目案例（须提供合同复印件（包括合同首页、服务内容页、双方盖章页复印件）加盖公章，若供应商存在名称变更，且本次谈判文件中案例的合同主体为变更前公司名称，应提供工商行政管理局等政府单位的批复/通知复印件加盖公章）。','需要提供业绩案例要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(13,6,NULL,'mandatory','qualification','保证金要求','人民币伍仟万元（不含）以上的，保证金为人民币肆万元）。','需要提供保证金要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 03:21:54','2025-10-23 03:21:54','hitl_1ffd461aca66');
INSERT INTO "tender_requirements" VALUES(14,7,NULL,'mandatory','qualification','营业执照信息','供应商必须是在中华人民共和国境内注册或开办的具有独立法人资格的企业，或事业单位，或特殊普通合伙单位等；
供应商资格要求：
供应商具有独立承担民事责任的能力；
供应商企业注册成立时间不少于3年（含）；','需要提供营业执照信息','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(15,7,NULL,'mandatory','qualification','财务要求','供应商具有良好的商业信誉和健全的财务会计制度（供应商提供近1年的经第三方机构审计的财务审计报告（每份报告应至少包含1）审计报告正文，2）资产负债表，3）利润表或收入费用表（事业单位提供），4）现金流量表。
）的复印件加盖供应商公章）或近三个月银行出具的资信证明原件）；','需要提供财务要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(16,7,NULL,'mandatory','qualification','依法纳税','提供以下资料：①供应商提供谈判截止日前6个月任意1个月的增值税缴纳证明文件；','需要提供依法纳税','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(17,7,NULL,'mandatory','qualification','缴纳社保','②供应商企业社保直接缴纳人数不得低于10人（含）（须近一年在本公司（含分公司）直接缴纳且连续缴费月数大于等于12个月（且截止月至少包括2025年6月）的“社会保险权益记录（必须体现缴费单位名称、缴费个人姓名、社会保障号码（至少保留社会保障号码后6位）、缴费起止年月，以及提供鉴定真伪的查询方式）”）；
被授权人近3个月在本公司（含分公司）直接缴纳且连续缴费月数大于等于3个月的（且截止月至少包括2025年6月）“社会保险权益记录（必须体现缴费单位名称、缴费个人姓名、社会保障号码（至少保留社会保障号码后6位）、缴费起止年月，以及提供鉴定真伪的查询方式）”）的证明资料并加盖公章。
供应商有依法缴纳税收和社会保障资金的良好记录。','需要提供缴纳社保','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(18,7,NULL,'mandatory','qualification','失信被执行人','供应商不得被列入“失信被执行人”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。
供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供失信被执行人','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(19,7,NULL,'mandatory','qualification','信用中国严重违法失信','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供信用中国严重违法失信','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(20,7,NULL,'mandatory','qualification','严重违法失信行为记录名单','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供严重违法失信行为记录名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(21,7,NULL,'mandatory','qualification','信用中国重大税收违法','供应商不得被列入“重大税收违法案件当事人名单（即：重大税收违法失信主体名单）”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供信用中国重大税收违法','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(22,7,NULL,'mandatory','qualification','采购人黑名单','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供采购人黑名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(23,7,NULL,'mandatory','qualification','承诺函','供应商具有履行合同所必需的设备和专业技术能力（供应商提供承诺函）；','需要提供承诺函','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(24,7,NULL,'mandatory','qualification','营业办公场所房产证明','供应商提供以下相关证明文件之一：①供应商自有房产的，须提供房产证明文件；
供应商应依法取得营业办公场所的房产证明文件，或营业办公场所房产证明和在有效期内的房屋租赁合同。','需要提供营业办公场所房产证明','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(25,7,NULL,'mandatory','qualification','业绩案例要求','供应商具备至少1个手机核验信息核验类领域同类项目案例（须提供合同复印件（包括合同首页、服务内容页、双方盖章页复印件）加盖公章，若供应商存在名称变更，且本次谈判文件中案例的合同主体为变更前公司名称，应提供工商行政管理局等政府单位的批复/通知复印件加盖公章）。','需要提供业绩案例要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(26,7,NULL,'mandatory','qualification','保证金要求','人民币伍仟万元（不含）以上的，保证金为人民币肆万元）。','需要提供保证金要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-23 07:41:43','2025-10-23 07:41:43','hitl_30a773ad71c5');
INSERT INTO "tender_requirements" VALUES(27,8,NULL,'mandatory','qualification','营业执照信息','供应商必须是在中华人民共和国境内注册或开办的具有独立法人资格的企业，或事业单位，或特殊普通合伙单位等；
供应商资格要求：
供应商具有独立承担民事责任的能力；
供应商企业注册成立时间不少于3年（含）；','需要提供营业执照信息','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(28,8,NULL,'mandatory','qualification','财务要求','供应商具有良好的商业信誉和健全的财务会计制度（供应商提供近1年的经第三方机构审计的财务审计报告（每份报告应至少包含1）审计报告正文，2）资产负债表，3）利润表或收入费用表（事业单位提供），4）现金流量表。
）的复印件加盖供应商公章）或近三个月银行出具的资信证明原件）；','需要提供财务要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(29,8,NULL,'mandatory','qualification','依法纳税','提供以下资料：①供应商提供谈判截止日前6个月任意1个月的增值税缴纳证明文件；','需要提供依法纳税','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(30,8,NULL,'mandatory','qualification','缴纳社保','②供应商企业社保直接缴纳人数不得低于10人（含）（须近一年在本公司（含分公司）直接缴纳且连续缴费月数大于等于12个月（且截止月至少包括2025年6月）的“社会保险权益记录（必须体现缴费单位名称、缴费个人姓名、社会保障号码（至少保留社会保障号码后6位）、缴费起止年月，以及提供鉴定真伪的查询方式）”）；
被授权人近3个月在本公司（含分公司）直接缴纳且连续缴费月数大于等于3个月的（且截止月至少包括2025年6月）“社会保险权益记录（必须体现缴费单位名称、缴费个人姓名、社会保障号码（至少保留社会保障号码后6位）、缴费起止年月，以及提供鉴定真伪的查询方式）”）的证明资料并加盖公章。
供应商有依法缴纳税收和社会保障资金的良好记录。','需要提供缴纳社保','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(31,8,NULL,'mandatory','qualification','失信被执行人','供应商不得被列入“失信被执行人”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。
供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供失信被执行人','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(32,8,NULL,'mandatory','qualification','信用中国严重违法失信','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供信用中国严重违法失信','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(33,8,NULL,'mandatory','qualification','严重违法失信行为记录名单','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供严重违法失信行为记录名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(34,8,NULL,'mandatory','qualification','信用中国重大税收违法','供应商不得被列入“重大税收违法案件当事人名单（即：重大税收违法失信主体名单）”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供信用中国重大税收违法','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(35,8,NULL,'mandatory','qualification','采购人黑名单','供应商不得被列入“工商严重违法失信行为（即：列入严重违法失信名单（黑名单）信息）”、“政府采购严重违法失信行为记录名单”（本项谈判时不需提供证明文件，由采购代理机构在谈判前一个工作日至谈判截止后初步评审前查询供应商的信用记录，以查询结果为准，并由采购代理机构留存打印截图。','需要提供采购人黑名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(36,8,NULL,'mandatory','qualification','承诺函','供应商具有履行合同所必需的设备和专业技术能力（供应商提供承诺函）；','需要提供承诺函','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(37,8,NULL,'mandatory','qualification','营业办公场所房产证明','供应商提供以下相关证明文件之一：①供应商自有房产的，须提供房产证明文件；
供应商应依法取得营业办公场所的房产证明文件，或营业办公场所房产证明和在有效期内的房屋租赁合同。','需要提供营业办公场所房产证明','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(38,8,NULL,'mandatory','qualification','业绩案例要求','供应商具备至少1个手机核验信息核验类领域同类项目案例（须提供合同复印件（包括合同首页、服务内容页、双方盖章页复印件）加盖公章，若供应商存在名称变更，且本次谈判文件中案例的合同主体为变更前公司名称，应提供工商行政管理局等政府单位的批复/通知复印件加盖公章）。','需要提供业绩案例要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(39,8,NULL,'mandatory','qualification','保证金要求','人民币伍仟万元（不含）以上的，保证金为人民币肆万元）。','需要提供保证金要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 01:03:33','2025-10-24 01:03:33','hitl_5a00b2b7e859');
INSERT INTO "tender_requirements" VALUES(40,10,NULL,'mandatory','qualification','营业执照信息','附件1	投标函
附件2	开标一览表
附件3	采购需求偏离表
附件4	商务条款偏离表
附件5	资格证明文件
附件5-1	企业法人营业执照、事业单位法人证书或登记证
附件5-2	法定代表人（或单位负责人）授权书
附件5-3	投标人的资格声明
附件5-4	会计师事务所出具的上一年度财务审计报告或新设企业当年验资报告的复印件（报告须具有出具单位公章），或银行出具的资信证明
附件5-5	依法缴纳税收记录证明文件
附件5-6	社会保障资金缴纳记录证明文件
附件5-7	承诺书（投标人须提供以下承诺）
附件5-8	查询截图文件
附件6	投标人业绩案例
附件7	优于采购需求的承诺
附件8	投标人控股及关联关系情况表
附件9	拟用于本项目的团队人员
附件10	其它资格证明文件要求
投标人提供的以上材料必须真实有效，任何一项的虚假将导致其投标文件被拒绝。','需要提供营业执照信息','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 09:55:42','2025-10-24 09:55:42','hitl_f771fdaddab5');
INSERT INTO "tender_requirements" VALUES(41,10,NULL,'mandatory','qualification','财务要求','附件1	投标函
附件2	开标一览表
附件3	采购需求偏离表
附件4	商务条款偏离表
附件5	资格证明文件
附件5-1	企业法人营业执照、事业单位法人证书或登记证
附件5-2	法定代表人（或单位负责人）授权书
附件5-3	投标人的资格声明
附件5-4	会计师事务所出具的上一年度财务审计报告或新设企业当年验资报告的复印件（报告须具有出具单位公章），或银行出具的资信证明
附件5-5	依法缴纳税收记录证明文件
附件5-6	社会保障资金缴纳记录证明文件
附件5-7	承诺书（投标人须提供以下承诺）
附件5-8	查询截图文件
附件6	投标人业绩案例
附件7	优于采购需求的承诺
附件8	投标人控股及关联关系情况表
附件9	拟用于本项目的团队人员
附件10	其它资格证明文件要求
投标人提供的以上材料必须真实有效，任何一项的虚假将导致其投标文件被拒绝。','需要提供财务要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 09:55:42','2025-10-24 09:55:42','hitl_f771fdaddab5');
INSERT INTO "tender_requirements" VALUES(42,10,NULL,'mandatory','qualification','依法纳税','开标一览表（报价表）中不含增值税价格、所报税率计算结果与含增值税价格价格不一致，以不含增值税价格和所报税率为准调整含税价格；','需要提供依法纳税','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 09:55:42','2025-10-24 09:55:42','hitl_f771fdaddab5');
INSERT INTO "tender_requirements" VALUES(43,10,NULL,'mandatory','qualification','缴纳社保','附件1	投标函
附件2	开标一览表
附件3	采购需求偏离表
附件4	商务条款偏离表
附件5	资格证明文件
附件5-1	企业法人营业执照、事业单位法人证书或登记证
附件5-2	法定代表人（或单位负责人）授权书
附件5-3	投标人的资格声明
附件5-4	会计师事务所出具的上一年度财务审计报告或新设企业当年验资报告的复印件（报告须具有出具单位公章），或银行出具的资信证明
附件5-5	依法缴纳税收记录证明文件
附件5-6	社会保障资金缴纳记录证明文件
附件5-7	承诺书（投标人须提供以下承诺）
附件5-8	查询截图文件
附件6	投标人业绩案例
附件7	优于采购需求的承诺
附件8	投标人控股及关联关系情况表
附件9	拟用于本项目的团队人员
附件10	其它资格证明文件要求
投标人提供的以上材料必须真实有效，任何一项的虚假将导致其投标文件被拒绝。','需要提供缴纳社保','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 09:55:42','2025-10-24 09:55:42','hitl_f771fdaddab5');
INSERT INTO "tender_requirements" VALUES(44,10,NULL,'mandatory','qualification','承诺函','附件1	投标函
附件2	开标一览表
附件3	采购需求偏离表
附件4	商务条款偏离表
附件5	资格证明文件
附件5-1	企业法人营业执照、事业单位法人证书或登记证
附件5-2	法定代表人（或单位负责人）授权书
附件5-3	投标人的资格声明
附件5-4	会计师事务所出具的上一年度财务审计报告或新设企业当年验资报告的复印件（报告须具有出具单位公章），或银行出具的资信证明
附件5-5	依法缴纳税收记录证明文件
附件5-6	社会保障资金缴纳记录证明文件
附件5-7	承诺书（投标人须提供以下承诺）
附件5-8	查询截图文件
附件6	投标人业绩案例
附件7	优于采购需求的承诺
附件8	投标人控股及关联关系情况表
附件9	拟用于本项目的团队人员
附件10	其它资格证明文件要求
投标人提供的以上材料必须真实有效，任何一项的虚假将导致其投标文件被拒绝。','需要提供承诺函','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 09:55:42','2025-10-24 09:55:42','hitl_f771fdaddab5');
INSERT INTO "tender_requirements" VALUES(45,10,NULL,'mandatory','qualification','保证金要求','中标人提交履约保证金构成合同生效的条件之一。
投标保证金
投标人应提交规定金额的投标保证金，并作为其投标文件的一部分。','需要提供保证金要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 09:55:42','2025-10-24 09:55:42','hitl_f771fdaddab5');
INSERT INTO "tender_requirements" VALUES(46,10,NULL,'mandatory','qualification','营业执照信息','营业执照副本复印件；
其他必须满足的要求：
1.在中华人民共和国境内注册的独立法人或者其他组织，具备有效的营业执照。
合格投标人的基本资质要求（须同时满足）：
投标人的资质要求如下：
1.投标人须具有独立承担民事责任的能力，遵守法律、法规，具有良好的商业信誉和健全的财务会计制度。','需要提供营业执照信息','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(47,10,NULL,'mandatory','qualification','财务要求','具有良好的商业信誉和健全的财务会计制度；
6.参加本项目的投标人近三年来企业财务状况良好，企业财产没有处于被接管、全部资金被冻结以及破产状态；','需要提供财务要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(48,10,NULL,'mandatory','qualification','依法纳税','9.投标人须能够提供增值税合法抵扣凭证（即增值税专用发票）。','需要提供依法纳税','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(49,10,NULL,'mandatory','qualification','缴纳社保','有依法缴纳税收和社会保障资金的良好记录。','需要提供缴纳社保','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(50,10,NULL,'mandatory','qualification','失信被执行人','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供失信被执行人','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(51,10,NULL,'mandatory','qualification','信用中国严重违法失信','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供信用中国严重违法失信','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(52,10,NULL,'mandatory','qualification','严重违法失信行为记录名单','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供严重违法失信行为记录名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(53,10,NULL,'mandatory','qualification','信用中国重大税收违法','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供信用中国重大税收违法','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(54,10,NULL,'mandatory','qualification','采购人黑名单','未被列入《哈银消金不良行为供应商禁用名单》和《哈银消金不良行为供应商黑名单》。','需要提供采购人黑名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(55,10,NULL,'mandatory','qualification','业绩案例要求','2.投标人近五年内至少承接过2个与招标人需求相近（运营商类数据，至少包含三要素验证、在网时长和在网状态三个产品）的成功案例，所提供的案例要求出具合同复印件首末及内容页(首页即项目名称页，末页即签字盖章页并能清楚体现最终用户名称、时间，内容页即项目主要内容), 需提供发票，不能清楚提供的视为无效案例，须注明案例范围。','需要提供业绩案例要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-24 13:42:45','2025-10-24 13:42:45','hitl_2c9dd1cf72a4');
INSERT INTO "tender_requirements" VALUES(66,10,NULL,'mandatory','qualification','营业执照信息','营业执照副本复印件；
其他必须满足的要求：
1.在中华人民共和国境内注册的独立法人或者其他组织，具备有效的营业执照。
合格投标人的基本资质要求（须同时满足）：
投标人的资质要求如下：
1.投标人须具有独立承担民事责任的能力，遵守法律、法规，具有良好的商业信誉和健全的财务会计制度。','需要提供营业执照信息','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(67,10,NULL,'mandatory','qualification','财务要求','具有良好的商业信誉和健全的财务会计制度；
6.参加本项目的投标人近三年来企业财务状况良好，企业财产没有处于被接管、全部资金被冻结以及破产状态；','需要提供财务要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(68,10,NULL,'mandatory','qualification','依法纳税','9.投标人须能够提供增值税合法抵扣凭证（即增值税专用发票）。','需要提供依法纳税','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(69,10,NULL,'mandatory','qualification','缴纳社保','有依法缴纳税收和社会保障资金的良好记录。','需要提供缴纳社保','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(70,10,NULL,'mandatory','qualification','失信被执行人','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供失信被执行人','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(71,10,NULL,'mandatory','qualification','信用中国严重违法失信','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供信用中国严重违法失信','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(72,10,NULL,'mandatory','qualification','严重违法失信行为记录名单','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供严重违法失信行为记录名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(73,10,NULL,'mandatory','qualification','信用中国重大税收违法','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供信用中国重大税收违法','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(74,10,NULL,'mandatory','qualification','采购人黑名单','未被列入《哈银消金不良行为供应商禁用名单》和《哈银消金不良行为供应商黑名单》。','需要提供采购人黑名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(75,10,NULL,'mandatory','qualification','业绩案例要求','2.投标人近五年内至少承接过2个与招标人需求相近（运营商类数据，至少包含三要素验证、在网时长和在网状态三个产品）的成功案例，所提供的案例要求出具合同复印件首末及内容页(首页即项目名称页，末页即签字盖章页并能清楚体现最终用户名称、时间，内容页即项目主要内容), 需提供发票，不能清楚提供的视为无效案例，须注明案例范围。','需要提供业绩案例要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:52:32','2025-10-25 01:52:32','hitl_7955013df7a4');
INSERT INTO "tender_requirements" VALUES(76,11,NULL,'mandatory','qualification','营业执照信息','营业执照副本复印件；
其他必须满足的要求：
1.在中华人民共和国境内注册的独立法人或者其他组织，具备有效的营业执照。
合格投标人的基本资质要求（须同时满足）：
投标人的资质要求如下：
1.投标人须具有独立承担民事责任的能力，遵守法律、法规，具有良好的商业信誉和健全的财务会计制度。','需要提供营业执照信息','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(77,11,NULL,'mandatory','qualification','财务要求','具有良好的商业信誉和健全的财务会计制度；
6.参加本项目的投标人近三年来企业财务状况良好，企业财产没有处于被接管、全部资金被冻结以及破产状态；','需要提供财务要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(78,11,NULL,'mandatory','qualification','依法纳税','9.投标人须能够提供增值税合法抵扣凭证（即增值税专用发票）。','需要提供依法纳税','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(79,11,NULL,'mandatory','qualification','缴纳社保','有依法缴纳税收和社会保障资金的良好记录。','需要提供缴纳社保','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(80,11,NULL,'mandatory','qualification','失信被执行人','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供失信被执行人','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(81,11,NULL,'mandatory','qualification','信用中国严重违法失信','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供信用中国严重违法失信','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(82,11,NULL,'mandatory','qualification','严重违法失信行为记录名单','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供严重违法失信行为记录名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(83,11,NULL,'mandatory','qualification','信用中国重大税收违法','3.未被列入“信用中国www.creditchina.gov.cn”网站失信被执行人、重大税收违法案件当事人名单、政府采购严重违法失信记录名单，且其被禁止参加采购的期限已届满的供应商。','需要提供信用中国重大税收违法','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(84,11,NULL,'mandatory','qualification','采购人黑名单','未被列入《哈银消金不良行为供应商禁用名单》和《哈银消金不良行为供应商黑名单》。','需要提供采购人黑名单','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
INSERT INTO "tender_requirements" VALUES(85,11,NULL,'mandatory','qualification','业绩案例要求','2.投标人近五年内至少承接过2个与招标人需求相近（运营商类数据，至少包含三要素验证、在网时长和在网状态三个产品）的成功案例，所提供的案例要求出具合同复印件首末及内容页(首页即项目名称页，末页即签字盖章页并能清楚体现最终用户名称、时间，内容页即项目主要内容), 需提供发票，不能清楚提供的视为无效案例，须注明案例范围。','需要提供业绩案例要求','','high',0.8,NULL,NULL,0,NULL,NULL,NULL,'2025-10-25 01:54:25','2025-10-25 01:54:25','hitl_3abc8818b9d7');
CREATE TABLE tender_requirements_draft (
    draft_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER,  -- NULL 表示新增的要求
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) NOT NULL,

    -- 草稿内容（与 tender_requirements 字段一致）
    constraint_type VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100),
    detail TEXT NOT NULL,
    source_location VARCHAR(255),
    priority VARCHAR(10) DEFAULT 'medium',

    -- 编辑操作
    operation VARCHAR(20) NOT NULL,  -- 'add'（新增）/ 'edit'（编辑）/ 'delete'（删除）
    edited_by VARCHAR(100),
    edited_at TIMESTAMP,

    -- 草稿状态
    is_published BOOLEAN DEFAULT FALSE,  -- 是否已发布（写入正式表）
    published_at TIMESTAMP,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (requirement_id) REFERENCES tender_requirements(requirement_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);
CREATE TABLE tender_user_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100),
    user_id VARCHAR(100),  -- 用户ID（可选）

    -- 操作信息
    action_type VARCHAR(50) NOT NULL,  -- 'chapter_selected', 'chunk_restored', 'requirement_edited' 等
    action_step INTEGER,  -- 1, 2, 3
    action_data TEXT,  -- JSON: 操作详细数据

    -- 元数据
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);
INSERT INTO "tender_user_actions" VALUES(1,5,'hitl_25f04ef24f1a',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-23 02:24:34');
INSERT INTO "tender_user_actions" VALUES(2,6,'hitl_1ffd461aca66',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-23 03:21:38');
INSERT INTO "tender_user_actions" VALUES(3,7,'hitl_30a773ad71c5',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-23 07:41:28');
INSERT INTO "tender_user_actions" VALUES(4,8,'hitl_5a00b2b7e859',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-24 01:03:14');
INSERT INTO "tender_user_actions" VALUES(5,10,'hitl_f771fdaddab5',NULL,'chapter_selected',1,'{"selected_ids": ["ch_1"]}',NULL,NULL,'2025-10-24 09:55:14');
INSERT INTO "tender_user_actions" VALUES(6,10,'hitl_2c9dd1cf72a4',NULL,'chapter_selected',1,'{"selected_ids": ["ch_2", "ch_0"]}',NULL,NULL,'2025-10-24 13:42:39');
INSERT INTO "tender_user_actions" VALUES(7,10,'hitl_7955013df7a4',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-24 14:47:53');
INSERT INTO "tender_user_actions" VALUES(8,10,'hitl_7955013df7a4',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-25 01:50:01');
INSERT INTO "tender_user_actions" VALUES(9,10,'hitl_7955013df7a4',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-25 01:52:27');
INSERT INTO "tender_user_actions" VALUES(10,11,'hitl_3abc8818b9d7',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-25 01:54:10');
INSERT INTO "tender_user_actions" VALUES(11,8,'hitl_5a00b2b7e859',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-26 02:49:16');
INSERT INTO "tender_user_actions" VALUES(12,8,'hitl_5a00b2b7e859',NULL,'chapter_selected',1,'{"selected_ids": ["ch_0"]}',NULL,NULL,'2025-10-26 02:53:32');
CREATE TABLE user_roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_description TEXT,
    privacy_level_access INTEGER DEFAULT 1, -- 最高可访问隐私级别
    can_upload BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_modify_privacy BOOLEAN DEFAULT FALSE,
    can_manage_users BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO "user_roles" VALUES(1,'普通用户','只能访问公开文档',1,0,0,0,0,'2025-10-23 01:43:59');
INSERT INTO "user_roles" VALUES(2,'内部员工','可访问公开和内部文档',2,1,0,0,0,'2025-10-23 01:43:59');
INSERT INTO "user_roles" VALUES(3,'项目经理','可访问机密级别文档',3,1,1,1,0,'2025-10-23 01:43:59');
INSERT INTO "user_roles" VALUES(4,'高级管理','可访问所有级别文档',4,1,1,1,1,'2025-10-23 01:43:59');
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255),
    role_id INTEGER NOT NULL,
    company_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
CREATE INDEX idx_companies_name ON companies(company_name);
CREATE INDEX idx_products_company ON products(company_id);
CREATE INDEX idx_products_category ON products(product_category);
CREATE INDEX idx_libraries_owner ON document_libraries(owner_type, owner_id);
CREATE INDEX idx_libraries_type ON document_libraries(library_type);
CREATE INDEX idx_documents_library ON documents(library_id);
CREATE INDEX idx_documents_status ON documents(parse_status, vector_status);
CREATE INDEX idx_documents_privacy ON documents(privacy_classification);
CREATE INDEX idx_chunks_doc ON document_chunks(doc_id);
CREATE INDEX idx_audit_user ON access_audit_logs(user_id, timestamp);
CREATE INDEX idx_audit_resource ON access_audit_logs(resource_type, resource_id);
CREATE INDEX idx_tender_projects_company ON tender_projects(company_id);
CREATE INDEX idx_tender_projects_status ON tender_projects(status);
CREATE INDEX idx_toc_doc ON document_toc(doc_id);
CREATE INDEX idx_toc_heading_text ON document_toc(heading_text);
CREATE INDEX idx_toc_section_number ON document_toc(section_number);
CREATE INDEX idx_toc_parent ON document_toc(parent_toc_id);
CREATE INDEX idx_case_studies_company ON case_studies(company_id);
CREATE INDEX idx_case_studies_product ON case_studies(product_id);
CREATE INDEX idx_case_studies_customer ON case_studies(customer_name);
CREATE INDEX idx_case_studies_industry ON case_studies(industry);
CREATE INDEX idx_case_studies_status ON case_studies(case_status);
CREATE INDEX idx_case_studies_contract_type ON case_studies(contract_type);
CREATE INDEX idx_case_studies_dates ON case_studies(contract_start_date, contract_end_date);
CREATE INDEX idx_case_studies_party_a_customer ON case_studies(party_a_customer_name);
CREATE INDEX idx_case_studies_party_b_company ON case_studies(party_b_company_name);
CREATE INDEX idx_case_attachments_case ON case_attachments(case_id);
CREATE INDEX idx_resumes_company ON resumes(company_id);
CREATE INDEX idx_resumes_name ON resumes(name);
CREATE INDEX idx_resumes_position ON resumes(current_position);
CREATE INDEX idx_resumes_education ON resumes(education_level);
CREATE INDEX idx_resumes_status ON resumes(status);
CREATE INDEX idx_resumes_created ON resumes(created_at);
CREATE INDEX idx_resume_attachments ON resume_attachments(resume_id);
CREATE INDEX idx_attachment_category ON resume_attachments(attachment_category);
CREATE TRIGGER update_resumes_timestamp
AFTER UPDATE ON resumes
FOR EACH ROW
BEGIN
    UPDATE resumes SET updated_at = CURRENT_TIMESTAMP WHERE resume_id = NEW.resume_id;
END;
CREATE INDEX idx_chunks_project_id ON tender_document_chunks(project_id);
CREATE INDEX idx_chunks_project_index ON tender_document_chunks(project_id, chunk_index);
CREATE INDEX idx_chunks_valuable ON tender_document_chunks(project_id, is_valuable);
CREATE INDEX idx_chunks_type ON tender_document_chunks(chunk_type);
CREATE INDEX idx_requirements_project_id ON tender_requirements(project_id);
CREATE INDEX idx_requirements_type ON tender_requirements(project_id, constraint_type);
CREATE INDEX idx_requirements_category ON tender_requirements(project_id, category);
CREATE INDEX idx_requirements_priority ON tender_requirements(priority);
CREATE INDEX idx_requirements_verified ON tender_requirements(is_verified);
CREATE INDEX idx_logs_project_id ON tender_processing_logs(project_id);
CREATE INDEX idx_logs_task_id ON tender_processing_logs(task_id);
CREATE INDEX idx_logs_step_status ON tender_processing_logs(step, status);
CREATE INDEX idx_logs_created_at ON tender_processing_logs(created_at DESC);
CREATE INDEX idx_tasks_project_id ON tender_processing_tasks(project_id);
CREATE INDEX idx_tasks_status ON tender_processing_tasks(overall_status);
CREATE TRIGGER update_chunks_timestamp
AFTER UPDATE ON tender_document_chunks
BEGIN
    UPDATE tender_document_chunks
    SET updated_at = CURRENT_TIMESTAMP
    WHERE chunk_id = NEW.chunk_id;
END;
CREATE TRIGGER update_requirements_timestamp
AFTER UPDATE ON tender_requirements
BEGIN
    UPDATE tender_requirements
    SET updated_at = CURRENT_TIMESTAMP
    WHERE requirement_id = NEW.requirement_id;
END;
CREATE TRIGGER update_logs_timestamp
AFTER UPDATE ON tender_processing_logs
BEGIN
    UPDATE tender_processing_logs
    SET updated_at = CURRENT_TIMESTAMP
    WHERE log_id = NEW.log_id;
END;
CREATE VIEW v_processing_statistics AS
SELECT
    t.project_id,
    t.task_id,
    t.overall_status,
    t.progress_percentage,
    t.total_chunks,
    t.valuable_chunks,
    t.total_requirements,
    -- 成本汇总
    SUM(l.actual_cost) as total_cost,
    SUM(l.api_calls) as total_api_calls,
    SUM(l.total_tokens) as total_tokens,
    -- 时间汇总
    t.created_at,
    t.started_at,
    t.completed_at,
    CASE
        WHEN t.completed_at IS NOT NULL AND t.started_at IS NOT NULL
        THEN CAST((julianday(t.completed_at) - julianday(t.started_at)) * 86400 AS INTEGER)
        ELSE NULL
    END as duration_seconds
FROM tender_processing_tasks t
LEFT JOIN tender_processing_logs l ON t.task_id = l.task_id
GROUP BY t.task_id;
CREATE VIEW v_requirements_summary AS
SELECT
    project_id,
    constraint_type,
    category,
    COUNT(*) as count,
    COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_count,
    AVG(extraction_confidence) as avg_confidence
FROM tender_requirements
GROUP BY project_id, constraint_type, category;
CREATE INDEX idx_chapters_project_task ON tender_document_chapters(project_id, task_id);
CREATE INDEX idx_chapters_selected ON tender_document_chapters(is_selected);
CREATE INDEX idx_chapters_node_id ON tender_document_chapters(chapter_node_id);
CREATE INDEX idx_filter_review_project_task ON tender_filter_review(project_id, task_id);
CREATE INDEX idx_filter_review_chunk ON tender_filter_review(chunk_id);
CREATE INDEX idx_filter_review_decision ON tender_filter_review(ai_decision);
CREATE INDEX idx_draft_project_task ON tender_requirements_draft(project_id, task_id);
CREATE INDEX idx_draft_requirement ON tender_requirements_draft(requirement_id);
CREATE INDEX idx_draft_published ON tender_requirements_draft(is_published);
CREATE INDEX idx_hitl_project ON tender_hitl_tasks(project_id);
CREATE INDEX idx_hitl_task ON tender_hitl_tasks(task_id);
CREATE INDEX idx_hitl_current_step ON tender_hitl_tasks(current_step);
CREATE INDEX idx_hitl_overall_status ON tender_hitl_tasks(overall_status);
CREATE INDEX idx_actions_project ON tender_user_actions(project_id);
CREATE INDEX idx_actions_task ON tender_user_actions(task_id);
CREATE INDEX idx_actions_type ON tender_user_actions(action_type);
CREATE INDEX idx_actions_created ON tender_user_actions(created_at DESC);
CREATE TRIGGER update_chapters_timestamp
AFTER UPDATE ON tender_document_chapters
BEGIN
    UPDATE tender_document_chapters
    SET updated_at = CURRENT_TIMESTAMP
    WHERE chapter_id = NEW.chapter_id;
END;
CREATE TRIGGER update_filter_review_timestamp
AFTER UPDATE ON tender_filter_review
BEGIN
    UPDATE tender_filter_review
    SET updated_at = CURRENT_TIMESTAMP
    WHERE review_id = NEW.review_id;
END;
CREATE TRIGGER update_draft_timestamp
AFTER UPDATE ON tender_requirements_draft
BEGIN
    UPDATE tender_requirements_draft
    SET updated_at = CURRENT_TIMESTAMP
    WHERE draft_id = NEW.draft_id;
END;
CREATE TRIGGER update_hitl_tasks_timestamp
AFTER UPDATE ON tender_hitl_tasks
BEGIN
    UPDATE tender_hitl_tasks
    SET updated_at = CURRENT_TIMESTAMP
    WHERE hitl_task_id = NEW.hitl_task_id;
END;
CREATE VIEW v_hitl_progress AS
SELECT
    h.hitl_task_id,
    h.project_id,
    h.task_id,
    h.current_step,
    h.overall_status,

    -- 步骤1统计
    (SELECT COUNT(*) FROM tender_document_chapters
     WHERE task_id = h.task_id) as total_chapters,
    (SELECT COUNT(*) FROM tender_document_chapters
     WHERE task_id = h.task_id AND is_selected = 1) as selected_chapters,

    -- 步骤2统计
    (SELECT COUNT(*) FROM tender_filter_review r
     JOIN tender_document_chunks c ON r.chunk_id = c.chunk_id
     WHERE r.task_id = h.task_id AND r.ai_decision = 'NON-REQUIREMENT') as filtered_chunks,
    (SELECT COUNT(*) FROM tender_filter_review r
     WHERE r.task_id = h.task_id AND r.user_decision = 'restore') as restored_chunks,

    -- 步骤3统计
    (SELECT COUNT(*) FROM tender_requirements_draft
     WHERE task_id = h.task_id) as draft_requirements,
    (SELECT COUNT(*) FROM tender_requirements_draft
     WHERE task_id = h.task_id AND is_published = 1) as published_requirements,

    -- 时间统计
    h.created_at,
    h.updated_at,
    CASE
        WHEN h.step3_completed_at IS NOT NULL
        THEN CAST((julianday(h.step3_completed_at) - julianday(h.created_at)) * 86400 AS INTEGER)
        ELSE NULL
    END as total_duration_seconds

FROM tender_hitl_tasks h;
CREATE VIEW v_chapter_selection_stats AS
SELECT
    task_id,
    COUNT(*) as total_chapters,
    SUM(CASE WHEN is_selected = 1 THEN 1 ELSE 0 END) as selected_count,
    SUM(CASE WHEN auto_selected = 1 THEN 1 ELSE 0 END) as auto_selected_count,
    SUM(CASE WHEN skip_recommended = 1 THEN 1 ELSE 0 END) as skip_recommended_count,
    SUM(CASE WHEN is_selected = 1 THEN word_count ELSE 0 END) as selected_words
FROM tender_document_chapters
GROUP BY task_id;
CREATE INDEX idx_requirements_hitl_task
ON tender_requirements(hitl_task_id);
CREATE INDEX idx_requirements_project_hitl
ON tender_requirements(project_id, hitl_task_id);
CREATE INDEX idx_chunks_hitl_task
ON tender_document_chunks(hitl_task_id);
CREATE INDEX idx_chunks_project_hitl
ON tender_document_chunks(project_id, hitl_task_id);
CREATE INDEX idx_company_qualifications_company ON company_qualifications(company_id);
CREATE INDEX idx_company_qualifications_expire ON company_qualifications(expire_date);
CREATE INDEX idx_company_qualifications_status ON company_qualifications(verify_status);
CREATE INDEX idx_company_qual_key_seq ON company_qualifications(company_id, qualification_key, file_sequence);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('companies',1);
INSERT INTO "sqlite_sequence" VALUES('company_profiles',4);
INSERT INTO "sqlite_sequence" VALUES('products',3);
INSERT INTO "sqlite_sequence" VALUES('user_roles',4);
INSERT INTO "sqlite_sequence" VALUES('knowledge_base_configs',13);
INSERT INTO "sqlite_sequence" VALUES('tender_projects',11);
INSERT INTO "sqlite_sequence" VALUES('qualification_types',3271);
INSERT INTO "sqlite_sequence" VALUES('tender_document_chapters',73);
INSERT INTO "sqlite_sequence" VALUES('tender_user_actions',12);
INSERT INTO "sqlite_sequence" VALUES('resumes',1);
INSERT INTO "sqlite_sequence" VALUES('tender_requirements',85);
INSERT INTO "sqlite_sequence" VALUES('resume_attachments',4);
INSERT INTO "sqlite_sequence" VALUES('case_studies',2);
INSERT INTO "sqlite_sequence" VALUES('company_qualifications',19);

COMMIT;
PRAGMA foreign_keys=ON;
