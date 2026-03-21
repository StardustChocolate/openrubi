
import subprocess
import os
import time
from pathlib import Path
from textwrap import dedent
from configs.config_manager import config_manager
from utils.logger import get_logger
import json

class DockerManager:
    def __init__(self):
        self.name = None
        self.self_id = None
        self.ws_port = None
        self.webui_port = None
        self.ws_token = None
        self.webui_token = None
        self.mac_address = None
        self.project_path = None
        self.compose_path = None
        self.logger = get_logger()

    def init_docker(self):
        self.name = config_manager.info["self_name_en"].lower()
        self.self_id = config_manager.info["self_id"]
        self.ws_port = config_manager.ws_port
        self.webui_port = config_manager.webui_port
        self.ws_token = config_manager.ws_token
        self.webui_token = config_manager.webui_token
        mac_last_two = str(self.ws_port)[-2:].zfill(2)
        self.mac_address = f"02:42:ac:11:00:{mac_last_two}"
        current_path = Path(__file__).resolve()
        self.project_path = current_path.parent.parent  # 获取项目根目录路径
        self.compose_path = self.project_path / "napcat-docker" / self.name / "docker-compose.yml"

        compose_content = dedent(f"""
            # docker-compose.yml
            # NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker-compose -f ./docker-compose.yml up -d
            # NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker compose -f ./docker-compose.yml up -d
            services:
                napcat:
                    image: mlikiowa/napcat-docker:latest
                    container_name: {self.name}
                    restart: always
                    network_mode: bridge
                    mac_address: {self.mac_address}  # 添加MAC地址固化配置
                    
                    environment:
                        - NAPCAT_UID=${{NAPCAT_UID}}
                        - NAPCAT_GID=${{NAPCAT_GID}}
                    
                    ports:
                        - {self.ws_port}:3001
                        - {self.webui_port}:6099

                    volumes:
                        - ./napcat/config:/app/napcat/config
                        - ./ntqq:/app/.config/QQ
                        - {self.project_path}:{self.project_path}
        """).strip()

        self.compose_path.parent.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        with open(self.compose_path, 'w', encoding='utf-8') as f:
            f.write(compose_content)

        self.logger.info(f"生成 {self.name} 的 docker-compose.yml 文件成功")
    
    def init_napcat(self):
        # 检查onebot配置
        config_file_path = self.project_path / "napcat-docker" / self.name / "napcat" / "config" / f"onebot11_{self.self_id}.json"
        
        desired_ws_config = {
            "enable": True,
            "name": self.name,
            "host": "0.0.0.0",
            "port": 3001,
            "reportSelfMessage": False,
            "enableForcePushEvent": True,
            "messagePostFormat": "array",
            "token": self.ws_token,
            "debug": False,
            "heartInterval": 30000
        }

        default_config = {
            "network": {
                "httpServers": [],
                "httpSseServers": [],
                "httpClients": [],
                "websocketServers": [desired_ws_config],
                "websocketClients": [],
                "plugins": []
            },
            "musicSignUrl": "",
            "enableLocalFile2Url": False,
            "parseMultMsg": False,
            "imageDownloadProxy": ""
        }

        def write_default_config():
            config_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            self.logger.info("配置文件已覆写为默认配置")

        if config_file_path.exists():
            self.logger.info(f"配置文件 {config_file_path} 已存在，正在检查内容...")
            try:
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                network = content.get("network")
                if network is None or not isinstance(network, dict):
                    self.logger.info("配置文件缺少有效的 network 配置，正在覆写为默认配置...")
                    write_default_config()
                    return

                websocket_servers = network.get("websocketServers")
                if not isinstance(websocket_servers, list):
                    self.logger.info("配置文件 websocketServers 格式不正确，正在覆写为默认配置...")
                    write_default_config()
                    return

                # 继续处理 websocket_servers
                exist_item = None
                for item in websocket_servers:
                    if isinstance(item, dict) and item.get("name") == desired_ws_config["name"]:
                        exist_item = item
                        break

                if exist_item is not None:
                    if all(exist_item.get(k) == v for k, v in desired_ws_config.items()):
                        self.logger.info("找到同名 websocketServers 条目且与当前属性完全一致，保持不变")
                    else:
                        self.logger.info("找到同名 websocketServers 条目但属性不一致，正在更新条目...")
                        for k, v in desired_ws_config.items():
                            exist_item[k] = v
                        content["network"] = network
                        with open(config_file_path, 'w', encoding='utf-8') as f:
                            json.dump(content, f, indent=4, ensure_ascii=False)
                        self.logger.info("已将同名 websocketServers 条目更新为当前属性")
                else:
                    websocket_servers.append(desired_ws_config)
                    content["network"] = network
                    with open(config_file_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, indent=4, ensure_ascii=False)
                    self.logger.info("未找到同名 websocketServers 条目，已新增")

                self.logger.info(f"配置文件内容检查完成")
            except json.JSONDecodeError as e:
                self.logger.error(f"配置文件 JSON 格式错误: {e}")
        
        else:
            self.logger.info(f"配置文件 {config_file_path} 不存在，正在新建...")
            write_default_config()
            self.logger.info(f"配置文件 {config_file_path} 已创建并设置默认参数")

        # 检查 webui.json 配置
        webui_config_path = config_file_path.parent / "webui.json"
        if webui_config_path.exists():
            try:
                with open(webui_config_path, 'r', encoding='utf-8') as f:
                    webui_content = json.load(f)
                token = webui_content.get("token")
                auto_login = webui_content.get("autoLoginAccount")
                if token == self.webui_token and str(auto_login) == str(self.self_id):
                    self.logger.info("webui.json 配置检查通过")
                else:
                    webui_content["token"] = self.webui_token
                    webui_content["autoLoginAccount"] = str(self.self_id)
                    with open(webui_config_path, 'w', encoding='utf-8') as f:
                        json.dump(webui_content, f, indent=4, ensure_ascii=False)
                    self.logger.info("webui.json 配置已更新")
            except json.JSONDecodeError:
                self.logger.error("webui.json 文件格式错误")
        else:
            self.logger.info("webui.json 文件不存在")
    
    def start_docker(self):
        self.logger.info(f"正在启动Docker容器 {self.name}...")
        try:
            # 检查容器是否已经存在
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self.name}", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            if self.name in result.stdout.strip().split('\n'):
                self.logger.info(f"Docker容器 {self.name} 已存在，跳过启动...")
                return
            
            uid = os.getuid()
            gid = os.getgid()
            env = os.environ.copy()
            env["NAPCAT_UID"] = str(uid)
            env["NAPCAT_GID"] = str(gid)
            subprocess.run(
                ["docker", "compose", "-f", str(self.compose_path), "up", "-d"],
                check=True,
                env=env,
                cwd=self.compose_path.parent
            )
            time.sleep(15)  # 等待容器启动
            self.logger.info(f"Docker容器 {self.name} 启动成功")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"启动Docker容器 {self.name} 失败: {e}")


docker_manager = DockerManager()
