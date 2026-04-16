import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from utils.time_parser import parse_reminder_time
from utils.logger import get_logger

class ReminderPlugin(BasePlugin):
    """定时提醒插件"""
    
    name: str = "定时提醒"
    description: str = "🌟引用需要提醒的内容，输入[设置提醒：+时间]即可设置定时提醒啦~\n🌟输入[清空提醒]即可清除所有提醒~🌟该功能需要管理员权限哦~"
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.reminder_tasks: Dict[str, List[Dict[str, Any]]] = {}  # group_id -> reminders
        self.check_task: Optional[asyncio.Task] = None
        
    async def on_load(self, bot):
        """插件加载时调用"""
        await super().on_load(bot)
        # 加载现有的提醒
        await self.load_reminders()
        # 启动检查任务
        self.check_task = asyncio.create_task(self.check_reminders())
        
    async def on_unload(self):
        """插件卸载时调用"""
        if self.check_task and not self.check_task.done():
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)

        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            await self.send_private_msg(data.get("user_id"), "你还不是我的好友呀~")
            return False
        
        if msg == "清空提醒":
            # 检查开关
            if not await self.check_enable(data, bot):
                return True
            
            # 检查权限
            bot_admin = data.get("user_id") in config_manager.info["admin_id"]  # 监护人
            group_admin = data.get("sender").get("role") in ["owner", "admin"]  # 群管理员或群主
            if data.get("message_type") == "group" and not (group_admin or bot_admin):
                await self.send_group_msg(data.get("group_id"), "你的权限还不够呢\nヽ(*。>Д<)o゜")
                return True
            
            # 清空提醒任务
            group_id = str(data.get('group_id', data.get('user_id')))
            count = len(self.reminder_tasks.get(group_id, []))
            self.reminder_tasks[group_id] = []
            group_data = await config_manager.get_group_info(group_id)
            if 'reminders' in group_data:
                group_data.pop('reminders', None)
            await config_manager.save_group_info()
            if count == 0:
                await self.send_reply(data, "当前没有任何提醒任务哦\no(￣▽￣*)ゞ")
            else:
                await self.send_reply(data, "嗯呐(*ෆ´ ˘ `ෆ*)♡")
            return True

        if not msg.startswith(("设置提醒：", "设置提醒:")):
            return False
            
        # 检查开关
        if not await self.check_enable(data, bot):
            return True
            
        reminder_text = msg[5:].strip()  # 移除"设置提醒："
        
        # 解析时间
        parsed = parse_reminder_time(reminder_text)
        if not parsed:
            await self.send_reply(data, "无法解析提醒时间，请检查格式哦~\n(￣▽￣*)ゞ")
            return True
            
        # 获取引用消息
        quoted_msg = None
        if 'message' in data:
            for item in data['message']:
                if item.get('type') == 'reply':
                    # 获取原始消息
                    try:
                        reply_data = await bot.api_client.call_api("get_msg", {"message_id": item['data']['id']})
                        if reply_data:
                            if 'data' in reply_data:
                                msg_data = reply_data['data']
                            else:
                                msg_data = reply_data
                            quoted_msg = msg_data.get('raw_message')
                    except Exception as e:
                        self.logger.error(f"获取引用消息失败: {e}")
                    break

        if not quoted_msg:
            await self.send_reply(data, "需引用要提醒的信息哦~\n(￣▽￣*)ゞ")
            return True

        # 检查权限
        bot_admin = data.get("user_id") in config_manager.info["admin_id"]  # 监护人
        group_admin = data.get("sender").get("role") in ["owner", "admin"]  # 群管理员或群主
        if not (group_admin or bot_admin):
            await self.send_group_msg(data.get("group_id"), "你的权限还不够呢\nヽ(*。>Д<)o゜")
            return True

        # 创建提醒
        reminder = {
            'id': f"{data.get('group_id', data.get('user_id'))}_{datetime.now().timestamp()}",
            'user_id': data.get('user_id'),
            'group_id': data.get('group_id'),
            'message_type': data.get('message_type'),
            'reminder_text': reminder_text,
            'parsed_time': {
                'type': parsed['type'],
                'next_time': parsed['next_time'].isoformat(),
                'interval': parsed['interval'],
                'description': parsed['description']
            },
            'quoted_message': quoted_msg,
            'created_at': datetime.now().isoformat()
        }
        
        # 保存到group_info
        group_id = str(data.get('group_id', data.get('user_id')))
        if group_id not in self.reminder_tasks:
            self.reminder_tasks[group_id] = []
        self.reminder_tasks[group_id].append(reminder)
        
        # 保存到配置文件
        await self.save_reminders()
        
        await self.send_reply(data, f"提醒设置成功！\n类型：{parsed['type']}\n下次提醒：{parsed['next_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    async def check_reminders(self):
        """检查提醒任务"""
        while True:
            try:
                now = datetime.now()
                triggered = []
                changed = False
                
                for group_id, reminders in self.reminder_tasks.items():
                    for reminder in reminders[:]:  # 复制列表以便修改
                        try:
                            next_trigger = reminder['parsed_time']['next_time']
                            
                            # 确保 next_trigger 是 datetime 对象（仅用于比较，不修改存储）
                            if isinstance(next_trigger, str):
                                next_trigger = datetime.fromisoformat(next_trigger)
                            
                            if now >= next_trigger:
                                # 检查开关，通过才触发提醒，避免在功能关闭时仍然触发
                                check_data = {
                                    'message_type': reminder['message_type'],
                                    'group_id': reminder.get('group_id'),
                                    'user_id': reminder.get('user_id')
                                }
                                if await self.check_enable(check_data, self.bot, disable_notice=False, close_notice=False):
                                    await self.trigger_reminder(reminder)   # 触发提醒
                                
                                if reminder['parsed_time']['type'] == 'once':
                                    # 单次提醒，删除
                                    reminders.remove(reminder)
                                    triggered.append((group_id, reminder))
                                    changed = True
                                else:
                                    # 重复提醒，更新下次时间（保持为字符串格式）
                                    interval = reminder['parsed_time']['interval']
                                    new_next = next_trigger + timedelta(seconds=interval)
                                    reminder['parsed_time']['next_time'] = new_next.isoformat()  # 立即转换为字符串
                                    changed = True
                        except Exception as e:
                            self.logger.error(f"处理提醒失败: {e}, 提醒数据: {reminder}")
                            continue
                
                # 保存更改
                if changed:
                    await self.save_reminders()
                    
            except Exception as e:
                self.logger.error(f"检查提醒时出错: {e}")
                
            await asyncio.sleep(60)  # 每60秒检查一次
            
    async def trigger_reminder(self, reminder: Dict[str, Any]):
        """触发提醒"""
        try:
            message = f"⏰\n"
            
            if reminder['quoted_message']:
                message += f"{reminder['quoted_message']}"
            
            if reminder['message_type'] == 'group':
                await self.send_group_msg(reminder['group_id'], message)
            else:
                await self.send_private_msg(reminder['user_id'], message)
                
        except Exception as e:
            self.logger.error(f"触发提醒失败: {e}")
            
        
    async def load_reminders(self):
        """加载提醒任务"""
        try:
            total_reminders = 0
            # 直接从group_info字典读取，避免异步调用
            for group_id, group_data in config_manager.group_info.items():
                if 'reminders' in group_data and group_data['reminders']:
                    # 反序列化提醒任务
                    # 直接使用 JSON 中的字符串格式时间，运行时按需解析
                    self.reminder_tasks[group_id] = [reminder.copy() for reminder in group_data['reminders']]
                    total_reminders += len(group_data['reminders'])
            
            if total_reminders > 0:
                self.logger.info(f"共加载 {total_reminders} 个提醒任务")
        except Exception as e:
            self.logger.error(f"加载提醒失败: {e}")
            
    async def save_reminders(self):
        """保存提醒任务"""
        try:
            for group_id, reminders in self.reminder_tasks.items():
                # 深拷贝提醒列表，避免修改原始数据
                reminders_copy = []
                for reminder in reminders:
                    reminder_copy = reminder.copy()
                    # 确保 datetime 对象被转换为字符串
                    if 'parsed_time' in reminder_copy and isinstance(reminder_copy['parsed_time']['next_time'], datetime):
                        reminder_copy['parsed_time'] = reminder_copy['parsed_time'].copy()
                        reminder_copy['parsed_time']['next_time'] = reminder_copy['parsed_time']['next_time'].isoformat()
                    reminders_copy.append(reminder_copy)
                
                group_data = await config_manager.get_group_info(group_id)
                group_data['reminders'] = reminders_copy
                await config_manager.save_group_info()
        except Exception as e:
            self.logger.error(f"保存提醒失败: {e}")
            
    async def send_reply(self, data, message: str):
        """发送回复消息"""
        if data.get('message_type') == 'group':
            await self.send_group_msg(data['group_id'], message)
        else:
            await self.send_private_msg(data['user_id'], message)