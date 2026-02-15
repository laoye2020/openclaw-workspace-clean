---
name: skill-finder
description: AI技能发现助手 - 根据需求智能推荐可用技能，避免重复造轮子
---

# 🔍 AI技能发现助手

## 功能

根据你的需求描述，智能推荐 OpenClaw 技能库中的现成技能，**避免重复造轮子**！

## 使用方法

### 命令行使用

```bash
# 查找语音识别技能
python3 skill_finder.py "语音识别"

# 查找PDF编辑技能
python3 skill_finder.py "PDF编辑"

# 查找天气查询技能
python3 skill_finder.py "天气"

# 模糊描述也行
python3 skill_finder.py "我想做语音转文字"
```

### 作为OpenClaw技能使用

在对话中直接问我：
```
"我想做XX功能，有什么现成技能吗？"
"帮我找一下语音识别的技能"
"有没有现成的PDF编辑工具？"
```

## 示例输出

```
==================================================
📝 任务: 语音识别
🔑 关键词: 语音, 语音识别

✅ 推荐技能:
  1. speech-to-text
  2. faster-whisper
  3. openai-whisper
  4. local-whisper
  5. voice-wake-say

💾 安装命令:
  npx clawhub install speech-to-text
==================================================
```

## 技能映射表（持续更新）

目前已收录的技能领域：

| 领域 | 推荐技能 |
|------|---------|
| 语音识别 | openai-whisper, faster-whisper, speech-to-text |
| 天气查询 | weather |
| PDF编辑 | nano-pdf |
| 图片生成 | openai-image-gen, stable-diffusion |
| 视频剪辑 | video-frames |
| 网络搜索 | tavily, web-search |
| 笔记管理 | obsidian, notion |
| GitHub管理 | github, coding-agent |
| 邮件发送 | himalaya |
| 数据库 | sqlite, mysql-query |

## 工作原理

1. **关键词提取**：从你的描述中提取关键需求
2. **本地映射查询**：优先查本地知识库（快速）
3. **ClawHub搜索**：本地没有则搜索远程仓库
4. **智能推荐**：返回最匹配的技能列表

## 好处

✅ **节省时间**：不用重复造轮子
✅ **发现新工具**：了解生态中的现成方案
✅ **对比选择**：同一功能多个实现，可选最优
✅ **避免踩坑**：优先推荐经过验证的流行技能

## 持续改进

每次发现新技能，更新 `skill_finder.py` 中的 `SKILL_MAPPING` 表！

---
*让OpenClaw生态更高效*
