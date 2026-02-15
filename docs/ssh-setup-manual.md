# SSH 免密登录配置指南

## 方法：手动复制公钥

### 步骤1：打开终端，运行以下命令

```bash
# 确保密钥已生成
ls ~/.ssh/id_rsa.pub

# 如果显示文件不存在，先运行：
# ssh-keygen -t rsa -b 4096 -C "douya@openclaw" -f ~/.ssh/id_rsa -N ""

# 复制公钥内容
cat ~/.ssh/id_rsa.pub
```

### 步骤2：登录阿里云服务器

```bash
ssh root@47.107.58.190
# 密码: @Qwer092319
```

### 步骤3：添加公钥到 authorized_keys

```bash
# 创建 .ssh 目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 编辑 authorized_keys 文件
nano ~/.ssh/authorized_keys
# 或
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys

# 设置权限
chmod 600 ~/.ssh/authorized_keys
```

### 步骤4：退出服务器，测试免密登录

```bash
exit

# 测试免密登录
ssh root@47.107.58.190 "date"
```

如果显示服务器时间，说明配置成功！

---

## 自动上传日历脚本

配置完成后，运行以下命令上传日历：

```bash
scp ~/.openclaw/workspace/life-system/calendar.ics root@47.107.58.190:/usr/share/nginx/html/calendar.ics
```

---

## 公钥内容（复制这一整行）

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDQ8g3EFasYrWkJUmiReW0498Vr3HdumIeGcF45qzPKpI8/Je9QdhTOppXV+Hwgk0e9oZqY/vGirenBZvmjqPPooDXpOKPfgF/XBLyXL5XKP0FUQ7MBtk7fWPP1xl8r2If5XJ7y6/Nzhs6njabnkd5ef6udR01STeegyfIvZ4rCsy7XxetCKvzHd9qLV1s3HopKV/U+G2AxFbqCwVYqSL9PdDStOJOhMjc5gp5JchhWlrNI3fcnAovIxv6mj1AHA9khUum8WjrcntN1n0VZXF0ieID6UjC6lJCcUVva43mRswE58C3XiMc5Sts6vrKbeBKoXreK0HK4jVz0yMqlJLsPkyCsx+vRyqRZHXYnCnlkMoNZs7wqbB7kxDWEDGgceQ+P65i48v0r0j8ex3Cq3g5rkeBY/gL7aqUiywIPgWmOTdc8O+shEiqn26VYIJONDW+zDRs9Wu1DcrfZ9PrhXpJDhFQ+0rVVBSu/xiHS5pzcK3fkEcY76ALBdcp3F8kgqtmfLn1M26OGIj8IhXjtJV4ByEgznQAOFbqkja80YmpwYh1pWeODdmDNcW5iFz+gtS/5lbSR0TuRDlpbakVfzLb1soMAKAkTq6RG6/tIB7+0iumMsx3hF7IiEt1NAOBxA87WZk8/JjSJGNNLOgUm25CKA8AQLSpzn7hkz0AqsRGBcQ== douya@openclaw
```

---

## 快捷命令

配置完成后，以下是常用命令：

```bash
# 测试连接
ssh root@47.107.58.190 "date"

# 上传日历
scp ~/.openclaw/workspace/life-system/calendar.ics root@47.107.58.190:/usr/share/nginx/html/calendar.ics

# 查看服务器上的日历
curl https://laoye2025.top/calendar.ics | head -20
```
