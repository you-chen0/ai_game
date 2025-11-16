"""
LLM客户端 v2 - 改进版本
"""
import requests
import json
import os
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from src.types.story import ImageAnalysisResult, StoryGenre, ChoiceType, Choice

class LLMClient:
    """LLM API客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GRS_AI_API_KEY", "sk-c15186bd658749e0a4ad09ef6af985d8")
        self.base_url = "https://api.grsai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _url_to_base64(self, image_url: str) -> Optional[str]:
        """将图片URL转换为base64编码"""
        try:
            # 获取项目根目录 - 直接使用绝对路径
            current_dir = Path.cwd()  # 获取当前工作目录
            project_root = current_dir  # e:\project\game

            print(f"   📁 项目根目录: {project_root}")

            # 如果是本地URL
            if image_url.startswith("http://localhost") or image_url.startswith("http://127.0.0.1"):
                # 提取文件路径
                path = image_url.replace("http://localhost:8000", "")
                file_path = (project_root / path.lstrip('/')).resolve()

                print(f"   📂 查找文件: {file_path}")

                if not file_path.exists():
                    print(f"   ⚠️ 文件不存在: {file_path}")
                    # 尝试相对路径查找
                    alt_path = project_root / "uploads" / Path(image_url).name
                    print(f"   🔄 尝试替代路径: {alt_path}")
                    if alt_path.exists():
                        file_path = alt_path
                        print(f"   ✅ 在替代路径找到文件")
                    else:
                        return None
            else:
                # 直接下载远程图片
                print(f"   📥 下载远程图片: {image_url}")
                response = requests.get(image_url, timeout=30)
                if response.status_code != 200:
                    print(f"   ❌ 下载失败: {response.status_code}")
                    return None
                file_path = None

            # 读取图片并转换为base64
            if file_path:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
            else:
                image_data = response.content

            # 获取文件扩展名
            if file_path:
                ext = file_path.suffix.lower()
            else:
                # 从URL或响应头获取
                ext = '.png'  # 默认

            # 转换为base64
            base64_string = base64.b64encode(image_data).decode('utf-8')
            mime_type = {
                '.jpg': 'jpeg',
                '.jpeg': 'jpeg',
                '.png': 'png',
                '.gif': 'gif',
                '.bmp': 'bmp',
            }.get(ext, 'jpeg')

            result = f"data:image/{mime_type};base64,{base64_string}"
            print(f"   ✅ 转换成功，base64长度: {len(result)}")
            return result

        except Exception as e:
            print(f"   ❌ 转换失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def analyze_image(
        self,
        image_url: str,
        max_retries: int = 2
    ) -> Optional[ImageAnalysisResult]:
        """分析图片内容"""
        prompt = """
你是一个专业的图片内容分析专家。请仔细分析这张图片，并制定**完整的10步故事规划**。

**重要：必须生成完整的故事规划，包含开头、发展、高潮、结局四个部分，确保故事在第10步有令人满意的结局。**

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
  "genre_suggestion": "建议的故事类型",

  "story_outline": {
    "characters": [
      {"name": "主角名", "description": "性格特点、能力背景"}
    ],
    "key_items": [
      {"name": "道具名", "description": "外观、用途、重要性"}
    ],
    "important_npcs": [
      {"name": "NPC名", "role": "角色定位", "description": "性格、动机、与主角关系"}
    ],
    "key_decisions": [
      "影响结局的重要决策点1",
      "影响结局的重要决策点2"
    ],
    "success_conditions": "故事成功需要达成的条件描述",
    "failure_conditions": "可能导致失败的条件描述",
    "plot_threads": [
      "主线情节：核心冲突和解决方案",
      "支线情节1：辅助故事线",
      "支线情节2：可选探索线"
    ],

    "complete_story_plan": {
      "story_summary": "完整故事概述（用户不知道，需要通过选择探索，必须包含完整的故事结构：开头-发展-高潮-结局）",
      "correct_path": [
        {"step": 1, "description": "故事开头：引入主角、场景和初始冲突", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 2, "description": "故事发展：推进情节，引入新元素", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 3, "description": "故事发展：深化冲突，增加紧张感", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 4, "description": "故事发展：角色成长，情节转折", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 5, "description": "故事发展：关键发现，重要线索", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 6, "description": "故事发展：进入关键阶段，埋下伏笔", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 7, "description": "故事发展：高潮前的准备，紧张升级", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 8, "description": "故事高潮：核心冲突爆发，最关键的选择", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 9, "description": "故事高潮尾声：解决冲突的关键行动", "requirement": "需要做什么", "consequence": "正确选择的结果"},
        {"step": 10, "description": "故事结局：圆满收尾，解决所有悬念，给出令人满意的结尾", "requirement": "需要做什么", "consequence": "正确选择的结果"}
      ],
      "wrong_paths": [
        {
          "step": 1,
          "description": "错误分支1：在第1步可能的选择错误",
          "wrong_choice": "错误选择的描述",
          "punishment": "错误选择的后果",
          "recovery": "如何从错误中恢复"
        },
        {
          "step": 2,
          "description": "错误分支2：在第2步可能的选择错误",
          "wrong_choice": "错误选择的描述",
          "punishment": "错误选择的后果",
          "recovery": "如何从错误中恢复"
        }
      ],
      "key_choice_points": [
        {"step": 3, "description": "第3步的关键选择点", "correct_choice": "正确选择", "wrong_choices": ["错误选择1", "错误选择2"]},
        {"step": 5, "description": "第5步的关键选择点", "correct_choice": "正确选择", "wrong_choices": ["错误选择1", "错误选择2"]},
        {"step": 8, "description": "第8步的关键选择点", "correct_choice": "正确选择", "wrong_choices": ["错误选择1", "错误选择2"]}
      ]
    }
  }
}
```

重要要求：
1. story_summary不能让用户看到，是AI内部使用的完整剧情
2. correct_path是用户应该遵循的正确路径，但用户不知道
3. wrong_paths是常见的错误分支及惩罚
4. key_choice_points是需要在提示中重点设计的选择点，每个要有1个正确选择和2个错误选择
5. 错误选择要有明显的惩罚（如失去道具、危险增加等），但不是直接死亡
6. 即使选错，也要有恢复的可能，不是彻底的失败
"""

        # 将图片转换为base64
        print(f"\n🔄 [LLM] 转换图片为base64...")
        base64_image = self._url_to_base64(image_url)
        if not base64_image:
            print("   ❌ 图片转换失败")
            return None

        data = {
            "model": "gemini-2.5-flash-lite",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": base64_image}}
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
                    timeout=120  # 增加超时时间到120秒
                )

                print(f"   📡 HTTP状态: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"   📝 响应键: {list(result.keys())}")

                    # 检查choices
                    if 'choices' in result:
                        choices = result['choices']
                        print(f"   ✅ 找到choices，数量: {len(choices) if choices else 0}")

                        if choices and len(choices) > 0:
                            # 获取content
                            message = choices[0].get('message', {})
                            content = message.get('content', '')

                            print(f"   📄 内容长度: {len(content)} 字符")

                            if content:
                                # 尝试解析
                                parsed = self._parse_analysis_result(content)
                                if parsed:
                                    print(f"   ✅ 解析成功")
                                    return parsed
                                else:
                                    print(f"   ⚠️ 解析失败，内容: {content[:100]}...")
                            else:
                                print(f"   ⚠️ 内容为空")
                        else:
                            print(f"   ⚠️ choices列表为空")
                            print(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
                    else:
                        print(f"   ⚠️ 没有choices字段")
                        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
                else:
                    print(f"   ❌ HTTP错误: {response.status_code}")
                    print(f"   错误: {response.text[:200]}")

                if attempt < max_retries - 1:
                    print(f"   ⏳ 1秒后重试...")
                    import time
                    time.sleep(1)

            except Exception as e:
                print(f"   ❌ 异常: {e}")
                import traceback
                traceback.print_exc()
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)

        print(f"   ❌ 分析失败，已重试 {max_retries} 次")
        return None

    def generate_initial_story(
        self,
        image_analysis: ImageAnalysisResult,
        genre: StoryGenre,
        max_retries: int = 2
    ) -> Optional[tuple[str, list[Choice]]]:
        """生成初始故事"""
        prompt = f"""
请基于以下图片分析结果，创作一个{genre.value}风格的故事开头：

场景：{image_analysis.scene_description}
角色：{', '.join([c.get('name', '') for c in image_analysis.characters])}
物品：{', '.join(image_analysis.key_objects)}

要求：
- 80-100字，**极其简洁，直接进入核心冲突**
- **立即引入危机、谜团或关键问题**，不要铺垫
- 引出3个不同类型的选择（action/dialogue/item）
- **禁止环境描写和背景铺垄**，只写核心事件

请以JSON格式返回：
```json
{{
  "story": "直接进入冲突的简洁开头",
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
            "temperature": 0.7,  # 降低随机性
            "max_tokens": 800  # 限制长度
        }

        for attempt in range(max_retries):
            try:
                print(f"\n📖 [LLM] 生成故事中... (尝试 {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    choices = result.get('choices', [])

                    if choices and len(choices) > 0:
                        content = choices[0].get('message', {}).get('content', '')
                        if content:
                            parsed = self._parse_story_generation_result(content)
                            if parsed and len(parsed) >= 2:
                                print(f"   ✅ 故事生成成功")
                                # 只返回前2个值：story, choices（忽略 choice_count 和 choice_necessity）
                                return parsed[0], parsed[1]

                print(f"   ⚠️ 失败，状态码: {response.status_code}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)

            except Exception as e:
                print(f"   ❌ 错误: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)

        return None

    def continue_story(
        self,
        story_text: str,
        last_choice: str,
        choice_type: ChoiceType,
        max_retries: int = 2,
        progress_info: Optional[dict] = None,
        story_outline: Optional['StoryOutline'] = None
    ) -> Optional[tuple[str, list[Choice], int, str]]:
        """继续故事

        Returns:
            tuple: (故事内容, 选择列表, 选择数量, 必要性类型)
        """
        # 获取当前步数
        current_step = progress_info.get('current_scene_count', 0) + 1 if progress_info else 1

        # 构建故事规划约束
        story_plan_constraint = ""
        outline_info = ""

        if story_outline:
            # 基本信息
            outline_info = f"""
故事角色：{', '.join([c.get('name', '') + ': ' + c.get('description', '') for c in story_outline.characters])}
关键道具：{', '.join([item.get('name', '') + ': ' + item.get('description', '') for item in story_outline.key_items])}
主线情节：{', '.join(story_outline.plot_threads)}
"""

            # 检查是否有完整故事规划
            if hasattr(story_outline, 'to_dict'):
                story_outline_dict = story_outline.to_dict()
                if 'complete_story_plan' in story_outline_dict:
                    story_plan = story_outline_dict['complete_story_plan']

                    # 获取当前步骤的规划
                    current_plan = None
                    if current_step <= len(story_plan.get('correct_path', [])):
                        current_plan = story_plan['correct_path'][current_step - 1]

                    # 构建约束
                    if current_plan:
                        story_plan_constraint = f"""
📋 **故事框架（必须在第{current_step}步遵循）**：
{outline_info}

🎯 **当前步骤规划**：
- 步骤 {current_step}：{current_plan.get('description', '')}
- 要求：{current_plan.get('requirement', '')}
- 结果：{current_plan.get('consequence', '')}

⭐ **严格要求**：
- 故事概要：{story_plan.get('story_summary', '')}
- 当前是第 {current_step} 步，请严格按照上述规划推进剧情
- 第 10 步必须生成完整的结局：解决所有悬念，给出令人满意的结尾
- 禁止在第 10 步制造新悬念或未解决的情节

🎲 **选择设计**：
- 提供 2-3 个不同的选择，每个选择都要有明确的权衡和后果
- 如果用户的选择符合规划，请朝正确结局推进
- 如果用户选择偏离规划，也要提供合理的延续（任务可以失败）
"""
                    else:
                        story_plan_constraint = f"""
📋 **故事框架**：
{outline_info}
故事概要：{story_plan.get('story_summary', '')}
当前是第 {current_step} 步，请延续剧情并朝结局推进。
"""

        # 移除复杂进度约束
        prompt = f"""
{story_plan_constraint}

📖 **当前故事进度**：{story_text}

👤 **用户刚才的选择**：{last_choice}

请继续故事，生成一个完整的事件发展：
- 包含完整的事件过程，不只是微小动作
- 推进故事到下一个关键节点
- 如果当前是第10步，必须生成完整结局（解决所有悬念，给出满意结尾）

请以JSON格式返回：
```json
{{
  "story": "完整的事件发展",
  "choice_count": 2,  // 1-3个选择
  "choice_necessity": "optional",
  "choices": [
    {{"id": "1", "text": "选择1", "type": "action", "reasoning": "风险和收益"}},
    {{"id": "2", "text": "选择2", "type": "dialogue", "reasoning": "风险和收益"}}
  ],
  "reasoning": "选择设计说明"
}}
```
"""

        data = {
            "model": "gemini-2.5-flash-lite",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.75,  # 保持适度的创意
            "max_tokens": 1500  # 增加长度以支持200-300字剧情
        }

        for attempt in range(max_retries):
            try:
                print(f"\n📝 [LLM] 继续故事中...")
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    choices = result.get('choices', [])

                    if choices and len(choices) > 0:
                        content = choices[0].get('message', {}).get('content', '')
                        if content:
                            parsed = self._parse_story_generation_result(content)
                            if parsed:
                                return parsed

                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)

            except Exception as e:
                print(f"   ❌ 错误: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)

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

            # 解析故事大纲
            outline_data = data.get('story_outline', {})
            story_outline = None
            if outline_data:
                from src.types.story import StoryOutline
                story_outline = StoryOutline.from_dict(outline_data)

            return ImageAnalysisResult(
                scene_description=data.get('scene_description', ''),
                characters=data.get('characters', []),
                key_objects=data.get('key_objects', []),
                color_style=data.get('color_style', {}),
                story_elements=data.get('story_elements', ''),
                emotional_tone=data.get('emotional_tone', ''),
                genre_suggestion=data.get('genre_suggestion', ''),
                story_outline=story_outline
            )
        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON解析错误: {e}")
            print(f"   原始内容: {content[:200]}")
            return None
        except Exception as e:
            print(f"   ⚠️ 解析错误: {e}")
            return None

    def _parse_story_generation_result(self, content: str) -> Optional[tuple[str, list[Choice], int, str]]:
        """解析故事生成结果（包含动态选择）"""
        try:
            # 移除markdown代码块
            if content.startswith('```'):
                lines = content.split('\n')
                json_lines = [line for line in lines if not line.startswith('```')]
                content = '\n'.join(json_lines)

            data = json.loads(content)

            story = data.get('story', '')
            choice_count = data.get('choice_count', 3)
            choice_necessity_str = data.get('choice_necessity', 'optional')
            choices_data = data.get('choices', [])
            reasoning = data.get('reasoning', '')

            # 验证选择数量
            actual_choice_count = min(len(choices_data), choice_count)
            choices_data = choices_data[:actual_choice_count]

            choices = []
            from src.types.story import ChoiceNecessity
            necessity_map = {
                'mandatory': ChoiceNecessity.MANDATORY,
                'optional': ChoiceNecessity.OPTIONAL,
                'forced': ChoiceNecessity.FORCED
            }
            necessity = necessity_map.get(choice_necessity_str, ChoiceNecessity.OPTIONAL)

            for choice_data in choices_data:
                choice_type_str = choice_data.get('type', 'action')
                try:
                    choice_type = ChoiceType(choice_type_str)
                except ValueError:
                    choice_type = ChoiceType.ACTION

                choices.append(Choice(
                    id=str(choice_data.get('id', '')),
                    text=choice_data.get('text', ''),
                    type=choice_type,
                    necessity=necessity,
                    reasoning=choice_data.get('reasoning', '')
                ))

            return story, choices, actual_choice_count, choice_necessity_str
        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON解析错误: {e}")
            print(f"   原始内容: {content[:200]}")
            return None
        except Exception as e:
            print(f"   ⚠️ 解析错误: {e}")
            return None
