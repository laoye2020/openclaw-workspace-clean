"""
使用 py-clob-client 测试
需要：私钥 + API Key
"""
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

# 配置
API_KEY = "019c3d3c-80a9-725f-96bd-2e29348b07f6"
API_SECRET = ""  # 需要 Secret
API_PASSPHRASE = ""  # 需要 Passphrase

# 你的钱包私钥（用于签名）
PRIVATE_KEY = ""  # 需要填写

def main():
    if not PRIVATE_KEY:
        print("❌ 需要提供钱包私钥才能测试完整功能")
        print("\n需要的信息：")
        print("1. 钱包私钥（用于签名）")
        print("2. API Secret")
        print("3. API Passphrase")
        return
    
    # 创建客户端
    creds = ApiCreds(API_KEY, API_SECRET, API_PASSPHRASE)
    client = ClobClient(
        host="https://clob.polymarket.com",
        key=PRIVATE_KEY,
        creds=creds
    )
    
    # 获取市场
    markets = client.get_markets()
    print(f"找到 {len(markets)} 个市场")
    
    # 获取订单簿
    if markets:
        token_id = markets[0].get("tokens", [{}])[0].get("token_id")
        orderbook = client.get_order_book(token_id)
        print(f"订单簿: {orderbook}")

if __name__ == "__main__":
    main()
