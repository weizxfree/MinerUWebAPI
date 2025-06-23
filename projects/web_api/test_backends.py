#!/usr/bin/env python3
"""
测试脚本：验证 MinerU 2.0 Web API 的所有后端模式

使用方法:
python test_backends.py --file /path/to/test.pdf --base-url http://localhost:8888
"""

import argparse
import json
import requests
import time
from pathlib import Path


def test_backend(base_url: str, file_path: str, backend: str, server_url: str = None):
    """测试指定后端"""
    print(f"\n{'='*50}")
    print(f"测试后端: {backend}")
    print(f"{'='*50}")
    
    # 准备请求数据
    files = {'file': open(file_path, 'rb')}
    data = {
        'backend': backend,
        'return_content_list': True,
        'return_info': False,  # 减少返回数据量
        'return_layout': False,
        'return_images': False
    }
    
    # 为 vlm-sglang-client 添加 server_url
    if backend == 'vlm-sglang-client':
        if not server_url:
            print(f"⚠️  跳过 {backend}：需要 server_url 参数")
            files['file'].close()
            return None
        data['server_url'] = server_url
    
    # 为 pipeline 模式添加特定参数
    if backend == 'pipeline':
        data.update({
            'parse_method': 'auto',
            'lang': 'ch',
            'formula_enable': True,
            'table_enable': True
        })
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/file_parse",
            files=files,
            data=data,
            timeout=300  # 5分钟超时
        )
        end_time = time.time()
        
        files['file'].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {backend} 测试成功")
            print(f"   耗时: {end_time - start_time:.2f} 秒")
            print(f"   返回数据大小: {len(json.dumps(result))} 字符")
            if 'md_content' in result:
                print(f"   Markdown 长度: {len(result['md_content'])} 字符")
            if 'content_list' in result:
                print(f"   内容列表项数: {len(result.get('content_list', []))} 项")
            print(f"   使用后端: {result.get('backend', 'unknown')}")
            return result
        else:
            print(f"❌ {backend} 测试失败")
            print(f"   状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏰ {backend} 测试超时（5分钟）")
        files['file'].close()
        return None
    except Exception as e:
        print(f"❌ {backend} 测试出错: {str(e)}")
        files['file'].close()
        return None


def main():
    parser = argparse.ArgumentParser(description='测试 MinerU 2.0 Web API 的所有后端模式')
    parser.add_argument('--file', '-f', required=True, help='测试用的PDF文件路径')
    parser.add_argument('--base-url', '-u', default='http://localhost:8888', help='API服务器地址')
    parser.add_argument('--sglang-server', '-s', help='SGLang服务器地址（用于测试 vlm-sglang-client）')
    parser.add_argument('--backends', '-b', nargs='+', 
                       choices=['pipeline', 'vlm-transformers', 'vlm-sglang-engine', 'vlm-sglang-client'],
                       default=['pipeline', 'vlm-transformers', 'vlm-sglang-engine', 'vlm-sglang-client'],
                       help='要测试的后端列表')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not Path(args.file).exists():
        print(f"❌ 文件不存在: {args.file}")
        return
    
    # 检查API服务器是否可访问
    try:
        response = requests.get(f"{args.base_url}/docs", timeout=10)
        if response.status_code == 200:
            print(f"✅ API服务器可访问: {args.base_url}")
        else:
            print(f"⚠️  API服务器响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法访问API服务器: {args.base_url}")
        print(f"   错误: {str(e)}")
        return
    
    print(f"\n开始测试文件: {args.file}")
    print(f"文件大小: {Path(args.file).stat().st_size / 1024 / 1024:.2f} MB")
    
    # 测试结果
    results = {}
    
    # 测试各个后端
    for backend in args.backends:
        result = test_backend(args.base_url, args.file, backend, args.sglang_server)
        results[backend] = result
    
    # 输出测试总结
    print(f"\n{'='*50}")
    print("测试总结")
    print(f"{'='*50}")
    
    successful_backends = [k for k, v in results.items() if v is not None]
    failed_backends = [k for k, v in results.items() if v is None]
    
    print(f"✅ 成功的后端 ({len(successful_backends)}): {', '.join(successful_backends)}")
    if failed_backends:
        print(f"❌ 失败的后端 ({len(failed_backends)}): {', '.join(failed_backends)}")
    
    print(f"\n总体成功率: {len(successful_backends)}/{len(args.backends)} = {len(successful_backends)/len(args.backends)*100:.1f}%")


if __name__ == '__main__':
    main() 