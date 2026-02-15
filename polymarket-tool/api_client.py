"""
Polymarket API Client (修复版)
⚡ 支持 API 限制检测
"""

import time
import json
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import streamlit as st


class Side(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    GTC = "GTC"


@dataclass
class OrderBook:
    bids: List[Dict]
    asks: List[Dict]
    token_id: str
    last_updated: float


@dataclass
class Market:
    id: str
    name: str
    token_id: str
    current_price: float
    volume: float
    liquidity: float


class PolymarketClient:
    """Polymarket API 客户端 - 修复版"""
    
    BASE_URL = "https://clob.polymarket.com"
    GAMMA_URL = "https://gamma-api.polymarket.com"
    
    def __init__(self, private_key: Optional[str] = None):
        self.private_key = private_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self.rate_limit_delay = 0.1
        self._api_restricted = False
    
    def _rate_limited_request(self, method: str, url: str, **kwargs) -> Any:
        """带速率限制的请求"""
        time.sleep(self.rate_limit_delay)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, **kwargs, timeout=5)
            else:
                response = self.session.request(method, url, **kwargs, timeout=5)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None
    
    def check_api_status(self) -> Dict:
        """检查 API 可用性"""
        try:
            # 测试 CLOB API
            url = f"{self.BASE_URL}/markets?limit=1"
            resp = self.session.get(url, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                markets = data.get("data", [])
                
                # 检查是否有接受订单的市场
                accepting = [m for m in markets if m.get('accepting_orders')]
                
                return {
                    "status": "ok",
                    "total_markets": len(markets),
                    "accepting_orders": len(accepting),
                    "restricted": len(accepting) == 0 and len(markets) > 0
                }
            else:
                return {"status": "error", "message": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_active_markets(self, limit: int = 50) -> List[Dict]:
        """获取活跃市场（支持 API 限制）"""
        url = f"{self.BASE_URL}/markets"
        params = {"limit": limit}
        
        data = self._rate_limited_request("GET", url, params=params)
        if not data:
            return []
        
        markets = data.get("data", [])
        
        # 过滤活跃市场 (只检查 accepting_orders)
        active = []
        for m in markets:
            if m.get('accepting_orders'):
                active.append(m)
        
        return active
    
    def search_markets(self, query: str) -> List[Market]:
        """搜索市场 - 使用 CLOB API"""
        url = f"{self.BASE_URL}/markets"
        params = {"limit": 100}  # 获取更多市场用于搜索
        
        data = self._rate_limited_request("GET", url, params=params)
        if not data:
            return []
        
        markets_data = data.get("data", [])
        
        # 过滤和搜索
        markets = []
        query_lower = query.lower()
        
        for m in markets_data:
            # 只保留接受订单的市场
            if not m.get('accepting_orders'):
                continue
            
            # 搜索匹配
            question = m.get('question', '').lower()
            slug = m.get('market_slug', '').lower()
            
            if query_lower in question or query_lower in slug:
                tokens = m.get('tokens', [])
                if tokens and len(tokens) > 0:
                    # 使用第一个 token（通常是 Yes）
                    token = tokens[0]
                    token_id = token.get('token_id', '')
                    
                    if token_id:
                        markets.append(Market(
                            id=m.get('condition_id', m.get('id', '')),
                            name=m.get('question', 'Unknown'),
                            token_id=token_id,
                            current_price=token.get('price', 0.5),
                            volume=m.get('volume', 0) or 0,
                            liquidity=m.get('liquidity', 0) or 0
                        ))
        
        return markets[:20]  # 限制结果数量
    
    def get_orderbook(self, token_id: str, depth: int = 10) -> Optional[OrderBook]:
        """获取订单簿 - 使用正确端点格式 /book?token_id=xxx"""
        if not token_id:
            return None
            
        # 正确的端点格式: /book?token_id={token_id}
        url = f"{self.BASE_URL}/book?token_id={token_id}"
        
        try:
            resp = self.session.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                bids = data.get("bids", [])[:depth]
                asks = data.get("asks", [])[:depth]
                
                return OrderBook(
                    bids=bids,
                    asks=asks,
                    token_id=token_id,
                    last_updated=time.time()
                )
            elif resp.status_code == 404:
                # 没有订单簿（市场无流动性）
                return OrderBook(
                    bids=[],
                    asks=[],
                    token_id=token_id,
                    last_updated=time.time()
                )
            else:
                return None
        except Exception:
            return None
    
    def create_order(
        self,
        token_id: str,
        price: float,
        size: float,
        side: Side,
        address: str
    ) -> Optional[Dict]:
        """创建订单 - 简化版（需要私钥签名）"""
        st.warning("⚠️ 下单功能需要完整的钱包签名实现\n请参考 Polymarket 官方文档")
        return None


# ============ 工具函数 ============

def format_price(price: float) -> str:
    """格式化价格"""
    return f"${price:.4f}"

def format_size(size: float) -> str:
    """格式化数量"""
    if size >= 1000:
        return f"{size/1000:.1f}K"
    return f"{size:.0f}"

def get_price_color(price: float, prev_price: float = None) -> str:
    """获取价格颜色"""
    if prev_price is None:
        return "white"
    if price > prev_price:
        return "green"
    elif price < prev_price:
        return "red"
    return "white"
