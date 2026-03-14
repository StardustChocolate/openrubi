
from plugins.base_plugin import BasePlugin
from configs.config_manager import config_manager
import asyncio
import subprocess

class Test(BasePlugin):
    """测试插件"""
    
    # 插件基本信息
    name: str = "test"
    description: str = "这是一个测试插件，可以修改为你需要测试的任何内容"
    
    def __init__(self):
        super().__init__()
        self.priority = 50  # 优先级，范围0-100，数字越小优先级越高，默认50
        
    async def on_message(self, data, bot) -> bool:
        """处理消息事件"""
        # 获取消息
        msg = self.get_texts(data)
        # 获取权限
        bot_admin = data.get("user_id") in config_manager.info["admin_id"]  

        # 该功能在群聊中不@时不响应
        if not self.at_if_group(data):
            return False
        
        # 非好友私聊过滤
        if self.filter_nonfriend(data):
            return False

        # 只响应群消息
        # if data.get("message_type") != "group":
        #     return False

        # 匹配关键词
        if msg == "测试" and bot_admin: 
            # 检查开关
            # if not await self.check_enable(data, bot):
            #     return True

            #异步重启Docker容器
            container_name = config_manager.info["self_name_en"]
            try:
                # 创建子进程并异步执行
                process = await asyncio.create_subprocess_exec(
                    "docker", "restart", container_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    bot.logger.info(f"容器 {container_name} 重启成功")
                else:
                    bot.logger.info(f"重启失败: {stderr.decode()}")
            
            except Exception as e:
                bot.logger.info(f"执行出错: {e}")
            
            return True
        
        return False