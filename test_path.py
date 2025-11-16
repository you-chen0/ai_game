"""
测试模块导入路径
"""
import sys
from pathlib import Path

print("当前工作目录:", Path.cwd())
print("脚本路径:", Path(__file__).parent)

# 添加src目录
src_path = Path(__file__).parent / "src"
print("src路径:", src_path)
print("src是否存在:", src_path.exists())

sys.path.insert(0, str(src_path))
print("\nPython路径:", sys.path[:3])

# 测试导入
try:
    print("\n尝试导入src.services.llm_client_v2...")
    from src.services.llm_client_v2 import LLMClient
    print("✅ 导入成功!")

    print("\n尝试导入src.types.story...")
    from src.types.story import StoryGenre
    print("✅ 导入成功!")

    print("\n尝试导入src.services.story_manager...")
    from src.services.story_manager import StoryManager
    print("✅ 导入成功!")

except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
