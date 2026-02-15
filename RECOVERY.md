# 🛡️ 豆芽灾难恢复指南

> 如果系统崩溃、配置丢失、或者我"犯傻"改坏了东西，用这份指南快速恢复！

---

## 📦 备份位置

**GitHub 仓库**: https://github.com/laoye2020/openclaw-workspace

包含：
- ✅ 所有技能配置和元数据
- ✅ 身份文件 (IDENTITY.md, USER.md, SOLO.md)
- ✅ 系统文档和工具配置
- ❌ API Keys（需重新配置，安全原因不存储）
- ❌ 大型媒体文件

---

## 🚀 一键恢复步骤

### 1. 安装 OpenClaw
```bash
# 如果系统重装，先安装 OpenClaw
npm install -g openclaw
```

### 2. 克隆备份仓库
```bash
cd ~
git clone https://github.com/laoye2020/openclaw-workspace.git .openclaw/workspace
```

### 3. 重新安装技能
```bash
cd ~/.openclaw/workspace
npx clawhub sync
# 或逐个安装:
# npx clawhub install tavily
# npx clawhub install github
# npx clawhub install obsidian
# npx clawhub install session-logs
# npx clawhub install skill-creator
```

### 4. 重新配置 API Keys

#### Tavily 搜索
```bash
# 获取 API Key: https://app.tavily.com
export TAVILY_API_KEY="tvly-你的key"
# 添加到 ~/.bashrc 永久保存
echo 'export TAVILY_API_KEY="tvly-你的key"' >> ~/.bashrc
```

#### GitHub
```bash
gh auth login
# 或使用 Token:
export GH_TOKEN="ghp_你的token"
```

#### 浏览器控制
1. 安装 Chrome 扩展
2. 点击扩展图标连接

#### Obsidian
```bash
# 安装 obsidian-cli
curl -L -o /tmp/obsidian-cli.tar.gz https://github.com/Yakitrak/obsidian-cli/releases/download/v0.2.3/obsidian-cli_0.2.3_linux_amd64.tar.gz
tar -xzf /tmp/obsidian-cli.tar.gz -C /tmp
sudo mv /tmp/obsidian-cli /usr/local/bin/
obsidian-cli set-default "laoye2025"
```

---

## 💾 定期备份

### 手动备份
```bash
cd ~/.openclaw/workspace
./backup.sh "备份说明"
```

### 自动备份（推荐）
添加到 crontab:
```bash
# 每天凌晨3点自动备份
0 3 * * * cd /home/laoye/.openclaw/workspace && ./backup.sh "🤖 自动每日备份"
```

---

## 🔧 常见问题

### Q: 恢复后我不记得之前的 API Keys 了
**A**: 查看 `TOOLS.md` 或 `.bashrc` 历史，或重新申请：
- Tavily: https://app.tavily.com
- GitHub: https://github.com/settings/tokens

### Q: 技能安装失败
**A**: 检查网络连接，或逐个安装排查问题：
```bash
npx clawhub install tavily --force
```

### Q: 浏览器扩展连不上
**A**: 
1. 确保 Chrome 已安装扩展
2. 刷新页面后点击扩展图标
3. 检查 `openclaw gateway status`

### Q: Obsidian 路径不对
**A**: 重新设置默认 vault：
```bash
obsidian-cli set-default "你的vault名称"
```

---

## 📋 配置清单

恢复后检查列表：

- [ ] Tavily API Key 配置
- [ ] GitHub 登录状态 (`gh auth status`)
- [ ] Chrome 扩展连接
- [ ] Obsidian vault 路径正确
- [ ] 浏览器控制测试 (`openclaw browser status`)
- [ ] 所有技能列表 (`openclaw skills list`)

---

## 🆘 紧急联系

如果完全无法恢复：
1. 查看 GitHub 仓库的完整历史: https://github.com/laoye2020/openclaw-workspace/commits/master
2. 下载任意历史版本的 zip 包
3. 从今天的对话重新开始配置

---

*最后更新: 2026-02-07*
*备份版本: $(git rev-parse --short HEAD 2>/dev/null || echo "未知")*
