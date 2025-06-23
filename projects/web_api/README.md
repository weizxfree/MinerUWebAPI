# 基于MinerU 2.0的PDF解析API

- MinerU 2.0的GPU镜像构建
- 基于FastAPI的PDF解析接口
- 支持三种解析后端：pipeline、vlm-transformers、vlm-sglang

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

## 构建方式

### 基础版本（支持 pipeline 和 vlm-transformers）
```
docker build -t mineru-api .
```

### 完整版本（支持所有后端，包括 sglang）
```
docker build --build-arg INSTALL_TYPE=all -t mineru-api-full .
```

或者使用代理：
```
docker build --build-arg http_proxy=http://127.0.0.1:7890 --build-arg https_proxy=http://127.0.0.1:7890 --build-arg INSTALL_TYPE=all -t mineru-api-full .
```

## 启动命令

### 基础版本
```
docker run --rm -it --gpus=all -p 8888:8888 mineru-api
```

### 完整版本
```
docker run --rm -it --gpus=all -p 8888:8888 mineru-api-full
```

### SGLang Server 模式
```
docker run --rm -it --gpus=all --shm-size 32g -p 30000:30000 mineru-api-full mineru-sglang-server --host 0.0.0.0 --port 30000
```

## API 使用示例

### 使用 Pipeline 模式（默认）
```bash
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@document.pdf" \
  -F "backend=pipeline" \
  -F "parse_method=auto" \
  -F "lang=ch" \
  -F "formula_enable=true" \
  -F "table_enable=true"
```

### 使用 VLM-Transformers 模式
```bash
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@document.pdf" \
  -F "backend=vlm-transformers"
```

### 使用 VLM-SGLang-Engine 模式
```bash
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@document.pdf" \
  -F "backend=vlm-sglang-engine"
```

### 使用 VLM-SGLang-Client 模式
```bash
# 首先启动 SGLang Server
mineru-sglang-server --port 30000

# 然后使用 Client 模式
curl -X POST "http://localhost:8888/file_parse" \
  -F "file=@document.pdf" \
  -F "backend=vlm-sglang-client" \
  -F "server_url=http://127.0.0.1:30000"
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
- `server_url`: SGLang服务器地址（必需）

## 测试参数

访问地址：
```
http://localhost:8888/docs
http://127.0.0.1:8888/docs
```

## 性能对比

| 后端模式 | 推理速度 | 显存需求 | 解析精度 | 适用场景 |
|---------|---------|---------|---------|---------|
| pipeline | 中等 | 6GB+ | 良好 | 通用场景，资源受限环境 |
| vlm-transformers | 中等 | 8GB+ | 很好 | 追求精度的场景 |
| vlm-sglang-engine | 快 | 24GB+ | 很好 | 高性能单机部署 |
| vlm-sglang-client | 最快 | 客户端无要求 | 很好 | 分布式部署，高并发 |

## 环境要求

### 硬件要求
- **pipeline**: 6GB+ 显存（支持CPU）
- **vlm-transformers**: 8GB+ 显存
- **vlm-sglang**: 24GB+ 显存（或多卡张量并行）

### 软件要求
- Python 3.10-3.13
- CUDA 11.8+ / ROCm / CPU
- Docker（推荐）