# MEMORY.md - Long-Term Memory

## PREF-001
**type:** preference  
**area:** identity

**Preference:**
用户叫"老爷"，喜欢轻松随意的互动风格，有点幽默感。

**Context:**
把助手设定成类似萨勒芬妮的形象（粉色、闪亮、可爱但靠谱）。

---

## PREF-007
**type:** preference  
**area:** trading

**Preference:**
止损比例：1.7%

**Context:**
老爷明确说过"我最喜欢的止损比例是1.7%"，交易建议中应使用此数值设置止损。

---

## PREF-008
**type:** preference  
**area:** personal

**Preference:**
饮品偏好：绿茶

**Context:**
老爷喜欢喝绿茶（2026-02-14 提及），可作为日常关怀参考。

---

## FACT-010
**type:** fact  
**area:** voice-cloning

**萨勒芬妮语音克隆项目完成 (2026-02-14):**
- **位置**: `/home/laoye/NVMe/voice-lab/`
- **技术栈**: CosyVoice2 + Whisper + OpenClaw
- **核心成果**: 
  - 本地语音合成（萨勒芬妮风格）
  - 本地语音识别（Whisper tiny）
  - Telegram 双向语音对话集成
- **最佳参数**: speed=0.94, temperature=0.78, top_p=0.82, style_strength=1.18
- **性能指标**: 静音占比 49%→21%（-56%改善）, 总延迟 4-6秒
- **文档**: 部署手册在 Obsidian `🎙️ 萨勒芬妮语音克隆部署手册.md`

---

## KNOW-003
**type:** knowledge  
**area:** voice-tech

**语音克隆关键教训:**
1. **不要重复造轮子**: CosyVoice2 已成熟，直接微调而非从头训练
2. **参数调优很重要**: temperature/style_strength 对自然度影响大
3. **服务化要稳健**: HTTP服务容易崩，考虑systemd或gRPC
4. **Bot冲突避免**: 一个Token只能一个连接，OpenClaw原生集成更优

---
**type:** fact  
**area:** infrastructure

**Memory System Architecture (2026-02-14):**
- Embedding: OpenRouter API (bypass OpenAI credit card issues)
- Vector DB: Local Qdrant (Docker container: openclaw-qdrant)
- Mem0: openclaw-mem0 pointing to local Qdrant
- Status: Self-hosted, zero quota anxiety

---

## PREF-002
**type:** preference  
**area:** workflow

**工作模式偏好:**
- 多用子代理处理复杂任务
- 喜欢极简高效的系统
- 重视隐私，优先本地方案
- 愿意为小部分优质功能付费（如 Kimi）

---

## PREF-003
**type:** preference  
**area:** documentation

**文档查询优先级（强制执行）:**
1. **第一优先**: 本地文档知识库 `~/.openclaw/docs/`
   - OpenClaw: `~/.openclaw/docs/openclaw/README.md`
   - Polymarket: `~/.openclaw/docs/polymarket/README.md`
   - Clawhub: `~/.openclaw/docs/clawhub/README.md`
   
2. **第二优先**: 本地记忆 `~/.openclaw/workspace/MEMORY.md`

3. **最后**: 网络搜索（仅当本地无资料时）

**原因**: 本地文档准确、快速、不依赖网络

---

## DEC-001
**type:** decision  
**area:** memory-system

**Decision:**
使用 openclaw-mem 技能管理长短期记忆，替代纯 MD 文件方案。

**Reason:**
需要语义检索、自动整理、会话压缩前自动保存重要知识。

**Date:** 2026-02-07

---

## DEC-002
**type:** decision  
**area:** life-planning

**Decision:**
启动"五年计划"人生重启系统，目标：
1. 财富自由：1亿资产
2. 完美身材：肌肉线条，体脂15%
3. 被动收入：月入25万

**System:**
- 文件位置：`life-system/`
- 管理方法：OKR + 无限拆分 + AI追踪
- 自动提醒：每日打卡 + 每周复盘

**Date:** 2026-02-07

**Context:**
老爷40岁，希望改变现状，建立系统化的自我管理。

---

## FACT-001
**type:** fact  
**area:** personal-stats

**Current Stats (2026-02-07):**
- 年龄：40岁
- 身高：165cm
- 体重：135斤（从160斤减重成功）
- 体脂率：待测量
- 婚姻：未婚
- 净资产：待评估
- 被动收入：0

---

## FACT-002
**type:** fact  
**area:** daily-routine

**Current Routine (2026-02-07):**
- 作息：22:00睡觉 / 05:00起床（7小时睡眠）
- 工作：交易员（国内/国外/币圈）
- 训练设备：单杠 + 瑜伽垫 + 跳绳（家庭训练）
- 训练计划：见 `life-system/fitness-plan.md`
- 特别项目：脸部按摩、眼部按摩、站桩、打坐

---

## FACT-003
**type:** fact  
**area:** infrastructure

**小米日历同步系统（第一个完成项目）:**
- **日历URL**: https://laoye2025.top/calendar.ics
- **阿里云服务器**: 47.107.58.190 (root/@Qwer092319)
- **Cloudflare域名**: laiye2025.top
- **日历文件位置**: /usr/share/nginx/html/calendar.ics
- **订阅方式**: 小米手机日历 → URL订阅
- **完成时间**: 2026-02-08

**配套系统:**
- Telegram打卡提醒: 05:00/05:20/05:30/22:00
- 惩罚结算: 每周日20:00
- 打卡方式: 回复"开始"/"完成"/"跳过"

---

## FACT-004
**type:** fact  
**area:** trading

**Polymarket 极速交易工具:**
- 位置: `polymarket-tool/`
- 启动: `./start.sh`
- 地址: http://localhost:8502
- API Key: 019c3d3c-80a9-725f-96bd-2e29348b07f6
- 功能: 市场搜索、订单簿查看、一键跳转官网
- 状态: API 端点格式已修复 (/book?token_id=xxx)

---

## FACT-005
**type:** fact  
**area:** trading-strategy

**15分钟 BTC 预测策略:**
1. 现货-预测套利 (胜率 65-70%)
2. RSI 超买超卖 (胜率 55-60%)
3. 布林带均值回归 (胜率 52-58%)
4. 订单流分析 (胜率 60-65%)

关键: 需要自动化、低延迟、严格风控

---

## FACT-006
**type:** fact  
**area:** configuration

**OpenClaw 配置摘要:**
- **模型**: kimi-coding/k2p5 (默认)
- **记忆**: openclaw-mem (OpenAI embedding)
- **压缩**: safeguard 模式 (已开启)
- **上下文**: 262k tokens, 当前约 40%
- **版本**: 2026.2.3-1 (待更新到 2026.2.6-3)

**自动维护:**
- 每30分钟健康检查 Gateway
- 每天凌晨3点强制重启 Gateway
- Git 自动备份 (每6小时)

---

## FACT-007
**type:** fact  
**area:** configuration

**Telegram Bot 配置:**
- **Bot 名称**: laoye5555
- **Username**: @laoye001_bot
- **Token**: 8592185500:AAHsiSK5tRkK3kvreKFcaZwUlG_-PUCyFFM
- **代理**: http://127.0.0.1:10808 (Clash/V2ray)
- **状态**: 运行正常，自动重启保护已配置

---

## FACT-008
**type:** fact  
**area:** knowledge-management

**Obsidian Vault 配置:**
- **位置**: /home/laoye/文档/laoye2025/
- **结构**: 极简 3 文件夹
  - 01 每日随手记/ (每天只写这里)
  - 02 核心资料库/ (自动整理)
  - 03 画布看板/ (Dashboard)
- **主题**: Border (卡片式)
- **同步**: Git 自动备份
- **模板**: 每日笔记、每周回顾

---

## KNOW-001
**type:** knowledge  
**area:** api-reference

**常用 API 密钥汇总:**

| 服务 | Key/Token | 用途 |
|------|-----------|------|
| Polymarket | 019c3d3c-80a9-725f-96bd-2e29348b07f6 | 交易工具 |
| Telegram Bot | 8592185500:AAH...CyFFM | 消息推送 |
| Kimi/OpenAI | [removed] | AI 对话 |

---

## KNOW-002
**type:** knowledge  
**area:** commands

**常用快捷命令:**

```bash
# OpenClaw
openclaw status              # 查看状态
openclaw gateway restart     # 重启网关
openclaw session status      # 会话状态

# Polymarket 工具
cd polymarket-tool && ./start.sh   # 启动交易工具

# Obsidian 整理
cd ~/文档/laoye2025 && ./organize.sh   # 整理笔记

# Git 备份
cd ~/文档/laoye2025 && git add -A && git commit -m "update"
```

---

## TODO-001
**type:** todo  
**area:** pending

**待办事项:**
- [ ] 更新 OpenClaw 到 2026.2.6-3 (含 Telegram 稳定性修复)
- [ ] 配置 DeepSeek API (可选)
- [ ] 开发 Polymarket 套利机器人
- [ ] 优化交易策略自动化

---

*最后更新: 2026-02-09*
*索引系统: openclaw-mem + MEMORY.md*
