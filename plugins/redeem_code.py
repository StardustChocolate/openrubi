
import json
from plugins.base_plugin import BasePlugin
from pathlib import Path
from datetime import datetime

class RedeemCode(BasePlugin):
    """兑换码插件"""
    
    # 插件基本信息
    name: str = "兑换码"
    description: str = ""
    
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
            
        if msg == "兑换码":
            # 检查开关
            if not await self.check_enable(data, bot):
                return True

            redeem_code_list = get_redeem_code()    # 获取兑换码
            send_list = []
            for redeem_code in redeem_code_list:
                # 跳过过期兑换码
                if redeem_code['valid'] and datetime.strptime(redeem_code['valid'], "%Y-%m-%d") < datetime.now():
                    continue
                # 添加有效兑换码
                text = redeem_code['code']
                if redeem_code['content']:
                    text += f"\n内容：{redeem_code['content']}"
                if redeem_code['valid']:
                    text += f"\n有效期至：{redeem_code['valid']}"
                send_list.append(text)
            send_buff = "\n".join(send_list)
            if not send_buff:
                send_buff = '现在还没有兑换码哦Σ( ° △ °)'

            # 发送消息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)  

            return True

        return False


# 获取兑换码
def get_redeem_code():
    # 获取路径
    current_file = Path(__file__)
    redeem_code_path = current_file.parent.parent / 'arkrecode' / 'redeem_code' / 'redeem_code.json'
    with open(redeem_code_path, 'r', encoding='utf-8') as f:
        redeem_code = json.load(f)
    return redeem_code