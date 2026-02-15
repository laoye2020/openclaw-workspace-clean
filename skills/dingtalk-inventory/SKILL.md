---
name: dingtalk-inventory
description: 钉钉文档库存管理技能 - 查询库存、录入出入库记录到钉钉表格
metadata:
  openclaw:
    emoji: 📦
    requires:
      bins: ["python3"]
      env: ["DINGTALK_APP_KEY", "DINGTALK_APP_SECRET"]
---

# 钉钉库存管理技能

## 功能

- 🔍 查询钉钉群共享表格中的库存数据
- 📝 自动录入出入库记录
- 📊 支持自然语言解析（如"入库100件iPhone"）

## 使用方法

### 1. 查询库存

```
@机器人 24芯光缆还剩多少？
@机器人 查询库存 iPhone15
@机器人 库存清单
```

### 2. 录入入库

```
@机器人 入库 100件 iPhone15 单号RK20240207001 经办人张三
@机器人 入库 50箱 数据线 单号RK001 李四
```

### 3. 录入出库

```
@机器人 出库 30台 华为Mate60 单号CK001 经办人王五 客户：赵六
```

## 配置

### 环境变量

```bash
export DINGTALK_APP_KEY="你的AppKey"
export DINGTALK_APP_SECRET="你的AppSecret"
export INVENTORY_SHEET_ID="库存表格ID"
```

### 钉钉权限要求

需要在钉钉开放平台开通：
- `dingtalk.oapi.ding.doc.read` - 读取文档
- `dingtalk.oapi.ding.doc.write` - 写入文档
- `dingtalk.oapi.ding.sheet.read` - 读取表格
- `dingtalk.oapi.ding.sheet.write` - 写入表格

## 表格格式要求

库存表格应包含以下列：
| 日期 | 单号 | 类型(入库/出库) | 物料名称 | 数量 | 单位 | 经办人 | 客户 | 备注 |

## 技术实现

- Python 3.8+
- 钉钉开放平台 API v2
- 支持 Stream Mode（无需公网IP）

---
*开发中... 预计本周末完成*
