
from plugins.base_plugin import BasePlugin

class CalcSpeed(BasePlugin):
    """速度计算插件"""
    
    # 插件基本信息
    name: str = "速度计算"
    description: str = "🌟关键词「速度计算：」，输入我方[角色名]+[起始行动条]+[终点行动条]+[速度]和敌方[角色名]+[起始行动条]+[终点行动条]即可计算敌方速度\n以下是用法示例：\n\n速度计算：\n我方\n彩伽 4 88 214\n火猫 2 77 195\naoi 1 62 155\n敌方\n朱音 5 100\n水马 3 74\n异变 1 50\n\nTips:\nQ: 为什么计算结果是区间？\nA: 游戏中的行动条是四舍五入的，该区间为考虑了所有我方角色的速度以及舍入情况的交集，即对方的速度最大最小是多少\nQ: 什么是回归拟合？\nA: 是基于所有我方角色速度计算的最小误差值，即对方实际最有可能的速度是多少，我方信息越多精度越高"
    
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
        if msg.startswith(('速度计算：', '速度计算:')):
            # 检查开关
            if not await self.check_enable(data, bot):
                return True

            msg_calc = msg[5:]   # 计算内容获取
            send_buff = calc_speed(msg_calc)    # 计算

            # 发送信息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)

            return True

        return False

def calc_speed(msg):
    our_team = []
    enemy_team = []
    current_section = None
    # 提取相关信息
    lines = msg.strip().split('\n')
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        if stripped_line == "我方":
            current_section = "our"
            continue
        elif stripped_line == "敌方":
            current_section = "enemy"
            continue
             
        parts = stripped_line.split()
        if current_section == "our":
            if len(parts) >= 4: 
                try:
                    # 最后三个元素是位置和速度（都是数字）
                    speed = int(parts[-1])
                    end_pos = int(parts[-2])
                    start_pos = int(parts[-3])
                    # 剩余部分合并为角色名（可能包含空格）
                    name = ' '.join(parts[:-3])
                    our_team.append({
                        "name": name,
                        "start_pos": start_pos,
                        "end_pos": end_pos,
                        "speed": speed
                    })
                except ValueError:
                    send_buff = f"数据错误，无法解析行: {line}"
                    return send_buff
            else:
                send_buff = f"格式错误，无法解析行: {line}{len(parts)}"
                return send_buff
        elif current_section == "enemy":
            if len(parts) >= 3:
                try:
                    # 最后两个元素是位置（都是数字）
                    end_pos = int(parts[-1])
                    start_pos = int(parts[-2])
                    # 剩余部分合并为角色名（可能包含空格）
                    name = ' '.join(parts[:-2])
                    enemy_team.append({
                        "name": name,
                        "start_pos": start_pos,
                        "end_pos": end_pos
                    })
                except ValueError:
                    send_buff = f"数据错误，无法解析行: {line}"
                    return send_buff
            else:
                send_buff = f"格式错误，无法解析行: {line}"
                return send_buff
    # 计算拟合速度因数
    c = 0       # 单位速度在单位时间内增加的行动条百分比(回归拟合)
    num = 0     # 分子
    denom = 0   # 分母
    for our_char in our_team:
        num += our_char["speed"] * (our_char["end_pos"] - our_char["start_pos"])
        denom += our_char["speed"] ** 2
    try:
        c = num / denom
    except ZeroDivisionError as e:
        send_buff = "数据错误，出现除零"
        return send_buff
    # 计算速度
    for enemy_char in enemy_team:
        upper = []
        lower = []
        for our_char in our_team:
            # 计算最大速度
            our_inc = (100 if our_char["end_pos"] == 100 else our_char["end_pos"] - 0.5) - min((our_char["start_pos"] + 0.5), 5) # 100行动条默认为最高速，不做-0.5处理
            enemy_inc = min((enemy_char["end_pos"] + 0.5), 100) - max((enemy_char["start_pos"] - 0.5), 0)
            upper.append(our_char["speed"] / our_inc * enemy_inc)
            # 计算最小速度
            our_inc = min((our_char["end_pos"] + 0.5), 100) - max((our_char["start_pos"] - 0.5), 0)
            enemy_inc = (100 if enemy_char["end_pos"] == 100 else enemy_char["end_pos"] - 0.5) - min((enemy_char["start_pos"] + 0.5), 5) # 100行动条默认为最高速，不做-0.5处理
            lower.append(our_char["speed"] / our_inc * enemy_inc)
        enemy_char["max_speed"] = min(upper)
        enemy_char["min_speed"] = max(lower)
        # 计算拟合速度
        temp_reg = (enemy_char["end_pos"] - enemy_char["start_pos"]) / c
        enemy_char["reg_speed"] = max(enemy_char["min_speed"], min(enemy_char["max_speed"], temp_reg))
    # 结果合并字符串
    result = "计算结果："
    for enemy_char in enemy_team:
        result += f'\n{enemy_char["name"]}  速度区间[{enemy_char["min_speed"]:.2f}, {enemy_char["max_speed"]:.2f}]  回归拟合{enemy_char["reg_speed"]:.2f}'

    send_buff = result
    return send_buff
