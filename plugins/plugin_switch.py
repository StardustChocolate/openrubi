
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager

class PluginSwitch(BasePlugin):
    """功能开关"""
    
    # 插件基本信息
    name: str = "功能开关"
    description: str = "🌟群主或管理员输入[开启]+功能名即可打开对应功能啦~[关闭]+功能名同理\n例如：开启一言"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False

        # 构建功能列表
        name_list = [
            plugin.name
            for plugin in bot.plugin_manager.plugins.values()
            if plugin.name != self.name and plugin.name not in ["test", "帮助菜单", "受邀保护"]   # 排除自身和不可关闭的插件
        ]

        # 群聊中
        if data.get("message_type") == "group":
            gid = str(data.get("group_id"))
            self_info = await config_manager.get_self_info()
            group_info = await config_manager.get_group_info(gid)

            # 开启功能
            if msg.startswith("开启"):
                func_name = msg[2:]             # 截出功能名
                if func_name not in name_list:  # 不在功能列表中则返回
                    return False

                # 禁用的情况
                if func_name in self_info.get("disable_plugins"):
                    send_buff = "该功能已封禁 = ="
                # 关闭的情况
                elif func_name in group_info.get("close_plugins"):
                    # 检查权限
                    if data.get("sender").get("role") in ["owner", "admin"] or data.get("user_id") in config_manager.info['admin_id']:
                        group_info["close_plugins"].remove(func_name)
                        await config_manager.save_group_info()
                        send_buff = "嗯呐(*ෆ´ ˘ `ෆ*)♡"
                    else:
                        send_buff = "你的权限还不够呢\nヽ(*。>Д<)o゜"
                # 已开启的情况
                else:
                    send_buff = "这个功能已经开启了哦\n⊙▽⊙"
                
                # 发送消息
                await self.send_group_msg(data.get("group_id"), send_buff)
                return True
            
            # 关闭功能
            elif msg.startswith("关闭"):
                func_name = msg[2:]             # 截出功能名
                if func_name not in name_list:  # 不在功能列表中则返回
                    return False

                # 禁用的情况
                if func_name in self_info.get("disable_plugins"):
                    send_buff = "该功能已封禁 = ="
                # 开启的情况
                elif func_name not in group_info.get("close_plugins"):
                    # 检查权限
                    if data.get("sender").get("role") in ["owner", "admin"] or data.get("user_id") in config_manager.info['admin_id']:
                        group_info["close_plugins"].append(func_name)
                        await config_manager.save_group_info()
                        send_buff = "嗯呐(*ෆ´ ˘ `ෆ*)♡"
                    else:
                        send_buff = "你的权限还不够呢\nヽ(*。>Д<)o゜"
                # 已关闭的情况
                else:
                    send_buff = "这个功能已经关闭了哦\n⊙▽⊙"
                
                # 发送消息
                await self.send_group_msg(data.get("group_id"), send_buff)
                return True
                
            # 解禁功能
            elif msg.startswith("解禁"):
                func_name = msg[2:]             # 截出功能名
                if func_name not in name_list:  # 不在功能列表中则返回
                    return False

                # 禁用的情况
                if func_name in self_info.get("disable_plugins"):
                    # 检查权限
                    if data.get("user_id") in config_manager.info['admin_id']:  # 监护人权限
                        self_info["disable_plugins"].remove(func_name)
                        await config_manager.save_self_info()
                        send_buff = "封禁已解除(ﾉ>ω<)ﾉ"
                    else:
                        send_buff = "你的权限还不够呢\nヽ(*。>Д<)o゜"
                # 未禁用的情况
                else:
                    send_buff = "该功能尚未封禁(ﾉ>ω<)ﾉ"
                
                # 发送消息
                await self.send_group_msg(data.get("group_id"), send_buff)
                return True

            # 禁用功能
            elif msg.startswith("禁用"):
                func_name = msg[2:]             # 截出功能名
                if func_name not in name_list:  # 不在功能列表中则返回
                    return False

                # 禁用的情况
                if func_name in self_info.get("disable_plugins"):
                    send_buff = "该功能已封禁(ﾉ>ω<)ﾉ"
                # 未禁用的情况
                else:
                    # 检查权限
                    if data.get("user_id") in config_manager.info['admin_id']:  # 监护人权限
                        self_info["disable_plugins"].append(func_name)
                        await config_manager.save_self_info()
                        send_buff = "嗯呐(*ෆ´ ˘ `ෆ*)♡"
                    else:
                        send_buff = "你的权限还不够呢\nヽ(*。>Д<)o゜"
                   
                # 发送消息
                await self.send_group_msg(data.get("group_id"), send_buff)
                return True

        # 私聊中
        elif data.get("message_type") == "private": 
            self_info = await config_manager.get_self_info()

            # 解禁功能
            if msg.startswith("解禁"):
                func_name = msg[2:]             # 截出功能名
                if func_name not in name_list:  # 不在功能列表中则返回
                    return False

                # 禁用的情况
                if func_name in self_info.get("disable_plugins"):
                    # 检查权限
                    if data.get("user_id") in config_manager.info['admin_id']:  # 监护人权限
                        self_info["disable_plugins"].remove(func_name)
                        await config_manager.save_self_info()
                        send_buff = "封禁已解除(ﾉ>ω<)ﾉ"
                    else:
                        send_buff = "你的权限还不够呢\nヽ(*。>Д<)o゜"
                # 未禁用的情况
                else:
                    send_buff = "该功能尚未封禁(ﾉ>ω<)ﾉ"
                
                # 发送消息
                await self.send_private_msg(data.get("user_id"), send_buff)
                return True

            # 禁用功能
            elif msg.startswith("禁用"):
                func_name = msg[2:]             # 截出功能名
                if func_name not in name_list:  # 不在功能列表中则返回
                    return False

                # 禁用的情况
                if func_name in self_info.get("disable_plugins"):
                    send_buff = "该功能已封禁(ﾉ>ω<)ﾉ"
                # 未禁用的情况
                else:
                    # 检查权限
                    if data.get("user_id") in config_manager.info['admin_id']:  # 监护人权限
                        self_info["disable_plugins"].append(func_name)
                        await config_manager.save_self_info()
                        send_buff = "嗯呐(*ෆ´ ˘ `ෆ*)♡"
                    else:
                        send_buff = "你的权限还不够呢\nヽ(*。>Д<)o゜"
                   
                # 发送消息
                await self.send_private_msg(data.get("user_id"), send_buff)
                return True

        return False