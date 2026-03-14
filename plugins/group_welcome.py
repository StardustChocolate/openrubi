
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from pathlib import Path

class GroupWelcome(BasePlugin):
    """入群欢迎插件"""
    
    # 插件基本信息
    name: str = "入群欢迎"
    description: str = "🌟有新成员入群时，会自动发送欢迎~\n🌟支持自定义，群主或管理员先发一段消息内容，然后引用并@我发送[修改欢迎语]即可修改当前群聊的入群欢迎"

    current_file = Path(__file__)  # 获取路径
    default_img = current_file.parent.parent / 'images' / 'emote' / 'Silvervale' / 'Glowsticks.gif'
    default_welcome = "欢迎光临~进群眼熟群公告哦~"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_notice(self, data, bot) -> bool:
        """处理通知事件"""
        
        if data.get("notice_type") == "group_increase" and data.get("user_id") != data.get("self_id"):    # 他人的入群通知
            gid = str(data.get("group_id"))
            group_info = await config_manager.get_group_info(gid)

            # 检查开关
            if not await self.check_enable(data, bot, disable_notice=False, close_notice=False):    # 功能关闭时不提示
                return True

            # 获取欢迎语
            if group_info.get("welcome_msg"):
                send_buff = f"[CQ:at,qq={data.get('user_id')}]{group_info.get('welcome_msg')}"
            else:
                if self.default_img.exists():
                    send_buff = f"[CQ:at,qq={data.get('user_id')}]{self.default_welcome}[CQ:image,file={self.default_img}]"
                else:
                    send_buff = f"[CQ:at,qq={data.get('user_id')}]{self.default_welcome}"
            
            # 发送消息
            await self.send_group_msg(data.get("group_id"), send_buff)

            return True

        return False

    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)
        bot_admin = data.get("user_id") in config_manager.info["admin_id"]  # 检查权限
        group_admin = data.get("sender").get("role") in ["owner", "admin"]  # 检查权限

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False

        # 只响应群消息
        if data.get("message_type") != "group":
            return False

        # 修改欢迎语
        if msg == "修改欢迎语": 
            # 检查开关
            if not await self.check_enable(data, bot):
                return True

            for item in data.get('message'):
                # 筛选“回复”类型的消息
                if item['type'] == 'reply':  
                    # 检查权限
                    if not (group_admin or bot_admin):
                        await self.send_group_msg(data.get("group_id"), "你的权限还不够呢\nヽ(*。>Д<)o゜")
                        return True

                    gid = str(data.get("group_id"))
                    group_info = await config_manager.get_group_info(gid)
                    reply_msg = await bot.api_client.call_api(
                        action="get_msg",
                        params={"message_id": item['data']['id']}
                    )
                    if not reply_msg:
                        await self.send_group_msg(data.get("group_id"), "啊这。。。获取引用消息出错啦Σ(っ °Д °;)っ")
                    else:
                        group_info["welcome_msg"] = reply_msg["raw_message"]
                        await config_manager.save_group_info()
                        await self.send_group_msg(data.get("group_id"), "嗯呐(*ෆ´ ˘ `ෆ*)♡")

                    return True
            
            await self.send_group_msg(data.get("group_id"), "未看到引用的消息哦~")
            return True

        elif msg == "重置欢迎语": 
            # 检查开关
            if not await self.check_enable(data, bot):
                return True
                
            # 检查权限
            if not (group_admin or bot_admin):
                await self.send_group_msg(data.get("group_id"), "你的权限还不够呢\nヽ(*。>Д<)o゜")
                return True
            gid = str(data.get("group_id"))
            group_info = await config_manager.get_group_info(gid)
            group_info.pop("welcome_msg", None)
            await config_manager.save_group_info()
            await self.send_group_msg(data.get("group_id"), "嗯呐(*ෆ´ ˘ `ෆ*)♡")
            return True

        return False
