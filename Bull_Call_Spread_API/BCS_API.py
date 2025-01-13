"""
File: bull_call_spreads_api.py

Description:
------------
A FastAPI application that calculates bull call spreads for a given ticker,
using a pluggable data provider (default = yfinance). 
It also provides a diagnostics endpoint to retrieve basic ticker info.
"""

import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import custom modules
from data_providers import YFinanceDataProvider
from calculations import (
    bs_call_delta,
    bs_call_gamma,
    bs_call_theta,
    bs_call_vega,
    calculate_bull_call_spreads,
)

##############################################################################
# Create FastAPI app
##############################################################################
app = FastAPI(
    title="Bull Call Spreads API",
    description=(
        "This API computes potential bull call spreads for a given ticker using "
        "Black-Scholes Greeks. It also provides a /diagnostics endpoint for basic info."
    ),
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:3000"],  # Adjust origins as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Instantiate your data provider (could swap later with RobinhoodDataProvider, etc.)
data_provider = YFinanceDataProvider()

##############################################################################
# Diagnostics Endpoint
##############################################################################
@app.get("/diagnostics")
def get_diagnostics(ticker: str = Query("NVDA", description="Stock ticker to retrieve diagnostics.")):
    """
    Returns basic diagnostics about the given stock (e.g. info from data provider).
    """
    try:
        info = data_provider.get_stock_info(ticker)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Failed to retrieve stock info: {exc}")
    
    return {"ticker": ticker, "info": info}

##############################################################################
# Bull Call Spreads Endpoint
##############################################################################
@app.get("/bull_call_spreads")
def get_bull_call_spreads(
    ticker: str = Query("NVDA", description="Stock ticker symbol, e.g. 'NVDA'."),
    risk_free_rate: float = Query(0.05, description="Annual risk-free interest rate."),
    max_expiries: int = Query(3, description="Max expiration cycles to analyze."),
    min_volume: int = Query(10, description="Minimum call option volume."),
    min_open_interest: int = Query(10, description="Minimum call option open interest."),
    results_limit: int = Query(10, description="Number of top spreads to display."),
    max_strike_diff: float = Query(20, description="Max allowable strike difference for spreads."),
    min_cost_debit: float = Query(2.0, description="Minimum cost debit for a valid spread."),
    max_short_strike: float = Query(142.5, description="Max short strike price (0 = no max).")
):
    """
    Retrieve potential bull call spreads for the specified ticker.
    """
    try:
        current_price = data_provider.get_current_price(ticker)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Failed to retrieve ticker data: {exc}")

    try:
        available_expirations = data_provider.get_expirations(ticker)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    expirations_to_check = available_expirations[:max_expiries]
    if not expirations_to_check:
        raise HTTPException(status_code=404, detail="No upcoming expirations found.")

    all_spreads_df = pd.DataFrame()

    for expiry in expirations_to_check:
        try:
            calls_df, _ = data_provider.get_option_chain(ticker, expiry)
        except Exception:
            continue

        calls_df = calls_df[
            (calls_df["volume"] >= min_volume) &
            (calls_df["openInterest"] >= min_open_interest)
        ].copy()

        if calls_df.empty:
            continue

        try:
            expiration_date = datetime.strptime(expiry, "%Y-%m-%d")
        except ValueError:
            continue

        days_to_expiry = (expiration_date - datetime.now()).days
        T = max(days_to_expiry / 365.0, 0.001)

        for idx, row in calls_df.iterrows():
            K = row["strike"]
            iv = row["impliedVolatility"]
            if (iv <= 0) or (iv > 2):
                continue

            try:
                delta = bs_call_delta(current_price, K, T, risk_free_rate, iv)
                gamma = bs_call_gamma(current_price, K, T, risk_free_rate, iv)
                theta = bs_call_theta(current_price, K, T, risk_free_rate, iv)
                vega  = bs_call_vega (current_price, K, T, risk_free_rate, iv)
            except:
                continue

            calls_df.loc[idx, "delta"] = delta
            calls_df.loc[idx, "gamma"] = gamma
            calls_df.loc[idx, "theta"] = theta
            calls_df.loc[idx, "vega"]  = vega
            calls_df.loc[idx, "expiration"] = expiry

        calls_df.dropna(subset=["delta", "gamma", "theta", "vega"], inplace=True)
        if calls_df.empty:
            continue

        spread_results = calculate_bull_call_spreads(
            calls_df=calls_df,
            current_price=current_price,
            T=T,
            r=risk_free_rate,
            max_strike_diff=max_strike_diff,
            min_cost_debit=min_cost_debit,
            max_short_strike=max_short_strike
        )

        if not spread_results.empty:
            all_spreads_df = pd.concat([all_spreads_df, spread_results], ignore_index=True)

    if all_spreads_df.empty:
        raise HTTPException(status_code=404, detail="No valid bull call spreads identified.")

    all_spreads_df.sort_values(by="risk_reward", ascending=False, inplace=True)
    top_spreads = all_spreads_df.head(results_limit)

    return top_spreads.to_dict(orient="records")