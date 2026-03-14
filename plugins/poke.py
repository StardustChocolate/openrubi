
import random
import httpx
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from pathlib import Path

class Poke(BasePlugin):
    """戳一戳插件"""
    
    # 插件基本信息
    name: str = "戳一戳"
    description: str = ""
    
    # 默认的文本回复列表
    poke_list_str = [
        "喵？", "怎么啦", "rua！", "乌拉！", "呐呐呐", "咪呜~",
        "总之你是个大笨蛋啦",
        "把我自己送给你好了，虽然很可爱但是我养不起了",
        "人类的坚韧性体现在虽然从没有人请过他疯狂星期四但他每周四都在发",
        "无人与我立黄昏，有人问我粥可温",
        "像你这种坏银，我才不稀罕哦",
        "无事献殷勤，非...非常喜欢你~",
        "这不是欺负人吗 > <",
        "{0}{0}{0}~希望你能有点自知之明，认识到超级无敌可爱的我",
        "我在哦！是有什么事情吗？",
        "你总说我懒，是啊，喜欢上你就懒得放弃你了呀",
        "你{0}的我有点开心奖励你哦",
        "是不是把我当老婆了？",
        "你{0}谁呢！你{0}谁呢！哼！",
        "你这个笨蛋蛋傻瓜瓜臭狗狗不要{0}了啦",
        "宝宝是不是又熬夜了，我看你还在线",
        "只要你需要我就会在哦",
        "你这个人傻FUFU的",
        "正在定位您的真实地址...定位成功，轰炸机已起飞",
        "群主大人快来鸭~有人欺负我",
        "你再{0}我~我就透你",
        "我......我......才不是傲娇呢",
        "劝你别整天对我{0}{0}{0}的有本事你来亲亲我",
        "呜呜呜，别{0}啦，已经很笨啦\n(っ╥╯﹏╰╥c)", 
        "呜呜呜，别{0}啦，再{0}。。。要变得奇怪啦\n｡ﾟ･ (>﹏<) ･ﾟ｡"
    ]
    # 默认的图片回复列表
    poke_list_img = []
    current_file = Path(__file__)   # 获取路径
    folders = config_manager.path["poke_img"]
    for folder in folders:
        folder_path = Path(folder)
        poke_list_img += [str(file_path) for file_path in folder_path.rglob('*') if file_path.is_file()]

    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_notice(self, data, bot) -> bool:
        """处理通知事件"""
        if data.get("sub_type") == "poke":
            if data.get("target_id") != data.get("self_id"):       # 戳的不是我
                return False

            # 检查开关
            if not await self.check_enable(data, bot):
                return True
                
            if "group_id" in data:
                # 群聊中
                gid = str(data.get("group_id")) 
                action_name = data['raw_info'][2]['txt'][:1]
                if random.random() < 0.5:       # 概率回复文字或图片
                    # 回复文字
                    if random.random() < 0.2:   # 当为文字时概率使用一言回复
                        try:
                            url = "https://v1.hitokoto.cn/"
                            async with httpx.AsyncClient() as client:
                                response = await client.get(url)
                                text = response.json()
                            author = text.get("from_who") or ""
                            source = f"《{text['from']}》" if text.get("from") else ""
                            send_buff = f"{text['hitokoto']}\n——{author}{source}"
                        except Exception as e:
                            send_buff = f"啊这......好像出了一点问题\n(开始胡言乱语)\nError of hitokoto:\n{e}"
                    else:
                        send_buff = random.choice(self.poke_list_str).format(action_name)
                else:
                    # 回复图片
                    send_buff = f"[CQ:image,file={random.choice(self.poke_list_img)}]"

                await self.send_group_msg(data.get("group_id"), send_buff)
            return True

        return False