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

class ChoiceNecessity(Enum):
    """选择必要性"""
    MANDATORY = "mandatory"    # 必须执行（只有1个选择）
    OPTIONAL = "optional"      # 可选（2-3个选择）
    FORCED = "forced"         # 强制推进（剧情需要必须选）

@dataclass
class Choice:
    """故事选择"""
    id: str
    text: str
    type: ChoiceType
    consequence: str = ""
    story_impact: int = 0  # 影响值 (-100 到 100)
    necessity: ChoiceNecessity = ChoiceNecessity.OPTIONAL  # 选择必要性
    reasoning: str = ""  # 为什么是这个选择（用于调试/记录）

@dataclass
class StoryScene:
    """故事场景"""
    id: str
    image_path: str
    story_text: str
    genre: StoryGenre
    choices: List[Choice] = field(default_factory=list)
    is_ending: bool = False
    ending_type: Optional[str] = None

@dataclass
class StoryOutline:
    """故事核心大纲"""
    characters: List[Dict[str, str]]  # 主要人物列表及特点
    key_items: List[Dict[str, str]]   # 关键道具清单及用途
    important_npcs: List[Dict[str, str]]  # 重要NPC列表及作用
    key_decisions: List[str]  # 关键决策点列表（影响结局的选择）
    success_conditions: str  # 成功条件定义
    failure_conditions: str  # 失败条件定义
    plot_threads: List[str]  # 3-5个核心情节线（支线/主线）
    story_arc: Optional[Dict[str, str]] = None  # 故事脉络（开头、发展、高潮、结局）
    ending_design: Optional[Dict[str, Any]] = None  # 结局设计
    ten_step_plan: Optional[List[Dict[str, Any]]] = None  # 十步故事计划

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "characters": self.characters,
            "key_items": self.key_items,
            "important_npcs": self.important_npcs,
            "key_decisions": self.key_decisions,
            "success_conditions": self.success_conditions,
            "failure_conditions": self.failure_conditions,
            "plot_threads": self.plot_threads
        }
        if self.story_arc:
            result["story_arc"] = self.story_arc
        if self.ending_design:
            result["ending_design"] = self.ending_design
        if self.ten_step_plan:
            result["ten_step_plan"] = self.ten_step_plan
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryOutline':
        """从字典创建"""
        return cls(
            characters=data.get("characters", []),
            key_items=data.get("key_items", []),
            important_npcs=data.get("important_npcs", []),
            key_decisions=data.get("key_decisions", []),
            success_conditions=data.get("success_conditions", ""),
            failure_conditions=data.get("failure_conditions", ""),
            plot_threads=data.get("plot_threads", []),
            story_arc=data.get("story_arc"),
            ending_design=data.get("ending_design"),
            ten_step_plan=data.get("ten_step_plan")
        )

@dataclass
class SceneContext:
    """场景上下文分析"""
    urgency: str  # HIGH/MEDIUM/LOW
    available_resources: str  # abundant/limited/zero
    natural_choice_count: int  # 1-3，自然情况下的选择数量
    must_advance: bool  # 是否必须推进剧情
    reasoning: str  # 分析原因

@dataclass
class ImageAnalysisResult:
    """图片分析结果"""
    scene_description: str
    characters: List[Dict[str, str]] = field(default_factory=list)
    key_objects: List[str] = field(default_factory=list)
    color_style: Dict[str, Any] = field(default_factory=dict)
    story_elements: str = ""
    emotional_tone: str = ""
    genre_suggestion: str = ""
    story_outline: Optional['StoryOutline'] = None  # 故事大纲

@dataclass
class StoryState:
    """完整故事状态"""
    current_scene: StoryScene
    choice_history: List[str] = field(default_factory=list)
    scene_history: List[Dict[str, Any]] = field(default_factory=list)  # 完整故事历史
    story_progress: float = 0.0  # 0-100
    scene_count: int = 0
    max_scenes: int = 10  # 最大场景数
    is_ending: bool = False
    story_theme: str = ""
    user_attributes: Dict[str, int] = field(default_factory=lambda: {
        "courage": 50,  # 勇气
        "wisdom": 50,   # 智慧
        "kindness": 50  # 善良
    })
    story_outline: Optional[StoryOutline] = None  # 故事大纲

    # 道具和NPC状态追踪
    item_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # 道具状态
    npc_relations: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # NPC关系

    # 危险度累积系统
    danger_level: int = 0  # 当前危险度 (0-100)
    consecutive_failures: int = 0  # 连续失败次数

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_choice(self, choice_id: str):
        """添加选择历史"""
        self.choice_history.append(choice_id)
        self.scene_count += 1
        self.update_progress()

    def update_progress(self):
        """更新进度"""
        self.story_progress = min(100.0, (self.scene_count / self.max_scenes) * 100.0)
        if self.scene_count >= self.max_scenes:
            self.is_ending = True

    def update_user_attribute(self, attr_name: str, delta: int):
        """更新用户属性"""
        if attr_name in self.user_attributes:
            self.user_attributes[attr_name] = max(0, min(100, self.user_attributes[attr_name] + delta))

    def get_user_attribute(self, attr_name: str) -> int:
        """获取用户属性值"""
        return self.user_attributes.get(attr_name, 0)

    def is_complete(self) -> bool:
        """检查是否完成"""
        return self.is_ending or self.current_scene.is_ending

@dataclass
class StoryGenerationConfig:
    """故事生成配置"""
    initial_prompt_template: str = """
请基于以下图片分析结果，创作一个{genre}风格的故事开头：

图片分析：
{image_analysis}

要求：
1. 字数控制在200-300字
2. 包含环境描写、角色介绍、情节铺垫
3. 营造{genre}氛围
4. 引出3个不同类型的选择（action/dialogue/item）

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

    continuation_prompt_template: str = """
当前故事：{story_text}

用户选择：{last_choice} (类型: {choice_type})

请继续故事并生成3个新选择，要求：
1. 符合故事逻辑发展
2. 字数控制在150-200字
3. 多样化选择类型
4. 增加故事悬念

JSON格式：
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

    image_prompt_template: str = """
基于故事内容：
{story_text}

用户选择：
{choice_text}

请生成下一场景图片，要求：
1. 风格保持一致
2. 场景连贯自然
3. 体现选择的后果
4. 突出故事转折点
5. 适合nano banana生成
"""
