#!/usr/bin/env python3
"""
钉钉库存查询脚本
用法: python3 query_inventory.py "查询内容" "群ID"
"""

import sys
import os

# 添加路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'scripts'))

from dingtalk_client import DingTalkDocClient, InventoryManager

def main():
    if len(sys.argv) < 2:
        print("用法: python3 query_inventory.py '查库存 24芯光缆' [群ID]")
        sys.exit(1)
    
    query = sys.argv[1]
    group_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔍 查询: {query}")
    if group_id:
        print(f"📍 群ID: {group_id}")
    
    try:
        # 初始化客户端
        client = DingTalkDocClient(
            app_key='dingavwnnqttvomgchgt',
            app_secret='ETZ6m6I6MFi29SPmYhH4CxNjmxRquIbdPCbv5iW0lYHpPJCBKBA839WWniv2i9S2'
        )
        
        if not group_id:
            print("❌ 错误: 需要在群里才能查询（缺少群ID）")
            sys.exit(1)
        
        # 创建管理器
        manager = InventoryManager(client, group_id=group_id)
        
        # 查找库存表
        print("🔍 正在扫描群文件...")
        sheet_id = manager.auto_find_sheet("库存")
        
        if not sheet_id:
            print("❌ 未找到库存表格")
            print("💡 提示: 请确保群里有名称包含'库存'的共享表格")
            sys.exit(1)
        
        print(f"✅ 找到表格，开始查询...")
        
        # 提取物品名（简单提取）
        import re
        match = re.search(r'(\d*芯\w+|\w+)(?:还剩|剩余|库存)?', query)
        item_name = match.group(1) if match else "物品"
        
        # 查询
        result = manager.query_item(item_name)
        
        # 输出结果（JSON格式，方便OpenClaw解析）
        output = {
            "success": True,
            "item": result.get('name', item_name),
            "stock": result.get('stock', '未找到'),
            "unit": result.get('unit', '件'),
            "sheet_id": sheet_id,
            "message": f"📦 {result.get('name', item_name)} 库存: {result.get('stock', '查询中...')} {result.get('unit', '件')}"
        }
        
        print(json.dumps(output, ensure_ascii=False))
        
    except Exception as e:
        error_output = {
            "success": False,
            "error": str(e),
            "message": f"❌ 查询失败: {e}"
        }
        print(json.dumps(error_output, ensure_ascii=False))
        sys.exit(1)

if __name__ == '__main__':
    import json
    main()
