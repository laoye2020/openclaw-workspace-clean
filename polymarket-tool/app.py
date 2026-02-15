"""
Polymarket ⚡ 极速交易工具
Web Interface - Streamlit

⚡ 实时盘口 | 极速下单 | 智能预警
"""

import streamlit as st
import time
import pandas as pd
from datetime import datetime
from api_client import PolymarketClient, Side, format_price, format_size, get_price_color

# ============ 配置 ============
st.set_page_config(
    page_title="Polymarket ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .price-up {
        color: #00C853;
        font-weight: bold;
    }
    .price-down {
        color: #FF5252;
        font-weight: bold;
    }
    .orderbook-buy {
        background-color: rgba(0, 200, 83, 0.1);
    }
    .orderbook-sell {
        background-color: rgba(255, 82, 82, 0.1);
    }
    .metric-card {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d3138;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .buy-btn {
        background-color: #00C853 !important;
        color: white !important;
    }
    .sell-btn {
        background-color: #FF5252 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============ Session State ============
if 'client' not in st.session_state:
    st.session_state.client = PolymarketClient()
if 'selected_market' not in st.session_state:
    st.session_state.selected_market = None
if 'orderbook_data' not in st.session_state:
    st.session_state.orderbook_data = None
if 'positions' not in st.session_state:
    st.session_state.positions = []
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = ""
if 'refresh_rate' not in st.session_state:
    st.session_state.refresh_rate = 1.0

# ============ 侧边栏 - 钱包连接 ============
with st.sidebar:
    st.title("⚡ Polymarket")
    st.markdown("---")
    
    # 钱包连接
    st.subheader("💼 钱包")
    wallet_input = st.text_input(
        "钱包地址",
        value=st.session_state.wallet_address,
        placeholder="0x...",
        help="输入你的 Polygon 钱包地址"
    )
    if wallet_input != st.session_state.wallet_address:
        st.session_state.wallet_address = wallet_input
    
    # 私钥输入（仅本地使用）
    with st.expander("🔐 高级设置（可选）"):
        private_key = st.text_input(
            "私钥",
            type="password",
            help="用于签名订单，仅本地运行"
        )
        if private_key:
            st.session_state.client = PolymarketClient(private_key)
    
    st.markdown("---")
    
    # 刷新设置
    st.subheader("⚙️ 设置")
    refresh_rate = st.slider(
        "刷新频率 (秒)",
        min_value=0.5,
        max_value=5.0,
        value=st.session_state.refresh_rate,
        step=0.5
    )
    st.session_state.refresh_rate = refresh_rate
    
    # 快捷搜索
    st.markdown("---")
    st.subheader("⭐ 常用市场")
    quick_markets = [
        "btc-over-100k",
        "trump-2024-election",
        "fed-rate-cut-2024",
        "bitcoin-2024"
    ]
    for market_slug in quick_markets:
        if st.button(f"📌 {market_slug}", key=f"quick_{market_slug}"):
            st.session_state.selected_market_slug = market_slug

# ============ 主界面 ============
st.title("⚡ Polymarket 极速交易")

# 市场搜索
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input(
        "🔍 搜索市场",
        placeholder="输入市场名称: BTC/大选/美联储...",
        key="market_search"
    )
with col2:
    if st.button("🔄 刷新", type="primary"):
        st.rerun()

# 显示搜索结果或选中市场
if 'selected_market_slug' in st.session_state and not search_query:
    # 快捷市场
    with st.spinner("加载市场数据..."):
        market = st.session_state.client.get_market_by_slug(
            st.session_state.selected_market_slug
        )
        if market:
            st.session_state.selected_market = market
            del st.session_state.selected_market_slug

elif search_query and len(search_query) > 2:
    # 搜索市场
    with st.spinner("搜索中..."):
        markets = st.session_state.client.search_markets(search_query)
        
    if markets:
        market_options = {m.name: m for m in markets}
        selected = st.selectbox(
            "选择市场",
            options=list(market_options.keys()),
            key="market_select"
        )
        if selected:
            st.session_state.selected_market = market_options[selected]
    else:
        st.warning("未找到市场")

# ============ 交易界面 ============
if st.session_state.selected_market:
    market = st.session_state.selected_market
    
    # 标题行
    st.markdown(f"### 📊 {market.name}")
    
    # 三大指标
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <small>当前价格</small><br>
            <span style="font-size: 24px; font-weight: bold;">{format_price(market.current_price)}</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <small>24h 交易量</small><br>
            <span style="font-size: 24px;">${market.volume:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <small>流动性</small><br>
            <span style="font-size: 24px;">${market.liquidity:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        status = st.selectbox("操作模式", ["🔵 只读观察", "🟢 允许下单"])
    
    st.markdown("---")
    
    # 盘口区域
    col_orderbook, col_trade = st.columns([1.2, 1])
    
    with col_orderbook:
        st.subheader("📈 订单簿")
        
        # 显示 API 限制警告
        st.info("ℹ️ **API 限制**: 订单簿数据需要 Polymarket 认证\n实盘数据请使用官方网页版")
        
        # 实时获取订单簿
        orderbook = st.session_state.client.get_orderbook(market.token_id)
        
        if orderbook and (orderbook.bids or orderbook.asks):
            # 卖盘（上）
            st.markdown("**卖盘 (Asks)** 🔴")
            asks_df = pd.DataFrame(orderbook.asks)
            if not asks_df.empty:
                asks_df['size'] = asks_df['size'].apply(format_size)
                st.dataframe(
                    asks_df[['size', 'price']].style.applymap(
                        lambda x: 'color: #FF5252', subset=['price']
                    ),
                    hide_index=True,
                    height=150
                )
            
            # 买盘（下）
            st.markdown("**买盘 (Bids)** 🟢")
            bids_df = pd.DataFrame(orderbook.bids)
            if not bids_df.empty:
                bids_df['size'] = bids_df['size'].apply(format_size)
                st.dataframe(
                    bids_df[['price', 'size']].style.applymap(
                        lambda x: 'color: #00C853', subset=['price']
                    ),
                    hide_index=True,
                    height=150
                )
            
            # 价差
            if orderbook.asks and orderbook.bids:
                best_ask = float(orderbook.asks[0].get('price', 0))
                best_bid = float(orderbook.bids[0].get('price', 0))
                spread = best_ask - best_bid
                spread_pct = (spread / best_ask) * 100 if best_ask > 0 else 0
                st.caption(f"📊 价差: {format_price(spread)} ({spread_pct:.2f}%)")
        else:
            st.warning("📭 订单簿数据不可用\n\n可能原因：\n1. API 访问限制\n2. 市场暂无流动性\n3. 需要使用官方 SDK 认证")
            
            # 显示市场链接
            st.markdown(f"[🔗 在 Polymarket 官网查看](https://polymarket.com/market/{market.id})")
    
    with col_trade:
        st.subheader("🔢 下单")
        
        # 交易参数
        side_col1, side_col2 = st.columns(2)
        with side_col1:
            trade_side = st.radio("方向", ["买入", "卖出"], horizontal=True)
        with side_col2:
            order_type = st.selectbox("类型", ["限价单", "市价单"])
        
        # 价格和数量
        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input(
                "价格 ($)",
                min_value=0.01,
                max_value=0.99,
                value=market.current_price,
                step=0.01,
                format="%.2f"
            )
        with c2:
            size = st.number_input(
                "数量 (SHARES)",
                min_value=1,
                value=100,
                step=10
            )
        
        # 计算
        total_cost = price * size
        st.markdown(f"""
        <div class="metric-card">
            <small>预估成本</small><br>
            <span style="font-size: 20px; font-weight: bold;">${total_cost:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 下单按钮
        btn_class = "buy-btn" if trade_side == "买入" else "sell-btn"
        
        if st.button(
            f"{'🟢 买入' if trade_side == '买入' else '🔴 卖出'} {size} @ ${price:.2f}",
            type="primary",
            use_container_width=True
        ):
            if not st.session_state.wallet_address:
                st.error("❌ 请先输入钱包地址")
            elif not private_key and not st.session_state.client.private_key:
                st.error("❌ 需要配置私钥才能下单")
            else:
                with st.spinner("提交订单中..."):
                    side = Side.BUY if trade_side == "买入" else Side.SELL
                    result = st.session_state.client.create_order(
                        token_id=market.token_id,
                        price=price,
                        size=size,
                        side=side,
                        address=st.session_state.wallet_address
                    )
                    
                    if result:
                        st.success(f"✅ 订单已提交: {result.get('id', 'unknown')}")
                    else:
                        st.error("❌ 下单失败")
        
        # 市价单按钮
        if st.button("⚡ 市价全仓买入", use_container_width=True):
            st.info("市价单功能需要额外配置")

# ============ 持仓展示 ============
if st.session_state.wallet_address:
    st.markdown("---")
    st.subheader("💼 我的持仓")
    
    with st.spinner("加载持仓..."):
        positions = st.session_state.client.get_positions(st.session_state.wallet_address)
    
    if positions:
        positions_df = pd.DataFrame(positions)
        st.dataframe(positions_df, hide_index=True)
    else:
        st.info("暂无持仓")

# ============ 底部 ============
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>⚡ Polymarket 极速交易工具 | 数据来源: Polymarket CLOB API</div>",
    unsafe_allow_html=True
)

# ============ 自动刷新 ============
if st.session_state.selected_market:
    time.sleep(st.session_state.refresh_rate)
    st.rerun()
