import yfinance as yf
import pandas as pd
from typing import List, Tuple

class IDataProvider:
    """
    Abstract interface for a data provider. 
    Implementations can use yfinance, Robinhood API, etc.
    """
    def get_current_price(self, ticker: str) -> float:
        raise NotImplementedError
    
    def get_expirations(self, ticker: str) -> List[str]:
        raise NotImplementedError

    def get_option_chain(self, ticker: str, expiry: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        raise NotImplementedError

    def get_stock_info(self, ticker: str) -> dict:
        raise NotImplementedError


class YFinanceDataProvider(IDataProvider):
    """
    A yfinance-based implementation of IDataProvider.
    """
    def get_current_price(self, ticker: str) -> float:
        yf_ticker = yf.Ticker(ticker)
        price_series = yf_ticker.history(period="1d")["Close"]
        if price_series.empty:
            raise ValueError(f"No recent price data found for ticker={ticker}.")
        return float(price_series.iloc[-1])

    def get_expirations(self, ticker: str) -> List[str]:
        yf_ticker = yf.Ticker(ticker)
        try:
            return yf_ticker.options
        except Exception as exc:
            raise ValueError(f"Failed to retrieve options chain for {ticker}: {exc}")

    def get_option_chain(self, ticker: str, expiry: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Return (calls, puts) data for the given ticker + expiry.
        """
        yf_ticker = yf.Ticker(ticker)
        try:
            opt_chain = yf_ticker.option_chain(expiry)
        except Exception as exc:
            raise ValueError(f"Could not retrieve option chain for {ticker}, {expiry}: {exc}")

        return opt_chain.calls.copy(), opt_chain.puts.copy()

    def get_stock_info(self, ticker: str) -> dict:
        """
        Return general stock info. 
        Using .fast_info or .info depending on yfinance version.
        """
        yf_ticker = yf.Ticker(ticker)
        # Some versions of yfinance prefer "fast_info"; others may still use "info".
        # We'll try "info" first, but note that it can be partially deprecated.
        # Adjust as needed for your yfinance version.
        try:
            return yf_ticker.info
        except:
            # Fallback or alternative usage
            return dict()