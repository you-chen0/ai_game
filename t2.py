import requests
import json
import os
import time

# GrsAI API configuration
API_URL = "https://api.grsai.com/v1/chat/completions"  # LLM API endpoint
API_KEY = os.getenv("GRS_AI_API_KEY", "sk-c15186bd658749e0a4ad09ef6af985d8")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Test data for LLM
test_prompt = """
你是一个创意故事生成器。请根据以下图片描述创作一个冒险故事的开头：

图片描述：一个穿着红色斗篷的小女孩站在森林入口，手里拿着一盏灯笼，远处传来神秘的歌声。

要求：
1. 故事要有悬疑和冒险元素
2. 字数控制在200-300字
3. 包含3个不同的选择选项
4. 选择应推动情节发展

请以JSON格式返回，格式如下：
{
  "story": "故事内容",
  "choices": [
    {"id": "1", "text": "选择1", "type": "action"},
    {"id": "2", "text": "选择2", "type": "dialogue"},
    {"id": "3", "text": "选择3", "type": "item"}
  ]
}
"""

data = {
    "model": "gemini-2.5-flash-lite",
    "messages": [
        {"role": "user", "content": test_prompt}
    ],
    "temperature": 0.8,
    "max_tokens": 1500
}

def test_llm():
    """Test LLM API call"""
    print("Calling LLM API (gemini-2.5-flash-lite)...")
    print(f"Model: {data['model']}")
    print(f"Temperature: {data['temperature']}")
    print("\nPrompt:")
    print("="*60)
    print(test_prompt)
    print("="*60)

    start_time = time.time()

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)

        elapsed_time = time.time() - start_time
        print(f"\n✓ Request completed in {elapsed_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")

        if response.status_code == 200:
            result = response.json()
            print(f"\nFull response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            if 'choices' in result and result['choices']:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"\n{'-'*60}")
                print(f"Generated Story:")
                print(f"{'-'*60}")
                print(content)
                print(f"{'-'*60}")

                # Try to parse as JSON
                try:
                    parsed = json.loads(content)
                    print("\n✓ Successfully parsed as JSON!")
                    return parsed
                except json.JSONDecodeError as e:
                    print(f"\n⚠ Content is not valid JSON: {e}")
                    print("Returning raw content...")
                    return content

            return result
        else:
            print(f"\n✗ Request failed: {response.status_code}")
            print(f"Error response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("\n⚠ Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Network request error: {e}")
        return None
    except Exception as e:
        print(f"\n✗ Unknown error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Set API key from environment variable if available
    API_KEY = os.getenv("GRS_AI_API_KEY", API_KEY)

    print(f"Using API Key: {API_KEY[:10]}...")
    print("="*60)

    # Run test
    result = test_llm()

    if result:
        print(f"\n{'='*60}")
        print("✓ Test successful!")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("✗ Test failed")
        print(f"{'='*60}")
