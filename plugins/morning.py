
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from datetime import datetime

class Morning(BasePlugin):
    """早安打卡"""
    
    # 插件基本信息
    name: str = "早安打卡"
    description: str = "🌟关键词：[早、早安、早上好、早呀、哦哈哟]，不同时段有不同反应哦~\n🎉该功能包含彩蛋哟~"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)
        keyword_morning = ["早", "早安", "早上好", "早呀", "哦哈哟"]
        keyword_morning_sp = ["草", "艹"]
        flag_match = False
        flag_morning = False
        flag_morning_sp = False
        if msg in keyword_morning:
            flag_morning = True
            flag_match = True
        elif msg in keyword_morning_sp:
            flag_morning_sp = True
            flag_match = True

        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            return False

        # 未匹配到关键词返回
        if not flag_match:
            return False

        # 检查开关
        if not await self.check_enable(data, bot):
            return True

        # 群聊中
        if data.get("message_type") == "group":
            gid = str(data.get("group_id"))
            uid = str(data.get("user_id"))
            # 获取性别信息
            stranger_info = await bot.api_client.call_api(
                action="get_group_member_info",
                params={"group_id": data.get("group_id"), "user_id": data.get("user_id")}
            )
            if not stranger_info:
                # await self.send_group_msg(data.get("group_id"), "啊这。。。获取成员信息出错啦Σ(っ °Д °;)っ")
                # return True
                stranger_info = {}  # 获取失败不发消息了，改为默认群员
            match stranger_info.get("sex"):
                case "female":
                    sex = "少女"
                case "male":
                    sex = "少年"
                case _:
                    sex = "群员"
            # 获取时间
            now = datetime.now()
            # 若第一次调用则初始化
            group_info = await config_manager.get_group_info(gid)
            group_info.setdefault("morning", {})
            group_info["morning"].setdefault("day", now.day)
            group_info["morning"].setdefault("members", [])
            group_info["morning"].setdefault("members_sp", [])
            if group_info["morning"]["day"] != now.day:        # 新的一天重新计数
                group_info["morning"]["day"] = now.day
                group_info["morning"]["members"] = []
                group_info["morning"]["members_sp"] = []
            members = group_info["morning"]["members"]
            members_sp = group_info["morning"]["members_sp"]

            # 逻辑判断
            send_buff = ""
            if flag_morning:
                # 早上好，不同时间返回不同信息
                if now.hour < 4:
                    send_buff = "早什么早，快去睡觉！\n(╬▔皿▔)"
                elif now.hour < 9:
                    if uid not in members:
                        members.append(uid)
                        send_buff = f"早上好呀！o(*≧▽≦)ツ你是今天第{len(members)}位起床的{sex}呢"
                    else:
                        send_buff = "你今天已经起过床啦~"
                elif now.hour < 12:
                    if uid not in members:
                        members.append(uid)
                        send_buff = f"上午好呀！o(*≧▽≦)ツ你是今天第{len(members)}位起床的{sex}呢"
                    else:
                        send_buff = "你今天已经起过床啦~"
                elif now.hour < 19:
                    if uid not in members:
                        members.append(uid)
                        send_buff = f"下午好╰(*°▽°*)╯已经很晚了哦，你是今天第{len(members)}位起床的{sex}呢"
                    else:
                        send_buff = "你今天已经起过床啦~"
                else:
                    if uid not in members:
                        send_buff = "已经晚上啦Σ( ° △ °|||)︴还是别起床了，再睡一觉吧"
                    else:
                        send_buff = "你今天已经起过床啦~"
            elif flag_morning_sp:
                # 彩蛋，草上好
                if uid not in members_sp:
                    members_sp.append(uid)
                    send_buff = f"草上好呀！o(*≧▽≦)ツ你是今天第{len(members_sp)}位生草的{sex}呢"
                else:
                    send_buff = "你今天已经生草过啦~"
            
            # 发送群聊消息
            await self.send_group_msg(data.get("group_id"), send_buff)

            # 保存修改信息
            await config_manager.save_group_info()

        # 私聊中
        elif data.get("message_type") == "private":   
            uid = str(data.get("user_id"))
            # 获取时间
            now = datetime.now()
            # 不同时间返回不同信息
            if now.hour < 4:
                send_buff = "早什么早，快去睡觉！\n(╬▔皿▔)"
            elif now.hour < 9:
                send_buff = "早上好呀！o(*≧▽≦)ツ"
            elif now.hour < 12:
                send_buff = "上午好呀！o(*≧▽≦)ツ"
            elif now.hour < 19:
                send_buff = "下午好╰(*°▽°*)╯已经很晚了哦"
            else:
                send_buff = "已经晚上啦Σ( ° △ °|||)︴还是别起床了，再睡一觉吧"

            # 发送私聊消息
            await self.send_private_msg(data.get("user_id"), send_buff)

        return True