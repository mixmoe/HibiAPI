<!-- spell-checker: disable -->
<!-- markdownlint-disable MD033 MD041 -->

<img src=".github/logo.svg" align="right">

<div align="left">

# HibiAPI

**_一个实现了多种常用站点的易用化API的程序._**

**_A program that implementis easy-to-use APIs for a variety of commonly used sites._**

[![Demo Version](https://img.shields.io/badge/dynamic/json?label=demo%20status&query=%24.info.version&url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json&style=for-the-badge&color=lightblue)](https://api.obfs.dev)

![Lint](https://github.com/mixmoe/HibiAPI/workflows/Lint/badge.svg)
![Test](https://github.com/mixmoe/HibiAPI/workflows/Test/badge.svg)
[![Coverage](https://codecov.io/gh/mixmoe/HibiAPI/branch/main/graph/badge.svg)](https://codecov.io/gh/mixmoe/HibiAPI)

![GitHub last commit](https://img.shields.io/github/last-commit/mixmoe/HibiAPI)
[![PyPI](https://img.shields.io/pypi/v/hibiapi)](https://pypi.org/project/hibiapi/)
[![GitHub license](https://img.shields.io/github/license/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/network)
[![GitHub issues](https://img.shields.io/github/issues/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/issues)
![Python version](https://img.shields.io/badge/python-3.8%2B-yellowgreen)

</div>

---

## 前言

- 在开发与第三方API对接的过程中, 你是否遇到了以下问题?
  - 提供的API带有CORS跨域, 无法直接调用
  - 调用公开数据但是需要登录凭证, 会导致登录凭证泄漏
  - 第三方API加密实现复杂, 很难实现

- 现在, 有了`HibiAPI`, 它提供多种网站公开内容的API集合, 它们包括:
  - Pixiv的图片/小说相关信息获取和搜索
  - Bilibili的视频/番剧等信息获取和搜索
  - 网易云音乐的音乐/MV等信息获取和搜索
  - 百度贴吧的帖子内容的获取
  - and more...

- 该项目的前身是 Imjad API<sup>[这是什么?](https://github.com/mixmoe/HibiAPI/wiki/FAQ#%E4%BB%80%E4%B9%88%E6%98%AFimjad-api)</sup>
  - 由于它的使用人数过多, 致使调用超出限制, 所以本人希望提供一个开源替代来供社区进行自由的部署和使用, 从而减轻一部分该 API 的使用压力

## 优势

### 开源

- 本项目以[Apache-2.0](https://github.com/mixmoe/HibiAPI/blob/main/LICENSE)许可开源, 这意味着你可以在**注明版权信息**的情况下进行任意使用

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fmixmoe%2FHibiAPI.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fmixmoe%2FHibiAPI?ref=badge_large)

### 高效

- 使用 Python 的[异步机制](https://docs.python.org/zh-cn/3/library/asyncio.html), 由[FastAPI](https://fastapi.tiangolo.com/)驱动, 带来高效的使用体验 ~~虽然性能瓶颈压根不在这~~

### 稳定

- 在代码中大量使用[PEP-484](https://www.python.org/dev/peps/pep-0484/)引入的类型标记语法

- 使用[PyLance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), [Flake8](https://flake8.pycqa.org/en/latest/)和[MyPy](https://mypy.readthedocs.io/)对代码进行类型推断和纠错

- 不直接使用第三方 API 库, 而是全部用更加适合 Web 应用的逻辑重写第三方 API 请求, 更加可控 ~~疯狂造轮子~~

## 实现进度

**_[Imjad 原有 API 实现请求 (#1)](https://github.com/mixmoe/HibiAPI/issues/1)_**

## 部署指南

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

- 手动部署指南: **[点击此处查看](https://github.com/mixmoe/HibiAPI/wiki/Deployment)**

## 应用实例

**我有更多的应用实例?** [立即 PR!](https://github.com/mixmoe/HibiAPI/pulls)

- [`journey-ad/pixiv-viewer`](https://github.com/journey-ad/pixiv-viewer)

  - **又一个 Pixiv 阅览工具**

- 公开搭建实例
  |    **站点名称**     |            **网址**             |        **状态**         |
  | :-----------------: | :-----------------------------: | :---------------------: |
  |    **官方 Demo**    |     <https://api.obfs.dev>      |  ![official][official]  |
  |      轻零 API       |   <https://hibiapi.lite0.com>   |     ![lite0][lite0]     |
  | Kyomotoi の菜几服务 |   <https://api.kyomotoi.moe>    |       ![kyo][kyo]       |
  |     老狐狸 API      | <https://hibiapi.aliserver.net> | ![older-fox][older-fox] |

[official]: https://img.shields.io/website?url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json
[lite0]: https://img.shields.io/website?url=https%3A%2F%2Fhibiapi.lite0.com%2Fopenapi.json
[kyo]: https://img.shields.io/website?url=https%3A%2F%2Fapi.kyomotoi.moe%2Fopenapi.json
[older-fox]: https://img.shields.io/website?url=https%3A%2F%2Fhibiapi.aliserver.net%2Fopenapi.json

## 特别鸣谢

[**@journey-ad**](https://github.com/journey-ad) 大佬的 [Imjad API](https://api.imjad.cn/), 是它带领我走上了编程之路

### 参考项目

> **正是因为有了你们, 这个项目才得以存在**

- Pixiv: [`Mikubill/pixivpy-async`](https://github.com/Mikubill/pixivpy-async) [`upbit/pixivpy`](https://github.com/upbit/pixivpy)

- Bilibili: [`SocialSisterYi/bilibili-API-collect`](https://github.com/SocialSisterYi/bilibili-API-collect) [`soimort/you-get`](https://github.com/soimort/you-get)

- 网易云音乐: [`metowolf/NeteaseCloudMusicApi`](https://github.com/metowolf/NeteaseCloudMusicApi) [`greats3an/pyncm`](https://github.com/greats3an/pyncm) [`Binaryify/NeteaseCloudMusicApi`](https://github.com/Binaryify/NeteaseCloudMusicApi)

- 百度贴吧: [`libsgh/tieba-api`](https://github.com/libsgh/tieba-api)

### 贡献者们

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

感谢这些为这个项目作出贡献的各位大佬:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://kyomotoi.moe"><img src="https://avatars.githubusercontent.com/u/37587870?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Kyomotoi</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=Kyomotoi" title="Documentation">📖</a> <a href="https://github.com/mixmoe/HibiAPI/commits?author=Kyomotoi" title="Tests">⚠️</a></td>
    <td align="center"><a href="http://thdog.moe"><img src="https://avatars.githubusercontent.com/u/46120251?v=4?s=100" width="100px;" alt=""/><br /><sub><b>城倉奏</b></sub></a><br /><a href="#example-shirokurakana" title="Examples">💡</a></td>
    <td align="center"><a href="http://skipm4.com"><img src="https://avatars.githubusercontent.com/u/40311581?v=4?s=100" width="100px;" alt=""/><br /><sub><b>SkipM4</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=SkipM4" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/leaf7th"><img src="https://avatars.githubusercontent.com/u/38352552?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nook</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=leaf7th" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/jiangzhuochi"><img src="https://avatars.githubusercontent.com/u/50538375?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jocky Chiang</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=jiangzhuochi" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

_本段符合 [all-contributors](https://github.com/all-contributors/all-contributors) 规范_
