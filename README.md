<div align="center">

# Yuki 🌟

<img src="./images/yuki/yuki.png" width="200" alt="Yuki">

一个简易的 QQ 机器人终端实现，定制你的AI猫娘。

[简体中文](./README.md) | [English](./README.en.md)

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-red.svg)](./LICENSE)
[![NapCat](https://img.shields.io/badge/Built%20with-NapCat-27A7E7.svg)](https://github.com/NapNeko/NapCatQQ)
[![QQ Group](https://img.shields.io/badge/QQ%20Group-512152733-5865F2.svg)](https://qm.qq.com/q/tE6OmKvDhu)

</div>

---

## 🍀 前言

这是一个早期项目，自Mirai时代以来断断续续维护至今，十分感谢Mirai、go-cqhttp、Lagrange、Shamrock、NapCat等开源框架作者们的奉献，是你们让此项目得以实现

⚠️ 注意：本项目仅供学习交流使用，本项目按“原样”和“可用性”提供，不附带任何明示或暗示的保证。使用本项目的风险由您自行承担。

## ✨ 功能特性

- 🎯 **插件化架构** - 支持动态加载插件，轻松扩展功能
- 💬 **聊天** - 默认调用 DeepSeek 模型，支持多轮对话，可自行修改代码以使用其它模型
- 🔄 **异步处理** - 基于 asyncio 的高效事件循环
- 🎛️ **灵活配置** - YAML 配置文件，支持多开
- 👥 **群宠** - 戳一戳、入群欢迎、早安、一言、疯狂星期四、猪猪测试等等丰富的整活功能

---

## 📦 快速开始

- 使用 `docker pull mlikiowa/napcat-docker` 拉取 NapCat Docker
- 配置 `docker-compose.yml` 文件中的 `volumes` 最后一行映射路径改为下载后本项目的实际位置
- `NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker compose -f ./docker-compose.yml up -d` 启动docker
- 使用 webui 登录自己的账号并配置 ws服务器
- 根据 `requirements.txt` 文件配置 python 环境
- `config.yml` 中修改自己的配置
- 启用环境后 `python main.py` 运行即可；`-c` 可以指定配置文件，不设默认用`config.yml`

