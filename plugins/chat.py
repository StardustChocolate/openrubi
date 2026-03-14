
import time
import openai
import asyncio
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
from utils.logger import get_logger
from typing import Dict, Optional, List

class Chat(BasePlugin):
    """聊天插件"""
    
    # 插件基本信息
    name: str = "聊天"
    description: str = "🌟当聊天功能开启时，未命中任何关键词会落在此处，当前模型为DeepSeek-V3.2-Exp，输入[重置聊天]可以恢复初始设定并清空聊天历史，输入[设定：+内容]可以将想要的内容覆盖掉初始设定"

    # ---------------------参数---------------------
    # api_key = ''                                                            # api-key(已改为配置文件中设置，不在此处放置)
    base_url = 'https://api.deepseek.com'                                   # api地址(deepseek官方)
    model = 'deepseek-chat'                                                 # 选择模型(deepseek官方)
    temperature = 1.0                                                       # 随机性, 0.0表示固定，最大为2.0, 默认值为1
    max_tokens = 4096                                                       # 输出长度限制, chat默认4k, 最大8k, reasoner默认32k, 最大64k

    # 类变量
    logger = get_logger()   # 获取日志
    max_turns = 20          # 多轮对话最大支持的轮数，超出会遗忘最早的消息
    cooldown_time = 5       # 冷却时间(秒)，防止过高频调用
    group_queues: Dict[str, List[str]] = {}         # 群聊消息队列
    private_queues: Dict[str, List[str]] = {}       # 私聊消息队列
    group_processing: Dict[str, bool] = {}          # 群聊是否正在处理中
    private_processing: Dict[str, bool] = {}        # 私聊是否正在处理中
    group_last_response: Dict[str, float] = {}      # 群聊最后响应时间
    private_last_response: Dict[str, float] = {}    # 私聊最后响应时间
    
    def __init__(self):
        super().__init__()
        self.priority = 99  # 优先级，范围0-100，数字越小优先级越高，默认50
        # 低优先级，未命中任何关键词会落在此处
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False

        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            await self.send_private_msg(data.get("user_id"), "你还不是我的好友呀~")
            return True

        # 空消息
        if msg == "":
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), "什么嘛，@人家后又什么都不说\nO(≧口≦)O")
                return True
            elif data.get("message_type") == "private":
                return False # 私聊空消息不回复
            return False

        # 指令：重置
        if msg == '重置聊天':
            # 检查开关
            if not await self.check_enable(data, bot):
                return True

            if data.get("message_type") == "group":
                gid = str(data.get("group_id"))
                group_info = await config_manager.get_group_info(gid)
                group_info["chat_prompt"] = [{"role": "system", "content": config_manager.info["prompt"].replace("{self_name}", config_manager.info["self_name"])}]
                # 保存修改信息
                await config_manager.save_group_info()
                # 发送消息
                await self.send_group_msg(data.get("group_id"), "嗯呐(*ෆ´ ˘ `ෆ*)♡")
            elif data.get("message_type") == "private":
                uid = str(data.get("user_id"))
                private_info = await config_manager.get_private_info(uid)
                private_info["chat_prompt"] = [{"role": "system", "content": config_manager.info["prompt"].replace("{self_name}", config_manager.info["self_name"])}]
                # 保存修改信息
                await config_manager.save_private_info()
                # 发送消息
                await self.send_private_msg(data.get("user_id"), "嗯呐(*ෆ´ ˘ `ෆ*)♡")

            return True
        
        # 指令：设定
        elif msg.startswith(('设定：', '设定:')):
            # 检查开关
            if not await self.check_enable(data, bot):
                return True

            set_msg = msg.lstrip('设定：:') # 截取设定内容
            if data.get("message_type") == "group":
                gid = str(data.get("group_id"))
                group_info = await config_manager.get_group_info(gid)
                group_info["chat_prompt"] = [{"role": "system", "content": set_msg}]
                # 保存修改信息
                await config_manager.save_group_info()
                # 发送消息
                await self.send_group_msg(data.get("group_id"), "嗯呐(*ෆ´ ˘ `ෆ*)♡")
            elif data.get("message_type") == "private":
                uid = str(data.get("user_id"))
                private_info = await config_manager.get_private_info(uid)
                private_info["chat_prompt"] = [{"role": "system", "content": set_msg}]
                # 保存修改信息
                await config_manager.save_private_info()
                # 发送消息
                await self.send_private_msg(data.get("user_id"), "嗯呐(*ෆ´ ˘ `ෆ*)♡")

            return True
        
        # 聊天回复
        else:
            # 检查开关
            if not await self.check_enable(data, bot, disable_notice=False, close_notice=False):    # 聊天被关或被禁时触发不再提示
                return True

            if data.get("message_type") == "group":
                gid = str(data.get("group_id"))
                group_info = await config_manager.get_group_info(gid)
                group_info.setdefault("chat_prompt", [{"role": "system", "content": config_manager.info["prompt"].replace("{self_name}", config_manager.info["self_name"])}])
                if gid not in self.group_queues:     # 初始化
                    self.group_queues[gid] = []
                    self.group_processing[gid] = False
                    self.group_last_response[gid] = 0
                # 将消息加入队列
                self.group_queues[gid].append(msg)

                # 开始处理
                if not self.group_processing[gid]:
                    self.group_processing[gid] = True  # 置标志位
                    
                    while self.group_queues[gid]:
                        # 检查冷却时间
                        current_time = time.time()
                        time_since_last = current_time - self.group_last_response.get(gid, 0)
                        # 若未到时间则等待
                        if time_since_last < self.cooldown_time:
                            wait_time = self.cooldown_time - time_since_last
                            await asyncio.sleep(wait_time)
                        # 合并队列中的所有消息
                        merged_content = "\n".join(self.group_queues[gid])
                        self.group_queues[gid] = []  # 清空队列
                        # 构建对话历史
                        conversation = group_info["chat_prompt"].copy()
                        conversation.append({"role": "user", "content": merged_content})

                        # 调用API
                        response = await self.call_gpt_api(conversation)
                        self.group_last_response[gid] = time.time()

                        # 发送消息
                        await self.send_group_msg(data.get("group_id"), response)
                        # 保存修改信息
                        group_info["chat_prompt"].extend([{"role": "user", "content": merged_content}, {"role": "assistant", "content": response}])
                        group_info["chat_prompt"] = self.prompt_limit(group_info["chat_prompt"], self.max_turns)    # 限制最大对话轮数
                        await config_manager.save_group_info()

                    self.group_processing[gid] = False  # 复位标志位
                    
            elif data.get("message_type") == "private":
                uid = str(data.get("user_id"))
                private_info = await config_manager.get_private_info(uid)
                private_info.setdefault("chat_prompt", [{"role": "system", "content": config_manager.info["prompt"].replace("{self_name}", config_manager.info["self_name"])}])
                if uid not in self.private_queues:     # 初始化
                    self.private_queues[uid] = []
                    self.private_processing[uid] = False
                    self.private_last_response[uid] = 0
                # 将消息加入队列
                self.private_queues[uid].append(msg)

                # 开始处理
                if not self.private_processing[uid]:
                    self.private_processing[uid] = True  # 置标志位
                    
                    while self.private_queues[uid]:
                        # 检查冷却时间
                        current_time = time.time()
                        time_since_last = current_time - self.private_last_response.get(uid, 0)
                        # 若未到时间则等待
                        if time_since_last < self.cooldown_time:
                            wait_time = self.cooldown_time - time_since_last
                            await asyncio.sleep(wait_time)
                        # 合并队列中的所有消息
                        merged_content = "\n".join(self.private_queues[uid])
                        self.private_queues[uid] = []  # 清空队列
                        # 构建对话历史
                        conversation = private_info["chat_prompt"].copy()
                        conversation.append({"role": "user", "content": merged_content})

                        # 调用API
                        response = await self.call_gpt_api(conversation)
                        self.private_last_response[uid] = time.time()

                        # 发送消息
                        await self.send_private_msg(data.get("user_id"), response)
                        # 保存修改信息
                        private_info["chat_prompt"].extend([{"role": "user", "content": merged_content}, {"role": "assistant", "content": response}])
                        private_info["chat_prompt"] = self.prompt_limit(private_info["chat_prompt"], self.max_turns)    # 限制最大对话轮数
                        await config_manager.save_private_info()

                    self.private_processing[uid] = False  # 复位标志位

            return True
        
        return False


    # api调用
    async def call_gpt_api(self, prompt):
        # 返回str
        try:
            client = openai.AsyncOpenAI(api_key = config_manager.api_key, base_url = self.base_url)
            completion = await client.chat.completions.create(
                model = self.model,                 # 选择模型
                messages = prompt,                  # 内容
                temperature = self.temperature,     # 控制结果随机性
                # top_p = 0.7,
                # top_k = 50,
                # stream = False,                                 # 是否返回部分进度流
                # frequency_penalty = 0.5,                        # 现有词频惩罚[-2.0,2.0]
                # n = 1,                                          # 生成多少个结果
                # max_tokens = max_tokens                         # 最大令牌数
            )
            self.logger.debug(f"聊天api响应内容: {completion}")
            return completion.choices[0].message.content
        except Exception as e:
            self.logger.error(f"聊天api调用失败: {e}", exc_info=True)
            raise

    # 队列上限处理
    def prompt_limit(self, prompt, turns):
        """
        prompt: 输入的对话列表
        turns: 限制的对话轮次
        return 返回处理后的对话列表，超限则从第一轮开始弹出，直到满足限制(system设定不弹出)
        """
        if len(prompt) <= turns * 2 + 1:  # +1 考虑可能的system消息
            return prompt
    
        # 检查是否有system消息
        start_index = 1 if prompt and prompt[0].get("role") == "system" else 0
        
        # 计算需要保留的对话消息数量(一来一回算一轮)
        keep_count = turns * 2
        
        # 组合结果：system消息(如果有) + 最后keep_count条对话消息
        return prompt[:start_index] + prompt[-keep_count:]