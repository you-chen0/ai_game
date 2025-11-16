#!/usr/bin/env python
"""
启动FastAPI后端服务器
"""
import os
import sys

# 设置Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    print("启动FastAPI服务器...")
    print("API文档: http://localhost:8000/docs")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
