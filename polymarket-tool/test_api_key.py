"""
Polymarket API Key 测试脚本
"""
import requests
import json

API_KEY = "019c3d3c-80a9-725f-96bd-2e29348b07f6"
BASE_URL = "https://clob.polymarket.com"

def test_with_auth():
    """测试带认证的 API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    # 1. 测试市场列表
    print("1. 测试市场列表...")
    resp = requests.get(f"{BASE_URL}/markets", headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        markets = data.get("data", [])
        print(f"   找到 {len(markets)} 个市场")
        
        # 找第一个 accepting_orders 的市场
        for m in markets:
            if m.get("accepting_orders"):
                print(f"\n2. 测试市场: {m.get('question')[:50]}...")
                tokens = m.get("tokens", [])
                if tokens:
                    token_id = tokens[0].get("token_id")
                    print(f"   Token: {token_id[:40]}...")
                    
                    # 3. 测试订单簿
                    print("\n3. 测试订单簿...")
                    book_url = f"{BASE_URL}/book/{token_id}"
                    book_resp = requests.get(book_url, headers=headers, timeout=5)
                    print(f"   Status: {book_resp.status_code}")
                    
                    if book_resp.status_code == 200:
                        book_data = book_resp.json()
                        print(f"   ✅ Bids: {len(book_data.get('bids', []))}")
                        print(f"   ✅ Asks: {len(book_data.get('asks', []))}")
                        return True
                    else:
                        print(f"   ❌ {book_resp.text[:100]}")
    
    return False

def test_order_api():
    """测试下单 API"""
    print("\n4. 测试下单 API...")
    
    # 这需要完整的签名实现
    # 参考: https://docs.polymarket.com
    
    print("   下单需要:")
    print("   - Poly-Address header")
    print("   - Poly-Signature header (EIP-712 签名)")
    print("   - 私钥签名订单数据")

if __name__ == "__main__":
    print("=" * 50)
    print("Polymarket API Key 测试")
    print("=" * 50)
    
    success = test_with_auth()
    
    if not success:
        test_order_api()
    
    print("\n" + "=" * 50)
    print("测试完成")
