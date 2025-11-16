"""
FastAPI后端服务
为Web前端提供故事生成API
"""
import os
import uuid
from pathlib import Path
from typing import Optional
import asyncio

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.services.llm_client_v2 import LLMClient
from src.services.nano_banana_client_fixed import NanoBananaClient
from src.services.story_manager import StoryManager
from src.types.story import StoryState, StoryGenre

# 创建FastAPI应用
app = FastAPI(
    title="交互式故事生成API",
    description="为Web前端提供故事生成服务",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量存储游戏状态
game_states = {}
current_state_id = None

# 创建图片保存目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 创建服务实例
llm_client = LLMClient()
image_client = NanoBananaClient()

@app.get("/")
async def root():
    """根路径"""
    return {"message": "交互式故事生成API运行中", "version": "2.0.0"}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    try:
        # 保存文件
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 返回文件URL
        file_url = f"/uploads/{file_id}_{file.filename}"

        return {
            "success": True,
            "url": file_url,
            "file_id": file_id,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.post("/api/story/start")
async def start_story(
    image_url: str = Form(...),
    genre: str = Form("adventure")
):
    """开始新故事"""
    global current_state_id

    try:
        # 获取完整图片URL
        full_image_url = f"http://localhost:8000{image_url}"

        # 创建故事管理器
        manager = StoryManager()

        # 开始故事
        state = manager.start_story_from_image(
            image_url=full_image_url,
            genre=StoryGenre.ADVENTURE  # 暂时固定为冒险类型
        )

        if not state:
            raise HTTPException(status_code=500, detail="故事初始化失败")

        # 存储状态
        state_id = str(uuid.uuid4())
        game_states[state_id] = {
            "manager": manager,
            "state": state
        }
        current_state_id = state_id

        # 返回状态
        return {
            "success": True,
            "state": serialize_story_state(state),
            "state_id": state_id
        }

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"故事开始失败: {str(e)}")

@app.post("/api/story/continue")
async def continue_story(
    choice_id: str = Form(...),
    state_id: str = Form(...)
):
    """继续故事"""
    try:
        # 获取状态
        if state_id not in game_states:
            raise HTTPException(status_code=404, detail="找不到游戏状态")

        game_data = game_states[state_id]
        manager = game_data["manager"]

        # 继续故事
        success = manager.continue_story(choice_id)

        if not success:
            raise HTTPException(status_code=500, detail="故事继续失败")

        # 更新状态
        game_data["state"] = manager.current_state

        # 返回新状态
        return {
            "success": True,
            "state": serialize_story_state(manager.current_state),
            "state_id": state_id
        }

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"故事继续失败: {str(e)}")

@app.post("/api/story/rollback")
async def rollback_story(
    target_step: int = Form(...),
    state_id: str = Form(...)
):
    """回溯到指定步骤"""
    try:
        # 获取状态
        if state_id not in game_states:
            raise HTTPException(status_code=404, detail="找不到游戏状态")

        game_data = game_states[state_id]
        manager = game_data["manager"]

        # 回溯故事
        success = manager.rollback_to_step(target_step)

        if not success:
            raise HTTPException(status_code=500, detail="故事回溯失败")

        # 更新状态
        game_data["state"] = manager.current_state

        # 返回新状态
        return {
            "success": True,
            "state": serialize_story_state(manager.current_state),
            "state_id": state_id,
            "message": f"已回溯到步骤 {target_step}"
        }

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"故事回溯失败: {str(e)}")

def serialize_story_state(state: StoryState) -> dict:
    """序列化故事状态"""
    # 转换图片路径为完整URL
    image_url = state.current_scene.image_path
    if image_url and not image_url.startswith('http'):
        # 转换相对路径为完整URL
        image_url = f"http://localhost:8000/images/{os.path.basename(image_url)}"

    # 处理场景历史中的图片URL
    scene_history = []
    for scene in state.scene_history:
        scene_copy = scene.copy()
        if scene_copy.get('image_path') and not scene_copy['image_path'].startswith('http'):
            scene_copy['image_path'] = f"http://localhost:8000/images/{os.path.basename(scene_copy['image_path'])}"
        scene_history.append(scene_copy)

    return {
        "current_scene": {
            "id": state.current_scene.id,
            "image_path": image_url,
            "story_text": state.current_scene.story_text,
            "genre": state.current_scene.genre.value,
            "choices": [
                {
                    "id": choice.id,
                    "text": choice.text,
                    "type": choice.type.value,
                    "consequence": choice.consequence,
                    "story_impact": choice.story_impact,
                    "necessity": choice.necessity.value if hasattr(choice, 'necessity') else "optional",
                    "reasoning": choice.reasoning if hasattr(choice, 'reasoning') else ""
                }
                for choice in state.current_scene.choices
            ],
            "is_ending": state.current_scene.is_ending,
            "ending_type": state.current_scene.ending_type
        },
        "choice_history": state.choice_history,
        "scene_history": scene_history,
        "story_progress": state.story_progress,
        "scene_count": state.scene_count,
        "max_scenes": state.max_scenes,
        "is_ending": state.is_ending,
        "story_theme": state.story_theme,
        "user_attributes": state.user_attributes,
        "story_outline": state.story_outline.to_dict() if state.story_outline else None,
        "item_states": state.item_states,
        "npc_relations": state.npc_relations,
        "danger_level": state.danger_level,
        "consecutive_failures": state.consecutive_failures,
        "metadata": getattr(state, 'metadata', {})
    }

# 创建图片目录（如果不存在）
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/images", StaticFiles(directory="images"), name="images")

if __name__ == "__main__":
    import uvicorn
    print("启动FastAPI服务器...")
    print("API文档: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
