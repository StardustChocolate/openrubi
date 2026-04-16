
import asyncio
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from utils.time_parser import extract_seconds

class Mute(BasePlugin):
    """测试插件"""
    
    # 插件基本信息
    name: str = "禁言"
    description: str = "🌟关键词：[禁言、沉默]，@后输入对应时长，可发动沉默魔法;[解禁、解除禁言、解除沉默]可以解除禁言\n🌟该功能需要管理员权限哦~"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        # 只响应群消息
        if data.get("message_type") != "group":
            return False
        
        # 获取消息
        msg = self.get_texts(data)
        # 获取权限
        bot_admin = data.get("user_id") in config_manager.info["admin_id"]
        group_admin = data.get("sender", {}).get("role") in ["owner", "admin"]

        # 匹配关键词
        if msg.startswith(("禁言", "沉默")):
            content = msg[2:].strip()  # 获取关键词后的内容

            # 解析时长
            time_seconds = extract_seconds(content)
            if time_seconds <= 0:
                return False
            
            # 获取被禁言用户列表
            user_id_list = [str(at["data"]["qq"]) for at in data.get("message") if at.get("type") == "at"]
            if str(data.get("self_id")) in user_id_list:
                user_id_list.remove(str(data.get("self_id")))   # 移除自身
            if not user_id_list:
                return False
            
            # 权限检查
            if not (bot_admin or group_admin):
                await self.send_group_msg(data.get("group_id"), "你的权限还不够呢\nヽ(*。>Д<)o゜")
                return True
            
            # 获取自身是否为管理员
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
            if member_info.get("role") not in ["owner", "admin"]:
                await self.send_group_msg(data.get("group_id"), "我还不是管理员呢\nヽ(*。>Д<)o゜")
                return True
            
            # 执行禁言
            for user_id in user_id_list:
                await bot.api_client.call_api(
                    action="set_group_ban",
                    params = {
                        "group_id": data.get("group_id"),
                        "user_id": user_id,
                        "duration": time_seconds
                    }
                )
            await self.send_group_msg(data.get("group_id"), "沉默魔法，发动！*(੭*ˊᵕˋ)੭*ଘ")
            return True
        
        elif msg in ["解禁", "解除禁言", "解除沉默"]:

            # 获取被解禁用户列表
            user_id_list = [str(at["data"]["qq"]) for at in data.get("message") if at.get("type") == "at"]
            if not user_id_list:
                await self.send_group_msg(data.get("group_id"), "请至少@一个用户哦\n( •̀ ω •́ )y")
                return True
            if str(data.get("self_id")) in user_id_list:
                user_id_list.remove(str(data.get("self_id")))   # 移除自身

            # 权限检查
            if not (bot_admin or group_admin):
                await self.send_group_msg(data.get("group_id"), "你的权限还不够呢\nヽ(*。>Д<)o゜")
                return True
            
            # 获取自身是否为管理员
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
            if member_info.get("role") not in ["owner", "admin"]:
                await self.send_group_msg(data.get("group_id"), "我还不是管理员呢\nヽ(*。>Д<)o゜")
                return True

            # 执行解禁
            for user_id in user_id_list:
                await bot.api_client.call_api(
                    action="set_group_ban",
                    params = {
                        "group_id": data.get("group_id"),
                        "user_id": user_id,
                        "duration": 0
                    }
                )
            await self.send_group_msg(data.get("group_id"), "沉默魔法，解除！*(੭*ˊᵕˋ)੭*ଘ")
            return True


        return False