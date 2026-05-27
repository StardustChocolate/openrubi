import httpx
from pathlib import Path
from plugins.base_plugin import BasePlugin
from utils.logger import get_logger

class TTSRepeat(BasePlugin):
    """语音复读插件"""

    # 插件基本信息
    name: str = "语音复读"
    description: str = "🌟关键词[“说：”、“跟我说：”]可以让我用语音复读哦~"

    # TTS API URL
    tts_url = "http://127.0.0.1:9880"

    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.temp_dir = Path(__file__).parent.parent / "temp"  # 上级目录的temp文件夹
        self.temp_dir.mkdir(exist_ok=True)  # 确保temp目录存在

    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False
        
        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            return False

        # 检查关键词
        if msg.startswith(("说：", "说:", "跟我说：", "跟我说:")):

            # 目前功能还在开发中，先回复提示消息
            # if data.get("message_type") == "group":
            #     await self.send_group_msg(data.get("group_id"), "该功能还在开发中哦~")
            # elif data.get("message_type") == "private":
            #     await self.send_private_msg(data.get("user_id"), "该功能还在开发中哦~")
            # return True

            # 提取文本
            if msg.startswith(("说：", "说:")):
                text = msg[2:].strip()
            else:
                text = msg[4:].strip()

            if not text:
                if data.get("message_type") == "group":
                    await self.send_group_msg(data.get("group_id"), "说什么呀QAQ")
                elif data.get("message_type") == "private":
                    await self.send_private_msg(data.get("user_id"), "说什么呀QAQ")
                return True

            # 检查开关（如果有的话）
            if not await self.check_enable(data, bot):
                return True

            try:
                # 调用TTS API
                audio_path = await self.get_tts_audio(text)
                # audio_path = "/home/ubuntu/openrubi/temp/TTS_Output.wav"  # 临时测试路径

                if audio_path:
                    if data.get("message_type") == "group":
                        await self.send_group_msg(data.get("group_id"), f"[CQ:record,file={audio_path}]")
                    elif data.get("message_type") == "private":
                        await self.send_private_msg(data.get("user_id"), f"[CQ:record,file={audio_path}]")
                    return True
                else:
                    error_msg = "啊。。。啊吧啊吧\nFailed to obtain the audio"
                    if data.get("message_type") == "group":
                        await self.send_group_msg(data.get("group_id"), error_msg)
                    elif data.get("message_type") == "private":
                        await self.send_private_msg(data.get("user_id"), error_msg)
                    return True

            except Exception as e:
                self.logger.error(f"TTS复读错误: {e}")
                error_msg = "啊。。。啊吧啊吧\nRequest failed"
                if data.get("message_type") == "group":
                    await self.send_group_msg(data.get("group_id"), error_msg)
                elif data.get("message_type") == "private":
                    await self.send_private_msg(data.get("user_id"), error_msg)
                return True

        return False

    async def get_tts_audio(self, text: str) -> str:
        """调用TTS API获取音频文件，返回文件路径"""
        if not self.tts_url:
            return ""

        ref_audio_path = r"E:\Project\GPT-SoVITS-v2pro-20250604\output\slicer_opt\H076_Summon.wav_0000000000_0000135360.wav"
        prompt_text = "子供扱いしないで、ちゃんと体を見てください。"
        req = {
            "text": text,
            "text_lang": "auto",
            "ref_audio_path": ref_audio_path,
            "prompt_text": prompt_text,
            "prompt_lang": "ja",
            "media_type": "wav",
            "text_split_method": "cut5",
            "batch_size": 1,
            "streaming_mode": False,
        }

        # if not ref_audio_path.exists():
        #     self.logger.error(f"参考音频不存在: {ref_audio_path}")
        #     return ""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.tts_url}/tts", json=req, timeout=60)
                if response.status_code == 200:
                    audio_filename = f"tts_output.wav"
                    audio_path = self.temp_dir / audio_filename
                    with open(audio_path, "wb") as f:
                        f.write(response.content)
                    return str(audio_path)
                else:
                    self.logger.error(f"TTS API错误: {response.status_code} body={response.text}")
                    return ""
        except Exception as e:
            self.logger.error(f"TTS请求错误: {e}")
            return ""