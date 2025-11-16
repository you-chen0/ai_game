"""
故事系统核心类型定义
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class StoryGenre(Enum):
    """故事类型"""
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    FANTASY = "fantasy"
    SCIFI = "scifi"
    ROMANCE = "romance"
    HORROR = "horror"
    COMEDY = "comedy"
    DRAMA = "drama"

class ChoiceType(Enum):
    """选择类型"""
    ACTION = "action"          # 行动选择
    DIALOGUE = "dialogue"      # 对话选择
    ITEM = "item"             # 物品选择
    EMOTION = "emotion"       # 情感选择

@dataclass
class Choice:
    """故事选择"""
    id: str
    text: str
    type: ChoiceType
    consequence: str = ""
    image_prompt: str = ""
    story_impact: int = 0  # 影响值 (-100 到 100)

@dataclass
class StoryScene:
    """故事场景"""
    id: str
    image_url: str
    image_prompt: str
    story_text: str
    genre: StoryGenre
    choices: List[Choice] = field(default_factory=list)
    is_ending: bool = False
    ending_type: Optional[str] = None

@dataclass
class StoryState:
    """完整故事状态"""
    current_scene: StoryScene
    choice_history: List[str] = field(default_factory=list)
    story_progress: int = 0  # 0-100
    user_attributes: Dict[str, Any] = field(default_factory=dict)
    story_theme: str = ""
    scene_count: int = 0
    max_scenes: int = 10  # 最大场景数

    def add_choice(self, choice_id: str):
        """添加选择历史"""
        self.choice_history.append(choice_id)
        self.scene_count += 1
        self.update_progress()

    def update_progress(self):
        """更新进度"""
        self.story_progress = min(100, (self.scene_count / self.max_scenes) * 100)

    def is_complete(self) -> bool:
        """检查是否完成"""
        return self.current_scene.is_ending or self.scene_count >= self.max_scenes

@dataclass
class NanoBananaResponse:
    """nano banana API响应"""
    status: str
    url: str
    prompt: str
    model: str
    metadata: Optional[Dict] = None

@dataclass
class StoryGenerationConfig:
    """故事生成配置"""
    initial_prompt_template: str = (
        "基于这张图片创作一个{genre}风格的故事开头。\n"
        "要求：\n"
        "1. 场景描述生动详细\n"
        "2. 包含3个不同的选择选项\n"
        "3. 选择应有明确的后果影响\n"
        "4. 字数控制在200-300字\n"
    )

    choice_generation_template: str = (
        "当前故事：{story_text}\n"
        "用户刚做了选择：{last_choice}\n"
        "请继续故事并生成3个新选择，要求：\n"
        "1. 符合故事逻辑\n"
        "2. 选择类型多样化（行动/对话/物品/情感）\n"
        "3. 每个选择对应不同的故事走向\n"
        "4. 字数控制在150-200字\n"
    )

    image_prompt_template: str = (
        "基于故事描述'{story_text}'和选择'{choice_text}'，"
        "生成下一场景的图片描述，要求：\n"
        "1. 风格一致\n"
        "2. 场景连贯\n"
        "3. 突出关键元素\n"
        "4. 适合AI图片生成"
    )
