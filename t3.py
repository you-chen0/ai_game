import requests
import json
import os

# GrsAI API configuration
API_URL = "https://api.grsai.com/v1/chat/completions"
API_KEY = os.getenv("GRS_AI_API_KEY", "sk-c15186bd658749e0a4ad09ef6af985d8")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 图片URL（之前生成的图片）
IMAGE_URL = "https://file17.grsai.com/file/8faba6f97e3a48c0b5e14cc32d878538.png"

# 图片分析提示词
image_analysis_prompt = """
你是一个专业的图片内容分析专家。请仔细分析这张图片，并提取以下信息：

1. **场景描述**: 详细描述图片中的环境、背景、氛围
2. **角色分析**: 识别图片中的角色（如果有），包括外观、表情、动作
3. **关键物品**: 列出图片中的重要物品或道具
4. **色彩与风格**: 描述图片的色调、风格（科幻、奇幻、写实等）
5. **故事元素**: 基于图片内容，推测可能的故事背景或情节
6. **情感氛围**: 图片传达的情感或情绪

请以JSON格式返回分析结果：
{
  "scene_description": "场景详细描述",
  "characters": [
    {"name": "角色名", "description": "外观和动作描述", "emotion": "情绪状态"}
  ],
  "key_objects": ["物品1", "物品2", "物品3"],
  "color_style": {"dominant_colors": ["颜色1", "颜色2"], "style": "风格描述"},
  "story_elements": "可能的故事背景和情节推测",
  "emotional_tone": "情感氛围描述",
  "genre_suggestion": "建议的故事类型"
}
"""

# 基础故事生成提示词
story_generation_prompt = """
基于以下图片分析结果，创作一个引人入胜的故事开头：

{image_analysis}

要求：
1. 故事类型：{genre}
2. 字数：200-300字
3. 包含环境描写、角色介绍、情节铺垫
4. 营造悬疑或冒险氛围
5. 引出3个不同类型的选择

JSON格式返回：
{
  "story": "故事内容",
  "choices": [
    {"id": "1", "text": "行动选择", "type": "action"},
    {"id": "2", "text": "对话选择", "type": "dialogue"},
    {"id": "3", "text": "物品选择", "type": "item"}
  ]
}
"""

data = {
    "model": "gemini-2.5-flash-lite",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": image_analysis_prompt},
                {"type": "image_url", "image_url": {"url": IMAGE_URL}}
            ]
        }
    ],
    "temperature": 0.8,
    "max_tokens": 2000
}

def test_image_analysis():
    """测试图片理解和分析"""
    print("🖼️  开始图片分析测试...")
    print(f"图片URL: {IMAGE_URL}")
    print("="*60)

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()

            if 'choices' in result and result['choices']:
                content = result['choices'][0].get('message', {}).get('content', '')

                print("\n📊 图片分析结果:")
                print("="*60)
                print(content)
                print("="*60)

                # 尝试解析JSON
                try:
                    # 处理markdown代码块
                    if content.startswith('```'):
                        lines = content.split('\n')
                        json_lines = [line for line in lines if not line.startswith('```')]
                        content = '\n'.join(json_lines)

                    parsed = json.loads(content)
                    print("\n✅ 图片分析完成！")

                    print(f"\n📋 分析摘要:")
                    print(f"  - 场景: {parsed.get('scene_description', '')[:100]}...")
                    print(f"  - 角色数: {len(parsed.get('characters', []))}")
                    print(f"  - 物品数: {len(parsed.get('key_objects', []))}")
                    print(f"  - 建议类型: {parsed.get('genre_suggestion', 'N/A')}")
                    print(f"  - 情感氛围: {parsed.get('emotional_tone', 'N/A')}")

                    return parsed
                except json.JSONDecodeError:
                    print("\n⚠️ 响应不是有效JSON，但分析已成功")
                    return content

            return None
        else:
            print(f"\n❌ API调用失败: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_story_from_analysis(analysis_result, genre="adventure"):
    """基于图片分析生成故事"""
    print(f"\n📖 基于分析结果生成故事...")
    print(f"故事类型: {genre}")
    print("="*60)

    # 如果分析结果是字典，转换为可读格式
    if isinstance(analysis_result, dict):
        # 创建一个简洁的格式化字符串
        image_analysis = f"""
场景: {analysis_result.get('scene_description', '')}

角色: {', '.join([c.get('name', '') + ':' + c.get('description', '') for c in analysis_result.get('characters', [])])}

物品: {', '.join(analysis_result.get('key_objects', []))}

风格: {analysis_result.get('color_style', {}).get('style', '')}

故事背景: {analysis_result.get('story_elements', '')}

情感氛围: {analysis_result.get('emotional_tone', '')}
"""
    else:
        image_analysis = str(analysis_result)

    # 使用简单的字符串连接而不是format，避免花括号转义问题
    story_prompt = f"""
基于以下图片分析结果，创作一个引人入胜的故事开头：

{image_analysis}

要求：
1. 故事类型：{genre}
2. 字数：200-300字
3. 包含环境描写、角色介绍、情节铺垫
4. 营造悬疑或冒险氛围
5. 引出3个不同类型的选择

请以JSON格式返回：
```json
{{
  "story": "故事内容",
  "choices": [
    {{"id": "1", "text": "行动选择", "type": "action"}},
    {{"id": "2", "text": "对话选择", "type": "dialogue"}},
    {{"id": "3", "text": "物品选择", "type": "item"}}
  ]
}}
```
"""

    story_data = {
        "model": "gemini-2.5-flash-lite",
        "messages": [
            {"role": "user", "content": story_prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 1500
    }

    try:
        response = requests.post(API_URL, headers=headers, json=story_data, timeout=60)

        if response.status_code == 200:
            result = response.json()

            if 'choices' in result and result['choices']:
                content = result['choices'][0].get('message', {}).get('content', '')

                print("\n📚 生成的故事:")
                print("="*60)
                print(content)
                print("="*60)

                # 尝试解析JSON
                try:
                    if content.startswith('```'):
                        lines = content.split('\n')
                        json_lines = [line for line in lines if not line.startswith('```')]
                        content = '\n'.join(json_lines)

                    parsed = json.loads(content)
                    print("\n✅ 故事生成完成！")
                    return parsed
                except json.JSONDecodeError:
                    print("\n⚠️ 响应不是有效JSON，但故事已生成")
                    return content

            return None
        else:
            print(f"\n❌ 故事生成失败: {response.status_code}")
            return None

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 图片理解与故事生成测试")
    print("=" * 60)

    # 第一步：分析图片
    analysis = test_image_analysis()

    if analysis:
        print(f"\n{'='*60}")
        print("✅ 第一阶段完成：图片分析")
        print(f"{'='*60}")

        # 第二步：生成故事
        story = generate_story_from_analysis(analysis)

        if story:
            print(f"\n{'='*60}")
            print("✅ 第二阶段完成：故事生成")
            print("🎉 全流程测试成功！")
            print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print("⚠️ 第二阶段失败：故事生成")
            print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ 第一阶段失败：图片分析")
        print(f"{'='*60}")
