
import asyncio
from plugins.base_plugin import BasePlugin
from pathlib import Path
from configs.config_manager import config_manager
from utils.logger import get_logger

class UpdateLogs(BasePlugin):
    """更新日志"""
    
    # 插件基本信息
    name: str = "更新日志"
    description: str = "🌟@我并发送[更新日志]即可获取最新的更新日志\n🌟监护人指令：[推送日志]即可向所有群发送更新日志\n🌟群主或管理员可以通过[关闭推送]以关闭更新日志的推送"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False

        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            return False

        if msg == "更新日志":
            # 检查开关
            if not await self.check_enable(data, bot):
                return True
            # 发送消息
            send_buff = get_update()
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)

            return True

        elif msg == "推送更新日志":
            # 检查权限
            if data.get("user_id") not in config_manager.info['admin_id']:
                if data.get("message_type") == "group":
                    await self.send_group_msg(data.get("group_id"), "你的权限还不够呢\nヽ(*。>Д<)o゜")
                elif data.get("message_type") == "private":
                    await self.send_private_msg(data.get("user_id"), "你的权限还不够呢\nヽ(*。>Д<)o゜")
                return True

            # 获取群列表
            group_list = await bot.api_client.call_api( 
                action="get_group_list",
                params={"no_cache": False}  # 是否不用缓存(默认False)
            )

            # 异步推送更新日志
            async def async_send(groups):
                send_buff = get_update()
                for group in groups:
                    gid = str(group.get('group_id'))
                    group_info = await config_manager.get_group_info(gid)
                    if 'post' not in group_info:
                        group_info['post'] = True               # 若无'post'属性默认给True，允许推送
                        await config_manager.save_group_info()  # 保存修改信息
                    if group_info.get('post'):
                        # if group.get('group_id') != config_manager.info.get("test_group_id"):  # 测试用 只响应固定群号
                        #     continue
                        await self.send_group_msg(group.get('group_id'), send_buff)
                        await asyncio.sleep(3)                  # 每次发送间隔时间(s)
                logger = get_logger()
                logger.info(f"{config_manager.info['self_name']}更新日志发送完毕")
                if data.get("message_type") == "group":
                    await self.send_group_msg(data.get("group_id"), "更新日志发送完毕")
                elif data.get("message_type") == "private":
                    await self.send_private_msg(data.get("user_id"), "更新日志发送完毕")

            # 创建任务开始发送
            asyncio.create_task(async_send(group_list))
            
            return True

        elif msg == "关闭推送":
            # 只响应群聊
            if data.get("message_type") == "group":
                gid = str(group.get('group_id'))
                # 检查权限
                if data.get("sender").get("role") == "owner":
                    group_info = await config_manager.get_group_info(gid)
                    group_info['post'] = False
                    await config_manager.save_group_info()  # 保存修改信息
                    await self.send_group_msg(data.get("group_id"), "嗯呐(*ෆ´ ˘ `ෆ*)♡")     
                else:
                    await self.send_group_msg(data.get("group_id"), "你的权限不够了啦\nヽ(*。>Д<)o゜")   
                        
            return True

        return False


# 获取更新日志
def get_update():
    # 获取路径
    current_file = Path(__file__)
    update_log_path = current_file.parent.parent / 'doc' / 'update_log.txt'
    with open(update_log_path, 'r', encoding='utf-8') as f:
        update_log = f.read().replace("{self_name}", config_manager.info['self_name'])
    return update_log