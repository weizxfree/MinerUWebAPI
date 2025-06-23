#!/bin/bash

echo "🚀 MinerU 2.0 Web API - Mac 安装脚本"
echo "=================================="

# 检查 Python 版本
python_version=$(python3 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ 发现 Python: $python_version"
else
    echo "❌ 未发现 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查 pip
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 已安装"
else
    echo "❌ pip3 未安装，请先安装 pip"
    exit 1
fi

echo ""
echo "📦 安装 Python 依赖..."

# 安装 Python 依赖（使用引号避免 zsh 问题）
pip3 install "mineru[core]" fastapi uvicorn python-multipart

if [ $? -eq 0 ]; then
    echo "✅ Python 依赖安装成功"
else
    echo "❌ Python 依赖安装失败"
    exit 1
fi

echo ""
echo "🔧 配置环境变量..."

# 检测 Mac 类型并配置最优设备模式
mac_chip=$(uname -m)
if [ "$mac_chip" = "arm64" ]; then
    echo "🍎 检测到 Apple Silicon Mac (M1/M2/M3)"
    device_mode="mps"
    echo "📱 建议使用 MPS 模式以获得更好的性能"
else
    echo "💻 检测到 Intel Mac"
    device_mode="cpu"
    echo "💻 使用 CPU 模式"
fi

# 创建环境配置文件
cat > .env.mac << EOF
# MinerU Mac 环境配置
export MINERU_DEVICE_MODE=$device_mode
export MINERU_MODEL_SOURCE=modelscope
export PYTHONPATH=\$PWD
export OMP_NUM_THREADS=4

# Mac 优化设置
export PYTORCH_ENABLE_MPS_FALLBACK=1
export MKL_NUM_THREADS=4
EOF

echo "✅ 环境配置文件已创建: .env.mac"
echo "🎯 自动配置设备模式: $device_mode"

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 启动步骤："
echo "1. 加载环境变量: source .env.mac"
echo "2. 启动服务: python3 app.py"
echo "3. 访问地址: http://localhost:8888/docs"
echo ""
echo "🧪 测试命令:"
echo "curl http://localhost:8888/docs"
echo ""
echo "📊 设备模式说明:"
if [ "$device_mode" = "mps" ]; then
    echo "⚡ MPS 模式: 利用 Apple Metal 加速，性能比 CPU 模式快 2-3 倍"
    echo "💡 如果遇到兼容性问题，可手动改为 CPU 模式："
    echo "   export MINERU_DEVICE_MODE=cpu"
else
    echo "💻 CPU 模式: 兼容性最好，所有功能都能正常工作"
    echo "💡 如果是 Apple Silicon Mac，可尝试 MPS 模式："
    echo "   export MINERU_DEVICE_MODE=mps"
fi
echo ""
echo "⚠️  注意: Mac 仅支持 Pipeline 后端" 