<div align="center">

# OpenRubi 🌟

<img src="./images/openrubi.png" width="200" alt="Yuki">

Rubi Bot for Starfall Chronicles, built with Python + NapCat, forked from Yuki

[简体中文](./README.md) | [English](./README.en.md)

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-red.svg?style=flat-square)](./LICENSE)
[![NapCat](https://img.shields.io/badge/Docker-NapCat-27A7E7.svg?style=flat-square)](https://github.com/NapNeko/NapCatQQ)
[![Yuki](https://img.shields.io/badge/Fork-yuki-4BC51D?style=flat-square)](https://github.com/yingxueOvO/yuki)
[![OneBot](https://img.shields.io/badge/OneBot-11-black?style=flat-square)](https://github.com/howmanybots/onebot)
[![QQ Group](https://img.shields.io/badge/QQ%20Group-1032070842-5865F2.svg?style=flat-square)](https://qm.qq.com/q/YsvXane7Wq)

</div>

---

## ✨ Features

- 🔍 **Encyclopedia Query** - Search for character and bond entries by name or alias, with fuzzy matching support
- ⏱️ **Speed Calculator** - Guild battle speed testing; see help for details
- 🎫 **Redemption Codes** - Query redemption codes
- 💬 **Chat** - Built-in Rubi personality, customizable
- 🎛️ **Flexible Configuration** - YAML configuration files, supports multiple instances
- 🎯 **Plugin Architecture** - Easily extend functionality
- 🎉 **Yuki Features** - Poke, welcome messages, morning greetings, quotes, Crazy Thursday, Piggy Test, and many other fun plugins

## 📦 Quick Start

### One-Click Start (Recommended)

- Pull the NapCat Docker image using `docker pull mlikiowa/napcat-docker`
- Configure the Python environment based on the `requirements.txt` file
- Modify your own configuration in `configs/config.yml`; you can also create a new configuration file
- Run `python main.py` ; use `-c` to specify a different configuration file
- After starting Docker, log in using the web UI
- Once logged in successfully, wait for the automatic reconnection

### Legacy Method

- Pull the NapCat Docker image using `docker pull mlikiowa/napcat-docker`
- In the `docker-compose.yml` file, change the last line of the `volumes` mapping path to the actual location of the downloaded project
- Start Docker with `NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker compose -f ./docker-compose.yml up -d`
- Log in to your account using the web UI and configure the WebSocket server
- Configure the Python environment based on the `requirements.txt` file
- Modify your configuration in `config.yml`
- After activating the environment, run `python main.py` ; use `-c` to specify a configuration file; if not set, `config.yml` is used by default

## ⚠️ Disclaimer

- This project is for **learning, research, and reference purposes only** and does not constitute any form of formal advice or commitment.

- This software is provided "**AS IS**", without any express or implied warranties, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement. The author or copyright holders shall not be liable for any results arising from the use of this software or other methods of handling it.

- In no event shall the authors or contributors be liable for any claim, damages, or other liability arising from the use of or inability to use this software, whether in contract, tort, or otherwise, even if advised of the possibility of such damage.

- If this project contains links to third-party websites, resources, or code, they are provided for reference only. The author assumes no responsibility for their accuracy, legality, or security.

- Users are solely responsible for ensuring their use of this project complies with the laws and regulations of their country/region. Any legal risks arising from the use of this project shall be borne by the user.

- If this project inadvertently infringes upon the rights of any individual or entity, please contact us via [Issue] or email. We will verify and address the issue promptly (e.g., remove the relevant content).
