<!-- spell-checker: disable -->
<!-- markdownlint-disable MD033 MD041 -->

<img src=".github/logo.svg" align="right">

<div align="left">

# HibiAPI

**_一个实现了多种常用站点的易用化 API 的程序._**

**_A program that implements easy-to-use APIs for a variety of commonly used sites._**

[![Demo Version](https://img.shields.io/badge/dynamic/json?label=demo%20status&query=%24.info.version&url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json&style=for-the-badge&color=lightblue)](https://api.obfs.dev)

![Lint](https://github.com/mixmoe/HibiAPI/workflows/Lint/badge.svg)
![Test](https://github.com/mixmoe/HibiAPI/workflows/Test/badge.svg)
[![Coverage](https://codecov.io/gh/mixmoe/HibiAPI/branch/main/graph/badge.svg)](https://codecov.io/gh/mixmoe/HibiAPI)

[![PyPI](https://img.shields.io/pypi/v/hibiapi)](https://pypi.org/project/hibiapi/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/hibiapi)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hibiapi)
![PyPI - License](https://img.shields.io/pypi/l/hibiapi)

![GitHub last commit](https://img.shields.io/github/last-commit/mixmoe/HibiAPI)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/mixmoe/hibiapi)
![Lines of code](https://img.shields.io/tokei/lines/github/mixmoe/hibiapi)
[![GitHub stars](https://img.shields.io/github/stars/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/network)
[![GitHub issues](https://img.shields.io/github/issues/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/issues)

</div>

---

## 前言

- `HibiAPI`提供多种网站公开内容的 API 集合, 它们包括:

  - Pixiv 的图片和小说相关信息获取和搜索
  - Bilibili 的视频/番剧等信息获取和搜索
  - 网易云音乐的音乐/MV 等信息获取和搜索
  - 百度贴吧的帖子内容的获取
  - [爱壁纸](https://adesk.com/)的横版和竖版壁纸获取
  - …

- 该项目的前身是 Imjad API[^1]
  - 由于它的使用人数过多, 致使调用超出限制, 所以本人希望提供一个开源替代来供社区进行自由地部署和使用, 从而减轻一部分该 API 的使用压力

[^1]: [什么是 Imjad API](https://github.com/mixmoe/HibiAPI/wiki/FAQ#%E4%BB%80%E4%B9%88%E6%98%AFimjad-api)

## 优势

### 开源

- 本项目以[Apache-2.0](./LICENSE)许可开源, 请看[开源许可](#开源许可)一节

### 高效

- 使用 Python 的[异步机制](https://docs.python.org/zh-cn/3/library/asyncio.html), 由[FastAPI](https://fastapi.tiangolo.com/)驱动, 带来高效的使用体验 ~~虽然性能瓶颈压根不在这~~

### 稳定

- 在代码中广泛使用了 Python 的[类型提示支持](https://docs.python.org/zh-cn/3/library/typing.html), 使代码可读性更高且更加易于维护和调试

- 在开发初期起就一直使用多种现代 Python 开发工具辅助开发, 包括:

  - 使用 [PyLance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) 进行静态类型推断
  - 使用 [Flake8](https://flake8.pycqa.org/en/latest/) 对代码格式进行检查
  - 使用 [Black](https://black.readthedocs.io/en/stable/) 格式化代码以提升代码可读性

- 不直接使用第三方开发的 API 调用库, 而是全部用更加适合 Web 应用的逻辑重写第三方 API 请求, 更加可控 ~~疯狂造轮子~~

## 已实现 API[^2]

[^2]: 请查看 [#1](https://github.com/mixmoe/HibiAPI/issues/1)

- [x] Pixiv
- [x] 网易云音乐
- [ ] ~~一言~~ (其代替方案<https://hitokoto.cn>提供的方案已足够好, 暂不考虑支持)
- [x] Bilibili
- [x] 二维码
- [ ] ~~企鹅 FM~~ (似乎用的人不是很多)
- [x] 百度贴吧
- [x] 爱壁纸

## 部署指南

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

- 手动部署指南: **[点击此处查看](https://github.com/mixmoe/HibiAPI/wiki/Deployment)**

## 应用实例

**我有更多的应用实例?** [立即 PR!](https://github.com/mixmoe/HibiAPI/pulls)

- [`journey-ad/pixiv-viewer`](https://github.com/journey-ad/pixiv-viewer)

  - **又一个 Pixiv 阅览工具**

- 公开搭建实例
  | **站点名称** | **网址** | **状态** |
  | :--------------------------: | :-----------------------------: | :---------------------: |
  | **官方 Demo[^3]** | <https://api.obfs.dev> | [![official][official]][official-stats] |
  | 轻零 API | <https://hibiapi.lite0.com> | ![lite0][lite0] |
  | Kyomotoi の菜几服务 | <https://api.kyomotoi.moe> | ![kyo][kyo] |
  | 老狐狸 API | <https://hibiapi.aliserver.net> | ![older-fox][older-fox] |
  | [MyCard](https://mycard.moe) | <https://hibi.moecube.com> | ![mycard][mycard] |

[^3]: 为了减轻服务器负担, Demo 服务器已开启了 Cloudflare 全站缓存, 如果有实时获取更新的需求, 请自行搭建或使用其他部署实例

[official]: https://img.shields.io/website?url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json
[official-stats]: https://metrics.librato.com/s/public/g1hepph3j
[lite0]: https://img.shields.io/website?url=https%3A%2F%2Fhibiapi.lite0.com%2Fopenapi.json
[kyo]: https://img.shields.io/website?url=https%3A%2F%2Fapi.kyomotoi.moe%2Fopenapi.json
[older-fox]: https://img.shields.io/website?url=https%3A%2F%2Fhibiapi.aliserver.net%2Fopenapi.json
[mycard]: https://img.shields.io/website?url=https%3A%2F%2Fhibi.moecube.com%2Fopenapi.json

## 特别鸣谢

[**@journey-ad**](https://github.com/journey-ad) 大佬的 **Imjad API**, 它是本项目的起源

### 参考项目

> **正是因为有了你们, 这个项目才得以存在**

- Pixiv: [`Mikubill/pixivpy-async`](https://github.com/Mikubill/pixivpy-async) [`upbit/pixivpy`](https://github.com/upbit/pixivpy)

- Bilibili: [`SocialSisterYi/bilibili-API-collect`](https://github.com/SocialSisterYi/bilibili-API-collect) [`soimort/you-get`](https://github.com/soimort/you-get)

- 网易云音乐: [`metowolf/NeteaseCloudMusicApi`](https://github.com/metowolf/NeteaseCloudMusicApi) [`greats3an/pyncm`](https://github.com/greats3an/pyncm) [`Binaryify/NeteaseCloudMusicApi`](https://github.com/Binaryify/NeteaseCloudMusicApi)

- 百度贴吧: [`libsgh/tieba-api`](https://github.com/libsgh/tieba-api)

### 贡献者们

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-10-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

感谢这些为这个项目作出贡献的各位大佬:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://kyomotoi.moe"><img src="https://avatars.githubusercontent.com/u/37587870?v=4?s=100" width="100px;" alt="Kyomotoi"/><br /><sub><b>Kyomotoi</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=Kyomotoi" title="Documentation">📖</a> <a href="https://github.com/mixmoe/HibiAPI/commits?author=Kyomotoi" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://thdog.moe"><img src="https://avatars.githubusercontent.com/u/46120251?v=4?s=100" width="100px;" alt="城倉奏"/><br /><sub><b>城倉奏</b></sub></a><br /><a href="#example-shirokurakana" title="Examples">💡</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://skipm4.com"><img src="https://avatars.githubusercontent.com/u/40311581?v=4?s=100" width="100px;" alt="SkipM4"/><br /><sub><b>SkipM4</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=SkipM4" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/leaf7th"><img src="https://avatars.githubusercontent.com/u/38352552?v=4?s=100" width="100px;" alt="Nook"/><br /><sub><b>Nook</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=leaf7th" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jiangzhuochi"><img src="https://avatars.githubusercontent.com/u/50538375?v=4?s=100" width="100px;" alt="Jocky Chiang"/><br /><sub><b>Jocky Chiang</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=jiangzhuochi" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/cleoold"><img src="https://avatars.githubusercontent.com/u/13920903?v=4?s=100" width="100px;" alt="midori"/><br /><sub><b>midori</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=cleoold" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.2yo.cc"><img src="https://avatars.githubusercontent.com/u/41198038?v=4?s=100" width="100px;" alt="Pretty9"/><br /><sub><b>Pretty9</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=Pretty9" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://nocilol.me/"><img src="https://avatars.githubusercontent.com/u/16256221?v=4?s=100" width="100px;" alt="Jad"/><br /><sub><b>Jad</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/issues?q=author%3Ajourney-ad" title="Bug reports">🐛</a> <a href="#ideas-journey-ad" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://nanoka.top"><img src="https://avatars.githubusercontent.com/u/31837214?v=4?s=100" width="100px;" alt="Yumine Sakura"/><br /><sub><b>Yumine Sakura</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=asadahimeka" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/yeyang52"><img src="https://avatars.githubusercontent.com/u/107110851?v=4?s=100" width="100px;" alt="yeyang"/><br /><sub><b>yeyang</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=yeyang52" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

_本段符合 [all-contributors](https://github.com/all-contributors/all-contributors) 规范_

## 开源许可

    Copyright 2020-2021 Mix Technology

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
