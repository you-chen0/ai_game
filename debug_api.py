"""
调试LLM API响应
"""
import requests
import json
import os

API_URL = "https://api.grsai.com/v1/chat/completions"
API_KEY = os.getenv("GRS_AI_API_KEY", "sk-c15186bd658749e0a4ad09ef6af985d8")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 测试简单提示
test_data = {
    "model": "gemini-2.5-flash-lite",
    "messages": [
        {"role": "user", "content": "测试消息"}
    ],
    "temperature": 0.7,
    "max_tokens": 500
}

print("测试API调用...")
response = requests.post(API_URL, headers=headers, json=test_data, timeout=60)

print(f"状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
print(f"响应内容前500字符:")
print(response.text[:500])

# 尝试解析JSON
try:
    result = response.json()
    print(f"\n✅ JSON解析成功")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
except Exception as e:
    print(f"\n❌ JSON解析失败: {e}")
