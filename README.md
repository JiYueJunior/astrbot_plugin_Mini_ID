# 🎮 迷你世界物品 ID 查询器

**AstrBot 插件 - 迷你世界游戏辅助工具**

[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-blue.svg)](https://github.com/AstrBotDevs/AstrBot)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-1.1.0-orange.svg)]()

---

## 📖 插件介绍

**迷你世界物品 ID 查询器** 是一个专为《迷你世界》玩家设计的 AstrBot 插件，提供快速、便捷的物品 ID 查询服务。通过简单的聊天指令，玩家可以轻松查找游戏中任何物品的 ID 和名称。

### ✨ 主要功能

- 🔍 **按名称查 ID** - 输入物品名称，快速获取对应 ID
- 🔢 **按 ID 查名称** - 输入 ID，查看对应的物品信息
- 📋 **浏览物品列表** - 分页查看所有物品的完整清单


### 🎯 适用场景

- 迷你世界玩家查询物品 ID
- 开发者/地图制作者查找方块 ID
- 游戏社区/群组中的快捷查询工具
- 游戏攻略/资料整理

---

## 🚀 快速开始

### 前置要求

- **运行环境**: [AstrBot](https://github.com/AstrBotDevs/AstrBot) v4.0+
- **Python 版本**: Python 3.8+
- **依赖库**: httpx

### 安装方法

#### 方法 1: Git 克隆（推荐）
```bash
cd /path/to/astrbot/data/plugins
git clone https://github.com/Soulter/helloworld.git astrbot_plugin_Mini_ID
```

#### 方法 2: 手动安装
1. 下载本仓库代码
2. 解压到 `astrbot/data/plugins/` 目录
3. 重命名文件夹为 `astrbot_plugin_Mini_ID`

### 安装依赖
```bash
cd astrbot/data/plugins/astrbot_plugin_Mini_ID
pip install -r requirements.txt
```

### 启动插件
重启 AstrBot 即可自动加载插件：
```bash
# Docker 部署
docker restart astrbot

# 直接运行
python main.py
```

---

## 💬 使用指南

### 可用命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `/mini_id <名称>` | 按名称查询物品 ID（快速） | `/mini_id 钻石` |
| `/mini_search <名称> [数量]` | 高级搜索，可指定显示数量 | `/mini_search 钻石 100` |
| `/mini_search_id <ID>` | 按 ID 查询物品名称 | `/mini_search_id 1` |
| `/mini_list [页码]` | 浏览所有物品列表 | `/mini_list 2` |
| `/mini_help` | 查看帮助文档 | `/mini_help` |

### 使用示例

#### 1️⃣ 按名称查询
```
用户：/mini_id 地心基石
机器人：
🔍 查询到 **1** 个相关物品:
• 地心基石 - ID: `1` 【方块】
```

#### 2️⃣ 按 ID 查询
```
用户：/mini_search_id 100
机器人：
🔍 ID **100** 对应的物品:
• 草块 【方块】
💡 该 ID 对应 1 个物品
```

#### 4 设置显示数量
```
用户：/mini_setlimit 200
机器人：
✅ 搜索结果显示数量已设置为 **200** 个

💡 提示：
• 使用 `/mini_search` 时将默认显示 200 个结果
• 也可以在搜索时临时指定数量：`/mini_search 钻石 100`
```

#### 5 浏览列表
```
用户：/mini_list
机器人：
📋 **迷你世界物品 ID 列表** (第 1/50 页)
共计 1000 个物品 | 每页 20 条
• ID: `1` | 地心基石【方块】
• ID: `2` | 功能方块【方块】
...
➡️ 下一页：`/mini_list 2`
```

---

## 🌐 数据来源

- **数据源**: 圣灵导航页 - 迷你世界物品 ID 查询
- **API 地址**: https://srcbs.cn/tool/mini/item.json
- **查询网站**: https://srcbs.cn/tool/mini/
- **更新频率**: 每次插件启动时自动加载最新数据

---

## 🛠️ 技术架构

### 核心特性

- **双向索引**: 同时支持名称→ID 和 ID→名称的查询
- **内存缓存**: 启动时一次性加载所有数据，查询速度快
- **模糊匹配**: 支持部分名称匹配，提升用户体验
- **分页系统**: 智能分页，避免消息过长
- **错误处理**: 完善的异常捕获和用户提示

### 代码结构

```
helloworld/
├── main.py              # 插件主程序
├── metadata.yaml        # 插件元数据配置
├── requirements.txt     # Python 依赖
├── README.md           # 使用说明
└── USAGE.md            # 详细使用文档
```

---

## 🤖 关于 AstrBot

**AstrBot** 是一个基于 Python 开发的开源聊天机器人框架，支持多平台部署（QQ、Telegram、微信等），并提供强大的插件系统和 AI 对话能力。

- **项目地址**: https://github.com/AstrBotDevs/AstrBot
- **官方文档**: https://docs.astrbot.app/
- **开发语言**: Python
- **核心特性**: 
  - 多平台消息适配
  - 大语言模型接入
  - 灵活的插件系统
  - 可视化管理面板

本插件基于 **AstrBot Plugin SDK** 开发，完全遵循官方插件规范。

---

## ❓ 常见问题

### Q: 为什么查询不到某个物品？
A: 请检查物品名称是否正确，或尝试使用部分名称进行模糊搜索。

### Q: 数据是最新的吗？
A: 插件每次启动时都会从官网重新加载数据，确保数据最新。

### Q: 可以离线使用吗？
A: 不可以。插件需要联网获取物品数据。

### Q: 如何反馈问题？
A: 欢迎在 GitHub Issues 中提交问题或建议。

---

## 📄 许可证

本插件遵循原项目许可证。

---

## 👨‍💻 开发者

- **作者**: Ling_Yue
- **基于项目**: [AstrBot](https://github.com/AstrBotDevs/AstrBot)
- **开发语言**: Python 3.8+
- **插件版本**: v1.1.0

---

## 🔗 相关链接

- [AstrBot 官方仓库](https://github.com/AstrBotDevs/AstrBot)
- [AstrBot 插件开发文档](https://docs.astrbot.app/dev/star/plugin-new.html)
- [迷你世界物品 ID 查询网站](https://srcbs.cn/tool/mini/)
- [详细使用文档](USAGE.md)

---

**⭐ 如果这个插件对你有帮助，请给个 Star 支持一下！**
