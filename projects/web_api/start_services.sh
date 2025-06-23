#!/usr/bin/env bash
set -euo pipefail

# 设置环境变量
export PYTHONPATH=/app
export MINERU_MODEL_SOURCE=modelscope

# 检查INSTALL_TYPE环境变量，决定是否启动SGLang server
if [ "${INSTALL_TYPE:-core}" = "all" ]; then
    echo "Starting SGLang server in background..."
    mineru-sglang-server --port 30000 &
    echo "SGLang server started on port 30000"
    
    # 等待SGLang server启动
    echo "Waiting for SGLang server to be ready..."
    sleep 10
    
    # 检查SGLang server是否正常运行
    if curl -f http://localhost:30000/health >/dev/null 2>&1; then
        echo "SGLang server is healthy"
    else
        echo "Warning: SGLang server may not be ready yet"
    fi
fi

# 启动主应用
echo "Starting FastAPI application..."
python3 app.py 