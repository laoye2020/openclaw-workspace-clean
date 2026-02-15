#!/usr/bin/env python3
"""
钉钉库存管理技能 - OpenClaw集成入口
处理钉钉消息，自动查询库存
"""

import os
import sys
import json

# 添加脚本路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'scripts'))

from dingtalk_client import DingTalkDocClient, InventoryManager

class DingTalkInventorySkill:
    """钉钉库存管理技能主类"""
    
    def __init__(self):
        self.client = None
        self.manager = None
        self._init_client()
    
    def _init_client(self):
        """初始化钉钉客户端"""
        try:
            # 从环境变量或配置读取
            app_key = os.getenv('DINGTALK_APP_KEY', 'dingavwnnqttvomgchgt')
            app_secret = os.getenv('DINGTALK_APP_SECRET', 'ETZ6m6I6MFi29SPmYhH4CxNjmxRquIbdPCbv5iW0lYHpPJCBKBA839WWniv2i9S2')
            
            self.client = DingTalkDocClient(app_key=app_key, app_secret=app_secret)
            print("✅ 钉钉客户端初始化成功")
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            self.client = None
    
    def handle_message(self, text, group_id=None, user_id=None):
        """
        处理用户消息
        
        Args:
            text: 消息内容
            group_id: 群ID（群聊时有）
            user_id: 用户ID
        
        Returns:
            回复消息
        """
        if not self.client:
            return "❌ 钉钉服务未初始化"
        
        text_lower = text.lower().strip()
        
        # 识别查询库存指令
        if any(keyword in text_lower for keyword in ['查库存', '库存', '还剩多少', '剩余']):
            return self._handle_inventory_query(text, group_id)
        
        # 识别入库指令
        if any(keyword in text_lower for keyword in ['入库', '进货', '收入']):
            return self._handle_inbound(text, group_id)
        
        # 识别出库指令
        if any(keyword in text_lower for keyword in ['出库', '发货', '支出']):
            return self._handle_outbound(text, group_id)
        
        # 默认回复
        return self._get_help_message()
    
    def _handle_inventory_query(self, text, group_id):
        """处理库存查询"""
        if not group_id:
            return "❌ 请在群里查询库存，私聊无法访问群文件"
        
        try:
            # 提取物品名称（简单提取"XX还剩多少"中的XX）
            import re
            match = re.search(r'(\d*芯\w+|\w+)(?:还剩|剩余|库存)', text)
            item_name = match.group(1) if match else "物品"
            
            # 创建管理器
            self.manager = InventoryManager(self.client, group_id=group_id)
            
            # 自动查找库存表
            sheet_id = self.manager.auto_find_sheet("库存")
            
            if not sheet_id:
                return "📂 未找到库存表格\n请确保群里共享的表格名称包含'库存'、'出入库'等关键词"
            
            # 查询物品
            result = self.manager.query_item(item_name)
            
            if 'error' in result:
                return f"❌ 查询失败: {result['error']}"
            
            # 格式化回复
            reply = f"📦 **库存查询结果**\n\n"
            reply += f"物品: {result.get('name', item_name)}\n"
            reply += f"库存: {result.get('stock', '查询中...')}\n"
            reply += f"单位: {result.get('unit', '件')}\n"
            reply += f"表格: ✅ 已连接\n"
            
            return reply
            
        except Exception as e:
            return f"❌ 查询出错: {e}"
    
    def _handle_inbound(self, text, group_id):
        """处理入库记录"""
        return "📝 入库功能开发中...\n请使用格式：\n入库 数量 物品名称 单号XXX 经办人XXX"
    
    def _handle_outbound(self, text, group_id):
        """处理出库记录"""
        return "📝 出库功能开发中...\n请使用格式：\n出库 数量 物品名称 单号XXX 经办人XXX"
    
    def _get_help_message(self):
        """获取帮助信息"""
        help_msg = """🤖 **钉钉库存管理助手**

**可用指令：**
• 查库存 - 自动扫描群里的库存表格
• XX还剩多少 - 查询指定物品库存
• 入库 数量 物品 单号 经办人
• 出库 数量 物品 单号 经办人

**示例：**
@机器人 查库存
@机器人 24芯光缆还剩多少？
@机器人 入库 100件 iPhone15 单号RK001 张三

**注意：**
• 需要在群里使用（才能访问群文件）
• 表格名称需包含"库存"关键词"""
        
        return help_msg


# 全局技能实例
_skill_instance = None

def get_skill():
    """获取技能单例"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = DingTalkInventorySkill()
    return _skill_instance


if __name__ == '__main__':
    # 测试
    skill = get_skill()
    
    # 模拟测试
    print("\n🧪 测试查询...")
    result = skill.handle_message("查库存 24芯光缆", group_id="test_group")
    print(result)
