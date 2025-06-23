FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置构建参数，用于选择安装类型
ARG INSTALL_TYPE=core
ARG http_proxy
ARG https_proxy

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置pip镜像源
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install --upgrade pip

# 安装uv包管理器
RUN pip3 install uv

# 设置工作目录
WORKDIR /app

# 复制requirements文件
COPY requirements.txt .

# 根据INSTALL_TYPE参数安装不同版本的mineru
RUN if [ "$INSTALL_TYPE" = "all" ]; then \
        echo "Installing mineru[all] for full functionality including sglang..."; \
        sed -i 's/mineru\[.*\]/mineru[all]/' requirements.txt; \
    elif [ "$INSTALL_TYPE" = "core" ]; then \
        echo "Installing mineru[core] for basic functionality..."; \
        sed -i 's/mineru\[.*\]/mineru[core]/' requirements.txt; \
    else \
        echo "Using default requirements.txt..."; \
    fi

# 安装Python依赖
RUN uv pip install --system -r requirements.txt

# 复制应用代码
COPY . .

# 设置启动脚本权限
RUN chmod +x start_services.sh

# 预热模型（下载默认模型）
RUN echo "Pre-downloading models..." && \
    python3 -c "import os; os.environ['MINERU_MODEL_SOURCE'] = 'modelscope'" && \
    if [ "$INSTALL_TYPE" = "all" ]; then \
        echo "Downloading VLM models for sglang-engine backend..." && \
        mineru-models-download -s modelscope -m vlm || echo "VLM model download failed, will download on first use"; \
        mineru-models-download -s modelscope -m pipeline || echo "Pipeline model download failed, will download on first use"; \
    else \
        mineru-models-download -s modelscope -m pipeline || echo "Model download failed, will download on first use"; \
    fi

# 设置环境变量
ENV PYTHONPATH=/app
ENV MINERU_MODEL_SOURCE=modelscope

# 暴露端口
EXPOSE 8888
EXPOSE 30000

# 默认启动命令
CMD ["./start_services.sh"]
