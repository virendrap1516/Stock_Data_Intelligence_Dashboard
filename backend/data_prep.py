"""
Data Collection & Preparation Module
Fetches stock data using yfinance, cleans it, computes metrics, and saves to SQLite.
Includes fallback to generate sample data if yfinance fails.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import time
import random

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Database path relative to backend folder
DB_PATH = os.path.join(BASE_DIR, "data", "stocks.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def generate_sample_data(symbol: str, days: int = 500) -> pd.DataFrame:
    """
    Generate sample stock data if yfinance fails.
    Creates realistic-looking price data with trends.
    """
    print(f"⚠ Generating sample data for {symbol}...")
    
    # Base prices for different symbols (approximate)
    base_prices = {
        "INFY.NS": 1500,
        "TCS.NS": 3500,
        "RELIANCE.NS": 2500,
        "HDFCBANK.NS": 1700,
        "ICICIBANK.NS": 1000,
    }
    
    base_price = base_prices.get(symbol.upper(), 1500)
    
    # Generate dates (trading days only - weekdays)
    end_date = datetime.now()
    dates = []
    current_date = end_date - timedelta(days=days*2)  # Start earlier to get enough weekdays
    
    while len(dates) < days and current_date <= end_date:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            dates.append(current_date)
        current_date += timedelta(days=1)
    
    dates = dates[-days:]  # Take last N days
    
    # Generate price data with trend
    np.random.seed(hash(symbol) % 1000)  # Consistent seed per symbol
    prices = []
    current_price = base_price
    
    for i in range(days):
        # Add trend and volatility
        trend = np.sin(i / 50) * 50  # Cyclical trend
        volatility = np.random.normal(0, 20)  # Random volatility
        change = trend + volatility
        current_price = max(100, current_price + change)  # Don't go below 100
        prices.append(current_price)
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.uniform(-0.01, 0.01)) for p in prices],
        'high': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
        'low': [p * (1 - np.random.uniform(0, 0.02)) for p in prices],
        'close': prices,
        'volume': [int(np.random.uniform(1000000, 5000000)) for _ in range(days)]
    })
    
    # Ensure high >= low and high/low around open/close
    df['high'] = df[['open', 'high', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.01))
    df['low'] = df[['open', 'low', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.01))
    
    return df

def fetch_save(symbol: str, period: str = "2y", use_sample_if_fails: bool = True) -> None:
    """
    Fetch stock data, compute metrics, and save to SQLite.
    
    Args:
        symbol: Stock symbol (e.g., "INFY.NS" for NSE)
        period: Period to fetch (default "2y" for 2 years)
        use_sample_if_fails: If True, generate sample data if yfinance fails
    """
    # Try fetching with retries
    max_retries = 3
    df = None
    
    for attempt in range(max_retries):
        try:
            print(f"Fetching {symbol} (attempt {attempt + 1}/{max_retries})...")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, timeout=30)
            
            if df is not None and not df.empty:
                break
            else:
                print(f"  Empty response for {symbol}")
                
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                print(f"  Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"  All retries failed for {symbol}")
    
    # If yfinance failed, use sample data
    if df is None or df.empty:
        if use_sample_if_fails:
            print(f"⚠ yfinance failed for {symbol}, generating sample data...")
            days = 500 if period == "2y" else 365 if period == "1y" else 250
            df = generate_sample_data(symbol, days)
        else:
            raise ValueError(f"No data for {symbol} after {max_retries} attempts")
    
    df = df.reset_index()
    
    # Cleanup column names
    df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }, inplace=True)
    
    df['date'] = pd.to_datetime(df['date'])
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    # Compute metrics
    # Daily Return
    df['daily_return'] = (df['close'] - df['open']) / df['open']
    
    # 7-day Moving Average
    df['ma_7'] = df['close'].rolling(window=7, min_periods=1).mean()
    
    # 52-week high/low (using 252 trading days)
    window_days = 252
    df['52w_high'] = df['high'].rolling(window=window_days, min_periods=1).max()
    df['52w_low'] = df['low'].rolling(window=window_days, min_periods=1).min()
    
    # Fill missing numeric values with forward/backward fill
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')
    
    # Custom metric: Volatility Score (annualized)
    # Rolling std of daily returns * sqrt(252 trading days)
    df['volatility'] = df['daily_return'].rolling(window=30, min_periods=1).std() * (252 ** 0.5)
    
    # Add symbol column
    df['symbol'] = symbol.upper()
    
    # Save to SQLite
    conn = sqlite3.connect(DB_PATH)
    try:
        # Create table if not exists
        df.to_sql('stock_data', conn, if_exists='append', index=False)
        print(f"✓ Saved {len(df)} rows for {symbol}")
    except Exception as e:
        print(f"✗ Error saving {symbol}: {e}")
    finally:
        conn.close()

def clear_old_data(symbol: str = None) -> None:
    """Clear old data for a symbol or all symbols."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if symbol:
        cursor.execute("DELETE FROM stock_data WHERE symbol = ?", (symbol.upper(),))
        print(f"Cleared data for {symbol}")
    else:
        cursor.execute("DELETE FROM stock_data")
        print("Cleared all stock data")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Example: Fetch data for popular NSE stocks
    symbols = ["INFY.NS", "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
    
    print("Fetching stock data...")
    print("=" * 50)
    print("Note: If yfinance fails, sample data will be generated automatically.")
    print("=" * 50)
    
    success_count = 0
    for symbol in symbols:
        try:
            fetch_save(symbol, period="2y", use_sample_if_fails=True)
            success_count += 1
            time.sleep(1)  # Small delay between requests
        except Exception as e:
            print(f"✗ Error fetching {symbol}: {e}")
    
    print("=" * 50)
    print(f"Data preparation complete! {success_count}/{len(symbols)} symbols processed.")
    print(f"Database saved to: {DB_PATH}")

