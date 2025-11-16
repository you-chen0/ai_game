#!/usr/bin/env python
"""
启动CLI - 从项目根目录运行
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 设置环境变量
os = __import__('os')
os.environ['PYTHONPATH'] = str(src_path)

# 导入并运行CLI
if __name__ == "__main__":
    from cli.main import main
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
