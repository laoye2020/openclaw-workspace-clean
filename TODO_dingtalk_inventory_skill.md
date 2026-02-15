# 🛠️ 钉钉文档操作技能开发计划

## 📋 需求
- 读取钉钉群共享表格
- 查询库存数据
- 自动录入出入库信息

## 🏗️ 技术方案

### 1. 权限申请（老爷完成）
- [ ] 钉钉开放平台 → 权限管理
- [ ] 开通 `dingtalk.oapi.ding.doc.read`
- [ ] 开通 `dingtalk.oapi.ding.doc.write`
- [ ] 开通 `dingtalk.oapi.ding.sheet.read`
- [ ] 开通 `dingtalk.oapi.ding.sheet.write`

### 2. 核心功能模块

#### 模块A：钉钉API客户端
```python
class DingTalkDocClient:
    - get_access_token()  # 获取访问令牌
    - get_sheet_data(sheet_id)  # 读取表格
    - update_sheet(sheet_id, data)  # 更新表格
    - search_files(keyword)  # 搜索文件
```

#### 模块B：库存查询
```python
class InventoryQuery:
    - query_stock(item_name)  # 查询某物品库存
    - list_all_items()  # 列出所有物品
    - get_low_stock_items()  # 获取低库存物品
```

#### 模块C：出入库录入
```python
class InventoryRecord:
    - add_inbound(data)  # 添加入库记录
    - add_outbound(data)  # 添加出库记录
    - parse_message(text)  # 解析自然语言
```

### 3. 使用场景

**场景1：查询库存**
```
用户：@机器人 24芯光缆还剩多少？
机器人：查询表格 → 返回：24芯光缆 库存 156.5 米
```

**场景2：录入入库**
```
用户：@机器人 入库 100件 iPhone15 单号RK001
机器人：解析 → 录入表格 → 返回确认
```

**场景3：录入出库**
```
用户：@机器人 出库 50台 华为Mate60 单号CK001 客户张三
机器人：解析 → 录入表格 → 返回确认
```

## 📅 开发时间表

| 阶段 | 时间 | 内容 |
|------|------|------|
| 第1阶段 | 30分钟 | 搭建基础API客户端 |
| 第2阶段 | 1小时 | 实现表格读写功能 |
| 第3阶段 | 30分钟 | 集成OpenClaw技能 |
| 第4阶段 | 30分钟 | 测试调试 |

**预计总时间：2.5-3小时**

## 📝 当前状态

- [x] 需求确认
- [ ] 等待老爷开通权限
- [ ] 开发API客户端
- [ ] 开发库存查询功能
- [ ] 开发出入库录入功能
- [ ] 测试验证

---

**创建时间**: 2026-02-07 18:10
**优先级**: 中
**预计完成**: 本周末
