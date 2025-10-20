# 使用Python 3.11官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件(优先使用生产环境依赖)
COPY requirements-prod.txt requirements.txt* ./

# 安装Python依赖(优先使用requirements-prod.txt)
RUN if [ -f requirements-prod.txt ]; then \
        pip install --no-cache-dir -r requirements-prod.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# 复制应用代码
COPY . .

# 暴露端口(Railway会动态设置)
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8080}/api/health').read()" || exit 1

# 启动命令 - 使用shell形式以支持环境变量
# 减少workers到2以加快启动,增加worker超时
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 300 --worker-class sync --preload main:app"]
