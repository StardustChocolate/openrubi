from abc import ABC, abstractmethod
from typing import Optional, Any
from configs.config_manager import config_manager

class BasePlugin(ABC):
    """插件基类"""
    
    # 插件基本信息
    name: str = "base_plugin"
    description: str = "插件基类"
    
    def __init__(self):
        self.enabled = True
        self.bot = None
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50

    async def on_load(self, bot):
        """插件加载时调用"""
        self.bot = bot
        
    async def handle_event(self, data, bot) -> Optional[bool]:
        """
        处理事件
        返回True可拦截事件，代表事件已被处理，阻止其他插件继续处理
        """
        if not self.enabled:
            return False
            
        # 根据事件类型分发到具体处理方法
        match data.get('post_type'):
            case 'message':
                return await self.on_message(data, bot)
            case 'notice':
                return await self.on_notice(data, bot)
            case 'request':
                return await self.on_request(data, bot)
            case 'meta_event':
                return await self.on_meta_event(data, bot)
            
        return False
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        return False
        
    async def on_notice(self, data, bot) -> bool:
        """处理通知事件"""
        return False
        
    async def on_request(self, data, bot) -> bool:
        """处理请求事件"""
        return False
        
    async def on_meta_event(self, data, bot) -> bool:
        """处理元事件"""
        return False
        
    async def send_private_msg(self, user_id: int, message: str):
        """发送私聊消息"""
        if self.bot:
            data = {
                "action": "send_private_msg",
                "params": {
                    "user_id": user_id,
                    "message": message
                }
            }
            await self.bot.send_message(data)
            
    async def send_group_msg(self, group_id: int, message: str):
        """发送群聊消息"""
        if self.bot:
            data = {
                "action": "send_group_msg",
                "params": {
                    "group_id": group_id,
                    "message": message
                }
            }
            await self.bot.send_message(data)

    async def check_enable(self, data, bot, disable_notice=True, close_notice=True) -> bool:
        """检查开关状态"""
        self_info = await config_manager.get_self_info()
        if data.get("message_type") == "private":   # 私聊中
            if self.name in self_info["disable_plugins"]:
                if disable_notice:  # 是否触发提示
                    await self.send_private_msg(data.get("user_id"), f"[{self.name}]功能已封禁 = =")
                return False
            else:
                return True
        elif data.get("message_type") == "group":   # 群聊中
            gid = str(data.get("group_id"))
            group_info = await config_manager.get_group_info(gid)
            if self.name in self_info["disable_plugins"]:
                if disable_notice:  # 是否触发提示
                    await self.send_group_msg(data.get("group_id"), f"[{self.name}]功能已封禁 = =")
                return False
            elif self.name in group_info["close_plugins"]:
                if close_notice:  # 是否触发提示
                    await self.send_group_msg(data.get("group_id"), f"[{self.name}]功能在本群被关闭啦，群管理可以开启哟~\n(p≧w≦q)")
                return False
            else:
                return True
        else:   # 非消息类，默认不提示
            if "group_id" in data:
                gid = str(data.get("group_id"))
                group_info = await config_manager.get_group_info(gid)
                if self.name in self_info["disable_plugins"]:
                    return False
                elif self.name in group_info["close_plugins"]:
                    return False
                else:
                    return True
            else:
                if self.name in self_info["disable_plugins"]:
                    return False
                else:
                    return True

    # async def check_enable(self, data, bot) -> bool:
    #     """检查开关状态"""
    #     if "group_id" in data:
    #         gid = str(data.get("group_id"))
    #         self_info = await config_manager.get_self_info()
    #         group_info = await config_manager.get_group_info(gid)
            
    #         if self.name in self_info["disable_plugins"]:
    #             if data.get("message_type") == "private":     # 有时会通过临时会话发送，此时仍包含group_id，故做此判断
    #                 await self.send_private_msg(data.get("user_id"), f"[{self.name}]功能已封禁 = =")
    #             elif data.get("message_type") == "group":
    #                 await self.send_group_msg(data.get("group_id"), f"[{self.name}]功能已封禁 = =")
    #             return False
    #         elif self.name in group_info["close_plugins"]:
    #             if data.get("message_type") == "private":     # 有时会通过临时会话发送，此时仍包含group_id，故做此判断
    #                 await self.send_private_msg(data.get("user_id"), f"[{self.name}]功能在本群被关闭啦，群管理可以开启哟~\n(p≧w≦q)")
    #             elif data.get("message_type") == "group":
    #                 await self.send_group_msg(data.get("group_id"), f"[{self.name}]功能在本群被关闭啦，群管理可以开启哟~\n(p≧w≦q)")
    #             return False
    #         else:
    #             return True
    #     elif "user_id" in data:
    #         uid = str(data.get("user_id"))
    #         self_info = await config_manager.get_self_info()
    #         private_info = await config_manager.get_private_info(uid)

    #         if self.name in self_info["disable_plugins"]:
    #             await self.send_private_msg(data.get("user_id"), f"[{self.name}]功能已封禁 = =")
    #             return False
    #         else:
    #             return True
    #     else:
    #         return True
            
    @staticmethod
    def get_texts(data) -> str:
        """获取文本信息"""
        return '\n'.join([                  # 使用换行符连接所有文本
            item['data']['text'].strip()    # 去除头尾空字符串
            for item in data.get('message') 
            if item['type'] == 'text' and item['data']['text'].strip()  # 类型为text且不为空
        ])

    @staticmethod
    def at_if_group(data) -> bool:
        """
        检查群聊中是否@自己
        当消息为群聊消息且未@自己时返回False, 否则返回True(非群聊消息与@自己的时候都返回True)
        """
        at_list = [
            str(item['data']['qq'])     # 提取@的Q号列表
            for item in data.get('message') 
            if item['type'] == 'at'
        ]
        if data.get("message_type") == "group" and str(data.get('self_id')) not in at_list:
            return False
        else:
            return True

    @staticmethod
    def filter_nonfriend(data) -> bool:
        """
        检查私聊中是否是自己好友
        当消息为私聊消息且对方不是自己好友时返回True, 否则返回False
        """
        
        return (
            data.get("message_type") == "private" 
            and data.get("sender", {}).get("nickname") == "临时会话"
        )
