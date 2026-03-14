
import httpx
import json
from plugins.base_plugin import BasePlugin

class RainbowFart(BasePlugin):
    """彩虹屁插件"""
    
    # 插件基本信息
    name: str = "彩虹屁"
    description: str = "🌟关键词：[彩虹屁]，即可返回一条彩虹屁~"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        # 获取消息
        msg = self.get_texts(data)

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False
        
        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            return False

        # 关键词判断
        if msg == "彩虹屁":
            # 检查开关
            if not await self.check_enable(data, bot):
                return True

            # 请求API    
            try:
                url = "https://api.shadiao.pro/chp"
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    res_json = response.json()
                send_buff = res_json["data"]["text"]
            except Exception as e:
                send_buff = f"啊这......好像出了一点问题\n(开始胡言乱语)\nError of rainbow_fart:\n{e}"

            # 发送信息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)

            return True
        
        return False