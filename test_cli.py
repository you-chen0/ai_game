"""
简化CLI测试 - 不需要用户交互
"""
import sys
from pathlib import Path

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.services.story_manager import StoryManager
from src.types.story import StoryGenre

def test_cli():
    """测试CLI基本功能"""
    print("=" * 70)
    print("🧪 CLI功能测试")
    print("=" * 70)

    # 创建故事管理器
    print("\n1. 创建故事管理器...")
    manager = StoryManager()
    print("   ✅ 创建成功")

    # 开始故事
    print("\n2. 开始新故事...")
    test_image_url = "https://file17.grsai.com/file/8faba6f97e3a48c0b5e14cc32d878538.png"
    state = manager.start_story_from_image(test_image_url, StoryGenre.SCIFI)

    if not state:
        print("   ❌ 故事启动失败")
        return False

    print("   ✅ 故事启动成功")
    print(f"   - 场景: {state.current_scene.id}")
    print(f"   - 类型: {state.current_scene.genre.value}")
    print(f"   - 选择数: {len(state.current_scene.choices)}")

    # 显示场景信息
    print("\n3. 显示场景信息...")
    manager.display_current_scene()

    # 测试选择
    print("\n4. 测试用户选择...")
    if state.current_scene.choices:
        first_choice = state.current_scene.choices[0]
        print(f"   选择: {first_choice.text}")
        success = manager.continue_story(first_choice.id)

        if not success:
            print("   ❌ 继续故事失败")
            return False

        print("   ✅ 继续故事成功")
        print(f"   - 新场景: {state.current_scene.id}")
        print(f"   - 进度: {state.story_progress:.1f}%")

    print("\n" + "=" * 70)
    print("✅ CLI功能测试通过！")
    print("=" * 70)

    # 获取当前状态
    current = manager.get_current_state()
    if current:
        print(f"\n📊 当前状态:")
        print(f"   - 场景数: {current.scene_count}")
        print(f"   - 进度: {current.story_progress:.1f}%")
        print(f"   - 是否完成: {current.is_complete()}")

    return True

if __name__ == "__main__":
    try:
        success = test_cli()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
