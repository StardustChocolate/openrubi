
import asyncio
import uuid
from typing import Dict, Any, Optional, Callable, Awaitable
from utils.logger import get_logger

class APIClient:
    """API客户端，管理异步请求-响应"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = get_logger()
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
    def generate_echo(self) -> str:
        """生成唯一的echo标识"""
        return str(uuid.uuid4())
        
    async def call_api(self, 
                      action: str, 
                      params: Dict[str, Any],
                      timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """
        调用API并等待响应
        """
        echo = self.generate_echo()
        future = asyncio.Future()
        self.pending_requests[echo] = future
        
        # 构造请求数据
        request_data = {
            "action": action,
            "params": params,
            "echo": echo
        }
        
        try:
            # 发送请求
            await self.bot.send_message(request_data)
            self.logger.debug(f"发送API请求: {action}, echo: {echo}")
            
            # 等待响应，带超时
            return await asyncio.wait_for(future, timeout=timeout)
            
        except asyncio.TimeoutError:
            self.logger.warning(f"API请求超时: {action}, echo: {echo}")
            return None
        except Exception as e:
            self.logger.error(f"API请求失败: {action}, 错误: {e}")
            return None
        finally:
            # 清理
            self.pending_requests.pop(echo, None)
            
    def handle_api_response(self, data):
        """处理API响应"""
        echo = data.get("echo")
        if echo and echo in self.pending_requests:
            future = self.pending_requests[echo]
            if not future.done():
                future.set_result(data.get("data"))
                self.logger.debug(f"收到API响应: {echo}")