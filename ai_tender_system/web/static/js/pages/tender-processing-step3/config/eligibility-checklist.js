/**
 * 18条供应商资格要求清单配置
 * 用于标书资格要求的智能匹配和检查
 *
 * @module EligibilityChecklist
 */

/**
 * 18条标准资格清单
 * 每条包含ID、名称、关键词、类别和优先级
 */
export const ELIGIBILITY_CHECKLIST = [
    {
        id: 1,
        name: "营业执照信息",
        keywords: ["营业执照", "注册", "法人", "注册资金", "注册资本", "注册时间", "成立时间"],
        category: "基本资质",
        priority: "high",
        description: "企业营业执照及基本工商信息"
    },
    {
        id: 2,
        name: "财务要求",
        keywords: ["审计报告", "财务报表", "财务", "财务会计制度"],
        category: "财务资质",
        priority: "high",
        description: "企业财务状况证明材料"
    },
    {
        id: 3,
        name: "依法纳税",
        keywords: ["增值税", "纳税", "税收", "税务"],
        category: "财务资质",
        priority: "high",
        description: "纳税证明及税务合规性材料"
    },
    {
        id: 4,
        name: "缴纳社保",
        keywords: ["社保", "社会保险", "缴费人数", "缴纳人数"],
        category: "财务资质",
        priority: "medium",
        description: "社会保险缴纳证明"
    },
    {
        id: 5,
        name: "失信被执行人",
        keywords: ["失信被执行人", "失信名单"],
        category: "信用资质",
        priority: "high",
        description: "失信被执行人查询结果"
    },
    {
        id: 6,
        name: "政府采购严重违法失信记录",
        keywords: ["信用中国", "严重违法失信", "违法失信", "政府采购违法", "政府采购失信", "记录名单", "失信行为"],
        category: "信用资质",
        priority: "high",
        description: "政府采购违法失信记录查询"
    },
    {
        id: 7,
        name: "信用中国：重大税收违法",
        keywords: ["重大税收违法", "税收违法失信"],
        category: "信用资质",
        priority: "high",
        description: "重大税收违法案件查询"
    },
    {
        id: 8,
        name: "采购人黑名单",
        keywords: ["黑名单", "采购人"],
        category: "信用资质",
        priority: "medium",
        description: "采购人自定义黑名单查询"
    },
    {
        id: 9,
        name: "承诺函",
        keywords: ["承诺函", "承诺书"],
        category: "基本资质",
        priority: "medium",
        description: "投标承诺函或声明"
    },
    {
        id: 10,
        name: "营业办公场所房产证明",
        keywords: ["房产", "办公场所", "经营场所", "房产证明"],
        category: "基本资质",
        priority: "low",
        description: "办公场所产权或租赁证明"
    },
    {
        id: 11,
        name: "业绩案例要求",
        keywords: ["业绩", "类似项目", "同类项目", "项目经验"],
        category: "业绩资质",
        priority: "high",
        description: "过往类似项目业绩证明"
    },
    {
        id: 12,
        name: "保证金要求",
        keywords: ["保证金", "投标保证金"],
        category: "财务资质",
        priority: "high",
        description: "投标保证金缴纳证明"
    },
    {
        id: 13,
        name: "增值电信业务许可证",
        keywords: ["增值电信业务许可证", "ICP许可证", "IDC许可证", "ISP许可证", "CDN许可证", "增值电信"],
        category: "行业资质",
        priority: "medium",
        description: "增值电信业务经营许可证"
    },
    {
        id: 14,
        name: "基础电信业务许可证",
        keywords: ["基础电信业务许可证", "电信业务经营许可证", "基础电信"],
        category: "行业资质",
        priority: "medium",
        description: "基础电信业务经营许可证"
    },
    {
        id: 15,
        name: "ISO9001质量管理体系认证",
        keywords: ["ISO9001", "ISO 9001", "质量管理体系", "质量认证", "GB/T19001", "质量体系认证"],
        category: "行业资质",
        priority: "medium",
        description: "ISO9001质量管理体系认证证书"
    },
    {
        id: 16,
        name: "ISO20000信息技术服务管理体系认证",
        keywords: ["ISO20000", "ISO 20000", "信息技术服务管理", "IT服务管理", "ISO/IEC 20000", "信息技术服务"],
        category: "行业资质",
        priority: "low",
        description: "ISO20000信息技术服务管理体系认证证书"
    },
    {
        id: 17,
        name: "ISO27001信息安全管理体系认证",
        keywords: ["ISO27001", "ISO 27001", "信息安全管理", "信息安全认证", "ISO/IEC 27001", "信息安全体系"],
        category: "行业资质",
        priority: "low",
        description: "ISO27001信息安全管理体系认证证书"
    },
    {
        id: 18,
        name: "等保三级认证",
        keywords: ["等保三级", "等级保护三级", "信息安全等级保护", "等保", "三级等保", "等级保护备案"],
        category: "行业资质",
        priority: "medium",
        description: "信息安全等级保护三级备案证明"
    }
];

/**
 * 资格类别配置
 */
export const QUALIFICATION_CATEGORIES = {
    '基本资质': {
        label: '基本资质',
        color: '#007bff',
        icon: 'bi-building',
        description: '企业基本工商、经营资质'
    },
    '财务资质': {
        label: '财务资质',
        color: '#28a745',
        icon: 'bi-cash-stack',
        description: '财务状况、纳税、社保等证明'
    },
    '信用资质': {
        label: '信用资质',
        color: '#17a2b8',
        icon: 'bi-shield-check',
        description: '信用记录、失信查询等'
    },
    '业绩资质': {
        label: '业绩资质',
        color: '#ffc107',
        icon: 'bi-trophy',
        description: '过往项目业绩证明'
    },
    '行业资质': {
        label: '行业资质',
        color: '#6f42c1',
        icon: 'bi-award',
        description: '行业许可证、认证证书等'
    }
};

/**
 * 优先级配置
 */
export const PRIORITY_LEVELS = {
    high: {
        label: '高',
        value: 3,
        color: '#dc3545',
        icon: 'bi-exclamation-circle-fill'
    },
    medium: {
        label: '中',
        value: 2,
        color: '#ffc107',
        icon: 'bi-info-circle-fill'
    },
    low: {
        label: '低',
        value: 1,
        color: '#6c757d',
        icon: 'bi-dash-circle-fill'
    }
};

/**
 * 资格匹配配置
 */
export const QUALIFICATION_MATCH_CONFIG = {
    // 最少匹配关键词数
    minKeywordMatches: 1,

    // 模糊匹配阈值（0-1）
    fuzzyMatchThreshold: 0.8,

    // 类别权重
    categoryWeights: {
        '基本资质': 1.0,
        '财务资质': 0.95,
        '信用资质': 0.95,
        '业绩资质': 0.9,
        '行业资质': 0.85
    },

    // 优先级权重
    priorityWeights: {
        high: 1.0,
        medium: 0.8,
        low: 0.6
    }
};

/**
 * 根据关键词匹配资格清单项
 * @param {string} text - 要匹配的文本
 * @returns {Array} 匹配的资格清单项
 */
export function matchEligibilityItems(text) {
    if (!text) return [];

    const lowerText = text.toLowerCase();
    const matches = [];

    for (const item of ELIGIBILITY_CHECKLIST) {
        let matchCount = 0;
        const matchedKeywords = [];

        for (const keyword of item.keywords) {
            if (lowerText.includes(keyword.toLowerCase())) {
                matchCount++;
                matchedKeywords.push(keyword);
            }
        }

        if (matchCount >= QUALIFICATION_MATCH_CONFIG.minKeywordMatches) {
            matches.push({
                ...item,
                matchCount,
                matchedKeywords,
                score: calculateMatchScore(matchCount, item)
            });
        }
    }

    // 按匹配分数降序排序
    return matches.sort((a, b) => b.score - a.score);
}

/**
 * 计算匹配分数
 * @param {number} matchCount - 匹配的关键词数量
 * @param {Object} item - 资格清单项
 * @returns {number} 匹配分数
 */
function calculateMatchScore(matchCount, item) {
    const categoryWeight = QUALIFICATION_MATCH_CONFIG.categoryWeights[item.category] || 0.5;
    const priorityWeight = QUALIFICATION_MATCH_CONFIG.priorityWeights[item.priority] || 0.5;

    // 分数 = 匹配关键词数 * 类别权重 * 优先级权重
    return matchCount * categoryWeight * priorityWeight;
}

/**
 * 根据ID获取资格清单项
 * @param {number} id - 资格ID
 * @returns {Object|null} 资格清单项
 */
export function getEligibilityItemById(id) {
    return ELIGIBILITY_CHECKLIST.find(item => item.id === id) || null;
}

/**
 * 根据类别获取资格清单项
 * @param {string} category - 类别名称
 * @returns {Array} 该类别的所有资格清单项
 */
export function getEligibilityItemsByCategory(category) {
    return ELIGIBILITY_CHECKLIST.filter(item => item.category === category);
}

/**
 * 获取所有类别
 * @returns {Array} 类别列表
 */
export function getAllCategories() {
    return Object.keys(QUALIFICATION_CATEGORIES);
}

/**
 * 获取所有优先级
 * @returns {Array} 优先级列表
 */
export function getAllPriorities() {
    return Object.keys(PRIORITY_LEVELS);
}
