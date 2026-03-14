
from plugins.base_plugin import BasePlugin
from plugins.update_logs import get_update

class AutoApproval(BasePlugin):
    """自动审批插件"""
    
    # 插件基本信息
    name: str = "自动审批"
    description: str = ""
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_request(self, data, bot) -> bool:
        """处理请求事件"""
        if data.get("request_type") == "friend" :    # 好友请求
            # 可以自定义过滤条件，当前默认为同意
            await bot.api_client.call_api(
                action="set_friend_add_request",
                params = {
                    "flag": data.get("flag"),
                    "approve": True,
                    "remark": ""
                }
            )
            return True
        
        return False

    async def on_notice(self, data, bot) -> bool:
        """处理通知事件"""
        if data.get("notice_type") == "friend_add":    # 新好友通知
            await self.send_private_msg(data.get("user_id"), get_update())   # 发更新日志
            
            return True

        return False