1.三个值并没有起到实质性的作用，几乎没有太大变化
2.故事拖沓，十个阶段完全连故事的开头都没有讲完，一直在打斗的细节中反复，越来越细。

## 解决方案：

### 2.1 优化LLM提示词（已部分实施）
- **初始故事生成**: 限制为80-120字，要求直接进入核心冲突，避免过多环境描写
- **故事继续生成**: 限制为60-100字，每次必须推进剧情，不能停留在细节描写
- **禁止事项**: 明确禁止LLM重复之前内容、过度描述打斗、停留在细节中


### 2.3 实现进度约束
- 每次选择必须带来实质性进展
- 建立场景类型检查，避免连续3个"action"类型场景
- 强制故事在max_scenes/2处进入高潮阶段

2.修改后效果不好

## 新解决方案：

### 2.1 故事核心大纲生成机制
**实施方法：**
- **图片分析阶段新增**：在图片分析完成后，要求LLM生成"故事核心大纲"
- **大纲内容**：
  - 主要人物/角色列表及其特点
  - 关键道具清单及其用途
  - 重要NPC列表及作用
  - 关键决策点列表（影响结局的选择）
  - 成功/失败条件定义
  - 3-5个核心情节线（支线/主线）
- **存储与使用**：将大纲存储在StoryState中，后续每次故事生成时引用此大纲
- **提示词更新**：在所有LLM生成提示中强制要求"严格遵循故事核心大纲"

### 2.2 动态选择数量系统（优化版）
**核心思想：**
根据剧情自然发展，选择数量应该动态变化，而不是固定3个。剧情紧张时只有1个"必选"选择，剧情平缓时可以有2-3个可选方案。

**实施方法：**

**1. 剧情分析机制：**
- **紧急程度评估**：根据当前剧情判断场景紧急度（HIGH/MEDIUM/LOW）
- **资源状态评估**：分析角色可用资源（道具、信息、盟友、时间）
- **选择可用性**：判断当前情境下自然有多少个选择
- **剧情推进需求**：强制推进/可选推进/深度探索

**2. 选择数量判断标准：**
- **1个选择**：角色陷入"必须立即行动"的情境（逃生、面对危险、关键时机）
- **2个选择**：面临明确的"二选一"困境（合作/对抗、留下/离开、信任/怀疑）
- **3个选择**：有充分时间和资源进行多方案思考（探索、调查、社交）

**3. 强制推进机制：**
- 故事发展到关键节点时，LLM可以返回"choice_count=1"表示这是剧情必须推进的地方
- 不是用户没选择，而是剧情逻辑上只有1个合理选项

## 代码实现方案：

### 2.2.1 类型定义更新

**修改 src/types/story.py，新增 StoryOutline 类：**

```python
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

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "characters": self.characters,
            "key_items": self.key_items,
            "important_npcs": self.important_npcs,
            "key_decisions": self.key_decisions,
            "success_conditions": self.success_conditions,
            "failure_conditions": self.failure_conditions,
            "plot_threads": self.plot_threads
        }

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
            plot_threads=data.get("plot_threads", [])
        )

# 更新 StoryState
@dataclass
class StoryState:
    """完整故事状态"""
    current_scene: StoryScene
    choice_history: List[str] = field(default_factory=list)
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

# 新增 ChoiceNecessity 枚举
class ChoiceNecessity(Enum):
    """选择必要性"""
    MANDATORY = "mandatory"    # 必须执行（只有1个选择）
    OPTIONAL = "optional"      # 可选（2-3个选择）
    FORCED = "forced"         # 强制推进（剧情需要必须选）

# 更新 Choice 类
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
class SceneContext:
    """场景上下文分析"""
    urgency: str  # HIGH/MEDIUM/LOW
    available_resources: str  # abundant/limited/zero
    natural_choice_count: int  # 1-3，自然情况下的选择数量
    must_advance: bool  # 是否必须推进剧情
    reasoning: str  # 分析原因
```

### 2.2.2 LLM提示词优化

**修改 src/services/llm_client_v2.py，在图片分析时生成故事大纲：**

```python
def analyze_image(
    self,
    image_url: str,
    max_retries: int = 2
) -> Optional[ImageAnalysisResult]:
    """分析图片内容"""
    prompt = """
你是一个专业的图片内容分析专家。请仔细分析这张图片，并提取以下信息：

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
    ]
  }
}
```
"""

# 将图片转换为base64并调用API...
# (现有代码不变)

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
    except Exception as e:
        print(f"   ⚠️ 解析错误: {e}")
        return None
```

**更新 continue_story 方法，支持动态选择：**

```python
def continue_story(
    self,
    story_text: str,
    last_choice: str,
    choice_type: ChoiceType,
    max_retries: int = 2,
    progress_info: Optional[dict] = None,
    scene_context: Optional[SceneContext] = None,
    story_outline: Optional[StoryOutline] = None
) -> Optional[tuple[str, list[Choice], int, str]]:
    """继续故事

    Returns:
        tuple: (故事内容, 选择列表, 选择数量, 必要性类型)
    """
    # 构建剧情分析提示
    context_analysis = ""
    if scene_context:
        context_analysis = f"""
当前剧情分析：
- 紧急程度：{scene_context.urgency}
- 可用资源：{scene_context.available_resources}
- 自然选择数量：{scene_context.natural_choice_count}个
- 必须推进：{scene_context.must_advance}
- 分析原因：{scene_context.reasoning}
"""

    # 构建大纲约束
    outline_constraint = ""
    if story_outline:
        outline_constraint = f"""
故事大纲约束（必须严格遵循）：
- 主要角色：{', '.join([c.get('name', '') for c in story_outline.characters])}
- 关键道具：{', '.join([item.get('name', '') for item in story_outline.key_items])}
- 关键NPC：{', '.join([npc.get('name', '') for npc in story_outline.important_npcs])}
- 成功条件：{story_outline.success_conditions}
- 失败条件：{story_outline.failure_conditions}
- 情节线：{', '.join(story_outline.plot_threads)}
"""

    # 构建进度约束提示词
    constraint_prompt = ""
    if progress_info:
        if progress_info.get('needs_climax'):
            constraint_prompt += "\n🎭 进入高潮阶段：故事应进入关键转折点，引入重大冲突或揭示。"

        if progress_info.get('should_push_progress'):
            constraint_prompt += "\n⚡ 必须推进剧情：避免停留在当前场景，引入新情节点或重要进展。"

        if progress_info.get('consecutive_action_count', 0) >= 2:
            constraint_prompt += "\n💬 强制对话：接下来必须引入dialogue或item类型选择，避免连续action。"

    prompt = f"""
{context_analysis}

{outline_constraint}

当前故事：{story_text}

用户选择：{last_choice}

请继续故事，要求：
- 60-100字，简洁推进剧情
- 不要重复之前的内容或细节
- 避免过度描述打斗、动作等细节
- 直接进入下一个情节点或冲突
- 每次都要有明显的进展{constraint_prompt}

请根据当前剧情分析，自然生成合理数量的选择：
- 1个选择：当角色面临"必须执行"的情况（逃生、解救、面对危机、关键时机）
- 2个选择：当角色面临"二选一"困境（合作/对抗、留下/离开、信任/怀疑）
- 3个选择：当角色有充分时间和资源考虑多种方案（探索、调查、社交）

请以JSON格式返回：
```json
{{
  "story": "简洁的故事进展",
  "choice_count": 1,  // 实际选择数量：1-3
  "choice_necessity": "mandatory",  // mandatory/optional/forced
  "choices": [
    {{"id": "1", "text": "选择内容", "type": "action", "reasoning": "选择原因"}}
  ],
  "reasoning": "为什么是这个数量选择的详细分析"
}}
```
"""

    data = {
        "model": "gemini-2.5-flash-lite",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.75,
        "max_tokens": 700
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
```

### 2.2.3 StoryManager修改

**修改 src/services/story_manager.py，添加场景分析功能：**

```python
from src.types.story import SceneContext, ChoiceNecessity

def analyze_scene_context(self) -> SceneContext:
    """分析当前场景，确定合理的选择数量"""
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
    """继续故事"""
    try:
        # 获取当前场景和选择
        current_scene = self.current_state.current_scene
        selected_choice = None
        for choice in current_scene.choices:
            if choice.id == choice_id:
                selected_choice = choice
                break

        if not selected_choice:
            print(f"❌ 找不到选择: {choice_id}")
            return False

        print(f"\n✅ 用户选择: {selected_choice.text}")

        # 检查进度约束
        progress_info = self._check_progress_constraints()

        # 分析场景上下文
        scene_context = self.analyze_scene_context()
        print(f"\n🔍 场景分析: {scene_context.reasoning}")

        # 计算选择结果
        self._calculate_choice_outcome(selected_choice)

        # 生成新场景
        result = self.llm_client.continue_story(
            story_text=current_scene.story_text,
            last_choice=selected_choice.text,
            choice_type=selected_choice.type,
            progress_info=progress_info,
            scene_context=scene_context,
            story_outline=self.current_state.story_outline
        )

        if not result or len(result) < 4:
            print("❌ LLM返回格式错误")
            return False

        new_story_text, new_choices, choice_count, necessity = result

        # 创建新场景
        new_scene = self._generate_scene_image(new_story_text, selected_choice.text)

        # 更新状态
        self.current_state.add_choice(choice_id)
        self.current_state.current_scene = StoryScene(
            id=str(uuid.uuid4()),
            image_path=new_scene,
            story_text=new_story_text,
            genre=current_scene.genre,
            choices=new_choices,
            is_ending=False
        )

        # 记录必要性和选择数量信息（可以用于调试）
        self.current_state.metadata = {
            "last_choice_count": choice_count,
            "last_choice_necessity": necessity
        }

        print(f"\n✅ 故事继续成功，选择数量: {choice_count}")
        return True

    except Exception as e:
        print(f"❌ 故事继续失败: {e}")
        import traceback
        traceback.print_exc()
        return False
```

### 2.2.4 前端类型更新

**修改 web/src/types/story.ts，新增类型定义：**

```typescript
export interface StoryOutline {
  characters: Array<{
    name: string;
    description: string;
  }>;
  key_items: Array<{
    name: string;
    description: string;
  }>;
  important_npcs: Array<{
    name: string;
    role: string;
    description: string;
  }>;
  key_decisions: string[];
  success_conditions: string;
  failure_conditions: string;
  plot_threads: string[];
}

export type ChoiceNecessity = 'mandatory' | 'optional' | 'forced';

export interface Choice {
  id: string;
  text: string;
  type: 'action' | 'dialogue' | 'item' | 'emotion';
  consequence?: string;
  story_impact?: number;
  necessity?: ChoiceNecessity;
  reasoning?: string;
}

export interface SceneContext {
  urgency: 'HIGH' | 'MEDIUM' | 'LOW';
  available_resources: 'abundant' | 'limited' | 'zero';
  natural_choice_count: number;
  must_advance: boolean;
  reasoning: string;
}

export interface GameStateMetadata {
  last_choice_count?: number;
  last_choice_necessity?: string;
}

export interface GameState {
  current_scene: {
    id: string;
    image_path: string;
    story_text: string;
    genre: string;
    choices: Choice[];
    is_ending: boolean;
    ending_type?: string;
  };
  choice_history: string[];
  story_progress: number;
  scene_count: number;
  max_scenes: number;
  is_ending: boolean;
  story_theme: string;
  user_attributes: Record<string, number>;
  story_outline?: StoryOutline;
  item_states?: Record<string, any>;
  npc_relations?: Record<string, any>;
  danger_level?: number;
  consecutive_failures?: number;
  metadata?: GameStateMetadata;
}
```

### 2.2.5 前端ChoiceButton组件优化

**修改 web/src/components/ChoiceButton.tsx，支持动态选择：**

```typescript
import React from 'react';
import { motion } from 'framer-motion';
import { Choice, ChoiceNecessity } from '@/types/story';
import { Zap, MessageCircle, Package, Heart, AlertTriangle } from 'lucide-react';

interface ChoiceButtonProps {
  choice: Choice;
  index: number;
  onSelect: (choice: Choice) => void;
  disabled?: boolean;
  totalChoices: number; // 新增：总选择数量
}

const getChoiceIcon = (type: string) => {
  switch (type) {
    case 'action':
      return <Zap size={20} />;
    case 'dialogue':
      return <MessageCircle size={20} />;
    case 'item':
      return <Package size={20} />;
    case 'emotion':
      return <Heart size={20} />;
    default:
      return <Zap size={20} />;
  }
};

const getChoiceColor = (type: string) => {
  switch (type) {
    case 'action':
      return 'from-red-500/20 to-orange-500/20 hover:from-red-500/40 hover:to-orange-500/40';
    case 'dialogue':
      return 'from-blue-500/20 to-cyan-500/20 hover:from-blue-500/40 hover:to-cyan-500/40';
    case 'item':
      return 'from-purple-500/20 to-pink-500/20 hover:from-purple-500/40 hover:to-pink-500/40';
    case 'emotion':
      return 'from-green-500/20 to-emerald-500/20 hover:from-green-500/40 hover:to-emerald-500/40';
    default:
      return 'from-primary-blue/50 to-primary-purple/50';
  }
};

// 根据选择必要性获取样式
const getNecessityStyle = (necessity?: ChoiceNecessity, totalChoices?: number) => {
  if (totalChoices === 1) {
    return 'border-accent-yellow/60 shadow-lg shadow-accent-yellow/20';
  }
  if (necessity === 'mandatory') {
    return 'border-red-500/60 shadow-lg shadow-red-500/20';
  }
  if (necessity === 'forced') {
    return 'border-accent-orange/60 shadow-lg shadow-accent-orange/20';
  }
  return '';
};

// 获取必要性提示
const getNecessityLabel = (necessity?: ChoiceNecessity, totalChoices?: number) => {
  if (totalChoices === 1) {
    return { icon: <AlertTriangle size={14} />, text: '必须执行', className: 'bg-accent-yellow/20 text-accent-yellow' };
  }
  if (necessity === 'mandatory') {
    return { icon: <AlertTriangle size={14} />, text: '必须选择', className: 'bg-red-500/20 text-red-400' };
  }
  if (necessity === 'forced') {
    return { icon: <AlertTriangle size={14} />, text: '强制推进', className: 'bg-accent-orange/20 text-accent-orange' };
  }
  return null;
};

export const ChoiceButton: React.FC<ChoiceButtonProps> = ({
  choice,
  index,
  onSelect,
  disabled = false,
  totalChoices = 3
}) => {
  const necessityInfo = getNecessityLabel(choice.necessity, totalChoices);

  return (
    <motion.button
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      onClick={() => !disabled && onSelect(choice)}
      disabled={disabled}
      className={`
        text-left p-6 rounded-xl backdrop-blur-sm border transition-all duration-300 group relative overflow-hidden
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${getChoiceColor(choice.type)}
        ${getNecessityStyle(choice.necessity, totalChoices)}
        hover:shadow-2xl hover:border-white/40
        ${totalChoices === 1 ? 'col-span-2' : ''}  // 单选时全宽
      `}
    >
      {/* 背景动画 */}
      {!disabled && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-accent-yellow/0 to-accent-orange/0 group-hover:from-accent-yellow/10 group-hover:to-accent-orange/10"
          initial={{ x: '-100%' }}
          whileHover={{ x: '100%' }}
          transition={{ duration: 0.6 }}
        />
      )}

      <div className="relative flex items-start space-x-4">
        <div className="flex-shrink-0 mt-1">
          {getChoiceIcon(choice.type)}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-bold text-accent-yellow">
              [{choice.id}]
            </span>
            <span className="text-xs px-2 py-1 rounded bg-white/10 text-white/70 uppercase tracking-wider">
              {choice.type}
            </span>
            {/* 必要性标签 */}
            {necessityInfo && (
              <span className={`text-xs px-2 py-1 rounded ${necessityInfo.className} flex items-center space-x-1`}>
                {necessityInfo.icon}
                <span>{necessityInfo.text}</span>
              </span>
            )}
          </div>

          <p className="text-white font-medium leading-relaxed">
            {choice.text}
          </p>

          {choice.consequence && (
            <p className="mt-2 text-sm text-white/60 italic">
              {choice.consequence}
            </p>
          )}

          {/* 推理说明（开发模式显示） */}
          {choice.reasoning && process.env.NODE_ENV === 'development' && (
            <p className="mt-2 text-xs text-white/40 italic">
              💡 {choice.reasoning}
            </p>
          )}
        </div>
      </div>

      {/* 悬浮效果 */}
      {!disabled && (
        <motion.div
          className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-accent-yellow to-accent-orange"
          initial={{ scaleX: 0 }}
          whileHover={{ scaleX: 1 }}
          transition={{ duration: 0.3 }}
        />
      )}
    </motion.button>
  );
};
```

### 2.2.6 前端App组件更新

**修改 web/src/App.tsx，传递总选择数量：**

```typescript
{/* 选择区域 */}
<AnimatePresence>
  {!isLoading && (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-4"
    >
      <h3 className="text-xl font-bold text-white/90 mb-4">
        你的选择将决定故事的走向...
      </h3>

      {/* 如果只有1个选择，显示提示 */}
      {currentState.current_scene.choices.length === 1 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-accent-yellow/10 border border-accent-yellow/30 rounded-lg p-4 mb-4 text-center"
        >
          <p className="text-accent-yellow text-sm">
            ⚠️ 当前情况紧急，你只有这一个选择...
          </p>
        </motion.div>
      )}

      <div className={`grid gap-3 ${currentState.current_scene.choices.length === 1 ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}>
        {currentState.current_scene.choices.map((choice, index) => (
          <ChoiceButton
            key={choice.id}
            choice={choice}
            index={index}
            onSelect={handleChoice}
            disabled={isLoading}
            totalChoices={currentState.current_scene.choices.length}
          />
        ))}
      </div>
    </motion.div>
  )}
</AnimatePresence>
```

### 2.2.7 后端API更新

**修改 api/main.py，序列化新增字段：**

```python
def serialize_story_state(state: StoryState) -> dict:
    """序列化故事状态"""
    # 转换图片路径为完整URL
    image_url = state.current_scene.image_path
    if image_url and not image_url.startswith('http'):
        # 转换相对路径为完整URL
        image_url = f"http://localhost:8000/images/{os.path.basename(image_url)}"

    return {
        "current_scene": {
            "id": state.current_scene.id,
            "image_path": image_url,
            "story_text": state.current_scene.story_text,
            "genre": state.current_scene.genre.value,
            "choices": [
                {
                    "id": choice.id,
                    "text": choice.text,
                    "type": choice.type.value,
                    "consequence": choice.consequence,
                    "story_impact": choice.story_impact,
                    "necessity": choice.necessity.value if hasattr(choice, 'necessity') else "optional",
                    "reasoning": choice.reasoning if hasattr(choice, 'reasoning') else ""
                }
                for choice in state.current_scene.choices
            ],
            "is_ending": state.current_scene.is_ending,
            "ending_type": state.current_scene.ending_type
        },
        "choice_history": state.choice_history,
        "story_progress": state.story_progress,
        "scene_count": state.scene_count,
        "max_scenes": state.max_scenes,
        "is_ending": state.is_ending,
        "story_theme": state.story_theme,
        "user_attributes": state.user_attributes,
        "story_outline": state.story_outline.to_dict() if state.story_outline else None,
        "item_states": state.item_states,
        "npc_relations": state.npc_relations,
        "danger_level": state.danger_level,
        "consecutive_failures": state.consecutive_failures,
        "metadata": getattr(state, 'metadata', {})
    }
```

### 2.2.8 使用场景示例

**场景1：单选（紧急情况）**
```
用户选择：张三发现房门被锁，浓烟从门缝涌入
LLM分析：紧急程度=HIGH，只能选择"立即破门逃生"
返回：choice_count=1, necessity="mandatory"
前端显示：单个大按钮，黄色边框，提示"必须执行"
```

**场景2：双选（二选一困境）**
```
用户选择：李四面对朋友的求助
LLM分析：可以选择"帮助朋友"或"保护自己"
返回：choice_count=2, necessity="optional"
前端显示：两个按钮并排，标准样式
```

**场景3：三选（充分选择）**
```
用户选择：王五在安全的地方观察环境
LLM分析：有时间思考，可以"探索房间"、"询问NPC"、"检查道具"
返回：choice_count=3, necessity="optional"
前端显示：三个按钮并排或垂直排列
```

## 实现优势

1. **自然剧情流**：选择数量反映剧情逻辑，紧急时单选，平缓时多选
2. **用户体验好**：避免"假选择"（实际只有1个合理选项时强制给3个）
3. **视觉反馈明确**：单选时突出显示（加粗边框、全宽），多选时正常显示
4. **开发友好**：包含reasoning字段便于调试和优化
5. **可扩展性**：为后续的道具系统、NPC系统预留了状态追踪字段

### 2.3 提前结局机制
**实施方法：**
- **危险行动成功率计算**：
  - 基础成功率 = LLM评估（30%-90%之间）
  - 用户属性加成：
    - 勇气越高，成功率越高（最高+20%）
    - 智慧越高，成功率越高（最高+15%）
    - 善良不影响成功率
  - 实际成功率 = min(95%, 基础成功率 + 属性加成)
  - 失败时不一定死亡，可能受伤或失去道具
- **提前失败条件**：
  - 仅当关键道具丢失且无法找回时触发
  - 或触发多次失败累积导致体力/资源耗尽
  - 不是单一选择导致死亡
- **死亡结局设计**：
  - 仅当连续3次重大失败时才可能死亡
  - 每次失败记录"危险度"，累积超过阈值才死亡
  - 死亡前必须警告用户"您已经很危险了，慎重选择"

### 2.4 道具/人物对话影响系统
**实施方法：**
- **道具影响规则**：
  - 每个道具在生成时必须指定至少3个后续场景中的使用方式
  - 道具状态（持有/遗失/使用）要在故事状态中保存（state_dict）
  - 在故事继续时检查所有道具状态，影响剧情分支
- **NPC对话规则**：
  - 每个NPC至少要有2次互动（初次见面 + 关键决策时）
  - NPC互动结果必须影响后续选择或剧情走向
  - 帮助/不帮助NPC要有明显不同的后果
- **代码实现**：
  - 添加道具状态追踪系统
  - 添加NPC关系系统（好感度、信任度）
  - 在LLM提示词中要求"根据道具和NPC状态生成剧情"

3.故事生成过程中什么都不显示，可以改一下界面
4，没有回溯功能

