"""
CLI界面 - 交互式故事生成系统
"""
import os
import sys
from pathlib import Path
from typing import Optional

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.story_manager import StoryManager
from src.types.story import StoryGenre

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印标题"""
    print("\n" + "=" * 70)
    print("🎭  交互式图片故事生成系统  🎭".center(70))
    print("=" * 70)
    print()

def get_user_image_url() -> Optional[str]:
    """
    获取用户输入的图片URL

    Returns:
        图片URL
    """
    print("\n📸 请选择图片来源:")
    print("  1. 使用之前的测试图片 (宇航员猫)")
    print("  2. 输入新的图片URL")
    print("  3. 退出")

    choice = input("\n请选择 (1-3): ").strip()

    if choice == '1':
        return "https://file17.grsai.com/file/8faba6f97e3a48c0b5e14cc32d878538.png"
    elif choice == '2':
        url = input("请输入图片URL: ").strip()
        if url:
            return url
        else:
            print("❌ URL不能为空")
            return None
    elif choice == '3':
        return None
    else:
        print("❌ 无效选择")
        return None

def get_genre_selection() -> Optional[StoryGenre]:
    """
    获取用户选择的故事类型

    Returns:
        故事类型
    """
    print("\n🎭 请选择故事类型 (留空使用AI推荐):")
    genres = list(StoryGenre)
    for i, genre in enumerate(genres, 1):
        genre_names = {
            StoryGenre.ADVENTURE: "冒险",
            StoryGenre.MYSTERY: "悬疑",
            StoryGenre.FANTASY: "奇幻",
            StoryGenre.SCIFI: "科幻",
            StoryGenre.ROMANCE: "爱情",
            StoryGenre.HORROR: "恐怖",
            StoryGenre.COMEDY: "喜剧",
            StoryGenre.DRAMA: "戏剧"
        }
        print(f"  {i}. {genre_names.get(genre, genre.value)}")

    choice = input("\n请选择 (1-8, 或按Enter跳过): ").strip()

    if not choice:
        return None

    try:
        index = int(choice) - 1
        if 0 <= index < len(genres):
            return genres[index]
        else:
            print("❌ 无效选择")
            return None
    except ValueError:
        print("❌ 请输入数字")
        return None

def display_story_scene(state):
    """
    显示故事场景

    Args:
        state: 故事状态
    """
    print("\n" + "=" * 70)
    print(f"📖 第 {state.scene_count + 1} 幕".center(70))
    print("=" * 70)

    scene = state.current_scene

    print(f"\n🖼️  场景图片:")
    print(f"   {scene.image_path}")

    print(f"\n📝 故事:")
    print(f"   {scene.story_text}")

    print(f"\n❓ 选择你的行动:")
    for choice in scene.choices:
        icons = {
            'action': '⚡',
            'dialogue': '💬',
            'item': '🎒',
            'emotion': '❤️'
        }
        icon = icons.get(choice.type.value, '•')
        print(f"   {icon} [{choice.id}] {choice.text}")

    print(f"\n📊 进度: {state.story_progress:.1f}% ({state.scene_count}/{state.max_scenes})")

def get_user_choice(max_id: str) -> str:
    """
    获取用户选择

    Args:
        max_id: 最大可选ID

    Returns:
        用户选择的选择ID
    """
    while True:
        choice = input("\n请输入选择 (或 'q' 退出): ").strip().lower()

        if choice == 'q':
            return 'quit'

        # 检查是否为有效ID
        if choice in ['1', '2', '3'] and choice in max_id:
            return choice

        print(f"❌ 请输入有效的选择 (1-3)")

def main():
    """主函数"""
    clear_screen()
    print_header()

    # 初始化故事管理器
    story_manager = StoryManager()

    # 获取图片
    image_url = get_user_image_url()
    if not image_url:
        print("\n👋 再见！")
        return

    # 获取故事类型
    genre = get_genre_selection()

    # 开始故事
    print("\n🚀 正在启动故事...")
    state = story_manager.start_story_from_image(image_url, genre)

    if not state:
        print("\n❌ 故事启动失败")
        input("\n按Enter键退出...")
        return

    # 游戏主循环
    while state and not state.is_complete():
        clear_screen()
        print_header()

        # 显示当前场景
        display_story_scene(state)

        # 获取用户选择
        choice_id = get_user_choice('123')
        if choice_id == 'quit':
            print("\n👋 感谢游玩！")
            break

        # 继续故事
        if not story_manager.continue_story(choice_id):
            print("\n❌ 故事继续失败")
            input("\n按Enter键退出...")
            break

        # 短暂暂停以便用户阅读
        input("\n按Enter键继续...")

    # 游戏结束
    clear_screen()
    print_header()

    if state and state.is_complete():
        print("\n🎭 故事结束！".center(70))
        print("=" * 70)
        print(f"\n📖 最终场景:")
        print(f"   {state.current_scene.story_text}")
        print(f"\n📊 游戏统计:")
        print(f"   总场景数: {state.scene_count}")
        print(f"   进度: {state.story_progress:.1f}%")
        print(f"\n✅ 感谢游玩！")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
