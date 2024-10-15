# 第一阶段：构建阶段
FROM python:3.10-slim AS builder

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir cython \
    && pip install --no-cache-dir -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 从构建阶段复制必要的文件
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露 Flask 端口
EXPOSE 5000

# 运行 Flask 应用
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}
