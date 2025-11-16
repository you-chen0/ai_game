#!/usr/bin/env python
"""
交互式故事生成系统 - 启动脚本
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 运行CLI
if __name__ == "__main__":
    try:
        from cli.main import main
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
