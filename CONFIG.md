# 📋 豆芽配置清单

> 快速查看当前配置状态和恢复所需信息

---

## 🌱 身份信息

- **名字**: 豆芽
- **称呼用户**: 老爷
- **风格**: 萨勒芬妮（粉色、闪亮、轻松幽默）
- **创建时间**: 2026-02-07

---

## 🔧 已安装技能 (5个)

| 技能 | 版本 | 用途 | 恢复命令 |
|------|------|------|----------|
| tavily | 1.0.0 | AI搜索 | `npx clawhub install tavily` |
| github | 1.0.0 | 代码管理 | `npx clawhub install github` |
| obsidian | 1.0.0 | 笔记管理 | `npx clawhub install obsidian` |
| session-logs | latest | 对话分析 | `npx clawhub install session-logs` |
| skill-creator | latest | 创建技能 | `npx clawhub install skill-creator` |

---

## 🔑 API Keys & 凭证

| 服务 | 状态 | Key位置 | 恢复方式 |
|------|------|---------|----------|
| **Tavily** | ✅ 已配置 | `~/.bashrc` | 重新申请: https://app.tavily.com |
| **GitHub** | ✅ 已登录 | Keyring | `gh auth login` |
| **Browser** | ✅ 已连接 | Chrome扩展 | 重新安装扩展 |
| **Obsidian** | ✅ 已配置 | obsidian-cli | `obsidian-cli set-default laoye2025` |

---

## 📁 重要路径

```
~/.openclaw/workspace/          # 工作区根目录
├── skills/                     # 技能目录
├── IDENTITY.md                 # 我的身份
├── USER.md                     # 用户信息
├── SOUL.md                     # 行为准则
├── TOOLS.md                    # 工具笔记
├── RECOVERY.md                 # 恢复指南
└── backup.sh                   # 备份脚本

~/文档/laoye2025/               # Obsidian Vault
```

---

## 🚀 一键操作

### 备份当前配置
```bash
cd ~/.openclaw/workspace
./backup.sh "手动备份说明"
```

### 检查所有服务状态
```bash
# 搜索
echo $TAVILY_API_KEY

# GitHub
gh auth status

# 浏览器
openclaw browser status

# Obsidian
obsidian-cli print-default

# 技能列表
openclaw skills list
```

### 完整恢复（新机器）
```bash
# 1. 克隆仓库
git clone https://github.com/laoye2020/openclaw-workspace.git ~/.openclaw/workspace

# 2. 进入目录
cd ~/.openclaw/workspace

# 3. 恢复技能
npx clawhub sync

# 4. 重新配置API（按RECOVERY.md指引）
```

---

## 📝 最近变更

| 时间 | 操作 | 提交 |
|------|------|------|
| 2026-02-07 | 初始配置 | cee9f14 |
| 2026-02-07 | 添加备份系统 | 8cdc2d6 |

---

*自动生成于: $(date '+%Y-%m-%d %H:%M:%S')*
# 最后测试时间: 2026-02-07 13:38:04
