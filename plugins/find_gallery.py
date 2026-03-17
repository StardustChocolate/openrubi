
import json
from plugins.base_plugin import BasePlugin
from utils.pinyin_converter import load_pinyin_cache, process_string_fast
from pathlib import Path

class FindGallery(BasePlugin):
    
    # 插件基本信息
    name: str = "图鉴查找"
    description: str = "🌟输入角色名即可查找对应的角色或羁绊图鉴啦~支持同音字匹配"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        # 获取路径
        current_file = Path(__file__)
        self.character_dic_path = current_file.parent.parent / 'arkrecode' / 'members' / 'character_dic.json'
        self.character_dic_pinyin_path = current_file.parent.parent / 'arkrecode' / 'members' / 'character_dic_pinyin.json'
        self.character_gallery_path = current_file.parent.parent / 'arkrecode' / 'members' / 'gallery'
        self.bonds_dic_path = current_file.parent.parent / 'arkrecode' / 'bonds' / 'bonds_search_dic.json'
        self.bonds_dic_pinyin_path = current_file.parent.parent / 'arkrecode' / 'bonds' / 'bonds_search_dic_pinyin.json'
        self.bonds_gallery_path = current_file.parent.parent / 'arkrecode' / 'bonds' / 'gallery'
        self.related_dic_path = current_file.parent.parent / 'arkrecode' / 'bonds' / 'related_dic.json'
        # 检查路径是否存在
        if not self.character_dic_path.exists():
            raise FileNotFoundError(f"角色筛查字典缺失: {self.character_dic_path}")
        if not self.character_dic_pinyin_path.exists():
            raise FileNotFoundError(f"角色筛查拼音字典缺失: {self.character_dic_pinyin_path}")
        if not self.character_gallery_path.exists():
            raise FileNotFoundError(f"角色图鉴缺失: {self.character_gallery_path}")
        if not self.bonds_dic_path.exists():
            raise FileNotFoundError(f"羁绊筛查字典缺失: {self.bonds_dic_path}")
        if not self.bonds_dic_pinyin_path.exists():
            raise FileNotFoundError(f"羁绊筛查拼音字典缺失: {self.bonds_dic_pinyin_path}")
        if not self.bonds_gallery_path.exists():
            raise FileNotFoundError(f"羁绊图鉴缺失: {self.bonds_gallery_path}")
        if not self.related_dic_path.exists():
            raise FileNotFoundError(f"角色映射羁绊字典缺失: {self.related_dic_path}")
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        msg = self.get_texts(data)

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False

        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            return False
            
        cache = load_pinyin_cache() # 获取多音字的选择缓存
        msg_pinyin = process_string_fast(msg, cache) # 字符串转为拼音

        # 调取储存信息
        try:
            with open(self.character_dic_path, 'r', encoding='utf-8') as f:
                character_dic = json.load(f)
            with open(self.character_dic_pinyin_path, 'r', encoding='utf-8') as f:
                character_dic_pinyin = json.load(f)
            with open(self.bonds_dic_path, 'r', encoding='utf-8') as f:
                bonds_dic = json.load(f)
            with open(self.bonds_dic_pinyin_path, 'r', encoding='utf-8') as f:
                bonds_dic_pinyin = json.load(f)
            with open(self.related_dic_path, 'r', encoding='utf-8') as f:
                related_dic = json.load(f)
        except Exception as e:
            raise RuntimeError(f"读取筛查字典时出错: {e}") from e

        # 关键词判断（若查找到图鉴则对路径赋值）
        img_path = ""
        if msg in character_dic:    # 角色原文匹配
            img_path = self.character_gallery_path / f"{character_dic[msg]}.png"
        elif msg in bonds_dic:      # 羁绊原文匹配
            img_path = self.bonds_gallery_path / f"{bonds_dic[msg]}.png"
        elif msg_pinyin in character_dic_pinyin:    # 角色拼音匹配
            img_path = self.character_gallery_path / f"{character_dic_pinyin[msg_pinyin]}.png"
        elif msg_pinyin in bonds_dic_pinyin:        # 羁绊拼音匹配
            img_path = self.bonds_gallery_path / f"{bonds_dic_pinyin[msg_pinyin]}.png"
        elif msg.endswith("羁绊"):  # 通过角色查找关联羁绊
            msg_tmp = msg[:-2]
            msg_tmp_pinyin = process_string_fast(msg_tmp, cache)
            if msg_tmp in character_dic and character_dic[msg_tmp] in related_dic:
                img_path = self.bonds_gallery_path / f"{related_dic[character_dic[msg_tmp]]}.png"
            elif msg_tmp_pinyin in character_dic_pinyin and character_dic_pinyin[msg_tmp_pinyin] in related_dic:
                img_path = self.bonds_gallery_path / f"{related_dic[character_dic_pinyin[msg_tmp_pinyin]]}.png"
        
        if img_path:    # 若匹配到关键词
            # 检查开关
            if not await self.check_enable(data, bot):
                return True

            send_buff = f"[CQ:image,file={img_path}]"
            # 发送消息
            if data.get("message_type") == "group":
                await self.send_group_msg(data.get("group_id"), send_buff)
            elif data.get("message_type") == "private":
                await self.send_private_msg(data.get("user_id"), send_buff)
            
            return True

        return False
        