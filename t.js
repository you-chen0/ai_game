import requestsimport json
 
API_URL = "https://api.grsai.com/v1/draw/nano-banana" # 或使用国内直连节点API_KEY = "你的GrsAI_API_Key"headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"}data = {
    "model": "nano-banana-fast",
    "prompt": "一只穿着宇航服的猫，在月球上喝咖啡，电影质感"}response = requests.post(API_URL, headers=headers, json=data)if response.status_code == 200:
    result = response.json()
    if result['status'] == 'succeeded':
        image_url = result['results'][0]['url']
        print("生成成功！图片URL:", image_url)else:
    print("生成失败")