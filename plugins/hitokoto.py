
import httpx
import json
from plugins.base_plugin import BasePlugin

class Hitokoto(BasePlugin):
    """一言插件(调用一言api)"""
    
    # 插件基本信息
    name: str = "一言"
    description: str = "🌟调用一言API，源项目地址https://github.com/hitokoto-osc\n可以指定类型哦~例如发送：「一言：动画」即可指定为动画类型~可选的类型有：\n🌟动画\n🌟漫画\n🌟游戏\n🌟文学\n🌟原创\n🌟网络\n🌟其他\n🌟影视\n🌟诗词\n🌟网易云\n🌟哲学\n🌟抖机灵"

    select_dic = {
        "动画": "a",
        "漫画": "b",
        "游戏": "c",
        "文学": "d",
        "原创": "e",
        "网络": "f",
        "其他": "g",
        "影视": "h",
        "诗词": "i",
        "网易云": "j",
        "哲学": "k",
        "抖机灵": "l",
    }
    
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

        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            return False

        # 关键词判断
        if msg.startswith("一言"):
            select = msg.lstrip('一言：:') # 截取选择的分类

            # 检查开关
            if not await self.check_enable(data, bot):
                return True
    
            # 未能识别的分类
            if select and select not in self.select_dic:
                send_buff = "啊这。。。没有这个分类哦Σ(っ °Д °;)っ"
            else:
                if select:
                    params = {"c": self.select_dic[select]}
                else:
                    params = {}
                try:
                    url = "https://v1.hitokoto.cn/"
        
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, params=params)
                        text = response.json()
                
                    author = text.get("from_who", "")
                    source = f"《{text['from']}》" if text.get("from") else ""
                    send_buff = f"{text['hitokoto']}\n——{author}{source}"
                except Exception as e:
                    send_buff = f"啊这......好像出了一点问题\n(开始胡言乱语)\nError of hitokoto:\n{e}"

            # 发送信息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)

            return True
        
        return False