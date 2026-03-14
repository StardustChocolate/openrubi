
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from plugins.update_logs import get_update

class InviteProtect(BasePlugin):
    """受邀保护"""
    
    # 插件基本信息
    name: str = "受邀保护"
    description: str = "🌟由于QQ端人数过少的群聊邀请会自动同意，设置此功能可以作为保护防止乱拉群\n🌟监护人指令:\n[添加群(输入群号，无需括号)]即可登记群聊\n[删除群(输入群号，无需括号)]取消登记(同时会自动退群)\n[列出群]即可列出已登记的群聊"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_request(self, data, bot) -> bool:
        """处理请求事件"""
        if data.get("request_type") == "group" and data.get("sub_type") == "invite":    # 群邀请
            self_info = await config_manager.get_self_info()
            if str(data.get("group_id")) in self_info["group_register"]:  # 允许的群聊自动同意
                await bot.api_client.call_api(
                    action="set_group_add_request",
                    params = {
                        "flag": data.get("flag"),
                        "sub_type": data.get("sub_type"),
                        "approve": True,
                        "reason": ""
                    }
                )
            return True
        
        return False

    async def on_notice(self, data, bot) -> bool:
        """处理通知事件"""
        if data.get("notice_type") == "group_increase" and data.get("user_id") == data.get("self_id"):    # 自己的入群通知
            self_info = await config_manager.get_self_info()
            if str(data.get("group_id")) not in self_info["group_register"]:  # 未允许的群聊自动退群
                await bot.api_client.call_api(
                    action="set_group_leave",   # 退出群聊
                    params = {
                        "group_id": data.get("group_id")
                    }
                )
            else:
                gid = str(data.get("group_id"))
                group_info = await config_manager.get_group_info(gid)   # 获取自带初始化
                await self.send_group_msg(data.get("group_id"), "呜呜呜。。。露比终于见到你了团长~ヽ(*。>Д<)o゜")
                await self.send_group_msg(data.get("group_id"), get_update())   # 发更新日志
            return True

        return False

    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)
        bot_admin = data.get("user_id") in config_manager.info["admin_id"]  # 检查权限
        
        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False
            
        # 添加群
        if msg.startswith("添加群") and msg[3:].isdigit(): 
            gid = msg[3:]
            if bot_admin:
                self_info = await config_manager.get_self_info()
                if gid in self_info["group_register"]:
                    send_buff = "该群聊已添加过了哦~\n(｡•̀ᴗ-)✧゜"
                else:
                    self_info["group_register"].append(gid)
                    await config_manager.save_self_info()
                    send_buff = "嗯呐(*ෆ´ ˘ `ෆ*)♡"
            else:
                send_buff = "你的权限不够了啦\nヽ(*。>Д<)o゜"
            
            # 发送消息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)  

            return True

        # 删除群
        if msg.startswith("删除群") and msg[3:].isdigit():
            gid = msg[3:]
            if bot_admin:
                self_info = await config_manager.get_self_info()
                if gid in self_info["group_register"]:
                    self_info["group_register"].remove(gid)
                    await config_manager.save_self_info()
                    send_buff = "嗯呐(*ෆ´ ˘ `ෆ*)♡"
                    await bot.api_client.call_api(
                        action="set_group_leave",   # 退出群聊
                        params = {
                            "group_id": int(gid)
                        }
                    )
                else:
                    send_buff = "该群聊还未添加哦~\n(｡•̀ᴗ-)✧"
            else:
                send_buff = "你的权限不够了啦\nヽ(*。>Д<)o゜"

            # 发送消息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)  

            return True
        
        # 列出群
        if msg == "列出群":
            if bot_admin:
                self_info = await config_manager.get_self_info()
                send_buff = "\n".join(self_info["group_register"])
            else:
                send_buff = "你的权限不够了啦\nヽ(*。>Д<)o゜"

            # 发送消息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff) 

            return True 

        return False