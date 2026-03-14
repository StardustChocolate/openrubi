import websockets
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional
from core.api_client import APIClient
from core.plugin_manager import PluginManager
from utils.logger import get_logger
from configs.config_manager import config_manager

class QQBotClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.api_client = None  # API客户端(napcat-API, 用于处理过程中获取数据)
        self.plugin_manager = PluginManager()
        self.logger = get_logger()
        self.is_connected = False
        self.reconnect_attempts = 0  # 重连尝试次数
        self.max_reconnect_attempts = 10  # 最大重连尝试次数
        self.base_reconnect_delay = 10  # 基础重连延迟（秒）
        self.max_reconnect_delay = 300  # 最大重连延迟（秒）

    async def connect(self):
        """连接WebSocket服务器"""
        self.reconnect_attempts = 0
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.logger.info(f"正在连接WebSocket服务器: {self.ws_url}")
                self.websocket = await websockets.connect(
                    self.ws_url,
                    ping_interval=None      # Ping 间隔
                    # ping_timeout=60,      # Ping 超时时间
                    # close_timeout=None,    # 禁用自动关闭
                )
                self.is_connected = True
                self.reconnect_attempts = 0  # 重置重连计数
                self.logger.info("WebSocket连接成功")
                
                # 初始化API客户端
                self.api_client = APIClient(self)

                # 加载插件
                await self.plugin_manager.load_plugins(self)

                # 开始监听消息
                await self._listen_messages()
                
            except websockets.exceptions.ConnectionClosed:
                self.is_connected = False
                self.logger.warning("WebSocket连接已关闭，尝试重连...")
                await self._handle_reconnect()
                
            except websockets.exceptions.WebSocketException as e:
                self.is_connected = False
                self.logger.error(f"WebSocket连接异常: {e}，尝试重连...")
                await self._handle_reconnect()
                
            except Exception as e:
                self.is_connected = False
                self.logger.error(f"连接WebSocket服务器失败: {e}，尝试重连...")
                await self._handle_reconnect()
    
    async def _handle_reconnect(self):
        """处理重连逻辑"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error("已达到最大重连次数，停止重连")
            return
            
        self.reconnect_attempts += 1
        
        # 使用指数退避算法计算重连延迟
        # delay = min(self.base_reconnect_delay * (2 ** (self.reconnect_attempts - 1)), 
        #             self.max_reconnect_delay)
        # 使用固定时间计算重连延迟
        delay = min(self.base_reconnect_delay, 
                    self.max_reconnect_delay)

        self.logger.info(f"第 {self.reconnect_attempts} 次重连尝试，等待 {delay} 秒后重连...")
        await asyncio.sleep(delay)

        # 次数过多时重启docker
        if self.reconnect_attempts >= 3:
            await self.docker_restart()
            self.logger.info("重启docker，缓冲30s")
            await asyncio.sleep(30)

    
    async def _listen_messages(self):
        """监听WebSocket消息"""
        async for message in self.websocket:
            # 不等待，直接创建新任务处理
            asyncio.create_task(self._handle_message(message))
            # await self._handle_message(message)
    
    async def _handle_message(self, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            self.logger.debug(f"收到消息: {data}")
            
            if data.get("echo"):
                # API响应交给API客户端处理
                self.api_client.handle_api_response(data)
            else:
                # 分发事件给插件处理
                await self.plugin_manager.handle_event(data, self)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"消息JSON解析失败: {e}, 原始消息: {message}")
        except Exception as e:
            self.logger.error(f"处理消息时出错: {e}")
    
    async def send_message(self, message_data: Dict[str, Any]):
        """发送消息"""
        if not self.is_connected or not self.websocket:
            self.logger.error("WebSocket未连接，无法发送消息")
            return
            
        try:
            message_str = json.dumps(message_data)
            await self.websocket.send(message_str)
            self.logger.debug(f"发送消息: {message_data}")
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
    
    async def disconnect(self):
        """断开连接"""
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()
        self.logger.info("WebSocket连接已关闭")

    async def docker_restart(self):
        """异步重启Docker容器"""
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
                self.logger.info(f"容器 {container_name} 重启成功")
                return True
            else:
                self.logger.info(f"重启失败: {stderr.decode()}")
                return False
        
        except Exception as e:
            self.logger.info(f"执行出错: {e}")
            return False
