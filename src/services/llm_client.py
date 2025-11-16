"""
LLM客户端 - 用于故事生成
"""
import requests
import json
import os
from typing import Optional, Dict, Any
from src.types.story import ImageAnalysisResult, StoryGenre, ChoiceType, Choice

class LLMClient:
    """LLM API客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GRS_AI_API_KEY")
        self.base_url = "https://api.grsai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def analyze_image(
        self,
        image_url: str,
        max_retries: int = 2
    ) -> Optional[ImageAnalysisResult]:
        """
        分析图片内容

        Args:
            image_url: 图片URL
            max_retries: 最大重试次数

        Returns:
            图片分析结果
        """
        prompt = """
你是一个专业的图片内容分析专家。请仔细分析这张图片，并提取以下信息：

1. **场景描述**: 详细描述图片中的环境、背景、氛围
2. **角色分析**: 识别图片中的角色（如果有），包括外观、表情、动作
3. **关键物品**: 列出图片中的重要物品或道具
4. **色彩与风格**: 描述图片的色调、风格（科幻、奇幻、写实等）
5. **故事元素**: 基于图片内容，推测可能的故事背景或情节
6. **情感氛围**: 图片传达的情感或情绪
7. **故事类型建议**: 基于内容推荐适合的故事类型

请以JSON格式返回分析结果：
```json
{
  "scene_description": "场景详细描述",
  "characters": [
    {"name": "角色名", "description": "外观和动作描述", "emotion": "情绪状态"}
  ],
  "key_objects": ["物品1", "物品2", "物品3"],
  "color_style": {"dominant_colors": ["颜色1", "颜色2"], "style": "风格描述"},
  "story_elements": "可能的故事背景和情节推测",
  "emotional_tone": "情感氛围描述",
  "genre_suggestion": "建议的故事类型"
}
```
"""

        data = {
            "model": "gemini-2.5-flash-lite",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        for attempt in range(max_retries):
            try:
                print(f"\n🔍 [LLM] 分析图片中... (尝试 {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        content = result['choices'][0].get('message', {}).get('content', '')
                        return self._parse_analysis_result(content)

                print(f"   ⚠️ 请求失败: {response.status_code}")
                if attempt < max_retries - 1:
                    print(f"   ⏳ 等待2秒后重试...")
                    import time
                    time.sleep(2)

            except Exception as e:
                print(f"   ❌ 错误: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)

        print(f"   ❌ 分析失败，已重试 {max_retries} 次")
        return None

    def generate_initial_story(
        self,
        image_analysis: ImageAnalysisResult,
        genre: StoryGenre,
        max_retries: int = 2
    ) -> Optional[tuple[str, list[Choice]]]:
        """
        生成初始故事

        Args:
            image_analysis: 图片分析结果
            genre: 故事类型
            max_retries: 最大重试次数

        Returns:
            (故事文本, 选择列表) 或 None
        """
        prompt = f"""
请基于以下图片分析结果，创作一个{genre.value}风格的故事开头：

场景描述：{image_analysis.scene_description}

角色：{', '.join([c.get('name', '') + ':' + c.get('description', '') for c in image_analysis.characters])}

关键物品：{', '.join(image_analysis.key_objects)}

风格：{image_analysis.color_style.get('style', '')}

故事背景：{image_analysis.story_elements}

情感氛围：{image_analysis.emotional_tone}

要求：
1. 故事类型：{genre.value}
2. 字数：200-300字
3. 包含环境描写、角色介绍、情节铺垫
4. 营造{genre.value}氛围
5. 引出3个选择

请以JSON格式返回：
```json
{{
  "story": "故事内容",
  "choices": [
    {{"id": "1", "text": "行动选择", "type": "action"}},
    {{"id": "2", "text": "对话选择", "type": "dialogue"}},
    {{"id": "3", "text": "物品选择", "type": "item"}}
  ]
}}
```
"""

        data = {
            "model": "gemini-2.5-flash-lite",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 1500
        }

        for attempt in range(max_retries):
            try:
                print(f"\n📖 [LLM] 生成初始故事中... (尝试 {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        content = result['choices'][0].get('message', {}).get('content', '')
                        parsed = self._parse_story_generation_result(content)
                        if parsed:
                            print(f"   ✅ 故事生成成功")
                            return parsed

                print(f"   ⚠️ 生成失败: {response.status_code}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)

            except Exception as e:
                print(f"   ❌ 错误: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)

        print(f"   ❌ 故事生成失败，已重试 {max_retries} 次")
        return None

    def continue_story(
        self,
        story_text: str,
        last_choice: str,
        choice_type: ChoiceType,
        max_retries: int = 2
    ) -> Optional[tuple[str, list[Choice]]]:
        """
        继续故事

        Args:
            story_text: 当前故事文本
            last_choice: 用户选择
            choice_type: 选择类型
            max_retries: 最大重试次数

        Returns:
            (故事文本, 选择列表) 或 None
        """
        prompt = f"""
当前故事：{story_text}

用户选择：{last_choice} (类型: {choice_type.value})

请继续故事并生成3个新选择，要求：
1. 符合故事逻辑发展
2. 字数控制在150-200字
3. 多样化选择类型
4. 增加故事悬念
5. 选择后果要明显不同

请以JSON格式返回：
```json
{{
  "story": "故事内容",
  "choices": [
    {{"id": "1", "text": "行动选择", "type": "action"}},
    {{"id": "2", "text": "对话选择", "type": "dialogue"}},
    {{"id": "3", "text": "物品选择", "type": "item"}}
  ]
}}
```
"""

        data = {
            "model": "gemini-2.5-flash-lite",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 1200
        }

        for attempt in range(max_retries):
            try:
                print(f"\n📝 [LLM] 继续故事中... (尝试 {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        content = result['choices'][0].get('message', {}).get('content', '')
                        parsed = self._parse_story_generation_result(content)
                        if parsed:
                            print(f"   ✅ 故事继续成功")
                            return parsed

                print(f"   ⚠️ 生成失败: {response.status_code}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)

            except Exception as e:
                print(f"   ❌ 错误: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)

        print(f"   ❌ 故事继续失败，已重试 {max_retries} 次")
        return None

    def _parse_analysis_result(self, content: str) -> Optional[ImageAnalysisResult]:
        """解析图片分析结果"""
        try:
            # 移除markdown代码块
            if content.startswith('```'):
                lines = content.split('\n')
                json_lines = [line for line in lines if not line.startswith('```')]
                content = '\n'.join(json_lines)

            data = json.loads(content)

            return ImageAnalysisResult(
                scene_description=data.get('scene_description', ''),
                characters=data.get('characters', []),
                key_objects=data.get('key_objects', []),
                color_style=data.get('color_style', {}),
                story_elements=data.get('story_elements', ''),
                emotional_tone=data.get('emotional_tone', ''),
                genre_suggestion=data.get('genre_suggestion', '')
            )
        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON解析错误: {e}")
            return None
        except Exception as e:
            print(f"   ⚠️ 解析错误: {e}")
            return None

    def _parse_story_generation_result(self, content: str) -> Optional[tuple[str, list[Choice]]]:
        """解析故事生成结果"""
        try:
            # 移除markdown代码块
            if content.startswith('```'):
                lines = content.split('\n')
                json_lines = [line for line in lines if not line.startswith('```')]
                content = '\n'.join(json_lines)

            data = json.loads(content)

            story = data.get('story', '')
            choices_data = data.get('choices', [])

            choices = []
            for choice_data in choices_data:
                choice_type_str = choice_data.get('type', 'action')
                try:
                    choice_type = ChoiceType(choice_type_str)
                except ValueError:
                    choice_type = ChoiceType.ACTION

                choices.append(Choice(
                    id=str(choice_data.get('id', '')),
                    text=choice_data.get('text', ''),
                    type=choice_type
                ))

            return story, choices
        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON解析错误: {e}")
            return None
        except Exception as e:
            print(f"   ⚠️ 解析错误: {e}")
            return None
