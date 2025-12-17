import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# ==========================================
# 🛠️ 核心運算：技術指標 (MACD, BOLL, SAR)
# ==========================================
def calculate_indicators(df):
    if df is None or df.empty or len(df) < 30: return None
    
    # 1. MACD
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # 2. 布林通道
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD20'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['MA20'] + (df['STD20'] * 2)
    df['Lower_Band'] = df['MA20'] - (df['STD20'] * 2)

    # 3. SAR (止損/轉折)
    high, low = df['High'], df['Low']
    sar = [low.iloc[0]] * len(df)
    trend = [1] * len(df) # 1=多, -1=空
    af = 0.02
    ep = high.iloc[0]
    
    for i in range(1, len(df)):
        sar[i] = sar[i-1] + af * (ep - sar[i-1])
        if trend[i-1] == 1:
            if low.iloc[i] < sar[i]:
                trend[i] = -1
                sar[i] = ep
                ep = low.iloc[i]
                af = 0.02
            else:
                trend[i] = 1
                if high.iloc[i] > ep:
                    ep = high.iloc[i]
                    af = min(af + 0.02, 0.2)
                sar[i] = min(sar[i], low.iloc[i-1], low.iloc[max(0, i-2)])
        else:
            if high.iloc[i] > sar[i]:
                trend[i] = 1
                sar[i] = ep
                ep = high.iloc[i]
                af = 0.02
            else:
                trend[i] = -1
                if low.iloc[i] < ep:
                    ep = low.iloc[i]
                    af = min(af + 0.02, 0.2)
                sar[i] = max(sar[i], high.iloc[i-1], high.iloc[max(0, i-2)])
                
    df['SAR'] = sar
    return df

# ==========================================
# 📥 資料下載模組
# ==========================================
def get_stock_data(ticker_symbol):
    try:
        df = yf.download(ticker_symbol, period="6mo", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return calculate_indicators(df)
    except:
        return None

# ==========================================
# 🤖 AI 選股雷達 (自動掃描)
# ==========================================
def auto_scanner():
    print("\n🔍 正在掃描台股熱門榜，尋找「強勢買點」股票，請稍等...")
    
    # 1. 抓熱門榜
    url = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL'
    try:
        res = requests.get(url)
        df = pd.DataFrame(res.json())
        cols = ['TradeValue', 'ClosingPrice']
        for col in cols:
            df[col] = df[col].astype(str).str.replace(',', '').replace('', '0').astype(float)
        
        # 取成交值前 20 名
        top_list = df.sort_values(by='TradeValue', ascending=False).head(20)
        candidates = []

        print(f"   (分析中", end="")
        for index, row in top_list.iterrows():
            code = row['Code']
            name = row['Name']
            print(".", end="", flush=True) # 進度條
            
            stock_df = get_stock_data(f"{code}.TW")
            if stock_df is not None:
                curr = stock_df.iloc[-1]
                # === 🔥 買進選股條件 ===
                # 1. 股價 > SAR (多頭排列)
                # 2. 股價 > 月線 (趨勢向上)
                # 3. MACD 紅柱 (MACD > Signal)
                if curr['Close'] > curr['SAR'] and curr['Close'] > curr['MA20'] and curr['MACD'] > curr['Signal_Line']:
                    candidates.append({'Code': code, 'Name': name, 'Price': curr['Close']})
        
        print(" 完成!)")
        return candidates, top_list
    except Exception as e:
        print(f"掃描失敗: {e}")
        return [], None

# ==========================================
# 📊 畫圖與分析
# ==========================================
def plot_analysis(stock_code):
    df = get_stock_data(f"{stock_code}.TW")
    if df is None:
        print("❌ 找不到資料 (請確認代碼)")
        return

    curr = df.iloc[-1]
    is_bullish = curr['Close'] > curr['SAR']
    
    # 訊號文字
    status = "🔴 多頭強勢" if is_bullish else "🟢 空頭修正"
    action = "✅ 建議買進 / 續抱" if is_bullish else "⚠️ 建議觀望 / 等待突破"
    stop_loss = f"{curr['SAR']:.2f}"
    
    print(f"\n{'='*15} {stock_code} 分析結果 {'='*15}")
    print(f"現價: {curr['Close']:.2f}")
    print(f"趨勢: {status}")
    print(f"建議: {action}")
    print(f"關鍵點位 (SAR): {stop_loss} (跌破賣出/突破買進)")
    print("="*45)

    # 繪圖
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3],
                        subplot_titles=(f'{stock_code} 智能圖表 (止損: {stop_loss})', 'MACD 動能'))

    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                 low=df['Low'], close=df['Close'], name='K線'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SAR'], mode='markers', marker=dict(color='purple', size=4), name='SAR'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='orange'), name='月線'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Upper_Band'], line=dict(color='gray', dash='dot'), name='壓力'), row=1, col=1)
    
    colors = ['red' if v > 0 else 'green' for v in (df['MACD'] - df['Signal_Line'])]
    fig.add_trace(go.Bar(x=df.index, y=(df['MACD'] - df['Signal_Line']), marker_color=colors, name='MACD'), row=2, col=1)
    
    fig.update_layout(xaxis_rangeslider_visible=False, height=700, title=f"{stock_code} 進出場分析")
    fig.show()

# ==========================================
# 🚀 主程式 (無限循環)
# ==========================================
if __name__ == "__main__":
    # 1. 先抓大盤
    print("\n🌍 正在讀取大盤數據...")
    twii = get_stock_data("^TWII")
    if twii is not None:
        idx_now = twii.iloc[-1]['Close']
        idx_trend = "🔴 多頭 (安全)" if idx_now > twii.iloc[-1]['SAR'] else "🟢 空頭 (危險)"
        print(f"\n📊 加權指數目前數值: {idx_now:.2f}")
        print(f"   大盤趨勢判定: {idx_trend}")
        if "空頭" in idx_trend: print("   ⚠️ 提醒: 大盤不穩，建議減少持股，嚴格停損！")
    
    # 2. 自動選股 (只跑一次)
    good_stocks, _ = auto_scanner()
    
    print("\n🏆 【AI 嚴選：目前可考慮買進的強勢股】")
    if good_stocks:
        for stock in good_stocks:
            print(f"   👉 {stock['Code']} {stock['Name']} (現價: {stock['Price']:.2f})")
        print("   (篩選條件：股價站上SAR + 站上月線 + MACD黃金交叉)")
    else:
        print("   ⚠️ 目前熱門股中沒有完美符合強勢條件的股票，建議觀望。")

    # 3. 進入無限查詢模式
    while True:
        print("\n" + "-"*50)
        code = input("請輸入股票代碼查看圖表 (輸入 q 離開, r 重新掃描): ").strip()
        
        if code.lower() == 'q':
            print("👋 程式結束，祝操作順利！")
            break
        elif code.lower() == 'r':
            good_stocks, _ = auto_scanner()
            print("\n🏆 【AI 嚴選：目前可考慮買進的強勢股】")
            if good_stocks:
                for stock in good_stocks:
                    print(f"   👉 {stock['Code']} {stock['Name']} (現價: {stock['Price']:.2f})")
            continue
        elif not code:
            continue
            
        plot_analysis(code)