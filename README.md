<div align="center">

![HibiAPI Logo](.github/logo.svg)

# HibiAPI

[![Demo Version](https://img.shields.io/badge/dynamic/json?label=demo%20status&query=%24.info.version&url=https%3A%2F%2Fhibiapi.herokuapp.com%2Fopenapi.json&style=for-the-badge&color=lightblue)](https://hibiapi.herokuapp.com)

![Lint](https://github.com/mixmoe/HibiAPI/workflows/Lint/badge.svg)
![Test](https://github.com/mixmoe/HibiAPI/workflows/Test/badge.svg)

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

- 由于Imjad API<sup>[这是什么?](https://github.com/mixmoe/HibiAPI/wiki/FAQ#%E4%BB%80%E4%B9%88%E6%98%AFimjad-api)</sup>使用人数过多, 致使调用超出限制, 所以本人希望提供一个开源替代来供社区进行自由的部署和使用, 从而减轻一部分该API的使用压力

## 优势

### 开源

- 本项目以[Apache-2.0](https://github.com/mixmoe/HibiAPI/blob/main/LICENSE)许可开源, 这意味着你可以在**注明版权信息**的情况下进行任意使用

### 高效

- 使用Python的[异步机制](https://docs.python.org/zh-cn/3/library/asyncio.html), 由[FastAPI](https://fastapi.tiangolo.com/)驱动, 带来高效的使用体验 ~~虽然性能瓶颈压根不在这~~

### 稳定

- 在代码中大量使用[PEP-484](https://www.python.org/dev/peps/pep-0484/)引入的类型标记语法

- 使用[PyLance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), [Flake8](https://flake8.pycqa.org/en/latest/)和[MyPy](https://mypy.readthedocs.io/)对代码进行类型推断和纠错

- 不直接使用第三方API库, 而是全部用更加适合Web应用的逻辑重写第三方API请求, 更加可控 ~~疯狂造轮子~~

## 实现进度

***[Imjad原有API实现请求  (#1)](https://github.com/mixmoe/HibiAPI/issues/1)***

## 部署指南

***[点击此处查看](https://github.com/mixmoe/HibiAPI/wiki/Deployment)***

## 鸣谢

> - [@journey-ad](https://github.com/journey-ad) 大佬的 [Imjad API](https://api.imjad.cn/)
> - 为本项目实现API提供参考的各种开源项目
>   - Pixiv: [`Mikubill/pixivpy-async`](https://github.com/Mikubill/pixivpy-async) [`upbit/pixivpy`](https://github.com/upbit/pixivpy)
>   - Bilibili: [`SocialSisterYi/bilibili-API-collect`](https://github.com/SocialSisterYi/bilibili-API-collect) [`soimort/you-get`](https://github.com/soimort/you-get)
>   - 网易云音乐: [`metowolf/NeteaseCloudMusicApi`](https://github.com/metowolf/NeteaseCloudMusicApi) [`greats3an/pyncm`](https://github.com/greats3an/pyncm) [`Binaryify/NeteaseCloudMusicApi`](https://github.com/Binaryify/NeteaseCloudMusicApi)
>   - 百度贴吧: [`libsgh/tieba-api`](https://github.com/libsgh/tieba-api)
