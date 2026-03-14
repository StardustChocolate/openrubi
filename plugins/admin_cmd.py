
import logging
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from utils.logger import get_logger

class AdminCmd(BasePlugin):
    """监护人指令"""
    
    # 插件基本信息
    name: str = "监护人指令"
    description: str = ""
    
    def __init__(self):
        super().__init__()
        self.priority = 10  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        # 获取消息
        msg = self.get_texts(data)

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False

        bot_admin = data.get("user_id") in config_manager.info["admin_id"]  # 检查权限

        # 关键词判断
        if msg == "调试模式":
            if bot_admin:
                logger = get_logger()
                logger.setLevel(logging.DEBUG)
                send_buff = "已切换为调试模式"
            else:
                send_buff = "你的权限还不够呢\nヽ(*。>Д<)o゜"
            # 发送信息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)
            
            return True

        elif msg == "退出调试模式":
            if bot_admin:
                logger = get_logger()
                logger.setLevel(logging.INFO)
                send_buff = "已退出调试模式"
            else:
                send_buff = "你的权限还不够呢\nヽ(*。>Д<)o゜"
            # 发送信息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)
            
            return True
        
        return False