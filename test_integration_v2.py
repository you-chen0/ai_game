"""
集成测试 v2 - 使用改进的LLM客户端
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.services.llm_client_v2 import LLMClient
from src.services.nano_banana_client import NanoBananaClient
from src.types.story import StoryGenre

def test_llm_client():
    """测试LLM客户端"""
    print("=" * 70)
    print("🧪 测试1：LLM客户端")
    print("=" * 70)

    client = LLMClient()

    # 测试图片分析
    print("\n1. 测试图片分析...")
    test_image_url = "https://file17.grsai.com/file/8faba6f97e3a48c0b5e14cc32d878538.png"
    analysis = client.analyze_image(test_image_url)

    if not analysis:
        print("   ❌ 图片分析失败")
        return False

    print(f"   ✅ 分析成功")
    print(f"   - 场景: {analysis.scene_description[:100]}...")
    print(f"   - 角色数: {len(analysis.characters)}")
    print(f"   - 物品数: {len(analysis.key_objects)}")
    print(f"   - 建议类型: {analysis.genre_suggestion}")

    # 测试故事生成
    print("\n2. 测试故事生成...")
    result = client.generate_initial_story(analysis, StoryGenre.SCIFI)

    if not result:
        print("   ❌ 故事生成失败")
        return False

    story_text, choices = result
    print(f"   ✅ 故事生成成功")
    print(f"   - 故事长度: {len(story_text)} 字符")
    print(f"   - 选择数: {len(choices)}")

    for i, choice in enumerate(choices, 1):
        print(f"     [{choice.id}] {choice.text[:50]}...")

    print("\n" + "=" * 70)
    print("✅ LLM客户端测试通过！")
    print("=" * 70)
    return True

def test_nano_banana():
    """测试nano banana客户端"""
    print("\n" + "=" * 70)
    print("🧪 测试2：nano banana客户端")
    print("=" * 70)

    client = NanoBananaClient()

    print("\n1. 测试图片生成...")
    prompt = "一只穿着宇航服的猫在月球上喝咖啡，科幻风格"
    image_path = client.generate_image(prompt, "images")

    if not image_path:
        print("   ❌ 图片生成失败")
        return False

    print(f"   ✅ 图片生成成功")
    print(f"   - 图片路径: {image_path}")

    print("\n" + "=" * 70)
    print("✅ nano banana客户端测试通过！")
    print("=" * 70)
    return True

def main():
    """主测试函数"""
    print("\n🚀 开始集成测试...\n")

    # 测试LLM客户端
    if not test_llm_client():
        print("\n❌ LLM客户端测试失败")
        return False

    # 测试nano banana客户端
    if not test_nano_banana():
        print("\n❌ nano banana客户端测试失败")
        return False

    print("\n" + "=" * 70)
    print("🎉 所有测试通过！")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
