<div align="center">

# Yuki 🌟

<img src="./images/yuki/yuki.png" width="200" alt="Yuki">

A simple QQ bot terminal implementation to customize your AI catgirl.

[简体中文](./README.md) | [English](./README.en.md)

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-red.svg)](./LICENSE)
[![NapCat](https://img.shields.io/badge/Built%20with-NapCat-27A7E7.svg)](https://github.com/NapNeko/NapCatQQ)
[![QQ Group](https://img.shields.io/badge/QQ%20Group-512152733-5865F2.svg)](https://qm.qq.com/q/tE6OmKvDhu)

</div>

---

## 🍀 Preface

This is an early-stage project that has been maintained intermittently since the Mirai era. We are extremely grateful to the authors of open-source frameworks such as Mirai, go-cqhttp, Lagrange, Shamrock, and NapCat for their contributions. It is their dedication that has made this project possible.

⚠️ Note: This project is for learning and communication purposes only. It is provided "AS IS" and "AS AVAILABLE", without any express or implied warranties. You assume all risks associated with using this project.

## ✨ Features

- 🎯 **Plugin-based Architecture** – Dynamically load plugins to easily extend functionality.
- 💬 **Chat** – By default, it calls the DeepSeek model, supports multi-turn conversations, and you can modify the code to use other models.
- 🔄 **Asynchronous Processing** – Efficient event loop based on asyncio.
- 🎛️ **Flexible Configuration** – YAML configuration file, supports multiple instances.
- 👥 **Group Pet Features** – Poke, welcome messages, morning greetings, Iching, Crazy Thursday, piggy tests, and many other fun features.

---

## 📦 Quick Start

- Pull the NapCat Docker image: `docker pull mlikiowa/napcat-docker`
- In your `docker-compose.yml`, map the last volume path to the actual location of this project after downloading.
- Start the container with:  
  `NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker compose -f ./docker-compose.yml up -d`
- Use the web UI to log in to your QQ account and configure the WebSocket server.
- Set up the Python environment according to the `requirements.txt` file.
- Modify your configuration in `config.yml`.
- Activate the environment and run: `python main.py`.  
  Use `-c` to specify a configuration file (defaults to `config.yml` if not provided).