
from plugins.base_plugin import BasePlugin

class ViewAffection(BasePlugin):
    """查询好感度插件"""
    
    # 插件基本信息
    name: str = "查询好感度"
    description: str = "🌟关键词：[查询好感度]，点击查看地球Online旮旯给木好感度系统💗~"
    
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
        if msg == "查询好感度":
            # 检查开关
            if not await self.check_enable(data, bot):
                return True

            send_buff = "点击查看地球Online旮旯给木好感度系统💗https://h5.qzone.qq.com/close/rank"

            # 发送信息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)

            return True
        
        return False