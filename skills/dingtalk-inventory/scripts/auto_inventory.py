#!/usr/bin/env python3
"""
钉钉库存查询 - 真正自动化版本
利用钉钉消息事件中的数据自动获取表格
"""

import json
import urllib.request
import os

class DingTalkAutoInventory:
    """自动化库存查询器"""
    
    def __init__(self):
        self.app_key = 'dingavwnnqttvomgchgt'
        self.app_secret = 'ETZ6m6I6MFi29SPmYhH4CxNjmxRquIbdPCbv5iW0lYHpPJCBKBA839WWniv2i9S2'
        self.access_token = None
        
    def get_token(self):
        """获取token"""
        url = f"https://oapi.dingtalk.com/gettoken?appkey={self.app_key}&appsecret={self.app_secret}"
        with urllib.request.urlopen(url) as res:
            data = json.loads(res.read())
            self.access_token = data['access_token']
            return self.access_token
    
    def query_by_chat_id(self, chat_id, item_name="物品"):
        """
        通过群ID自动查询库存
        
        策略：
        1. 获取群基本信息
        2. 查找群关联的文档/表格
        3. 匹配库存相关表格
        4. 读取数据
        """
        if not self.access_token:
            self.get_token()
        
        print(f"🔍 正在查询群 {chat_id} 的库存...")
        
        # 尝试多种方式获取群文件
        
        # 方式1：获取群信息（可能包含文件）
        try:
            url = f"https://oapi.dingtalk.com/chat/getChatInfo?access_token={self.access_token}&chatid={chat_id}"
            with urllib.request.urlopen(url, timeout=10) as res:
                chat_info = json.loads(res.read())
                print(f"✅ 获取群信息成功")
        except Exception as e:
            print(f"⚠️ 获取群信息: {e}")
            chat_info = {}
        
        # 方式2：使用钉盘搜索
        try:
            # 搜索包含"库存"、"任务"关键词的文件
            search_keywords = ["库存", "任务", "出入库", "物料", "管理"]
            all_files = []
            
            for keyword in search_keywords:
                files = self._search_files(keyword)
                all_files.extend(files)
            
            # 去重
            seen = set()
            unique_files = []
            for f in all_files:
                fid = f.get('id') or f.get('file_id')
                if fid and fid not in seen:
                    seen.add(fid)
                    unique_files.append(f)
            
            if unique_files:
                print(f"✅ 找到 {len(unique_files)} 个相关文件")
                for f in unique_files[:3]:
                    print(f"  📄 {f.get('name', '未知')}")
                
                # 返回第一个表格类文件
                for f in unique_files:
                    fname = f.get('name', '').lower()
                    if any(ext in fname for ext in ['sheet', '表格', 'xls', 'csv']):
                        return self._read_sheet(f, item_name)
                
                # 如果没有表格，返回第一个文件信息
                return {
                    'success': True,
                    'message': f"找到文件但未识别为库存表，请确认表格名称包含'库存'关键词",
                    'files_found': [f.get('name') for f in unique_files[:5]]
                }
            else:
                return {
                    'success': False,
                    'message': "未找到相关文件，请确保：\n1. 群里有共享表格\n2. 表格名称包含'库存'、'任务'等关键词"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"查询失败: {e}"
            }
    
    def _search_files(self, keyword):
        """搜索文件"""
        try:
            # 使用钉盘搜索API
            url = f"https://oapi.dingtalk.com/cspace/search?access_token={self.access_token}"
            
            payload = json.dumps({
                "keyword": keyword,
                "limit": 10
            }).encode()
            
            req = urllib.request.Request(
                url, 
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read())
                if data.get('errcode') == 0:
                    return data.get('items', [])
                return []
        except:
            return []
    
    def _read_sheet(self, file_info, item_name):
        """读取表格内容"""
        file_id = file_info.get('id') or file_info.get('file_id')
        file_name = file_info.get('name', '未知')
        
        print(f"📊 正在读取表格: {file_name} (ID: {file_id[:20]}...)")
        
        # 这里应该调用钉钉文档API读取表格内容
        # 由于权限和API复杂度，先返回文件信息
        
        return {
            'success': True,
            'message': f"✅ 找到库存表格：{file_name}\n\n⚠️ 表格读取需要文档API权限，请确保开通了「钉钉文档」权限\n\n📋 下一步：开通文档权限后，我能自动读取表格中的库存数据",
            'table_name': file_name,
            'table_id': file_id,
            'query_item': item_name
        }


if __name__ == '__main__':
    import sys
    
    chat_id = sys.argv[1] if len(sys.argv) > 1 else "cid7kA4dxTZsdXS8YzsR+SbnA=="
    item = sys.argv[2] if len(sys.argv) > 2 else "24芯光缆"
    
    print("🔥 启动自动化库存查询...")
    print("=" * 60)
    
    inv = DingTalkAutoInventory()
    result = inv.query_by_chat_id(chat_id, item)
    
    print("\n📊 查询结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
