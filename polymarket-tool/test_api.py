#!/usr/bin/env python3
"""
Polymarket API 测试脚本
验证 API 连接和数据格式
"""
import sys
sys.path.insert(0, '/home/laoye/.openclaw/workspace/polymarket-tool')

from api_client import PolymarketClient

client = PolymarketClient()

print("🧪 测试 Polymarket API...")
print("=" * 50)

# 测试搜索
print("\n1️⃣ 搜索市场 (BTC)...")
try:
    markets = client.search_markets("BTC")
    if markets:
        print(f"✅ 找到 {len(markets)} 个市场")
        print(f"   第一个: {markets[0].name}")
        print(f"   Token: {markets[0].token_id}")
    else:
        print("⚠️ 未找到市场")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

# 测试订单簿
if markets:
    print("\n2️⃣ 获取订单簿...")
    try:
        orderbook = client.get_orderbook(markets[0].token_id)
        if orderbook:
            print(f"✅ 订单簿获取成功")
            print(f"   Bids: {len(orderbook.bids)} 条")
            print(f"   Asks: {len(orderbook.asks)} 条")
        else:
            print("⚠️ 无法获取订单簿")
    except Exception as e:
        print(f"❌ 错误: {e}")

print("\n" + "=" * 50)
print("✅ 测试完成")
