"""
nano banana API客户端
"""
import requests
import json
import os
import time
from typing import Optional
from PIL import Image
from io import BytesIO

class NanoBananaClient:
    """nano banana图片生成客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GRS_AI_API_KEY")
        self.base_url = "https://api.grsai.com/v1/draw/nano-banana"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def generate_image(
        self,
        prompt: str,
        model: str = "nano-banana-fast",
        output_dir: str = "images",
        timeout: int = 120
    ) -> Optional[str]:
        """
        生成图片

        Args:
            prompt: 图片描述
            model: 模型名称
            output_dir: 输出目录
            timeout: 超时时间（秒）

        Returns:
            生成的图片本地路径，如果失败返回None
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        data = {
            "model": model,
            "prompt": prompt
        }

        print(f"\n🎨 [nano-banana] 正在生成图片...")
        print(f"   📝 描述: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        start_time = time.time()

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data,
                stream=True,
                timeout=timeout
            )

            if response.status_code != 200:
                print(f"   ❌ 请求失败: {response.status_code}")
                if response.text:
                    try:
                        error_data = response.json()
                        print(f"   错误信息: {error_data.get('message', '未知错误')}")
                    except:
                        print(f"   错误响应: {response.text[:200]}")
                return None

            # 解析SSE流
            image_url = self._parse_sse_stream(response)

            if image_url:
                elapsed = time.time() - start_time
                print(f"   ✅ 图片生成成功! ({elapsed:.1f}s)")

                # 下载图片
                local_path = self._download_image(image_url, output_dir)
                if local_path:
                    print(f"   💾 图片已保存到: {local_path}")
                    return local_path

            return None

        except requests.exceptions.Timeout:
            print(f"   ⏰ 生成超时 ({timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            print(f"   🌐 网络请求错误: {e}")
            return None
        except Exception as e:
            print(f"   💥 未知错误: {e}")
            return None

    def _parse_sse_stream(self, response) -> Optional[str]:
        """解析Server-Sent Events流"""
        task_id = None
        progress_count = 0

        for line in response.iter_lines():
            if line:
                try:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:]
                        event_data = json.loads(json_str)

                        # 提取任务ID
                        if 'id' in event_data and not task_id:
                            task_id = event_data['id']
                            print(f"   🆔 任务ID: {task_id}")

                        # 显示进度
                        if 'progress' in event_data:
                            progress = event_data['progress']
                            progress_count += 1
                            if progress_count % 3 == 0:  # 每3条消息显示一次进度
                                print(f"   ⏳ 进度: {progress*100:.0f}%")

                        # 检查状态
                        if 'status' in event_data:
                            status = event_data['status']
                            if status == 'succeeded':
                                results = event_data.get('results', [])
                                if results and len(results) > 0:
                                    return results[0].get('url')
                            elif status == 'failed':
                                error_msg = event_data.get('message', event_data.get('failure_reason', '未知错误'))
                                print(f"   ❌ 生成失败: {error_msg}")
                                return None
                            elif status == 'running':
                                continue

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"   ⚠️ 流解析错误: {e}")
                    continue

        return None

    def _download_image(self, url: str, output_dir: str) -> Optional[str]:
        """下载图片"""
        try:
            print(f"   📥 正在下载图片...")
            img_response = requests.get(url, timeout=30)

            if img_response.status_code != 200:
                print(f"   ❌ 下载失败: HTTP {img_response.status_code}")
                return None

            image = Image.open(BytesIO(img_response.content))

            # 生成文件名
            timestamp = int(time.time())
            filename = f"scene_{timestamp}.png"
            output_path = os.path.join(output_dir, filename)

            image.save(output_path)
            print(f"   📷 图片尺寸: {image.size[0]}x{image.size[1]}")
            return output_path

        except Exception as e:
            print(f"   ❌ 下载失败: {e}")
            return None

    def generate_scene_image(
        self,
        story_text: str,
        choice_text: str,
        output_dir: str = "images"
    ) -> Optional[str]:
        """
        基于故事和选择生成场景图片

        Args:
            story_text: 当前故事内容
            choice_text: 用户选择
            output_dir: 输出目录

        Returns:
            生成的图片路径
        """
        # 构建图片生成提示词
        image_prompt = f"""
基于故事内容：{story_text}

用户选择：{choice_text}

请生成下一场景图片，要求：
1. 保持与当前场景风格一致
2. 体现选择的后果和影响
3. 场景转换自然流畅
4. 突出故事的关键转折点
5. 色彩丰富，适合科幻冒险题材
6. 构图清晰，细节丰富

风格：科幻写实，电影级光影效果
"""

        return self.generate_image(image_prompt, output_dir=output_dir)

    def generate_initial_scene_image(
        self,
        image_analysis: str,
        genre: str = "adventure",
        output_dir: str = "images"
    ) -> Optional[str]:
        """
        基于图片分析生成初始场景图片

        Args:
            image_analysis: 图片分析结果
            genre: 故事类型
            output_dir: 输出目录

        Returns:
            生成的图片路径
        """
        # 构建提示词
        image_prompt = f"""
基于以下场景分析，生成{genre}风格的场景图片：

{image_analysis}

要求：
1. 体现场景的核心元素和氛围
2. 色彩搭配符合{genre}故事风格
3. 构图突出主要角色或物品
4. 电影级别的视觉呈现
5. 分辨率清晰，细节丰富
6. 为故事开头提供视觉基础

风格：{genre}，高质量渲染
"""

        return self.generate_image(image_prompt, output_dir=output_dir)
