import numpy as np
from scipy.stats import norm
import pandas as pd
from datetime import datetime

##############################################################################
# Black-Scholes Greeks Calculations
##############################################################################
def d1(S, K, T, r, sigma):
    """
    Calculate the d1 term in the Black-Scholes model.
    """
    return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

def d2(S, K, T, r, sigma):
    """
    Calculate the d2 term in the Black-Scholes model.
    """
    return d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

def bs_call_delta(S, K, T, r, sigma):
    """
    Calculate the Delta of a call option using Black-Scholes.
    """
    return norm.cdf(d1(S, K, T, r, sigma))

def bs_call_gamma(S, K, T, r, sigma):
    """
    Calculate the Gamma of a call option using Black-Scholes.
    """
    return norm.pdf(d1(S, K, T, r, sigma)) / (S * sigma * np.sqrt(T))

def bs_call_theta(S, K, T, r, sigma):
    """
    Calculate the Theta of a call option using Black-Scholes.
    """
    d1_ = d1(S, K, T, r, sigma)
    d2_ = d2(S, K, T, r, sigma)
    term1 = - (S * norm.pdf(d1_) * sigma) / (2 * np.sqrt(T))
    term2 = - r * K * np.exp(-r * T) * norm.cdf(d2_)
    return term1 + term2

def bs_call_vega(S, K, T, r, sigma):
    """
    Calculate the Vega of a call option using Black-Scholes.
    """
    return S * np.sqrt(T) * norm.pdf(d1(S, K, T, r, sigma))


def calculate_bull_call_spreads(
    calls_df: pd.DataFrame,
    current_price: float,
    T: float,
    r: float,
    max_strike_diff: float,
    min_cost_debit: float,
    max_short_strike: float
) -> pd.DataFrame:
    """
    Given a DataFrame of call options with columns:
      [strike, bid, ask, impliedVolatility, delta, gamma, theta, vega]
    and other parameters, calculate potential bull call spreads. Return
    a DataFrame of all possible spreads.

    :param calls_df: Filtered call options DataFrame
    :param current_price: float
    :param T: time to expiration in years
    :param r: risk-free rate
    :param max_strike_diff: Maximum allowable strike difference
    :param min_cost_debit: Minimum net debit cost
    :param max_short_strike: Maximum short strike price
    :return: DataFrame of bull call spreads
    """
    if calls_df.empty:
        return pd.DataFrame()

    # Sort the strikes
    strikes = sorted(calls_df["strike"].unique())
    all_spreads = []

    # Generate pairs for bull call spreads
    for i in range(len(strikes) - 1):
        for j in range(i + 1, len(strikes)):
            K1 = strikes[i]
            K2 = strikes[j]

            # Apply the max_short_strike constraint
            if max_short_strike > 0 and K2 > max_short_strike:
                continue

            # Skip spreads that exceed allowed strike diff
            if (K2 - K1) > max_strike_diff:
                break

            # Get rows
            long_candidates  = calls_df[calls_df["strike"] == K1]
            short_candidates = calls_df[calls_df["strike"] == K2]
            if long_candidates.empty or short_candidates.empty:
                continue

            long_call  = long_candidates.iloc[0]
            short_call = short_candidates.iloc[0]

            # Midpoint cost approach
            cost_long  = (long_call["ask"] + long_call["bid"]) / 2
            cost_short = (short_call["ask"] + short_call["bid"]) / 2
            cost_debit = long_call["ask"] - short_call["bid"]

            if cost_debit < min_cost_debit:
                continue

            if cost_debit <= 0:
                continue

            max_profit = (K2 - K1) - cost_debit
            max_loss   = cost_debit
            if max_loss <= 0 or max_profit <= 0:
                continue

            risk_reward = max_profit / max_loss

            spread_data = {
                "long_strike":    float(K1),
                "short_strike":   float(K2),
                "cost_long":      round(cost_long, 2),
                "cost_short":     round(cost_short, 2),
                "cost_debit":     round(cost_debit, 2),
                "max_profit":     round(max_profit, 2),
                "max_loss":       round(max_loss, 2),
                "risk_reward":    round(risk_reward, 2),
                "long_IV":        round(long_call["impliedVolatility"], 4),
                "short_IV":       round(short_call["impliedVolatility"], 4),
                "spread_delta":   round(long_call["delta"] - short_call["delta"], 4),
                "spread_gamma":   round(long_call["gamma"] - short_call["gamma"], 6),
                "spread_theta":   round(long_call["theta"] - short_call["theta"], 6),
                "spread_vega":    round(long_call["vega"]  - short_call["vega"], 6),
                "expiration":     long_call.get("expiration", "N/A"),  # filled later if needed
            }
            all_spreads.append(spread_data)

    return pd.DataFrame(all_spreads)