# 使用Python 3.11官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 设置pip镜像源加速下载
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

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

# 启动命令 - 使用shell形式以支持环境变量
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 4 --timeout 120 main:app"]
