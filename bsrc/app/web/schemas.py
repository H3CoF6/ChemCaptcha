from pydantic import BaseModel
from typing import List

class CaptchaGenerateResponse(BaseModel):
    """验证码生成响应"""
    slug: str                 # 插件类型 (方便前端debug，或者生产环境知道是啥)
    img_base64: str           # 图片数据
    width: int
    height: int
    prompt: str               # 人类可读提示 (如：请点击所有的芳香环)
    token: str                # 加密后的答案 (前端验证时传回)

class Point(BaseModel):
    x: float
    y: float

class CaptchaVerifyRequest(BaseModel):
    """验证请求"""
    token: str                # 生成接口返回的 token
    user_input: List[Point]   # 用户点击的坐标点列表

class CaptchaVerifyResponse(BaseModel):
    """验证结果"""
    success: bool
    message: str