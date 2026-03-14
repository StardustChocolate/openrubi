import logging
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "Yuki"):
    """设置日志"""
    log_dir = Path(f'./logs/{name}')
    log_dir.mkdir(parents=True, exist_ok=True)  # parents=True 可以创建多级目录
    
    # 创建日志器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # logger.setLevel(logging.DEBUG)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建滚轮文件处理器
    log_file = f'logs/{name}/{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,  # 保留5个备份文件
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 添加处理器到日志器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def get_logger():
    """获取日志器"""
    return logging.getLogger()
