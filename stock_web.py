import streamlit as st
import yfinance as yf
import datetime
import plotly.graph_objects as go

st.title("📈 台股股價 K 線圖")

# 股票代號輸入（只允許數字）
raw_code = st.text_input("請輸入股票代號 (例如: 2330):").strip()
code = "".join(c for c in raw_code if c.isdigit())  # 只保留數字

# 選擇顯示模式
mode = st.radio("選擇顯示內容：", ["分時走勢 (今天/最近交易日)", "日線", "週線", "月線"])

if code:
    if len(code) != 4:
        st.error("⚠️ 請輸入正確的 4 位數股票代號，例如 2330")
    else:
        ticker = code + ".TW"
        stock = yf.Ticker(ticker)
        hist = None

        if mode == "分時走勢 (今天/最近交易日)":
            today = datetime.date.today()
            hist = stock.history(start=today, interval="5m")

            if hist.empty:
                # 如果今天沒資料，抓最近 5 天，取最後一個交易日
                hist = stock.history(period="5d", interval="5m")
                if not hist.empty:
                    last_day = hist.index[-1].date()
                    st.warning(f"⚠️ 今天休市，顯示最近交易日：{last_day}")
                    hist = hist[hist.index.date == last_day]

        elif mode == "日線":
            hist = stock.history(period="6mo", interval="1d")
        elif mode == "週線":
            hist = stock.history(period="2y", interval="1wk")
        elif mode == "月線":
            hist = stock.history(period="5y", interval="1mo")

        # 確認資料
        if hist is not None and not hist.empty:
            last_date = hist.index[-1].date()
            st.write(f"📅 顯示資料截至：{last_date}, 共 {len(hist)} 筆資料")

            # 建立 K 線圖 + 成交量
            fig = go.Figure()

            # K 線
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name="K線圖"
            ))

            # 成交量
            fig.add_trace(go.Bar(
                x=hist.index,
                y=hist["Volume"],
                name="成交量",
                marker_color="lightblue",
                yaxis="y2"
            ))

            # 設定雙 y 軸
            fig.update_layout(
                xaxis=dict(domain=[0, 1]),
                yaxis=dict(title="股價 (NTD)", side="right", position=1),
                yaxis2=dict(title="成交量", overlaying="y", side="left", showgrid=False),
                xaxis_rangeslider_visible=False,
                template="plotly_white",
                height=700
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("⚠️ 找不到股價資料，可能是 Yahoo Finance 資料延遲。")
