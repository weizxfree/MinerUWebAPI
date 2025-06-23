# MinerU 2.0 Web API - Mac 部署指南

## Mac 兼容性说明

### 🖥️ **支持的 Mac 类型**
- ✅ **Intel Mac**: 完全支持，CPU 模式运行
- ✅ **Apple Silicon (M1/M2/M3)**: 通过 Rosetta 2 支持，CPU 模式运行
- ❌ **GPU 加速**: Mac 没有 NVIDIA GPU，仅支持 CPU 模式

### 🚀 **推荐部署方式**

#### 方案1: 使用 Mac 专用 Dockerfile（推荐）

```bash
# 构建 Mac 优化版本
docker build -f Dockerfile.mac -t mineru-api-mac .

# 运行（注意：不使用 --gpus 参数）
docker run -p 8888:8888 -v $(pwd)/output:/app/output mineru-api-mac
```

#### 方案2: 修改主 Dockerfile

编辑 `Dockerfile` 第一行：
```dockerfile
FROM ubuntu:22.04
```

然后构建：
```bash
docker build -t mineru-api-cpu .
docker run -p 8888:8888 -v $(pwd)/output:/app/output mineru-api-cpu
```

#### 方案3: 原生 Python 安装（最佳性能）

```bash
# 1. 安装 Python 依赖（注意：zsh 需要用引号包围方括号）
pip install "mineru[core]" fastapi uvicorn python-multipart

# 2. 设置环境变量
export MINERU_DEVICE_MODE=cpu
export MINERU_MODEL_SOURCE=modelscope

# 3. 进入项目目录
cd projects/web_api

# 4. 运行
python app.py
```

## ⚠️ **zsh Shell 注意事项**

Mac 默认使用 zsh shell，在安装带方括号的包时需要特别注意：

```bash
# ❌ 错误（zsh 会报 "no matches found" 错误）
pip install mineru[core]

# ✅ 正确方法1：使用引号
pip install "mineru[core]"

# ✅ 正确方法2：使用转义字符
pip install mineru\[core\]

# ✅ 正确方法3：分别安装
pip install mineru fastapi uvicorn python-multipart
```

## 🔧 **Mac 特殊配置**

### Docker Desktop 设置

1. **启用 Rosetta 2**（Apple Silicon）：
   - Docker Desktop → Settings → General
   - 勾选 "Use Rosetta for x86/amd64 emulation on Apple Silicon"

2. **资源分配**：
   - Memory: 建议 8GB+
   - CPUs: 建议 4 核+

### 环境变量

```bash
# CPU 模式（必需）
export MINERU_DEVICE_MODE=cpu

# 模型源（推荐 ModelScope）
export MINERU_MODEL_SOURCE=modelscope

# 线程数优化
export OMP_NUM_THREADS=4
```

## 📊 **性能对比**

| 部署方式 | 启动速度 | 推理速度 | 内存占用 | 推荐场景 |
|---------|---------|---------|---------|---------|
| Docker (Intel Mac) | 中等 | 中等 | 高 | 开发测试 |
| Docker (Apple Silicon) | 慢 | 慢 | 高 | 兼容性测试 |
| 原生 Python | 快 | 快 | 低 | 生产使用 |

## 🧪 **测试命令**

### Docker 版本测试

```bash
# 启动服务
docker run -p 8888:8888 -v $(pwd)/output:/app/output mineru-api-mac

# 检查服务状态
curl http://localhost:8888/docs

# 测试 pipeline 后端（Mac 唯一支持的后端）
python test_backends.py --file test.pdf --backends pipeline
```

### 原生版本测试

```bash
# 启动服务
python app.py

# 测试 API
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@test.pdf" \
  -F "backend=pipeline" \
  -F "parse_method=auto"
```

## ⚠️ **Mac 限制说明**

### 不支持的功能
- ❌ VLM-Transformers 后端（需要 GPU）
- ❌ VLM-SGLang 后端（需要 GPU）
- ❌ GPU 加速推理

### 仅支持的功能
- ✅ Pipeline 后端（CPU 模式）
- ✅ 基础 OCR 功能
- ✅ 公式和表格解析
- ✅ 多语言支持

## 🔍 **故障排除**

### 1. zsh shell 方括号问题

```bash
# 如果遇到 "no matches found: mineru[core]" 错误
# 解决方案：使用引号
pip install "mineru[core]" fastapi uvicorn python-multipart
```

### 2. Apple Silicon 构建慢

```bash
# 使用 buildx 指定架构
docker buildx build --platform linux/amd64 -f Dockerfile.mac -t mineru-api-mac .
```

### 3. 内存不足

```bash
# 增加 Docker Desktop 内存分配
# Settings → Resources → Memory → 8GB+
```

### 4. 模型下载失败

```bash
# 手动下载模型（原生安装）
python -c "
import os
os.environ['MINERU_MODEL_SOURCE'] = 'modelscope'
from mineru.utils.magic_model import magic_model_downloads
magic_model_downloads()
"
```

### 5. 端口占用

```bash
# 使用不同端口
docker run -p 8889:8888 -v $(pwd)/output:/app/output mineru-api-mac
```

## 📈 **性能优化建议**

### 1. 原生安装（推荐）
- 避免 Docker 虚拟化开销
- 更好的内存管理
- 更快的启动速度

### 2. 环境变量优化
```bash
export OMP_NUM_THREADS=$(sysctl -n hw.logicalcpu)  # 使用所有 CPU 核心
export MKL_NUM_THREADS=$(sysctl -n hw.logicalcpu)
```

### 3. 模型缓存
```bash
# 预下载模型到本地缓存
export MINERU_MODEL_CACHE_DIR=~/.cache/mineru
```

## 🚀 **推荐工作流**

### 开发环境
```bash
# 1. 原生 Python 安装（注意引号）
pip install "mineru[core]" fastapi uvicorn python-multipart

# 2. 设置环境变量
export MINERU_DEVICE_MODE=cpu
export MINERU_MODEL_SOURCE=modelscope

# 3. 进入项目目录
cd projects/web_api

# 4. 启动开发服务器
python app.py

# 5. 测试
curl http://localhost:8888/docs
```

### 部署环境
```bash
# 1. 使用 Docker（隔离性更好）
docker build -f Dockerfile.mac -t mineru-api-mac .

# 2. 启动生产服务
docker run -d --name mineru-api \
  -p 8888:8888 \
  -v $(pwd)/output:/app/output \
  --restart unless-stopped \
  mineru-api-mac
```

## 💡 **一键安装脚本**

创建一个 `install_mac.sh` 脚本：

```bash
#!/bin/bash
echo "🚀 安装 MinerU Web API for Mac..."

# 安装 Python 依赖
pip install "mineru[core]" fastapi uvicorn python-multipart

# 设置环境变量
export MINERU_DEVICE_MODE=cpu
export MINERU_MODEL_SOURCE=modelscope

echo "✅ 安装完成！"
echo "📝 运行命令: python app.py"
echo "🌐 访问地址: http://localhost:8888/docs"
```

使用方法：
```bash
chmod +x install_mac.sh
./install_mac.sh
``` 