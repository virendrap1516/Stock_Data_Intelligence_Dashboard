"""
FastAPI Application - Stock Data Intelligence API
Provides REST endpoints for stock data queries.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import db
from datetime import datetime, timedelta

app = FastAPI(
    title="Stock Data Intelligence API",
    version="1.0",
    description="REST API for stock market data with metrics and analytics"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class CompanyResponse(BaseModel):
    companies: List[str]

class StockDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    daily_return: float
    ma_7: float
    volatility: float
    symbol: str

class StockDataResponse(BaseModel):
    symbol: str
    data: List[dict]

class SummaryResponse(BaseModel):
    symbol: str
    high_52w: float
    low_52w: float
    avg_close: float

class CompareResponse(BaseModel):
    symbol1: str
    symbol2: str
    data: List[dict]

@app.get("/", tags=["meta"])
def root():
    """Root endpoint with API information."""
    return {
        "message": "Stock Data Intelligence API",
        "version": "1.0",
        "docs": "/docs",
        "endpoints": {
            "/companies": "GET - List all available companies",
            "/data/{symbol}": "GET - Get last 30 days of stock data",
            "/summary/{symbol}": "GET - Get 52-week summary",
            "/compare": "GET - Compare two stocks"
        }
    }

@app.get("/companies", response_model=CompanyResponse, tags=["companies"])
def companies():
    """
    Get list of all available companies.
    
    Returns:
        List of stock symbols
    """
    if not db.check_db_exists():
        raise HTTPException(
            status_code=503,
            detail="Database not initialized. Run data_prep.py first."
        )
    
    symbols = db.get_all_symbols()
    if not symbols:
        raise HTTPException(
            status_code=404,
            detail="No companies found. Run data_prep.py to fetch data."
        )
    
    return {"companies": symbols}

@app.get("/data/{symbol}", response_model=StockDataResponse, tags=["data"])
def get_last_30(symbol: str):
    """
    Get last 30 days of stock data for a symbol.
    
    Args:
        symbol: Stock symbol (e.g., INFY.NS)
    
    Returns:
        Stock data with all metrics for last 30 days
    """
    symbol = symbol.upper()
    
    if not db.check_db_exists():
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    df = db.get_symbol_data(symbol, limit=60)
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    # Get last 30 days
    df_recent = df.tail(30)
    
    # Convert to dict format
    rows = []
    for _, row in df_recent.iterrows():
        rows.append({
            "date": row['date'].strftime('%Y-%m-%d'),
            "open": float(row['open']),
            "high": float(row['high']),
            "low": float(row['low']),
            "close": float(row['close']),
            "volume": float(row['volume']),
            "daily_return": float(row['daily_return']) if pd.notna(row['daily_return']) else 0.0,
            "ma_7": float(row['ma_7']) if pd.notna(row['ma_7']) else float(row['close']),
            "volatility": float(row['volatility']) if pd.notna(row['volatility']) else 0.0,
            "symbol": row['symbol']
        })
    
    return {"symbol": symbol, "data": rows}

@app.get("/summary/{symbol}", response_model=SummaryResponse, tags=["data"])
def summary(symbol: str):
    """
    Get 52-week summary (high, low, average close) for a symbol.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        52-week high, low, and average close price
    """
    symbol = symbol.upper()
    
    if not db.check_db_exists():
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    summary_data = db.get_symbol_summary(symbol)
    
    if not summary_data:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    return {
        "symbol": symbol,
        "high_52w": summary_data["52w_high"],
        "low_52w": summary_data["52w_low"],
        "avg_close": summary_data["avg_close"]
    }

@app.get("/compare", response_model=CompareResponse, tags=["compare"])
def compare(
    symbol1: str = Query(..., description="First stock symbol"),
    symbol2: str = Query(..., description="Second stock symbol"),
    days: int = Query(30, ge=1, le=90, description="Number of days to compare")
):
    """
    Compare two stocks' performance.
    """
    s1 = symbol1.upper()
    s2 = symbol2.upper()
    
    if not db.check_db_exists():
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    # Get data for both symbols with a larger limit to ensure we have enough data points
    df1 = db.get_symbol_data(s1, limit=days * 2)
    df2 = db.get_symbol_data(s2, limit=days * 2)
    
    if df1.empty or df2.empty:
        missing = []
        if df1.empty:
            missing.append(s1)
        if df2.empty:
            missing.append(s2)
        raise HTTPException(
            status_code=404,
            detail=f"No data found for: {', '.join(missing)}"
        )
    
    # Convert date strings to datetime objects for proper comparison
    df1['date'] = pd.to_datetime(df1['date'])
    df2['date'] = pd.to_datetime(df2['date'])
    
    # Get the most recent date common to both datasets
    latest_common_date = min(df1['date'].max(), df2['date'].max())
    
    # Filter data to the last 'days' days from the latest common date
    start_date = latest_common_date - timedelta(days=days)
    
    df1 = df1[df1['date'] >= start_date].sort_values('date')
    df2 = df2[df2['date'] >= start_date].sort_values('date')
    
    if df1.empty or df2.empty:
        raise HTTPException(
            status_code=400,
            detail="Not enough data points for comparison in the selected date range"
        )
    
    # Normalize the close prices for comparison (start at 100)
    df1['normalized'] = (df1['close'] / df1['close'].iloc[0]) * 100
    df2['normalized'] = (df2['close'] / df2['close'].iloc[0]) * 100
    
    # Prepare the response
    result = {
        "symbol1": s1,
        "symbol2": s2,
        "days": days,
        "data": []
    }
    
    # Combine the data
    for idx in range(min(len(df1), len(df2))):
        date_str = df1['date'].iloc[idx].strftime('%Y-%m-%d')
        result["data"].append({
            "date": date_str,
            f"{s1}_normalized": round(df1['normalized'].iloc[idx], 2),
            f"{s2}_normalized": round(df2['normalized'].iloc[idx], 2)
        })
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

