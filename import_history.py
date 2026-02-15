"""导入历史会话到长期记忆"""
import json
import os
from datetime import datetime

# 关键信息提取
critical_facts = []

# 从现有 MEMORY.md 加载
if os.path.exists("MEMORY.md"):
    with open("MEMORY.md", "r") as f:
        content = f.read()

# 添加 Polymarket 相关信息
new_facts = """
## FACT-006
**type:** fact  
**area:** trading

**Polymarket 极速交易工具:**
- 位置: `polymarket-tool/`
- 启动: `./start.sh`
- 地址: http://localhost:8502
- API Key: 019c3d3c-80a9-725f-96bd-2e29348b07f6
- 功能: 市场搜索、订单簿查看、一键跳转官网

---

## FACT-007
**type:** fact  
**area:** trading-strategy

**15分钟 BTC 预测策略:**
1. 现货-预测套利 (胜率 65-70%)
2. RSI 超买超卖 (胜率 55-60%)
3. 布林带均值回归 (胜率 52-58%)
4. 订单流分析 (胜率 60-65%)

关键: 需要自动化、低延迟、严格风控

---

## FACT-008
**type:** decision  
**area:** infrastructure

**长期记忆配置:**
- 方案: openclaw-mem
- Embedding: OpenAI text-embedding-3-small
- 存储: MEMORY.md + memory/日志
- 启用时间: 2026-02-09

---
"""

# 追加到 MEMORY.md
with open("MEMORY.md", "a") as f:
    f.write(new_facts)

print("✅ 关键信息已导入到 MEMORY.md")
print("✅ 下次对话将自动检索这些记忆")
