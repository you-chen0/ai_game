"""
故事管理器 - 整合所有服务
"""
import os
import uuid
from typing import Optional, Tuple
from src.types.story import (
    StoryState,
    StoryScene,
    ImageAnalysisResult,
    StoryGenre,
    Choice,
    ChoiceType
)
from src.services.llm_client_v2 import LLMClient
from src.services.nano_banana_client_fixed import NanoBananaClient

class StoryManager:
    """故事管理器"""

    def __init__(self):
        self.llm_client = LLMClient()
        self.image_client = NanoBananaClient()
        self.current_state: Optional[StoryState] = None

    def start_story_from_image(
        self,
        image_url: str,
        genre: Optional[StoryGenre] = None,
        output_dir: str = "images"
    ) -> Optional[StoryState]:
        """
        从图片开始故事

        Args:
            image_url: 图片URL
            genre: 故事类型，如果为None则使用AI推荐
            output_dir: 输出目录

        Returns:
            故事状态
        """
        print("=" * 60)
        print("🎬 开始新的交互式故事")
        print("=" * 60)

        # 1. 分析图片
        print("\n📸 第一步：分析图片...")
        image_analysis = self.llm_client.analyze_image(image_url)
        if not image_analysis:
            print("❌ 图片分析失败")
            return None

        print(f"   ✅ 分析完成")
        print(f"      场景: {image_analysis.scene_description[:100]}...")
        print(f"      建议类型: {image_analysis.genre_suggestion}")

        # 2. 确定故事类型
        if genre is None:
            # 根据建议选择类型
            genre = self._determine_genre(image_analysis.genre_suggestion)

        print(f"   🎭 故事类型: {genre.value}")

        # 3. 生成初始场景图片
        print("\n🎨 第二步：生成初始场景图片...")
        # 将分析结果转换为文本（注意：开头不能有换行符）
        analysis_text = f"""场景: {image_analysis.scene_description}
角色: {', '.join([c.get('name', '') for c in image_analysis.characters])}
物品: {', '.join(image_analysis.key_objects)}
风格: {image_analysis.color_style.get('style', '')}
氛围: {image_analysis.emotional_tone}
"""
        initial_image_path = self.image_client.generate_initial_scene_image(
            analysis_text,
            genre.value,
            output_dir
        )
        if not initial_image_path:
            print("❌ 初始场景图片生成失败")
            return None

        # 4. 生成初始故事
        print("\n📖 第三步：生成初始故事...")
        result = self.llm_client.generate_initial_story(image_analysis, genre)
        if not result:
            print("❌ 初始故事生成失败")
            return None

        story_text, choices = result
        print(f"   ✅ 故事生成完成 ({len(story_text)} 字符)")
        print(f"      选择数量: {len(choices)}")

        # 5. 创建初始场景
        scene = StoryScene(
            id=str(uuid.uuid4())[:8],
            image_path=initial_image_path,
            story_text=story_text,
            genre=genre,
            choices=choices
        )

        # 6. 创建故事状态
        self.current_state = StoryState(
            current_scene=scene,
            scene_count=0,
            max_scenes=10,
            story_theme=image_analysis.story_elements,
            story_outline=image_analysis.story_outline,
            is_ending=False
        )

        # 添加初始场景到历史
        self.current_state.scene_history.append({
            "step": 0,
            "scene_id": scene.id,
            "image_path": scene.image_path,
            "story_text": scene.story_text,
            "user_choice": "故事开始",
            "choices": [{"id": c.id, "text": c.text, "type": c.type.value} for c in scene.choices],
            # 保存完整的游戏状态快照
            "game_state_snapshot": {
                "user_attributes": self.current_state.user_attributes.copy(),
                "choice_history": self.current_state.choice_history.copy(),
                "item_states": self.current_state.item_states.copy() if self.current_state.item_states else {},
                "npc_relations": self.current_state.npc_relations.copy() if self.current_state.npc_relations else {},
                "danger_level": self.current_state.danger_level,
                "consecutive_failures": self.current_state.consecutive_failures
            }
        })

        print("\n✅ 故事初始化完成！")
        return self.current_state

    def analyze_scene_context(self) -> 'SceneContext':
        """
        分析当前场景，确定合理的选择数量

        Returns:
            SceneContext: 场景分析结果
        """
        from src.types.story import SceneContext

        current_scene = self.current_state.current_scene
        last_choice_id = self.current_state.choice_history[-1] if self.current_state.choice_history else ""

        # 分析紧急程度
        urgency = "MEDIUM"
        story_text_lower = current_scene.story_text.lower()
        if any(keyword in story_text_lower for keyword in ['危险', '紧急', '立即', '快', '危险', '逃跑', '救援']):
            urgency = "HIGH"
        elif any(keyword in story_text_lower for keyword in ['休息', '观察', '思考', '可以']):
            urgency = "LOW"

        # 分析连续失败
        consecutive_failures = self.current_state.consecutive_failures

        # 分析资源状态
        resources = "abundant"
        if consecutive_failures > 0:
            resources = "limited"
        if self.current_state.danger_level > 70:
            resources = "zero"

        # 分析选择数量
        if urgency == "HIGH":
            choice_count = 1
            must_advance = True
        elif "但是" in story_text_lower or "然而" in story_text_lower or "突然" in story_text_lower:
            choice_count = 2
            must_advance = True
        else:
            choice_count = 3
            must_advance = False

        reasoning = f"紧急程度: {urgency}, 连续失败: {consecutive_failures}, 危险度: {self.current_state.danger_level}"

        return SceneContext(
            urgency=urgency,
            available_resources=resources,
            natural_choice_count=choice_count,
            must_advance=must_advance,
            reasoning=reasoning
        )

    def continue_story(self, choice_id: str) -> bool:
        """
        根据用户选择继续故事

        Args:
            choice_id: 用户选择的选择ID

        Returns:
            是否成功
        """
        if not self.current_state:
            print("❌ 没有活跃的故事")
            return False

        # 获取选择
        choice = next(
            (c for c in self.current_state.current_scene.choices if c.id == choice_id),
            None
        )
        if not choice:
            print(f"❌ 无效的选择: {choice_id}")
            return False

        print("\n" + "=" * 60)
        print(f"➡️  用户选择: {choice.text}")
        print("=" * 60)

        # 进度约束检查
        progress_info = self._check_progress_constraints(choice)

        # 分析场景上下文
        scene_context = self.analyze_scene_context()
        print(f"\n🔍 场景分析: {scene_context.reasoning}")

        # 先继续故事，生成新场景
        print("\n📝 继续故事...")
        result = self.llm_client.continue_story(
            self.current_state.current_scene.story_text,
            choice.text,
            choice.type,
            progress_info=progress_info,
            story_outline=self.current_state.story_outline
        )
        if not result or len(result) < 4:
            print("❌ LLM返回格式错误")
            return False

        story_text, new_choices, choice_count, necessity = result

        # 生成下一场景图片
        print("\n🎨 生成下一场景图片...")
        image_path = self.image_client.generate_scene_image(
            story_text,
            choice.text,
            "images"
        )
        if not image_path:
            print("❌ 场景图片生成失败")
            return False

        # 创建新场景
        new_scene = StoryScene(
            id=str(uuid.uuid4())[:8],
            image_path=image_path,
            story_text=story_text,
            genre=self.current_state.current_scene.genre,
            choices=new_choices
        )

        # 更新状态
        self.current_state.current_scene = new_scene
        self.current_state.add_choice(choice_id)

        # 添加到完整故事历史
        self.current_state.scene_history.append({
            "step": self.current_state.scene_count,
            "scene_id": new_scene.id,
            "image_path": new_scene.image_path,
            "story_text": new_scene.story_text,
            "user_choice": choice.text,
            "choices": [{"id": c.id, "text": c.text, "type": c.type.value} for c in new_scene.choices],
            # 保存完整的游戏状态快照
            "game_state_snapshot": {
                "user_attributes": self.current_state.user_attributes.copy(),
                "choice_history": self.current_state.choice_history.copy(),
                "item_states": self.current_state.item_states.copy() if self.current_state.item_states else {},
                "npc_relations": self.current_state.npc_relations.copy() if self.current_state.npc_relations else {},
                "danger_level": self.current_state.danger_level,
                "consecutive_failures": self.current_state.consecutive_failures
            }
        })

        # 检查是否应该结束
        if self.current_state.is_complete():
            # 标记当前场景为结束场景
            self.current_state.current_scene.is_ending = True
            print("\n🎭 故事结束！")
            return True

        # 记录必要性和选择数量信息（可以用于调试）
        self.current_state.metadata = {
            "last_choice_count": choice_count,
            "last_choice_necessity": necessity
        }

        print(f"\n✅ 故事继续完成，选择数量: {choice_count}")
        return True

    def get_current_state(self) -> Optional[StoryState]:
        """获取当前故事状态"""
        return self.current_state

    def display_current_scene(self):
        """显示当前场景信息"""
        if not self.current_state:
            print("❌ 没有活跃的故事")
            return

        scene = self.current_state.current_scene

        print("\n" + "=" * 60)
        print(f"📖 故事场景 #{self.current_state.scene_count + 1}")
        print("=" * 60)
        print(f"\n🖼️  场景图片:")
        print(f"   {scene.image_path}")
        print(f"\n📝 故事内容:")
        print(f"   {scene.story_text}")
        print(f"\n❓ 可选选择:")
        for choice in scene.choices:
            type_icon = {
                ChoiceType.ACTION: "⚡",
                ChoiceType.DIALOGUE: "💬",
                ChoiceType.ITEM: "🎒",
                ChoiceType.EMOTION: "❤️"
            }.get(choice.type, "•")
            print(f"   {type_icon} [{choice.id}] {choice.text}")

        print(f"\n📊 进度: {self.current_state.story_progress:.1f}%")
        if self.current_state.is_complete():
            print("🎭 故事即将结束...")

    def _determine_genre(self, genre_suggestion: str) -> StoryGenre:
        """
        根据AI建议确定故事类型

        Args:
            genre_suggestion: AI建议的类型

        Returns:
            故事类型
        """
        suggestion_lower = genre_suggestion.lower()

        # 匹配关键词
        if '科幻' in suggestion_lower or 'scifi' in suggestion_lower:
            return StoryGenre.SCIFI
        elif '奇幻' in suggestion_lower or 'fantasy' in suggestion_lower:
            return StoryGenre.FANTASY
        elif '悬疑' in suggestion_lower or 'mystery' in suggestion_lower:
            return StoryGenre.MYSTERY
        elif '爱情' in suggestion_lower or 'romance' in suggestion_lower:
            return StoryGenre.ROMANCE
        elif '恐怖' in suggestion_lower or 'horror' in suggestion_lower:
            return StoryGenre.HORROR
        elif '喜剧' in suggestion_lower or 'comedy' in suggestion_lower:
            return StoryGenre.COMEDY
        elif '戏剧' in suggestion_lower or 'drama' in suggestion_lower:
            return StoryGenre.DRAMA
        else:
            return StoryGenre.ADVENTURE  # 默认类型

    def _check_progress_constraints(self, current_choice: Choice) -> dict:
        """
        检查进度约束并返回相关信息

        Args:
            current_choice: 当前选择

        Returns:
            包含进度信息的字典
        """
        if not self.current_state:
            return {}

        info = {
            'current_scene_count': self.current_state.scene_count,
            'max_scenes': self.current_state.max_scenes,
            'is_climax_reached': False,
            'needs_climax': False,
            'should_push_progress': False,
            'consecutive_action_count': 0,
            'choice_types_history': []
        }

        # 检查是否达到高潮点（max_scenes的一半）
        if self.current_state.scene_count >= self.current_state.max_scenes / 2:
            info['is_climax_reached'] = True
            info['needs_climax'] = True
            print(f"   🎭 已进入高潮阶段")

        # 检查连续action类型
        choice_history = self.current_state.choice_history
        recent_choices = self.current_state.current_scene.choices

        # 记录当前选择类型
        info['choice_types_history'].append(current_choice.type)

        # 计算连续action数量
        consecutive_action = 0
        for choice_id in reversed(choice_history[-5:]):  # 检查最近5个选择
            if choice_id == current_choice.id:
                continue

            # 找到对应的选择类型
            matched_choice = next(
                (c for c in recent_choices if c.id == choice_id),
                None
            )
            if matched_choice:
                if matched_choice.type == ChoiceType.ACTION:
                    consecutive_action += 1
                else:
                    break

        info['consecutive_action_count'] = consecutive_action

        # 如果连续3个action，需要推进剧情
        if consecutive_action >= 2:
            info['should_push_progress'] = True
            print(f"   ⚡ 检测到连续{consecutive_action + 1}个action选择，需要推进剧情")

        return info

    def reset_story(self):
        """重置故事"""
        self.current_state = None
        print("\n🔄 故事已重置")

    def rollback_to_step(self, target_step: int) -> bool:
        """
        回溯到指定步骤

        Args:
            target_step: 目标步骤（0-based）

        Returns:
            是否成功
        """
        if not self.current_state:
            print("❌ 没有活跃的故事")
            return False

        if target_step < 0 or target_step >= len(self.current_state.scene_history):
            print(f"❌ 无效的步骤: {target_step}")
            return False

        print(f"\n⏪ 回溯到步骤 {target_step}...")

        # 获取目标步骤的历史记录
        target_history = self.current_state.scene_history[target_step]
        snapshot = target_history.get("game_state_snapshot", {})

        # 恢复游戏状态
        if snapshot:
            self.current_state.user_attributes = snapshot.get("user_attributes", {}).copy()
            self.current_state.choice_history = snapshot.get("choice_history", []).copy()
            self.current_state.item_states = snapshot.get("item_states", {}).copy()
            self.current_state.npc_relations = snapshot.get("npc_relations", {}).copy()
            self.current_state.danger_level = snapshot.get("danger_level", 0)
            self.current_state.consecutive_failures = snapshot.get("consecutive_failures", 0)

        # 截断历史记录到目标步骤
        self.current_state.scene_history = self.current_state.scene_history[:target_step + 1]

        # 如果目标步骤不是最后一步，我们需要重新生成下一步的场景
        if target_step < len(self.current_state.scene_history) - 1:
            # 从目标步骤的历史记录重新创建场景（让用户重新选择）
            from src.types.story import StoryScene, Choice, ChoiceType
            import uuid

            # 从目标步骤历史中重新构建场景
            # 注意：这一步实际上是步骤 target_step + 1 的场景，是用户需要做选择的场景
            next_step_history = self.current_state.scene_history[target_step + 1]

            # 重新创建选择列表
            choices = []
            for c in next_step_history.get("choices", []):
                if isinstance(c, dict):
                    # 从字典创建Choice对象
                    choice_type = ChoiceType(c.get("type", "action"))
                    choices.append(Choice(
                        id=c["id"],
                        text=c["text"],
                        type=choice_type
                    ))
                else:
                    # 如果已经是Choice对象，直接使用
                    choices.append(c)

            # 创建新的场景（基于步骤 target_step + 1 的状态）
            self.current_state.current_scene = StoryScene(
                id=str(uuid.uuid4())[:8],
                image_path=next_step_history["image_path"],
                story_text=next_step_history["story_text"],
                genre=self.current_state.current_scene.genre,
                choices=choices,
                is_ending=False  # 重置结束状态
            )

            # 更新场景计数为 target_step + 1（因为我们要显示的是下一步的场景）
            self.current_state.scene_count = target_step + 1
        else:
            # 如果是最后一步，保持当前场景
            self.current_state.scene_count = target_step

        # 重置结束状态
        self.current_state.is_ending = False
        if hasattr(self.current_state.current_scene, 'is_ending'):
            self.current_state.current_scene.is_ending = False

        self.current_state.update_progress()

        print(f"✅ 已回溯到步骤 {target_step}")
        print(f"   当前进度: {self.current_state.scene_count}/{self.current_state.max_scenes}")
        print(f"   请重新选择以继续故事")

        return True
