/*!
 * 公司管理统一配置文件
 * 包含字段映射、资质分类、API配置等
 */

const CompanyConfig = {
    // 公司字段映射关系
    fieldMapping: {
        'companyName': '公司名称',
        'companyCode': '公司代码',
        'establishDate': '成立日期',
        'legalRepresentative': '法定代表人',
        'legalRepresentativePosition': '法定代表人职务',
        'socialCreditCode': '统一社会信用代码',
        'registeredCapital': '注册资本',
        'companyType': '公司类型',
        'registeredAddress': '注册地址',
        'businessScope': '经营范围',
        'fixedPhone': '固定电话',
        'fax': '传真',
        'postalCode': '邮政编码',
        'email': '电子邮箱',
        'website': '官方网址',
        'officeAddress': '办公地址',
        'employeeCount': '员工人数',
        'companyDescription': '公司简介',
        'bankName': '开户行全称',
        'bankAccount': '银行账号',
        'industryType': '行业类型'
    },

    // 资质分类配置
    qualificationCategories: {
        'basic': {
            name: '基本证件资质',
            icon: 'bi-card-text',
            color: 'primary',
            description: '营业执照、法人身份证等基础证件'
        },
        'iso': {
            name: 'ISO体系认证',
            icon: 'bi-award',
            color: 'warning',
            description: 'ISO9001、ISO27001等体系认证'
        },
        'credit': {
            name: '信用资质',
            icon: 'bi-shield-check',
            color: 'danger',
            description: '信用中国查询结果等信用证明'
        },
        'tax': {
            name: '税务资质',
            icon: 'bi-receipt',
            color: 'success',
            description: '纳税人资格认定书等税务证明'
        },
        'financial': {
            name: '财务资质',
            icon: 'bi-graph-up',
            color: 'info',
            description: '审计报告、财务报表等财务证明'
        },
        'industry': {
            name: '行业资质',
            icon: 'bi-gear',
            color: 'secondary',
            description: '行业特定的资质认证'
        },
        'social': {
            name: '社保资质',
            icon: 'bi-people',
            color: 'dark',
            description: '社会保险登记证等社保证明'
        },
        'intellectual': {
            name: '知识产权',
            icon: 'bi-lightbulb',
            color: 'success',
            description: '软件著作权、专利证书等知识产权'
        }
    },

    // 标准资质类型定义
    standardQualificationTypes: [
        // 基本证件资质
        { key: 'business_license', name: '营业执照', icon: 'bi-building', category: 'basic', required: true },
        { key: 'legal_id_front', name: '法定代表人身份证（正面）', icon: 'bi-person-badge', category: 'basic', required: true },
        { key: 'legal_id_back', name: '法定代表人身份证（反面）', icon: 'bi-person-badge', category: 'basic', required: true },

        // ISO体系认证
        { key: 'iso9001', name: '质量管理体系认证（ISO9001）', icon: 'bi-award', category: 'iso' },
        { key: 'iso14001', name: '环境管理体系认证（ISO14001）', icon: 'bi-tree', category: 'iso' },
        { key: 'iso45001', name: '职业健康安全管理体系认证（ISO45001）', icon: 'bi-shield-lock', category: 'iso' },
        { key: 'iso20000', name: 'IT服务管理体系认证（ISO20000）', icon: 'bi-server', category: 'iso' },
        { key: 'iso27001', name: '信息安全管理体系认证（ISO27001）', icon: 'bi-shield-lock', category: 'iso' },

        // 税务和财务资质
        { key: 'taxpayer_certificate', name: '一般纳税人资格认定书', icon: 'bi-receipt', category: 'tax' },
        { key: 'audit_report', name: '审计报告', icon: 'bi-file-earmark-text', category: 'financial' },
        { key: 'financial_statement', name: '财务报表', icon: 'bi-graph-up', category: 'financial' },

        // 行业资质
        { key: 'construction_license', name: '建筑业企业资质证书', icon: 'bi-building', category: 'industry' },
        { key: 'software_enterprise', name: '软件企业认定证书', icon: 'bi-code-slash', category: 'industry' },
        { key: 'high_tech_enterprise', name: '高新技术企业证书', icon: 'bi-lightbulb', category: 'industry' },
        { key: 'safety_production_license', name: '安全生产许可证', icon: 'bi-shield-check', category: 'industry' },

        // 信用资质
        { key: 'credit_dishonest', name: '信用中国-失信被执行人查询结果', icon: 'bi-exclamation-triangle', category: 'credit' },
        { key: 'credit_corruption', name: '信用中国-行贿犯罪档案查询结果', icon: 'bi-x-circle', category: 'credit' },
        { key: 'credit_tax', name: '信用中国-重大税收违法案件查询结果', icon: 'bi-receipt', category: 'credit' },
        { key: 'credit_procurement', name: '信用中国-政府采购严重违法失信查询结果', icon: 'bi-building', category: 'credit' },

        // 社保资质
        { key: 'social_security', name: '社会保险登记证', icon: 'bi-people', category: 'social' },
        { key: 'employee_social_security', name: '员工社保缴费证明', icon: 'bi-people', category: 'social' },

        // 知识产权
        { key: 'software_copyright', name: '软件著作权登记证书', icon: 'bi-code-slash', category: 'intellectual' },
        { key: 'patent_certificate', name: '专利证书', icon: 'bi-lightbulb', category: 'intellectual' }
    ],

    // 资质字段映射表：将公司管理资质映射到标书分析字段
    qualificationMapping: {
        // 基本证件资质
        'business_license': 'business_license_required',
        'legal_id_front': 'business_license_required',
        'legal_id_back': 'business_license_required',

        // ISO体系认证
        'iso9001': 'iso9001_required',
        'iso14001': 'iso14001_required',
        'iso45001': 'iso45001_required',
        'iso20000': 'iso27001_required',
        'iso27001': 'iso27001_required',

        // 信用资质
        'credit_dishonest': 'credit_china_required',
        'credit_corruption': 'credit_china_required',
        'credit_tax': 'credit_china_required',
        'credit_procurement': 'credit_china_required',

        // 税务资质
        'taxpayer_certificate': 'taxpayer_qualification_required',

        // 财务资质
        'audit_report': 'audit_report_required',
        'financial_statement': 'audit_report_required',

        // 社保资质
        'social_security': 'social_security_required',
        'employee_social_security': 'social_security_required',

        // 知识产权和行业资质
        'software_copyright': 'commitment_letter_required',
        'patent_certificate': 'commitment_letter_required',
        'high_tech_enterprise': 'commitment_letter_required',
        'software_enterprise': 'commitment_letter_required'
    },

    // API配置
    api: {
        baseUrl: '/api/companies',
        endpoints: {
            list: '',
            detail: '/{id}',
            create: '',
            update: '/{id}',
            delete: '/{id}',
            qualifications: '/{id}/qualifications',
            uploadQualification: '/{id}/qualifications/upload',
            downloadQualification: '/{id}/qualifications/{key}/download',
            deleteQualification: '/{id}/qualifications/{key}'
        },
        timeout: 30000,
        retryAttempts: 3
    },

    // 缓存配置
    cache: {
        ttl: 5 * 60 * 1000, // 5分钟
        maxSize: 100,
        keys: {
            companies: 'companies_list',
            company: 'company_detail_{id}',
            qualifications: 'company_qualifications_{id}'
        }
    },

    // 验证规则
    validation: {
        companyName: {
            required: true,
            minLength: 2,
            maxLength: 255
        },
        socialCreditCode: {
            pattern: /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/,
            message: '统一社会信用代码格式不正确'
        },
        email: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: '邮箱格式不正确'
        },
        phone: {
            pattern: /^[\d-\s\+\(\)]+$/,
            message: '电话号码格式不正确'
        }
    },

    // 公司类型选项
    companyTypes: [
        '有限责任公司',
        '股份有限公司',
        '合伙企业',
        '个人独资企业',
        '外商投资企业',
        '其他'
    ],

    // 行业类型选项
    industryTypes: [
        'telecommunications', // 电信
        'technology', // 科技
        'manufacturing', // 制造业
        'construction', // 建筑业
        'finance', // 金融业
        'consulting', // 咨询服务
        'other' // 其他
    ],

    // 默认配置
    defaults: {
        securityLevel: 1,
        pageSize: 20,
        autoSave: true,
        autoSaveInterval: 30000 // 30秒
    }
};

// 导出配置（支持不同的模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CompanyConfig;
} else if (typeof define === 'function' && define.amd) {
    define([], function() { return CompanyConfig; });
} else {
    window.CompanyConfig = CompanyConfig;
}