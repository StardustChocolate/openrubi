<div align="center">

# OpenRubi 🌟

<img src="./images/openrubi.png" width="200" alt="Yuki">

星陨计划露比机器人，基于 Python + NapCat 制作，Fork自Yuki

[简体中文](./README.md) | [English](./README.en.md)

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-red.svg?style=flat-square)](./LICENSE)
[![NapCat](https://img.shields.io/badge/Docker-NapCat-27A7E7.svg?style=flat-square)](https://github.com/NapNeko/NapCatQQ)
[![Yuki](https://img.shields.io/badge/Fork-yuki-4BC51D?style=flat-square)](https://github.com/yingxueOvO/yuki)
[![OneBot](https://img.shields.io/badge/OneBot-11-black?style=flat-square)](https://github.com/howmanybots/onebot)
[![QQ Group](https://img.shields.io/badge/QQ%20Group-1032070842-5865F2.svg?style=flat-square)](https://qm.qq.com/q/YsvXane7Wq)

</div>

---

## ✨ 功能特性

- 🔍 **图鉴查询** - 通过名称或别称查询角色、羁绊图鉴，支持模糊匹配
- ⏱️ **速度计算** - 团战测速，详见帮助说明
- 🎫 **兑换码** - 查询兑换码
- 💬 **聊天** - 内置露比性格，可自定义调整
- 🎛️ **灵活配置** - YAML 配置文件，支持多开
- 🎯 **插件化架构** - 轻松扩展功能
- 🎉 **Yuki功能** - 戳一戳、入群欢迎、早安、一言、疯狂星期四、猪猪测试等等丰富的整活功能


## 📦 快速开始

### 一键式启动（推荐）

- 使用 `docker pull mlikiowa/napcat-docker` 拉取 NapCat Docker
- 根据 `requirements.txt` 文件配置 python 环境
- `configs/config.yml` 中修改自己的配置，也可自己新建配置
- 运行`python main.py` 、`-c`可指定其它配置文件
- docker启动后使用webui登录
- 登录成功后等待自动重连即可

### 旧版方法

- 使用 `docker pull mlikiowa/napcat-docker` 拉取 NapCat Docker
- 配置 `docker-compose.yml` 文件中的 `volumes` 最后一行映射路径改为下载后本项目的实际位置
- `NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker compose -f ./docker-compose.yml up -d` 启动docker
- 使用 webui 登录自己的账号并配置 ws服务器
- 根据 `requirements.txt` 文件配置 python 环境
- `config.yml` 中修改自己的配置
- 启用环境后 `python main.py` 运行即可；`-c` 可以指定配置文件，不设默认用`config.yml`

## ⚠️注意

- 本项目仅供**学习、研究和参考**用途，不构成任何形式的正式建议或承诺。

- 本软件按“**原样**”（AS IS）提供，不附带任何明示或暗示的担保，包括但不限于适销性、特定用途适用性及不侵权的担保。作者或版权持有人不对软件的使用或其他处理方式所产生的结果负责。

- 在任何情况下，即使事先被告知可能发生损害，作者或贡献者均不对因使用本软件或无法使用本软件而引起的任何索赔、损害或其他责任负责，无论是合同诉讼、侵权行为还是其他原因。

- 如果本项目中包含指向第三方网站、资源或代码的链接，这些内容仅供参考，作者不对其准确性、合法性或安全性承担任何责任。

- 用户应自行确保其使用本项目的行为符合所在国家/地区的法律法规。因使用本项目而产生的任何法律风险由用户自行承担。

- 若本项目无意中侵犯了任何个人或实体的权益，请通过 [Issue] 或邮件联系我们，我们将在核实后第一时间处理（如删除相关内容）。
