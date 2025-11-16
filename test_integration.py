"""
集成测试脚本
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.services.story_manager import StoryManager
from src.types.story import StoryGenre

def test_story_manager():
    """测试故事管理器"""
    print("=" * 70)
    print("🧪 集成测试：交互式故事生成系统")
    print("=" * 70)

    # 创建故事管理器
    print("\n1. 创建故事管理器...")
    manager = StoryManager()
    print("   ✅ 成功")

    # 使用之前的测试图片开始故事
    print("\n2. 开始新故事...")
    test_image_url = "https://file17.grsai.com/file/8faba6f97e3a48c0b5e14cc32d878538.png"
    state = manager.start_story_from_image(test_image_url, StoryGenre.SCIFI)

    if not state:
        print("   ❌ 故事启动失败")
        return False

    print("   ✅ 成功")
    print(f"   - 场景ID: {state.current_scene.id}")
    print(f"   - 故事类型: {state.current_scene.genre.value}")
    print(f"   - 选择数量: {len(state.current_scene.choices)}")

    # 显示初始场景
    print("\n3. 显示初始场景:")
    print("   " + "-" * 66)
    print(f"   {state.current_scene.story_text[:200]}...")
    print("   " + "-" * 66)
    print("   可选选择:")
    for choice in state.current_scene.choices:
        print(f"     [{choice.id}] {choice.text[:50]}...")

    # 测试选择继续
    if state.current_scene.choices:
        print("\n4. 测试选择继续...")
        first_choice = state.current_scene.choices[0]
        success = manager.continue_story(first_choice.id)

        if not success:
            print("   ❌ 继续故事失败")
            return False

        print("   ✅ 成功")
        print(f"   - 新场景ID: {state.current_scene.id}")
        print(f"   - 进度: {state.story_progress:.1f}%")
        print(f"   - 场景数量: {state.scene_count}")

    print("\n" + "=" * 70)
    print("✅ 所有测试通过！")
    print("=" * 70)

    return True

if __name__ == "__main__":
    try:
        success = test_story_manager()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
