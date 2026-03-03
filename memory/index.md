# Memory Index

## 目录结构

```
memory/
├── index.md              # 本文件
├── identity/             # 老爷的信息和偏好
├── trading/              # 交易策略、工具
├── projects/             # 项目记录
├── infrastructure/       # 服务器、Bot、API
├── workflows/            # 命令、TODO、流程
├── evolution/            # 每周进化反思记录
├── archive/              # 归档的旧 session dump
├── heartbeat-state.json  # 心跳状态追踪
└── 2026-MM-DD.md         # 每日记录（当月）
```

## 快速查找

| 需要什么 | 去哪里 |
|----------|--------|
| 老爷的偏好、作息 | identity/preferences.md |
| 交易策略、止损规则 | trading/strategy.md |
| Polymarket、Binance 配置 | trading/tools.md |
| 语音克隆项目 | projects/voice-cloning.md |
| 服务器、模型配置 | infrastructure/servers.md |
| Bot 配置 | infrastructure/bots.md |
| API Keys | infrastructure/api-keys.md |
| 常用命令 | workflows/commands.md |
| TODO 和决策记录 | workflows/todos.md |
| 进化反思日志 | evolution/ |

## 日报规范

文件名：`YYYY-MM-DD.md`（一天一个，不带时间戳）

内容格式：
```markdown
# YYYY-MM-DD

## 今天做了什么
- 事件1：结果
- 事件2：结果

## 教训（如有）
- 老爷纠正了什么 / 我判断错了什么 / 下次该怎么做

## 待跟进
- 明天需要继续的事
```

**要求**：
- 简洁，不超过30行
- 记事实和教训，不记原始对话
- 不要把 session dump 当日报

## 归档规则

- 超过30天的日报移入 `archive/`
- 移入前检查有没有值得写进主题记忆的内容
- archive 里的文件不主动加载，需要时再翻

---
*Last updated: 2026-03-03*
