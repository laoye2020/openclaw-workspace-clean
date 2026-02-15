#!/usr/bin/env python3
"""
Desktop Controller for Linux
兼容层，处理 pygetwindow 在 Linux 上不可用的问题
"""

import pyautogui
from PIL import Image
import subprocess
import re

class DesktopController:
    """Linux 兼容的桌面控制器"""
    
    def __init__(self, failsafe=True):
        pyautogui.FAILSAFE = failsafe
        self.failsafe = failsafe
    
    # ========== 鼠标控制 ==========
    def move_mouse(self, x, y, duration=0, smooth=True):
        """移动鼠标到指定坐标"""
        if duration > 0:
            pyautogui.moveTo(x, y, duration=duration)
        else:
            pyautogui.moveTo(x, y)
    
    def move_relative(self, x_offset, y_offset, duration=0):
        """相对移动"""
        pyautogui.moveRel(x_offset, y_offset, duration=duration)
    
    def click(self, x=None, y=None, button='left', clicks=1, interval=0.1):
        """点击"""
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
        else:
            pyautogui.click(clicks=clicks, interval=interval, button=button)
    
    def drag(self, start_x, start_y, end_x, end_y, duration=0.5, button='left'):
        """拖拽"""
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
    
    def scroll(self, clicks, direction='vertical', x=None, y=None):
        """滚动"""
        if direction == 'horizontal':
            pyautogui.hscroll(clicks, x=x, y=y)
        else:
            pyautogui.scroll(clicks, x=x, y=y)
    
    def get_mouse_position(self):
        """获取鼠标位置"""
        return pyautogui.position()
    
    # ========== 键盘控制 ==========
    def type_text(self, text, interval=0, wpm=None):
        """输入文字"""
        if wpm:
            interval = 60.0 / (wpm * 5)  # 粗略估算
        pyautogui.typewrite(text, interval=interval)
    
    def press(self, key, presses=1, interval=0.1):
        """按键"""
        pyautogui.press(key, presses=presses, interval=interval)
    
    def hotkey(self, *keys, interval=0.05):
        """快捷键"""
        pyautogui.hotkey(*keys, interval=interval)
    
    def key_down(self, key):
        """按下键（不释放）"""
        pyautogui.keyDown(key)
    
    def key_up(self, key):
        """释放键"""
        pyautogui.keyUp(key)
    
    # ========== 屏幕操作 ==========
    def screenshot(self, region=None, filename=None):
        """截图"""
        if region:
            img = pyautogui.screenshot(region=region)
        else:
            img = pyautogui.screenshot()
        
        if filename:
            img.save(filename)
        return img
    
    def get_pixel_color(self, x, y):
        """获取像素颜色"""
        return pyautogui.pixel(x, y)
    
    def get_screen_size(self):
        """获取屏幕大小"""
        return pyautogui.size()
    
    # ========== 窗口管理 (Linux 替代方案) ==========
    def get_all_windows(self):
        """获取所有窗口（使用 xdotool）"""
        try:
            result = subprocess.run(['xdotool', 'search', '--all', '--name', ''], 
                                  capture_output=True, text=True)
            window_ids = result.stdout.strip().split('\n')
            windows = []
            for wid in window_ids:
                if wid:
                    try:
                        name_result = subprocess.run(['xdotool', 'getwindowname', wid], 
                                                   capture_output=True, text=True)
                        if name_result.returncode == 0 and name_result.stdout.strip():
                            windows.append(name_result.stdout.strip())
                    except:
                        pass
            return windows
        except FileNotFoundError:
            print("⚠️  xdotool 未安装，窗口功能受限")
            return []
    
    def activate_window(self, title_substring):
        """激活窗口"""
        try:
            subprocess.run(['xdotool', 'search', '--name', title_substring, 
                          'windowactivate'], check=False)
            return True
        except FileNotFoundError:
            print("⚠️  xdotool 未安装")
            return False
    
    def get_active_window(self):
        """获取当前活动窗口"""
        try:
            result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except FileNotFoundError:
            return None

# 便捷导入
__all__ = ['DesktopController']
