<div align="center">

<img src="http://my.wkblog.com.cn/img/logo.ico" width="120" height="120" alt="Oxygen Reader Logo">

# Oxygen Reader | 氧气阅读器

**像氧气一样：轻盈、透明、不可或缺，却又难以察觉。**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-win.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Release](https://img.shields.io/badge/release-V1.1.2-orange.svg)](http://my.wkblog.com.cn/)

[🌐 访问官网](http://my.wkblog.com.cn/) | [📥 立即下载](http://my.wkblog.com.cn/azb/Oxygen.exe) | [🐞 提交反馈](http://my.wkblog.com.cn/)

</div>

---

## 📖 简介 (Introduction)

**Oxygen Reader** 是一款专为 Windows 10/11 用户打造的**极简主义透明阅读器**。

它打破了传统阅读软件的“边框”束缚，将文字直接悬浮于你的桌面壁纸、Excel 表格或代码编辑器之上。它拥有极致的**隐身能力**、**深度伪装**和强大的**格式兼容性**，旨在为你提供一种无压力、沉浸式、且随时可以“消失”的阅读体验。

无论是在高压的办公环境，还是在碎片化的休息时间，Oxygen 都能让你在数字世界的缝隙中，安全地呼吸到知识的氧气。

## ✨ 核心特性 (Features)

### 👻 极致隐身 (Ultimate Stealth)
- **全透明悬浮**：无边框、无背景，文字直接浮在屏幕上，完美融入工作流。
- **一键消失**：鼠标左键点击屏幕任意空白处，或按下 `Ctrl+Shift+Q`，文字瞬间隐形。
- **托盘驻留**：控制台最小化至系统托盘（右下角），任务栏不留痕迹，查岗无忧。

### 🛡️ 变色龙伪装 (Camouflage)
- **深度伪装**：支持自定义窗口标题（如“系统更新组件”、“数据报表”）及图标。
- **环境融合**：字体大小、颜色、透明度完全可调，甚至可以把小说伪装成 IDE 代码注释。

### 🎯 聚焦引导 (Focus Anchor)
- **启动高亮**：开始阅读时，文字自动居中并**红字高亮**，解决透明窗口难以定位的痛点。
- **自动隐退**：翻页后立即恢复隐蔽色（如深灰），回归潜行模式。

### 📚 全能解析 & 智能记忆
- **格式通吃**：原生支持 **PDF, EPUB, MOBI, AZW3, TXT** 等主流电子书格式。
- **数据持久化**：阅读进度（精确到行）、书架记录保存在系统 `%APPDATA%` 目录，删除软件不丢失数据。

## 🛠️ 安装与使用 (Installation & Usage)

### 方式一：直接使用 (推荐)
无需安装 Python 环境，下载即用。
1. 前往 [官网](http://my.wkblog.com.cn/) 下载最新版 `Oxygen.exe`。
2. 建议将软件放入单独文件夹（如 `D:\Tools\Oxygen`）。
3. 双击运行即可。

### 方式二：源码运行/打包
如果你是开发者，可以克隆本仓库进行二次开发。

1. **克隆仓库**
   ```bash
   git clone [https://github.com/iwkai312/OxygenReader.git](https://github.com/iwkai312/OxygenReader.git)
   cd OxygenReader

2. **安装依赖**
    ```bash
   pip install PyQt5 pymupdf keyboard requests pynput pyinstaller

3. **运行代码**
   ```bash
   python moyu_pro.py

4. **打包成 EXE 请确保目录下有 logo.ico 文件，然后运行：**
   ```bash
   pyinstaller --onefile --noconsole --icon=logo.ico --add-data "logo.ico;." moyu_pro.py

功能,默认按键,说明
下一行,T,阅读下一行文字
上一行,Q,回看上一行文字
老板键,Ctrl + Shift + Q,立即隐藏文字窗口
唤醒键,Ctrl + Shift + F,恢复显示文字窗口
   
版本更新内容
V1.1.2,2026-02-04,[细节优化] 底部新增版本号显示；官网按钮增加交互动效；优化底部布局。

V1.1.1,2026-02-04,[门户集成] 控制台底部增加官网跳转入口，方便获取更新与支持。

V1.1.0,2026-02-04,[聚焦引导] 新增启动时红字高亮并自动居中功能；新增自动隐退逻辑。

V1.0.2,2026-02-04,[配置自愈] 修复旧版本标题残留问题，强制清洗窗口标题中的版本号。

V1.0.1,2026-02-04,[交互完善] 新增“重置默认按键”功能；移除默认标题后缀。

V1.0.0,2026-02-04,[正式版] 重写快捷键录入组件，支持键盘按下自动录入；新增防误触逻辑。

V0.0.7,2026-02-04,[品牌重塑] 正式更名为 Oxygen阅读器；优化默认隐蔽配置。

V0.0.6,2026-02-04,[视觉定制] 支持自定义软件图标 (logo.ico)；修正数据存储文案。

V0.0.5,2026-02-04,[终极隐身] 引入系统托盘模式；实现数据持久化存储；阅读时自动隐藏控制台。

V0.0.4,2026-02-04,[性能重构] 引入信号槽机制，彻底修复翻页卡顿与无响应问题。

V0.0.3,2026-02-04,[全自定义] 新增全局鼠标点击隐藏；开放字体/颜色/背景设置；新增在线更新。

V0.0.1,2026-02-04,[诞生] 首个版本发布，支持 PDF/EPUB/MOBI 等格式解析与透明阅读。


☕ 请作者喝杯咖啡 (Sponsor)
如果这个小工具帮助你度过了无聊的时光，或者帮你“安全”地读完了几本好书，欢迎请作者喝一杯冰美式！你的支持是我持续更新的动力。

<div align="center"> <img src="http://my.wkblog.com.cn/img/weixin.png" alt="微信赞赏" width="200" style="margin-right: 20px;"> <img src="http://my.wkblog.com.cn/img/alipay.jpg" alt="支付宝赞赏" width="200">


</div>

📮 联系方式 (wk312@qq.com)
官方网站: http://my.wkblog.com.cn/

问题反馈: 请在 GitHub Issues 中提交，或通过官网联系。

开发者: [倒头就睡]
