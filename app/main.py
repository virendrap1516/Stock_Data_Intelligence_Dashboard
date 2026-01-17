from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from .services.data import (
    list_companies,
    get_last_n_days,
    get_summary_52w,
    compare_symbols,
)


app = FastAPI(title="Stock Data Intelligence Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Company(BaseModel):
    symbol: str
    yf_symbol: str
    name: str


@app.get("/", tags=["meta"]) 
def root():
    return {"message": "Stock Data Intelligence Dashboard API", "docs": "/docs"}


@app.get("/companies", response_model=List[Company], tags=["companies"]) 
def companies() -> List[Company]:
    return [Company(**c) for c in list_companies()]


@app.get("/data/{symbol}", tags=["data"]) 
def data_last_30(symbol: str):
    try:
        return get_last_n_days(symbol.upper(), days=30)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/summary/{symbol}", tags=["data"]) 
def summary_52w(symbol: str):
    try:
        return get_summary_52w(symbol.upper())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/compare", tags=["compare"]) 
def compare(symbol1: str, symbol2: str, days: int = 30):
    try:
        return compare_symbols(symbol1.upper(), symbol2.upper(), days=days)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)



