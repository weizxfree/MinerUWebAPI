# 基于MinerU 2.0的PDF解析API

- MinerU 2.0的GPU镜像构建
- 基于FastAPI的PDF解析接口
- 支持三种解析后端：pipeline、vlm-transformers、vlm-sglang
- **新增**：智能服务启动，自动管理SGLang server

## 支持的后端模式

### 1. Pipeline 模式 (默认)
- 更通用，兼容性最好
- 支持CPU和GPU推理
- 支持公式、表格解析开关
- 支持多语言OCR
- 最低6GB显存要求

### 2. VLM-Transformers 模式
- 基于 Hugging Face Transformers
- 更高的解析精度
- 需要8GB以上显存
- 支持GPU推理

### 3. VLM-SGLang 模式
- 最快的推理速度
- 支持 engine 和 client 两种部署方式
- 需要24GB以上显存或张量并行
- 峰值吞吐量超过10,000 token/s
- **新增**：完整版Docker自动启动SGLang server

## 构建方式

### 基础版本（支持 pipeline 和 vlm-transformers）
```bash
docker build --build-arg INSTALL_TYPE=core -t mineru-api .
```

### 完整版本（支持所有后端，包括 sglang，**推荐**）
```bash
docker build --build-arg INSTALL_TYPE=all -t mineru-api-full .
```

或者使用代理：
```bash
docker build --build-arg http_proxy=http://127.0.0.1:7890 \
              --build-arg https_proxy=http://127.0.0.1:7890 \
              --build-arg INSTALL_TYPE=all \
              -t mineru-api-full .
```

## 启动命令

### 基础版本（仅支持 pipeline 和 vlm-transformers）
```bash
docker run --rm -it --gpus=all -p 8888:8888 mineru-api
```

### 完整版本（**推荐**，自动启动所有服务）
```bash
# 标准启动（自动启动FastAPI + SGLang server）
docker run --rm -it --gpus=all \
           --memory=8g --shm-size=4g \
           -p 8888:8888 -p 30000:30000 \
           mineru-api-full
```

### 高性能部署（适合生产环境）
```bash
docker run --rm -d --gpus=all \
           --memory=16g --shm-size=8g \
           -p 8888:8888 -p 30000:30000 \
           --name mineru-api \
           mineru-api-full
```

### 仅启动 SGLang Server（独立部署）
```bash
docker run --rm -it --gpus=all \
           --shm-size=8g -p 30000:30000 \
           mineru-api-full \
           mineru-sglang-server --host 0.0.0.0 --port 30000
```

## API 使用示例

### 使用 Pipeline 模式（默认，适合大多数场景）
```bash
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@document.pdf" \
  -F "backend=pipeline" \
  -F "parse_method=auto" \
  -F "lang=ch" \
  -F "formula_enable=true" \
  -F "table_enable=true"
```

### 使用 VLM-Transformers 模式（高精度）
```bash
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@document.pdf" \
  -F "backend=vlm-transformers"
```

### 使用 VLM-SGLang-Engine 模式（**推荐完整版Docker**）
```bash
# 使用完整版Docker时，SGLang engine直接可用
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@document.pdf" \
  -F "backend=vlm-sglang-engine"
```

### 使用 VLM-SGLang-Client 模式（连接独立SGLang server）
```bash
# 完整版Docker自动启动了SGLang server在30000端口
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@document.pdf" \
  -F "backend=vlm-sglang-client" \
  -F "server_url=http://localhost:30000"
```

## 服务管理

### 完整版Docker服务状态

启动完整版Docker后，容器内会自动运行：

1. **FastAPI 服务**（端口8888）
   - 主要的PDF解析API
   - 支持所有后端模式

2. **SGLang Server**（端口30000，仅在INSTALL_TYPE=all时）
   - 自动后台启动
   - 支持 vlm-sglang-client 和 vlm-sglang-engine
   - 预加载VLM模型

### 服务健康检查
```bash
# 检查FastAPI服务
curl http://localhost:8888/docs

# 检查SGLang服务（仅完整版）
curl http://localhost:30000/health
```

### 日志查看
```bash
# 查看容器日志
docker logs <container_id>

# 实时查看日志
docker logs -f <container_id>
```

## 参数说明

### 通用参数
- `file` 或 `file_path`: 要解析的PDF文件
- `backend`: 解析后端 (`pipeline`, `vlm-transformers`, `vlm-sglang-engine`, `vlm-sglang-client`)
- `output_dir`: 输出目录
- `is_json_md_dump`: 是否保存解析结果到文件
- `return_layout`: 是否返回布局信息
- `return_info`: 是否返回详细信息
- `return_content_list`: 是否返回内容列表
- `return_images`: 是否返回图片（base64格式）

### Pipeline 模式专用参数
- `parse_method`: 解析方法 (`auto`, `txt`, `ocr`)
- `lang`: 文档语言（提升OCR准确率）
- `formula_enable`: 是否启用公式解析
- `table_enable`: 是否启用表格解析

### VLM-SGLang-Client 模式专用参数
- `server_url`: SGLang服务器地址（完整版Docker默认为 http://localhost:30000）

## 测试参数

访问地址：
```
http://localhost:8888/docs
http://127.0.0.1:8888/docs
```

## 性能对比

| 后端模式 | 推理速度 | 显存需求 | 解析精度 | Docker版本 | 适用场景 |
|---------|---------|---------|---------|-----------|---------|
| pipeline | 中等 | 6GB+ | 良好 | 基础版/完整版 | 通用场景，资源受限环境 |
| vlm-transformers | 中等 | 8GB+ | 很好 | 基础版/完整版 | 追求精度的场景 |
| vlm-sglang-engine | 快 | 24GB+ | 很好 | 完整版 | 高性能单机部署 |
| vlm-sglang-client | 最快 | 客户端无要求 | 很好 | 完整版 | 分布式部署，高并发 |

## 版本选择指南

### 基础版 (INSTALL_TYPE=core)
- **适用场景**: 仅需要 pipeline 和 vlm-transformers
- **资源要求**: 8GB+ 显存
- **镜像大小**: 较小
- **启动时间**: 快

### 完整版 (INSTALL_TYPE=all) **推荐**
- **适用场景**: 需要最佳性能和完整功能
- **资源要求**: 24GB+ 显存（SGLang）
- **镜像大小**: 较大（包含VLM模型）
- **启动时间**: 较慢（模型预加载）
- **自动服务**: FastAPI + SGLang server

## 环境要求

### 硬件要求
- **基础版**: 8GB+ 显存
- **完整版**: 24GB+ 显存（推荐）或多卡张量并行
- **内存**: 推荐16GB+ 系统内存

### 软件要求
- Python 3.10-3.13
- CUDA 11.8+ / ROCm / CPU
- Docker（推荐）

### Docker资源配置
```bash
# 推荐的Docker资源设置
--memory=16g        # 系统内存
--shm-size=8g      # 共享内存（重要）
--gpus=all         # GPU访问
```