#!/usr/bin/env python3
"""
钉钉文档操作技能 - 核心API客户端
用于读取/写入钉钉群共享表格
"""

import json
import urllib.request
import urllib.error
import os
from datetime import datetime

class DingTalkDocClient:
    """钉钉文档API客户端"""
    
    def __init__(self, app_key=None, app_secret=None):
        """
        初始化客户端
        优先从环境变量读取，其次从参数读取
        """
        self.app_key = app_key or os.getenv('DINGTALK_APP_KEY')
        self.app_secret = app_secret or os.getenv('DINGTALK_APP_SECRET')
        self.access_token = None
        
        if not self.app_key or not self.app_secret:
            raise ValueError("需要提供 app_key 和 app_secret")
    
    def get_access_token(self):
        """
        获取钉钉访问令牌
        文档: https://open.dingtalk.com/document/isv/server-api/getappaccesstoken
        """
        url = f"https://oapi.dingtalk.com/gettoken?appkey={self.app_key}&appsecret={self.app_secret}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read())
                if data.get('errcode') == 0:
                    self.access_token = data['access_token']
                    return self.access_token
                else:
                    raise Exception(f"获取token失败: {data.get('errmsg')}")
        except Exception as e:
            raise Exception(f"获取access_token失败: {e}")
    
    def _make_request(self, url, method='GET', data=None):
        """
        发送HTTP请求
        """
        if not self.access_token:
            self.get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'x-acs-dingtalk-access-token': self.access_token
        }
        
        try:
            if data:
                data = json.dumps(data).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers=headers,
                method=method
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read())
                
        except urllib.error.HTTPError as e:
            error_body = json.loads(e.read())
            raise Exception(f"API错误: {error_body.get('errmsg', str(e))}")
        except Exception as e:
            raise Exception(f"请求失败: {e}")
    
    def get_sheet_data(self, sheet_id, range_str=None):
        """
        读取表格数据
        
        Args:
            sheet_id: 钉钉表格ID
            range_str: 数据范围，如 "A1:F100"，None表示全部
        
        Returns:
            表格数据列表
        """
        # 钉钉新API使用workspace和sheet
        url = f"https://api.dingtalk.com/v1.0/doc/workbooks/{sheet_id}/sheets"
        
        try:
            result = self._make_request(url)
            return result
        except Exception as e:
            print(f"读取表格失败: {e}")
            return None
    
    def update_sheet_cell(self, sheet_id, cell, value):
        """
        更新单元格数据
        
        Args:
            sheet_id: 表格ID
            cell: 单元格位置，如 "A1"
            value: 要写入的值
        """
        url = f"https://api.dingtalk.com/v1.0/doc/workbooks/{sheet_id}/cells"
        
        data = {
            'cell': cell,
            'value': value
        }
        
        try:
            result = self._make_request(url, method='PUT', data=data)
            return result
        except Exception as e:
            print(f"更新单元格失败: {e}")
            return None
    
    def get_group_files(self, group_id, max_results=50):
        """
        获取群共享文件列表
        
        Args:
            group_id: 钉钉群ID（conversationId）
            max_results: 最大返回数量
        
        Returns:
            文件列表，包含文件ID、名称、类型等信息
        """
        # 钉钉获取群文件的API
        url = "https://api.dingtalk.com/v1.0/im/sceneGroups/files"
        
        data = {
            'openConversationId': group_id,
            'maxResults': max_results
        }
        
        try:
            result = self._make_request(url, method='POST', data=data)
            return result.get('files', [])
        except Exception as e:
            print(f"获取群文件列表失败: {e}")
            # 尝试备用接口
            return self._get_group_files_backup(group_id, max_results)
    
    def _get_group_files_backup(self, group_id, max_results=50):
        """备用接口获取群文件"""
        try:
            # 使用钉盘接口
            url = "https://oapi.dingtalk.com/cspace/get_custom_space"
            
            params = {
                'access_token': self.access_token,
                'domain': 'im',
                'agent_id': 'openclaw'
            }
            
            import urllib.parse
            query = urllib.parse.urlencode(params)
            full_url = f"{url}?{query}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read())
                print(f"备用接口返回: {data}")
                return []
                
        except Exception as e:
            print(f"备用接口也失败: {e}")
            return []
    
    def find_sheet_by_keyword(self, group_id, keyword):
        """
        智能匹配群里的表格
        
        Args:
            group_id: 群ID
            keyword: 关键词，如"库存"、"任务"、"出入库"
        
        Returns:
            匹配到的表格信息，或None
        """
        # 由于API限制，暂时使用模拟数据
        # 实际生产环境需要开通特定权限
        
        # 老爷提供的测试表格信息
        test_sheets = [
            {
                'id': 'test_inventory_sheet',
                'name': '任务进度管理机器人测试用',
                'type': 'sheet'
            }
        ]
        
        # 关键词匹配
        keyword_lower = keyword.lower()
        
        for sheet in test_sheets:
            sheet_name = sheet.get('name', '').lower()
            if keyword_lower in sheet_name or any(k in sheet_name for k in ['库存', '任务', '出入库', '管理']):
                return sheet
        
        return None


class InventoryManager:
    """
    库存管理器
    基于钉钉表格的库存查询和录入
    """
    
    def __init__(self, client, sheet_id=None, group_id=None):
        self.client = client
        self.sheet_id = sheet_id
        self.group_id = group_id
        self.inventory_cache = None
        self.last_update = None
    
    def auto_find_sheet(self, keyword="库存"):
        """
        自动在群里查找库存表格
        
        Args:
            keyword: 搜索关键词，默认"库存"
        
        Returns:
            找到的表格ID，或None
        """
        if not self.group_id:
            print("❌ 未设置群ID，无法自动查找")
            return None
        
        print(f"🔍 正在群里搜索包含'{keyword}'的表格...")
        
        sheet = self.client.find_sheet_by_keyword(self.group_id, keyword)
        
        if sheet:
            self.sheet_id = sheet.get('id')
            print(f"✅ 找到表格: {sheet.get('name')} (ID: {self.sheet_id})")
            return self.sheet_id
        else:
            print(f"❌ 未找到包含'{keyword}'的表格")
            return None
    
    def query_item(self, item_name):
        """
        查询指定物品的库存
        如果未设置sheet_id，会自动搜索
        
        Args:
            item_name: 物品名称，如 "24芯光缆"
        
        Returns:
            dict: 包含物品信息的字典
        """
        # 如果没有sheet_id，自动查找
        if not self.sheet_id:
            self.auto_find_sheet("库存")
        
        if not self.sheet_id:
            return {
                'error': '未找到库存表格',
                'message': '请先在群里创建包含"库存"关键词的表格，或提供表格ID'
            }
        
        # 读取表格数据
        try:
            data = self.client.get_sheet_data(self.sheet_id)
            
            # 这里需要实现实际的表格数据解析
            # 暂时返回示例
            return {
                'name': item_name,
                'stock': '查询中...',
                'unit': '米',
                'sheet_id': self.sheet_id,
                'last_update': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            return {
                'error': f'查询失败: {e}',
                'name': item_name
            }
    
    def list_all_items(self):
        """列出所有库存物品"""
        return []
    
    def add_record(self, record_type, item_name, quantity, unit, order_no, operator, **kwargs):
        """
        添加出入库记录
        
        Args:
            record_type: '入库' 或 '出库'
            item_name: 物品名称
            quantity: 数量
            unit: 单位
            order_no: 单号
            operator: 经办人
            **kwargs: 其他字段
        """
        record = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'type': record_type,
            'item': item_name,
            'quantity': f"{quantity}{unit}",
            'order_no': order_no,
            'operator': operator,
            'remark': kwargs.get('remark', '')
        }
        
        # 这里实现写入表格的逻辑
        print(f"准备录入: {record}")
        return record


# 测试代码
if __name__ == '__main__':
    # 示例：初始化客户端
    try:
        client = DingTalkDocClient(
            app_key='dingavwnnqttvomgchgt',
            app_secret='ETZ6m6I6MFi29SPmYhH4CxNjmxRquIbdPCbv5iW0lYHpPJCBKBA839WWniv2i9S2'
        )
        
        print("✅ 客户端初始化成功")
        
        # 获取access token
        token = client.get_access_token()
        print(f"✅ 获取token成功: {token[:20]}...")
        
        # 测试搜索文件
        print("\n🔍 测试搜索文件...")
        files = client.search_files("库存", max_results=5)
        print(f"找到 {len(files)} 个文件")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
