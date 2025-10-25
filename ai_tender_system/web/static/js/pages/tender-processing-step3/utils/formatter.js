/**
 * 格式化工具函数
 * 用于文本展开/收起、HTML转义、约束类型标签等
 *
 * @module Formatter
 */

/**
 * 约束类型配置
 */
const CONSTRAINT_TYPE_CONFIG = {
    badges: {
        'mandatory': 'danger',
        'optional': 'info',
        'scoring': 'success'
    },
    labels: {
        'mandatory': '强制性',
        'optional': '可选',
        'scoring': '加分项'
    }
};

/**
 * 标点符号优先级配置（用于智能截断）
 */
const PUNCTUATION_PRIORITIES = [
    { char: '。', priority: 5 },   // 句号 - 最高优先级
    { char: '；', priority: 4 },   // 中文分号
    { char: ';', priority: 4 },    // 英文分号
    { char: '！', priority: 4 },   // 感叹号
    { char: '？', priority: 4 },   // 问号
    { char: '，', priority: 3 },   // 中文逗号
    { char: ',', priority: 3 },    // 英文逗号
    { char: '、', priority: 2 },   // 顿号
    { char: '）', priority: 2 },   // 右括号
    { char: ')', priority: 2 }     // 英文右括号
];

/**
 * HTML转义
 * @param {string} str - 要转义的字符串
 * @returns {string} 转义后的字符串
 */
export function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * 查找最佳截断点
 * @param {string} text - 原始文本
 * @param {number} maxLength - 最大长度
 * @returns {number} 最佳截断位置，-1表示未找到
 */
function findBestCutPoint(text, maxLength) {
    const shortText = text.substring(0, maxLength);
    let bestCutPoint = -1;
    let bestPriority = 0;

    for (const punct of PUNCTUATION_PRIORITIES) {
        const pos = shortText.lastIndexOf(punct.char);
        // 如果找到标点，且在合理范围内（至少显示50%的内容）
        if (pos > maxLength * 0.5 && punct.priority > bestPriority) {
            bestCutPoint = pos;
            bestPriority = punct.priority;
        }
    }

    return bestCutPoint;
}

/**
 * 格式化detail文本，对于长文本添加展开/收起功能
 * @param {string} text - 要显示的文本
 * @param {number} maxLength - 默认显示的最大长度（默认150字符）
 * @returns {string} 格式化后的HTML
 */
export function formatDetailTextWithToggle(text, maxLength = 150) {
    if (!text) return '';

    const escapedText = escapeHtml(text);

    // 如果文本长度小于等于最大长度，直接返回
    if (text.length <= maxLength) {
        return escapedText;
    }

    // 生成唯一ID
    const uniqueId = 'detail_' + Math.random().toString(36).substr(2, 9);

    // 智能截断：优先在句号、分号等强分隔符处截断
    let shortText = text.substring(0, maxLength);

    // 查找最佳截断点
    const bestCutPoint = findBestCutPoint(text, maxLength);

    // 如果找到了合适的截断点，在标点符号之后截断
    if (bestCutPoint > 0) {
        shortText = text.substring(0, bestCutPoint + 1);
    }

    const escapedShortText = escapeHtml(shortText);

    return `
        <span id="${uniqueId}_short">
            ${escapedShortText}...
            <a href="#" class="text-primary ms-1 small" onclick="window.toggleDetailText('${uniqueId}', event)" style="text-decoration:none;">
                <i class="bi bi-chevron-down"></i> 展开
            </a>
        </span>
        <span id="${uniqueId}_full" style="display:none;">
            ${escapedText}
            <a href="#" class="text-primary ms-1 small" onclick="window.toggleDetailText('${uniqueId}', event)" style="text-decoration:none;">
                <i class="bi bi-chevron-up"></i> 收起
            </a>
        </span>
    `;
}

/**
 * 切换detail文本的展开/收起状态
 * @param {string} id - 元素ID前缀
 * @param {Event} event - 点击事件
 */
export function toggleDetailText(id, event) {
    event.preventDefault();
    const shortEl = document.getElementById(id + '_short');
    const fullEl = document.getElementById(id + '_full');

    if (!shortEl || !fullEl) {
        console.error('[toggleDetailText] 找不到元素:', id);
        return;
    }

    if (shortEl.style.display === 'none') {
        // 收起
        shortEl.style.display = '';
        fullEl.style.display = 'none';
    } else {
        // 展开
        shortEl.style.display = 'none';
        fullEl.style.display = '';
    }
}

/**
 * 获取约束类型的Bootstrap badge类名
 * @param {string} type - 约束类型 ('mandatory', 'optional', 'scoring')
 * @returns {string} Badge类名
 */
export function getConstraintTypeBadge(type) {
    return CONSTRAINT_TYPE_CONFIG.badges[type] || 'secondary';
}

/**
 * 获取约束类型的中文标签
 * @param {string} type - 约束类型 ('mandatory', 'optional', 'scoring')
 * @returns {string} 中文标签
 */
export function getConstraintTypeLabel(type) {
    return CONSTRAINT_TYPE_CONFIG.labels[type] || type;
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小（如 "1.5 MB"）
 */
export function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';

    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${units[i]}`;
}

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期对象或字符串
 * @param {string} format - 格式 ('date', 'time', 'datetime')
 * @returns {string} 格式化后的日期时间
 */
export function formatDateTime(date, format = 'datetime') {
    if (!date) return '';

    const d = typeof date === 'string' ? new Date(date) : date;

    if (isNaN(d.getTime())) {
        return '';
    }

    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');

    switch (format) {
        case 'date':
            return `${year}-${month}-${day}`;
        case 'time':
            return `${hours}:${minutes}:${seconds}`;
        case 'datetime':
        default:
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
}

/**
 * 截断文本
 * @param {string} text - 原始文本
 * @param {number} maxLength - 最大长度
 * @param {string} suffix - 后缀（默认为 '...'）
 * @returns {string} 截断后的文本
 */
export function truncateText(text, maxLength, suffix = '...') {
    if (!text || text.length <= maxLength) {
        return text || '';
    }

    return text.substring(0, maxLength) + suffix;
}

// 向后兼容：挂载到window对象
if (typeof window !== 'undefined') {
    window.toggleDetailText = toggleDetailText;
}
