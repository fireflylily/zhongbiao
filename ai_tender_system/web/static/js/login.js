/**
 * 元景AI智能标书生成平台 - 登录页面脚本
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const loginBtn = loginForm.querySelector('.login-btn');

    // 密码显示/隐藏切换
    togglePasswordBtn.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);

        // 切换图标
        const icon = this.querySelector('i');
        if (type === 'password') {
            icon.classList.remove('bi-eye-slash');
            icon.classList.add('bi-eye');
        } else {
            icon.classList.remove('bi-eye');
            icon.classList.add('bi-eye-slash');
        }
    });

    // 表单提交处理
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // 获取输入值
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // 基本验证
        if (!username) {
            showError('请输入用户名');
            usernameInput.focus();
            return;
        }

        if (!password) {
            showError('请输入密码');
            passwordInput.focus();
            return;
        }

        // 隐藏之前的错误信息
        hideError();

        // 显示加载状态
        setLoading(true);

        try {
            // 获取CSRF token
            let csrfToken = '';
            try {
                const tokenResponse = await fetch('/api/csrf-token');
                const tokenData = await tokenResponse.json();
                csrfToken = tokenData.csrf_token;
            } catch (err) {
                console.warn('获取CSRF token失败，尝试继续登录:', err);
            }

            // 发送登录请求
            const headers = {
                'Content-Type': 'application/json',
            };

            // 添加CSRF token（如果获取成功）
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            const response = await fetch('/login', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // 登录成功
                console.log('登录成功:', data.message);

                // 显示成功消息
                showSuccess('登录成功！正在跳转...');

                // 延迟跳转，让用户看到成功消息
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 800);
            } else {
                // 登录失败
                showError(data.message || '登录失败，请重试');
                setLoading(false);
            }
        } catch (error) {
            console.error('登录请求失败:', error);
            showError('网络错误，请检查您的连接');
            setLoading(false);
        }
    });

    // 输入框聚焦时隐藏错误信息
    usernameInput.addEventListener('focus', hideError);
    passwordInput.addEventListener('focus', hideError);

    // 回车键快捷登录
    usernameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            passwordInput.focus();
        }
    });

    passwordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loginForm.dispatchEvent(new Event('submit'));
        }
    });

    // 自动聚焦用户名输入框
    usernameInput.focus();

    /**
     * 显示错误信息
     */
    function showError(message) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';

        // 添加抖动动画
        errorMessage.style.animation = 'none';
        setTimeout(() => {
            errorMessage.style.animation = 'shake 0.5s ease';
        }, 10);
    }

    /**
     * 隐藏错误信息
     */
    function hideError() {
        errorMessage.style.display = 'none';
    }

    /**
     * 显示成功信息
     */
    function showSuccess(message) {
        errorMessage.classList.remove('alert-danger');
        errorMessage.classList.add('alert-success');
        errorMessage.querySelector('i').className = 'bi bi-check-circle-fill me-2';
        errorText.textContent = message;
        errorMessage.style.display = 'block';
    }

    /**
     * 设置加载状态
     */
    function setLoading(isLoading) {
        if (isLoading) {
            loginBtn.classList.add('loading');
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>登录中...';
        } else {
            loginBtn.classList.remove('loading');
            loginBtn.disabled = false;
            loginBtn.innerHTML = '<i class="bi bi-box-arrow-in-right me-2"></i>登录';
        }
    }

    // 添加键盘快捷键提示
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter 快速登录
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            loginForm.dispatchEvent(new Event('submit'));
        }
    });

    // 页面加载完成后的动画效果
    setTimeout(() => {
        document.querySelector('.form-container').style.opacity = '1';
    }, 100);
});
