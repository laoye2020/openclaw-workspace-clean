# 🖱️ Desktop Control 使用指南

> 自动化控制鼠标、键盘、屏幕的神器

---

## ✅ 安装状态

| 依赖 | 状态 |
|------|------|
| pyautogui | ✅ 已安装 |
| pillow | ✅ 已安装 |
| opencv-python | ⏳ 安装中 |
| pygetwindow | ⏳ 安装中 |

---

## 🚀 快速开始

### 1. 基础鼠标操作

```python
from skills.desktop_control import DesktopController

# 初始化
dc = DesktopController(failsafe=True)

# 移动鼠标到坐标 (x, y)
dc.move_mouse(500, 300)

# 点击
dc.click()

# 右键点击
dc.click(button='right')

# 双击
dc.click(clicks=2)

# 拖拽文件
dc.drag(100, 100, 500, 500, duration=1.0)
```

### 2. 键盘输入

```python
# 打字
dc.type_text("Hello 老爷！", wpm=60)

# 快捷键
dc.hotkey('ctrl', 'c')  # 复制
dc.hotkey('ctrl', 'v')  # 粘贴
dc.hotkey('win', 'r')   # 运行对话框

# 按特殊键
dc.press('enter')
dc.press('esc')
```

### 3. 屏幕操作

```python
# 截图
img = dc.screenshot()
img.save("screenshot.png")

# 区域截图
img = dc.screenshot(region=(100, 100, 500, 300))

# 获取鼠标位置
x, y = dc.get_mouse_position()
print(f"鼠标在: {x}, {y}")

# 获取屏幕分辨率
width, height = dc.get_screen_size()
```

### 4. 窗口管理

```python
# 列出所有窗口
windows = dc.get_all_windows()

# 激活指定窗口
dc.activate_window("Chrome")
dc.activate_window("Visual Studio Code")
```

---

## 🛡️ 安全特性

### Failsafe（防失控）
- 移动鼠标到**任意屏幕角落** → 立即停止所有自动化
- 默认开启，建议保持启用

### 使用建议
1. 先在安全环境测试
2. 重要操作前截图确认
3. 保持鼠标可移动到角落

---

## 💡 实用场景

### 场景1：自动填表
```python
dc.click(300, 200)  # 点击输入框
dc.type_text("用户名", wpm=80)
dc.press('tab')     # 跳到下一项
dc.type_text("密码")
dc.press('enter')   # 提交
```

### 场景2：定时截图
```python
import time
for i in range(10):
    dc.screenshot(filename=f"capture_{i}.png")
    time.sleep(60)  # 每分钟截一张
```

### 场景3：批量操作文件
```python
# Ctrl+点击多选
dc.key_down('ctrl')
dc.click(100, 200)
dc.click(100, 250)
dc.click(100, 300)
dc.key_up('ctrl')

# 复制
dc.hotkey('ctrl', 'c')
```

---

## 📋 坐标系说明

```
屏幕左上角 (0, 0)
    ↓
    ↓  Y 增加
    ↓
    →→→ X 增加
```

- **X**: 从左到右（0 到屏幕宽度）
- **Y**: 从上到下（0 到屏幕高度）

---

*最后更新: 2026-02-07*
*Skill: desktop-control v1.0.0*
