"""
nano banana API客户端 - 修复版
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
        self.api_key = api_key or os.getenv("GRS_AI_API_KEY", "sk-c15186bd658749e0a4ad09ef6af985d8")
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
                        print(f"   错误信息: {error_data.get('msg', '未知错误')}")
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
        基于故事和选择生成场景图片（带自动重试机制）
        """
        # 生成安全的图片提示词
        image_prompt = self._generate_safe_image_prompt(story_text, choice_text)

        # 第一次尝试
        print(f"   🎨 尝试生成场景图片 (第1次)...")
        result = self.generate_image(image_prompt, output_dir=output_dir)

        # 如果失败，尝试更安全的提示词
        if not result:
            print(f"   ⚠️ 第一次生成失败，尝试更安全的提示词...")
            safe_prompt = self._generate_ultra_safe_prompt()
            print(f"   🎨 尝试生成场景图片 (第2次)...")
            result = self.generate_image(safe_prompt, output_dir=output_dir)

            # 如果还是失败，再尝试通用场景
            if not result:
                print(f"   ⚠️ 第二次生成失败，尝试通用场景...")
                generic_prompt = self._generate_generic_prompt()
                print(f"   🎨 尝试生成场景图片 (第3次)...")
                result = self.generate_image(generic_prompt, output_dir=output_dir)

        return result

    def _generate_safe_image_prompt(self, story_text: str, choice_text: str) -> str:
        """
        生成安全的图片提示词，避免内容审核失败
        """
        # 提取关键视觉元素
        key_visual = ""

        # 场景关键词提取
        if "宫殿" in story_text or "庭院" in story_text or "广场" in story_text:
            key_visual += "古代宫殿建筑，宏伟庄严，"
        if "地宫" in story_text or "通道" in story_text or "密室" in story_text:
            key_visual += "神秘的地下空间，"
        if "宝藏" in story_text or "宝物" in story_text:
            key_visual += "闪闪发光的宝物，"
        if "光芒" in story_text or "光" in story_text:
            key_visual += "神秘的光芒，"
        if "壁画" in story_text or "雕像" in story_text:
            key_visual += "古老的艺术装饰，"

        # 基于选择推断场景
        if "探索" in choice_text or "深入" in choice_text:
            scene_type = "探索场景"
        elif "逃跑" in choice_text or "撤退" in choice_text:
            scene_type = "移动场景"
        elif "寻找" in choice_text:
            scene_type = "寻找场景"
        else:
            scene_type = "互动场景"

        # 构建安全的图片描述
        image_prompt = f"""古代宫殿风格的{scene_type}。

{key_visual}环境氛围神秘而充满冒险感。

要求：
1. 色调温暖，细节丰富
2. 突出场景的神秘感
3. 避免任何暴力或危险内容
4. 构图优美，适合冒险题材

风格：古代宫廷冒险，电影级光影效果"""

        return image_prompt

    def _generate_ultra_safe_prompt(self) -> str:
        """
        生成超级安全的提示词
        """
        return """古代宫殿内部场景，神秘而优雅。

环境：古典建筑风格，温暖的光线，精美的装饰。

要求：
1. 和谐宁静的氛围
2. 细节丰富的建筑元素
3. 色调温暖明亮
4. 构图简洁优美
5. 适合冒险故事

风格：古代宫廷风格，柔和光影效果"""

    def _generate_generic_prompt(self) -> str:
        """
        生成通用场景提示词
        """
        return """古代建筑内部场景。

环境：古典建筑风格，装饰精美。

要求：
1. 色调温暖
2. 构图美观
3. 细节丰富
4. 氛围神秘

风格：古代宫廷冒险风格"""

    def generate_initial_scene_image(
        self,
        image_analysis: str,
        genre: str = "adventure",
        output_dir: str = "images"
    ) -> Optional[str]:
        """
        基于图片分析生成初始场景图片
        """
        image_prompt = f"""基于以下场景分析，生成{genre}风格的场景图片：

{image_analysis}

要求：
1. 体现场景的核心元素和氛围
2. 色彩搭配符合{genre}故事风格
3. 构图突出主要角色或物品
4. 电影级别的视觉呈现
5. 分辨率清晰，细节丰富
6. 为故事开头提供视觉基础

风格：{genre}，高质量渲染"""
        return self.generate_image(image_prompt, output_dir=output_dir)
