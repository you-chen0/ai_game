import requests
import json
import os
import time
from PIL import Image
from io import BytesIO

# GrsAI API configuration
API_URL = "https://api.grsai.com/v1/draw/nano-banana"
API_KEY = os.getenv("GRS_AI_API_KEY", "sk-c15186bd658749e0a4ad09ef6af985d8")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Test data
data = {
    "model": "nano-banana-fast",
    "prompt": "A cat wearing a spacesuit drinking coffee on the moon, cinematic style"
}

def parse_sse_stream(response):
    """解析Server-Sent Events流"""
    print("\n开始接收生成进度...")
    task_id = None
    last_progress = 0

    for line in response.iter_lines():
        if line:
            # 解码行
            decoded_line = line.decode('utf-8')
            print(f"[SSE] {decoded_line}")

            # 解析JSON数据
            if decoded_line.startswith('data: '):
                try:
                    json_str = decoded_line[6:]  # 去掉 'data: ' 前缀
                    event_data = json.loads(json_str)

                    # 提取任务ID
                    if 'id' in event_data and not task_id:
                        task_id = event_data['id']
                        print(f"\n✓ 任务已创建，ID: {task_id}")

                    # 检查进度
                    if 'progress' in event_data:
                        progress = event_data['progress']
                        if progress != last_progress:
                            print(f"进度更新: {progress*100:.0f}%")
                            last_progress = progress

                    # 检查状态
                    if 'status' in event_data:
                        status = event_data['status']
                        if status == 'running':
                            print("图片生成中...")
                        elif status == 'succeeded':
                            print("\n✓ 生成完成!")
                            if 'results' in event_data and event_data['results']:
                                image_url = event_data['results'][0].get('url')
                                if image_url:
                                    return image_url
                        elif status == 'failed':
                            error_msg = event_data.get('message', '未知错误')
                            print(f"\n✗ 生成失败: {error_msg}")
                            return None

                except json.JSONDecodeError:
                    continue

    print("\n⚠ 流结束但未收到完成状态")
    return None

def test_nano_banana():
    """Test nano banana API call"""
    print("Calling nano banana API...")
    print(f"Prompt: {data['prompt']}")
    print(f"Model: {data['model']}")

    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=True, timeout=60)

        print(f"\nStatus code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")

        if response.status_code == 200:
            # 处理SSE流
            image_url = parse_sse_stream(response)

            if image_url:
                print(f"\n✓ 获取到图片URL: {image_url}")

                # 下载图片
                print("\n正在下载图片...")
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    # 保存图片
                    image = Image.open(BytesIO(img_response.content))
                    output_path = "generated_image.png"
                    image.save(output_path)
                    print(f"✓ 图片已保存到: {output_path}")
                    print(f"  格式: {image.format}, 尺寸: {image.size}")
                    return output_path
                else:
                    print(f"✗ 下载图片失败: {img_response.status_code}")
                    return None
            else:
                print("\n✗ 未能获取图片URL")
                return None

        else:
            print(f"\n✗ 请求失败: {response.status_code}")
            print(f"Error response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("\n⚠ 请求超时 - 图片生成可能需要更长时间")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n✗ 网络请求错误: {e}")
        return None
    except Exception as e:
        print(f"\n✗ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Set API key from environment variable if available
    API_KEY = os.getenv("GRS_AI_API_KEY", API_KEY)

    # Run test
    start_time = time.time()
    image_path = test_nano_banana()
    elapsed_time = time.time() - start_time

    if image_path:
        print(f"\n{'='*50}")
        print(f"✓ 测试成功! 总耗时: {elapsed_time:.2f}秒")
        print(f"图片位置: {image_path}")
        print(f"{'='*50}")
    else:
        print(f"\n{'='*50}")
        print(f"✗ 测试失败，总耗时: {elapsed_time:.2f}秒")
        print(f"{'='*50}")
