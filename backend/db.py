"""
Database Helper Functions
Simple SQLite utilities for querying stock data.
"""
import sqlite3
import pandas as pd
from typing import Optional, List, Dict
import os

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Database path relative to backend folder
DB_PATH = os.path.join(BASE_DIR, "data", "stocks.db")

def get_db_connection():
    """Get SQLite connection."""
    return sqlite3.connect(DB_PATH)

def query_df(query: str, params: tuple = ()) -> pd.DataFrame:
    """
    Execute SQL query and return as DataFrame.
    
    Args:
        query: SQL query string
        params: Query parameters tuple
    
    Returns:
        DataFrame with query results
    """
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params, parse_dates=['date'])
        return df
    finally:
        conn.close()

def get_all_symbols() -> List[str]:
    """Get list of all unique symbols in database."""
    query = "SELECT DISTINCT symbol FROM stock_data ORDER BY symbol"
    df = query_df(query)
    return df['symbol'].unique().tolist() if not df.empty else []

def get_symbol_data(symbol: str, limit: Optional[int] = None) -> pd.DataFrame:
    """
    Get stock data for a symbol.
    
    Args:
        symbol: Stock symbol
        limit: Optional limit on number of rows
    
    Returns:
        DataFrame with stock data
    """
    symbol = symbol.upper()
    query = "SELECT * FROM stock_data WHERE symbol = ? ORDER BY date DESC"
    if limit:
        query += f" LIMIT {limit}"
    df = query_df(query, (symbol,))
    return df.sort_values('date') if not df.empty else pd.DataFrame()

def get_symbol_summary(symbol: str) -> Dict:
    """
    Get 52-week summary for a symbol.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Dictionary with 52w_high, 52w_low, avg_close
    """
    df = get_symbol_data(symbol)
    if df.empty:
        return {}
    
    # Use last 252 rows (approximate trading days in a year)
    last_year = df.tail(252)
    
    return {
        "52w_high": float(last_year['high'].max()),
        "52w_low": float(last_year['low'].min()),
        "avg_close": float(last_year['close'].mean())
    }

def check_db_exists() -> bool:
    """Check if database file exists."""
    return os.path.exists(DB_PATH)

