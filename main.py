
import asyncio
import sys
import argparse
from core.bot_client import QQBotClient
from utils.logger import setup_logger, get_logger
from configs.config_manager import config_manager

class QQBot:
    def __init__(self, ws_url: str = "ws://127.0.0.1:3001/ws"):
        self.logger = get_logger()
        self.bot_client = QQBotClient(ws_url)
        
    async def start(self):
        """启动机器人"""
        self.logger.info("正在启动QQ机器人...")
        try:
            await self.bot_client.connect()
        except KeyboardInterrupt:
            self.logger.info("收到停止信号，正在关闭机器人...")
        except Exception as e:
            self.logger.error(f"机器人运行出错: {e}")
        finally:
            await self.bot_client.disconnect()

def main():
    # 解析命令行参数
    args = parse_arguments()

    # 设置配置路径并加载配置
    config_manager.load_config(args.config)

    # 设置日志
    logger = setup_logger(config_manager.info["self_name_en"])

    # 启动机器人
    if config_manager.token:
        ws_url = f"ws://127.0.0.1:{config_manager.port}/ws?access_token={config_manager.token}"
    else:
        ws_url = f"ws://127.0.0.1:{config_manager.port}/ws"
    bot = QQBot(ws_url)
    asyncio.run(bot.start())

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='OpenRubi')
    parser.add_argument('-c', '--config', default='config.yaml', help='指定配置文件路径')
    return parser.parse_args()


if __name__ == "__main__":
    main()