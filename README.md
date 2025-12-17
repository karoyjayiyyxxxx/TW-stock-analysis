# 📈 TW Stock Analysis (台股 AI 智能分析雷達)

這是一個基於 Python 的台股自動化分析工具，結合了 **MACD**、**布林通道 (Bollinger Bands)** 與 **SAR (拋物線指標)**，能協助投資人快速掃描市場熱門股，並提供精確的進出場訊號建議。

## ✨ 主要功能

* **📊 大盤即時診斷**：自動抓取加權指數 (^TWII)，判斷目前市場是多頭還是空頭。
* **🤖 AI 自動選股雷達**：
    * 自動掃描當日「成交值前 20 名」的熱門股。
    * 篩選出符合 **「股價 > SAR」 + 「站上月線」 + 「MACD 黃金交叉」** 的強勢買點股票。
* **📉 互動式技術圖表**：
    * 使用 Plotly 繪製 K 線圖。
    * 直接在圖表上標示 **SAR 止損點**、**壓力/支撐位**。
    * 提供明確的文字操作建議 (買進/觀望/止損點位)。
* **🔄 無限查詢模式**：查完一檔可立即輸入下一檔，支援連續操作。

## 🛠️ 安裝與使用

### 1. 安裝必要套件
請確保已安裝 Python 3.8+，並執行以下指令安裝套件：

```bash
pip install -r requirements.txt

```

### 2. 執行程式

```bash
python main.py

```

## 🚀 使用截圖

<img width="1012" height="630" alt="image" src="https://github.com/user-attachments/assets/bfc152ab-4735-4a20-a4e0-7edc5d6d026f" />
<img width="1012" height="626" alt="image" src="https://github.com/user-attachments/assets/49f1afb0-f0cc-4e3b-9088-442edd32686a" />
<img width="1702" height="856" alt="image" src="https://github.com/user-attachments/assets/c4c374e8-b924-4b2f-8403-1f48234c7166" />



## ⚠️ 免責聲明

本工具僅供技術分析研究與程式交易學習使用，不代表任何投資建議。股市投資有風險，請使用者自行判斷並承擔風險。
---
