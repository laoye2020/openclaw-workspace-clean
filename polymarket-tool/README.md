# ⚡ Polymarket 极速交易工具

> Web 界面版本的 Polymarket 交易工具，比网页快 5-10 倍

## ✨ 功能特性

- **⚡ 极速盘口** - API 直接获取，刷新延迟 < 100ms
- **🔢 快速下单** - 输入价格数量 → 立即提交
- **💼 持仓管理** - 实时查看当前仓位
- **🔔 价格预警** - 设置阈值推送提醒（可选）
- **📊 多市场** - 支持所有 Polymarket 市场

## 🚀 快速开始

### 1. 安装依赖

```bash
cd polymarket-tool
pip install -r requirements.txt
```

### 2. 配置钱包

编辑 `app.py` 或在界面中输入：
- **钱包地址** - 必须输入（用于查询持仓）
- **私钥** - 仅下单时需要（本地运行，不上传）

### 3. 启动工具

```bash
streamlit run app.py
```

然后浏览器访问：`http://localhost:8501`

## 📖 使用说明

### 搜索市场
- 直接输入市场名称（如 "BTC"、 "大选"）
- 或粘贴 Polymarket URL 中的 slug

### 查看盘口
- 左侧红色：卖盘（Asks）
- 左侧绿色：买盘（Bids）
- 自动刷新，实时价格

### 下单流程
1. 选择方向（买入/卖出）
2. 输入价格和数量
3. 点击下单按钮
4. 等待确认

### 快捷操作
- "🔵 只读观察" - 仅查看数据
- "🟢 允许下单" - 启用交易功能

## ⚠️ 重要提醒

1. **美国限制** - Polymarket 不对美国用户开放
2. **资金风险** - 加密货币交易有风险，请谨慎操作
3. **私钥安全** - 私钥仅本地使用，切勿上传
4. **测试优先** - 建议先用小额测试功能

## 🔧 技术架构

```
polymarket-tool/
├── app.py           # Streamlit 主界面
├── api_client.py    # Polymarket API 封装
├── requirements.txt # 依赖列表
└── README.md        # 本文件
```

## 📊 API 文档

- **CLOB API**: https://clob.polymarket.com
- **Gamma API**: https://gamma-api.polymarket.com
- **文档**: https://docs.polymarket.com

## 🐛 常见问题

**Q: 盘口数据不刷新？**
A: 检查网络连接，或调整刷新频率（侧边栏设置）

**Q: 下单失败？**
A: 1. 确认私钥正确 2. 确认钱包有足够 USDC 3. 检查价格范围

**Q: 找不到市场？**
A: 尝试更简短或更英文的关键词

---

*Built with ❤️ for faster trading*
