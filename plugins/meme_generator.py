import asyncio
import httpx
from PIL import Image, ImageDraw
from io import BytesIO
from pathlib import Path 
from plugins.base_plugin import BasePlugin
from utils.logger import get_logger

class MemeGenerator(BasePlugin):
    """表情包生成插件"""

    name: str = "表情包生成"
    description: str = "🌟生成表情包，关键词：[制作图片：+内容]，当前可使用的内容有[哒咩]，需@一位群成员"

    current_file = Path(__file__)
    base_image_path = current_file.parent.parent / 'images' / 'Ark_fan_art' / '露比' / '露比_禁止.png'
    mask_path = current_file.parent.parent / 'images' / 'tools' / '露比_禁止蒙版.png'
    output_image_path = current_file.parent.parent / 'temp' / 'meme_output.png'

    def __init__(self):
        super().__init__()
        self.logger = get_logger()

    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)

        # 该功能仅在群聊中响应
        if data.get("message_type") != "group":
            return False

        # 关键词判断
        if not msg.startswith("制作图片：哒咩"):
            return False

        # 检查开关
        if not await self.check_enable(data, bot):
            return True

        # 解析@的用户
        at_list = [
            int(item['data']['qq'])
            for item in data.get('message')
            if item['type'] == 'at'
        ]

        if not at_list:
            await self.send_group_msg(data.get("group_id"), "请@一位群成员哦~")
            return True

        target_user_id = at_list[0]

        try:
            # 获取用户头像
            avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={target_user_id}&s=640"
            avatar_image = await self.download_image(avatar_url)

            if avatar_image is None:
                await self.send_group_msg(data.get("group_id"), "获取头像失败了Σ(っ °Д °;)っ")
                return True

            # 生成梗图
            if not await self.create_meme_image(avatar_image):
                await self.send_group_msg(data.get("group_id"), "生成梗图失败了Σ(っ °Д °;)っ")
                return True

            # 发送图片
            await self.send_group_msg(data.get("group_id"), f"[CQ:image,file={self.output_image_path}]")

            return True

        except Exception as e:
            self.logger.error(f"生成梗图失败: {e}")
            await self.send_group_msg(data.get("group_id"), "生成梗图失败了Σ(っ °Д °;)っ")
            return True

    async def create_meme_image(self, avatar_image: Image.Image) -> bool:
        """根据头像生成最终梗图"""
        try:
            base_image = Image.open(self.base_image_path).convert('RGBA')
            mask_image = Image.open(self.mask_path).convert('RGBA')

            mask_size = mask_image.size
            avatar_resized = avatar_image.resize(mask_size, Image.LANCZOS).convert('RGBA')

            mask_alpha = mask_image.split()[3]
            avatar_resized.putalpha(mask_alpha)

            base_image.paste(avatar_resized, (184, 130), avatar_resized)

            self.output_image_path.parent.mkdir(parents=True, exist_ok=True)
            base_image.save(self.output_image_path, format='PNG')
            return True
        except Exception as e:
            self.logger.error(f"创建梗图失败: {e}")
            return False

    async def download_image(self, url: str) -> Image.Image | None:
        """下载图片"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    image_data = response.content
                    return Image.open(BytesIO(image_data)).convert('RGBA')
        except Exception as e:
            self.logger.error(f"下载图片失败: {e}")
        return None

