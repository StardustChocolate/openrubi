<div align="center">

# OpenRubi 🌟

<img src="./images/openrubi.png" width="200" alt="Yuki">

A Rubi robot for the Starfall Project, built with Python + NapCat, forked from Yuki

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

- 🔍 **Encyclopedia Query** - Query character and bond encyclopedias by name or alias, with fuzzy matching support
- ⏱️ **Speed Calculation** - Guild battle speed calculation, see help for details
- 🎫 **Redemption Codes** - Query redemption codes
- 💬 **Chat** - Built-in Rubi personality, customizable
- 🎛️ **Flexible Configuration** - YAML configuration file, supports multi-instance operation
- 🎯 **Plugin Architecture** - Easily extend functionality
- 🎉 **Yuki Features** - Poke, welcome messages, morning greetings, quotes, KFC quotes, Piggy test, and more fun features


## 📦 Quick Start

- Pull the NapCat Docker image using `docker pull mlikiowa/napcat-docker`
- In the `docker-compose.yml` file, change the last line of the `volumes` mapping path to the actual location of the project after downloading
- Start Docker with `NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker compose -f ./docker-compose.yml up -d`
- Log in to your account using the webui and configure the websocket server
- Set up the Python environment according to the `requirements.txt` file
- Modify your configuration in `config.yml`
- Activate the environment and run with `python main.py`; use `-c` to specify a configuration file (defaults to `config.yml` if not specified)

## ⚠️ Important Notes

- This project is provided for **learning, research, and reference purposes only** and does not constitute any form of official advice or commitment.

- This software is provided "**AS IS**", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from, out of, or in connection with the software or the use or other dealings in the software.

- In no event shall the authors or contributors be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software, even if advised of the possibility of such damages.

- If this project contains links to third-party websites, resources, or code, these are for reference only. The authors assume no responsibility for their accuracy, legality, or security.

- Users are responsible for ensuring their use of this project complies with the laws and regulations of their country/region. Any legal risks arising from the use of this project are borne solely by the user.

- If this project inadvertently infringes upon any individual or entity's rights, please contact us via [Issue] or email. We will verify and promptly address the matter (e.g., remove relevant content).