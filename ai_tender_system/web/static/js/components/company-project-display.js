/**
 * 公司项目信息展示组件 - 共用工具函数
 * 用于统一管理公司和项目信息的显示
 */

/**
 * 更新公司项目信息显示
 * @param {Object|null} companyData - 公司数据对象
 * @param {string} companyData.company_name - 公司名称
 * @param {string} companyData.project_name - 项目名称（可选）
 */
function updateCompanyProjectDisplay(companyData) {
    // 使用class选择器获取所有显示元素
    const companyNameDisplays = document.querySelectorAll('.companyNameDisplay');
    const projectNameDisplays = document.querySelectorAll('.projectNameDisplay');

    // 更新所有公司名称显示
    companyNameDisplays.forEach(function(element) {
        element.textContent = companyData && companyData.company_name ? companyData.company_name : '未选择';
    });

    // 更新所有项目名称显示
    projectNameDisplays.forEach(function(element) {
        element.textContent = companyData && companyData.project_name ? companyData.project_name : '未填写';
    });

    console.log('公司项目信息已更新 (所有section):', companyData);
}

/**
 * 初始化公司项目信息显示
 * 从全局状态管理器加载并显示信息，同时监听状态变更
 */
function initCompanyProjectDisplay() {
    console.log('初始化公司项目信息显示组件...');

    if (!window.globalState) {
        console.error('全局状态管理器未初始化');
        return;
    }

    // 加载当前保存的信息
    const company = window.globalState.getCompany();
    const project = window.globalState.getProject();
    const companyData = {
        company_id: company?.id,
        company_name: company?.name,
        project_id: project?.id,
        project_name: project?.name,
        project_number: project?.number
    };
    updateCompanyProjectDisplay(companyData);

    // 监听全局状态变更
    window.globalState.subscribe('company', function(companyData) {
        console.log('接收到公司状态变更，更新显示:', companyData);
        const project = window.globalState.getProject();
        const data = {
            company_id: companyData?.id,
            company_name: companyData?.name,
            project_id: project?.id,
            project_name: project?.name,
            project_number: project?.number
        };
        updateCompanyProjectDisplay(data);
    });
    window.globalState.subscribe('project', function(projectData) {
        console.log('接收到项目状态变更，更新显示:', projectData);
        const company = window.globalState.getCompany();
        const data = {
            company_id: company?.id,
            company_name: company?.name,
            project_id: projectData?.id,
            project_name: projectData?.name,
            project_number: projectData?.number
        };
        updateCompanyProjectDisplay(data);
    });

    console.log('公司项目信息显示组件初始化完成');
}

// 页面加载时自动初始化
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化，确保状态管理器已加载
    setTimeout(initCompanyProjectDisplay, 100);
});