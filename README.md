<div align="center">

![HibiAPI Logo](.github/logo.svg)

# HibiAPI

[![Demo Version](https://img.shields.io/badge/dynamic/json?label=demo%20status&query=%24.info.version&url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json&style=for-the-badge&color=lightblue)](https://api.obfs.dev)

![Code Linting](https://github.com/mixmoe/HibiAPI/workflows/Code%20Linting/badge.svg)
![Testing](https://github.com/mixmoe/HibiAPI/workflows/Testing/badge.svg)

![Version](https://img.shields.io/badge/dynamic/yaml?color=green&label=version&query=%24.version&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmixmoe%2FHibiAPI%2Fmain%2Fconfigs%2Fgeneral.default.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/mixmoe/HibiAPI)
[![GitHub license](https://img.shields.io/github/license/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/network)
[![GitHub issues](https://img.shields.io/github/issues/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/issues)
![Python version](https://img.shields.io/badge/python-3.8%2B-yellowgreen)

**An alternative implement of Imjad API.**

**Imjad API 的开源替代.**

</div>

---

## 前言

由于Imjad API使用人数过多致使调用超出限制, 所以本人希望提供一个开源替代来供社区进行自由的部署和使用, 从而减轻一部分该API的使用压力

## 实现进度

***[请点击此处查看](https://github.com/mixmoe/HibiAPI/issues/1)***

## 部署指南

### 准备环境

部署本项目, 你需要:

- Python 3.8 及以上

- 一个通畅的网络
  - 为了使用Pixiv等API功能, 您可能需要设置一个HTTP代理
  - 如果依赖安装过慢, 请更换一个在您地区速度较快的pip镜像

### 安装依赖

#### 使用传统 `pip`

> `requirements.txt` 生成状态: ![Generate Requirements](https://github.com/mixmoe/HibiAPI/workflows/Generate%20Requirements/badge.svg)

1. 保存本仓库到本地目录, 命令行进入该目录

2. **(推荐)** 使用 `virtualenv` 等工具设置虚拟环境

3. 安装依赖
    - 通常来讲,你只需要执行 `pip install -r requirements.txt`
    - 如果你遇到一些权限问题或者安装后无法使用, 请自行解决

#### 使用 `poetry` (推荐)

1. 保存本仓库到本地目录, 命令行进入该目录

2. [安装`poetry`](https://python-poetry.org/docs/#installation)

3. 激活虚拟环境
    - `poetry install` 安装本项目依赖 (可能需要较长时间)
    - `poetry shell` 进入激活了虚拟环境的shell

### 运行程序

1. 首次运行生成配置文件
    - `python main.py` 直接运行, 如果有未生成的配置文件会报错退出
    - 进入`config`目录修改对应的配置文件
    - **注意!后缀为.default.yml的配置文件为默认配置文件,不建议修改**

2. 运行程序
    - 在虚拟环境中直接输入 `python main.py` 即可

## 鸣谢

> - [@journey-ad](https://github.com/journey-ad) 大佬的 [Imjad API](https://api.imjad.cn/)
> - 为本项目实现API提供参考的各种开源项目
>   - Pixiv: [`Mikubill/pixivpy-async`](https://github.com/Mikubill/pixivpy-async) [`upbit/pixivpy`](https://github.com/upbit/pixivpy)
>   - Bilibili: [`SocialSisterYi/bilibili-API-collect`](https://github.com/SocialSisterYi/bilibili-API-collect) [`soimort/you-get`](https://github.com/soimort/you-get)
>   - 网易云音乐: [`metowolf/NeteaseCloudMusicApi`](https://github.com/metowolf/NeteaseCloudMusicApi) [`greats3an/pyncm`](https://github.com/greats3an/pyncm) [`Binaryify/NeteaseCloudMusicApi`](https://github.com/Binaryify/NeteaseCloudMusicApi)