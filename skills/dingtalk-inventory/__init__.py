"""
钉钉库存管理技能
DingTalk Inventory Management Skill
"""

from .scripts.dingtalk_client import DingTalkDocClient, InventoryManager

__version__ = '0.1.0'
__all__ = ['DingTalkDocClient', 'InventoryManager']
