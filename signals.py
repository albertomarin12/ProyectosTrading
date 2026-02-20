import pandas as pd
import ta

def generate_signals(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    df = data.copy()
    
    # 1. Indicators Calculation
    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(df.Close, window=params['rsi_window']).rsi()
    
    # Moving Average (Trend)
    df["ma"] = ta.trend.SMAIndicator(df.Close, window=params['ma_window']).sma_indicator()
    
    # MACD
    macd = ta.trend.MACD(df.Close)
    df["macd_diff"] = macd.macd_diff() # Histogram

    df = df.dropna()

    # 2. Individual Signals
    # RSI: Bullish if oversold, Bearish if overbought
    df["sig_rsi"] = 0
    df.loc[df["rsi"] < params['rsi_lower'], "sig_rsi"] = 1
    df.loc[df["rsi"] > params['rsi_upper'], "sig_rsi"] = -1

    # MA: Bullish if price above MA, Bearish if below
    df["sig_ma"] = 0
    df.loc[df.Close > df.ma, "sig_ma"] = 1
    df.loc[df.Close < df.ma, "sig_ma"] = -1

    # MACD: Bullish if histogram > 0, Bearish if < 0
    df["sig_macd"] = 0
    df.loc[df.macd_diff > 0, "sig_macd"] = 1
    df.loc[df.macd_diff < 0, "sig_macd"] = -1

    # 3. Consensus (2 out of 3)
    df["sum_signals"] = df["sig_rsi"] + df["sig_ma"] + df["sig_macd"]
    
    df["signal"] = 0
    df.loc[df["sum_signals"] >= 2, "signal"] = 1  # Long
    df.loc[df["sum_signals"] <= -2, "signal"] = -1 # Short

    return df