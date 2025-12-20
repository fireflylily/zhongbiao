-- 产品分类表
-- 用于统一管理和标准化产品分类

CREATE TABLE IF NOT EXISTS product_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE,  -- 分类名称：网络基建类、IT系统类等
    category_code VARCHAR(50) NOT NULL UNIQUE,   -- 分类代码：network_infra, it_system等
    category_description TEXT,                   -- 分类描述
    category_order INTEGER DEFAULT 999,          -- 显示顺序
    is_active BOOLEAN DEFAULT TRUE,              -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品分类示例值表
-- 用于定义每个分类下的具体业务类型
CREATE TABLE IF NOT EXISTS product_category_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    item_name VARCHAR(100) NOT NULL,             -- 示例值名称：基站、光缆等
    item_code VARCHAR(50),                       -- 示例值代码
    item_description TEXT,                       -- 示例值描述
    item_order INTEGER DEFAULT 999,              -- 显示顺序
    is_active BOOLEAN DEFAULT TRUE,              -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id) ON DELETE CASCADE,
    UNIQUE(category_id, item_name)
);

-- 初始化产品分类数据
INSERT OR IGNORE INTO product_categories (category_name, category_code, category_description, category_order) VALUES
('网络基建类', 'network_infra', '网络基础设施相关产品和服务', 1),
('IT系统类', 'it_system', 'IT系统开发和集成相关产品和服务', 2),
('数据与AI类', 'data_ai', '数据治理、大数据分析和AI相关产品和服务', 3),
('政企集成类', 'government_integration', '政企智慧化集成解决方案', 4),
('市场营销类', 'marketing', '市场营销和客户服务相关产品', 5),
('综合支撑类', 'comprehensive_support', '综合支撑和后勤服务', 6);

-- 初始化产品分类示例值数据
-- 网络基建类
INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '基站', 'base_station', 1 FROM product_categories WHERE category_code = 'network_infra';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '光缆', 'optical_cable', 2 FROM product_categories WHERE category_code = 'network_infra';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '代维', 'maintenance', 3 FROM product_categories WHERE category_code = 'network_infra';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '网优', 'network_optimization', 4 FROM product_categories WHERE category_code = 'network_infra';

-- IT系统类
INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '业务系统开发', 'business_system_dev', 1 FROM product_categories WHERE category_code = 'it_system';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '云集成', 'cloud_integration', 2 FROM product_categories WHERE category_code = 'it_system';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, 'IT维保', 'it_maintenance', 3 FROM product_categories WHERE category_code = 'it_system';

-- 数据与AI类
INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '数据治理', 'data_governance', 1 FROM product_categories WHERE category_code = 'data_ai';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '大数据分析', 'big_data_analytics', 2 FROM product_categories WHERE category_code = 'data_ai';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '大模型', 'large_model', 3 FROM product_categories WHERE category_code = 'data_ai';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '数据安全', 'data_security', 4 FROM product_categories WHERE category_code = 'data_ai';

-- 政企集成类
INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '智慧城市', 'smart_city', 1 FROM product_categories WHERE category_code = 'government_integration';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '公安/医疗专网', 'public_safety_medical_network', 2 FROM product_categories WHERE category_code = 'government_integration';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '物联网集成', 'iot_integration', 3 FROM product_categories WHERE category_code = 'government_integration';

-- 市场营销类
INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '呼叫中心', 'call_center', 1 FROM product_categories WHERE category_code = 'marketing';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '广告', 'advertising', 2 FROM product_categories WHERE category_code = 'marketing';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '渠道经营', 'channel_management', 3 FROM product_categories WHERE category_code = 'marketing';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '终端物流', 'terminal_logistics', 4 FROM product_categories WHERE category_code = 'marketing';

-- 综合支撑类
INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '咨询审计', 'consulting_audit', 1 FROM product_categories WHERE category_code = 'comprehensive_support';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '监理', 'supervision', 2 FROM product_categories WHERE category_code = 'comprehensive_support';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '物业后勤', 'property_logistics', 3 FROM product_categories WHERE category_code = 'comprehensive_support';

INSERT OR IGNORE INTO product_category_items (category_id, item_name, item_code, item_order)
SELECT category_id, '人力培训', 'hr_training', 4 FROM product_categories WHERE category_code = 'comprehensive_support';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_product_categories_code ON product_categories(category_code);
CREATE INDEX IF NOT EXISTS idx_product_categories_order ON product_categories(category_order);
CREATE INDEX IF NOT EXISTS idx_category_items_category ON product_category_items(category_id);
CREATE INDEX IF NOT EXISTS idx_category_items_order ON product_category_items(item_order);
