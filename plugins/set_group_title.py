
from plugins.base_plugin import BasePlugin

class SetGroupTitle(BasePlugin):
    """设置群头衔"""
    
    # 插件基本信息
    name: str = "设置群头衔"
    description: str = "🌟关键词：[获取头衔：+内容]即可获取群头衔啦（内容为空视为取消头衔）\n🌟该功能仅在我为群主的时候生效哦~"
    
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

        # 关键词判断
        if data.get("message_type") == "group":     # 该功能仅在群聊生效
            if msg.startswith("获取头衔"):
                title = msg.lstrip('获取头衔：:') # 截取头衔内容
                # 获取自身是否为群主
                member_info = await bot.api_client.call_api(
                    action="get_group_member_info",
                    params = {
                        "group_id": data.get("group_id"), 
                        "user_id": data.get("self_id")
                    }
                )
                if not member_info:
                    await self.send_group_msg(data.get("group_id"), "啊这。。。获取自身信息出错啦Σ(っ °Д °;)っ")
                    return True

                if member_info.get("role") != "owner":
                    send_buff = "我还不是群主呢\nヽ(*。>Д<)o゜"
                else:
                    send_buff = "嗯呐(*ෆ´ ˘ `ෆ*)♡"
                    await bot.api_client.call_api(
                        action="set_group_special_title",
                        params = {
                            "group_id": data.get("group_id"), 
                            "user_id": data.get("user_id"),
                            "special_title": title
                        }
                    )
                await self.send_group_msg(data.get("group_id"), send_buff)
                
                return True
        
        return False