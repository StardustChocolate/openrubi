
import yaml
import json
import sys
import asyncio
from pathlib import Path

class ConfigManager:
    def __init__(self):
        # 初始化所有配置属性
        self.config = None           # 总配置
        self.config_name = None      # 配置自身文件名
        self.info = None             # 基本信息
        self.port = None             # 端口
        self.token = None            # ws服务器token
        self.api_key = None          # 大模型api-key
        self.path = None             # 路径
        self.self_info = None        # 自身信息
        self.private_info = None     # 私聊信息
        self.group_info = None       # 群组信息
        self.doc_path = None         # 信息文件保存路径
        # 添加异步锁
        self._self_info_lock = asyncio.Lock()
        self._private_info_lock = asyncio.Lock()
        self._group_info_lock = asyncio.Lock()
        # 脏标记管理(批量写入相关)
        self._dirty_flags = {
            'self_info': False,
            'private_info': False,
            'group_info': False
        }
        self._debounce_delay = 5    # 防抖延迟，可调整

    def load_config(self, config_name):
        """加载配置文件并初始化相关属性"""
        try:
            self.config_name = config_name
            base_path = Path("./configs")
            full_path = base_path / config_name
            if not full_path.is_file():
                full_path = base_path / f"{config_name}.yaml" 
                if not full_path.is_file():
                    print(f"配置文件不存在: {base_path / config_name}")
                    sys.exit(1)
            with open(full_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)  # 使用更安全的加载方式
            self.info = self.config.get("info")
            self.port = self.config.get("port")
            self.api_key = self.config.get("api_key")
            self.token = self.config.get("token")
            self.path = self.config.get('path')
            self.doc_path = f"./data/{full_path.stem}"  # 直接取配置文件的名字
            # 初始化自身信息
            try:
                with open(f'{self.doc_path}/self_info.json', 'r', encoding='utf-8') as f:
                    self.self_info = json.load(f)   # 自身信息
            except (FileNotFoundError, json.decoder.JSONDecodeError):   # 如果文件不存在或JSON解析失败，初始化一个空字典
                self.self_info = {}
            # 初始化私聊信息
            try:
                with open(f'{self.doc_path}/private_info.json', 'r', encoding='utf-8') as f:
                    self.private_info = json.load(f)   # 私聊信息
            except (FileNotFoundError, json.decoder.JSONDecodeError):   # 如果文件不存在或JSON解析失败，初始化一个空字典
                self.private_info = {} 
            # 初始化群组信息
            try:
                with open(f'{self.doc_path}/group_info.json', 'r', encoding='utf-8') as f:
                    self.group_info = json.load(f)   # 群组信息
            except (FileNotFoundError, json.decoder.JSONDecodeError):   # 如果文件不存在或JSON解析失败，初始化一个空字典
                self.group_info = {} 
        except FileNotFoundError:
            raise RuntimeError(f"配置文件 {full_path} 不存在！")
        except yaml.YAMLError as e:
            raise RuntimeError(f"配置文件解析错误: {str(e)}")

    async def _debounced_save(self, data_type, data, lock, filename):
        """防抖保存：短时间内多次调用只执行最后一次"""
        # 标记脏数据
        self._dirty_flags[data_type] = True
        
        # 等待防抖延迟
        await asyncio.sleep(self._debounce_delay)
        
        async with lock:  # 使用各自的锁
            # 检查是否仍然需要保存
            if self._dirty_flags[data_type]:
                self._dirty_flags[data_type] = False
                await self._save_data(data, filename)

    async def save_self_info(self):
        """安全保存自身信息（使用异步锁）"""
        asyncio.create_task(
            self._debounced_save('self_info', self.self_info, 
                               self._self_info_lock, 'self_info.json')
        )

    async def save_private_info(self):
        """安全保存私聊信息（使用异步锁）"""
        asyncio.create_task(
            self._debounced_save('private_info', self.private_info,
                               self._private_info_lock, 'private_info.json')
        )

    async def save_group_info(self):
        """安全保存群聊信息（使用异步锁）"""
        asyncio.create_task(
            self._debounced_save('group_info', self.group_info,
                               self._group_info_lock, 'group_info.json')
        )

    async def _save_data(self, data, filename):
        """通用的保存数据方法"""
        # 确保数据目录存在
        Path(self.doc_path).mkdir(parents=True, exist_ok=True)
            
        # 创建临时文件，避免写入过程中出现问题导致文件损坏
        temp_path = f'{self.doc_path}/{filename}.tmp'
        final_path = f'{self.doc_path}/{filename}'
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # 原子性重命名操作
            Path(temp_path).rename(final_path)
        except Exception as e:
            # 如果出现错误，删除临时文件
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise e
 
    async def get_self_info(self) -> dict:
        """获取自身信息，带初始化"""
        change_flag = False
        if "default_close_plugins" not in self.self_info:
            self.self_info["default_close_plugins"] = ["聊天", "涩涩"]   # 默认关闭的插件(用于群聊)
            change_flag = True
        if "disable_plugins" not in self.self_info:
            self.self_info["disable_plugins"] = ["jmcomic"]             # 默认禁用的插件
            change_flag = True
        if "group_register" not in self.self_info:
            self.self_info["group_register"] = []                       # 群聊登记(由于QQ存在人少群邀请无视同意的情况，故在此设置保护，未登记的群聊在进群后将自动退群)
            change_flag = True
        if change_flag:
            await self.save_self_info() # 若有修改则启动保存
        return self.self_info

    async def get_private_info(self, user_id) -> dict:
        """获取私聊信息，带初始化"""
        uid = str(user_id)
        change_flag = False
        if uid not in self.private_info:
            self.private_info[uid] = {}   # 若无记录先建立空字典
            change_flag = True
        if change_flag:
            await self.save_private_info() # 若有修改则启动保存
        return self.private_info[uid]
    
    async def get_group_info(self, group_id):
        """获取群聊信息，带初始化"""
        gid = str(group_id)
        change_flag = False
        if gid not in self.group_info:
            self.group_info[gid] = {}   # 若无记录先建立空字典
            change_flag = True
        if "close_plugins" not in self.group_info[gid]:
            self_info = await self.get_self_info()
            self.group_info[gid]["close_plugins"] = self_info["default_close_plugins"]  # 关闭的插件
            change_flag = True
        if change_flag:
            await self.save_group_info() # 若有修改则启动保存
        return self.group_info[gid]

# 创建全局配置管理器实例
config_manager = ConfigManager()