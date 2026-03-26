"""Shared configuration for the stat-arb notebook pipeline."""

from math import ceil
from pathlib import Path

import pandas as pd

PAIR_Y = "CVX"
PAIR_X = "XOM"

START_DATE = "2025-06-26"
END_DATE = "2026-03-26"

BAR_INTERVAL = "5d"
ROLLING_WINDOW = 10

ENTRY_Z = 2.0
EXIT_Z = 0.5

TRADING_HOURS_PER_DAY = 6.5
WALK_FORWARD_WINDOW_TYPE = "rolling"
VALID_WALK_FORWARD_WINDOW_TYPES = ("expanding", "rolling")

VALID_INTERVALS = (
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "60m",
    "90m",
    "1h",
    "4h",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo",
)

INTRADAY_INTERVAL_MINUTES = {
    "1m": 1,
    "2m": 2,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "60m": 60,
    "90m": 90,
    "1h": 60,
    "4h": 240,
}

HIGHER_INTERVALS_PERIODS_PER_YEAR = {
    "1d": 252,
    "5d": 252 / 5,
    "1wk": 52,
    "1mo": 12,
    "3mo": 4,
}

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_RAW_PATH = PROJECT_ROOT.parent / "data" / "raw"
DATA_PATH = PROJECT_ROOT.parent / "data" / "processed"
RESULTS_FIGURES_PATH = PROJECT_ROOT.parent / "results" / "figures"
RESULTS_TABLES_PATH = PROJECT_ROOT.parent / "results" / "tables"

PROJECT_DIRS = [
    DATA_RAW_PATH,
    DATA_PATH,
    RESULTS_FIGURES_PATH,
    RESULTS_TABLES_PATH,
]

SLEEVES = {
    "selected_pair": [PAIR_Y, PAIR_X],
}

UNIVERSE = [ticker for sleeve_tickers in SLEEVES.values() for ticker in sleeve_tickers]
assert len(UNIVERSE) == len(set(UNIVERSE))


def interval_to_minutes(interval: str) -> int | None:
    """Return bar size in minutes for intraday intervals, else None."""
    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"Unsupported interval: {interval}. Valid intervals: {list(VALID_INTERVALS)}"
        )
    return INTRADAY_INTERVAL_MINUTES.get(interval)


def interval_to_bars_per_trading_day(
    interval: str, trading_hours_per_day: float = TRADING_HOURS_PER_DAY
) -> int | None:
    minutes = interval_to_minutes(interval)
    if minutes is None:
        return None
    return max(1, ceil((trading_hours_per_day * 60) / minutes))


def interval_to_periods_per_year(
    interval: str, trading_hours_per_day: float = TRADING_HOURS_PER_DAY
) -> float:
    bars_per_trading_day = interval_to_bars_per_trading_day(
        interval, trading_hours_per_day
    )
    if bars_per_trading_day is not None:
        return 252 * bars_per_trading_day
    return HIGHER_INTERVALS_PERIODS_PER_YEAR[interval]


def ensure_project_dirs() -> None:
    for path in PROJECT_DIRS:
        path.mkdir(parents=True, exist_ok=True)


BAR_INTERVAL_MINUTES = interval_to_minutes(BAR_INTERVAL)
WARMUP_BARS = 2 * ROLLING_WINDOW
BARS_PER_TRADING_DAY = interval_to_bars_per_trading_day(
    BAR_INTERVAL, TRADING_HOURS_PER_DAY
)
PERIODS_PER_YEAR = interval_to_periods_per_year(BAR_INTERVAL, TRADING_HOURS_PER_DAY)
WALK_FORWARD_INITIAL_TRAIN_BARS = max(2 * ROLLING_WINDOW, 80)
KALMAN_ALPHA_STATE_VAR = 1e-8
KALMAN_BETA_STATE_VAR = 4*1e-7
KALMAN_INIT_STATE_VAR = 1e-4
KALMAN_OBS_VAR_START = 1e-6


def make_position(zscore, entry=ENTRY_Z, exit=EXIT_Z):
    """Generate long/short/flat signal from a z-score series."""
    position = []
    current = 0
    for z in zscore:
        if pd.isna(z):
            position.append(current)
            continue
        if current == 1 and z >= -exit:
            current = 0
        elif current == -1 and z <= exit:
            current = 0
        if current == 0:
            if z < -entry:
                current = 1
            elif z > entry:
                current = -1
        position.append(current)
    return pd.Series(position, index=zscore.index)


def get_trade_stats(df, fee_bps=5):
    """Return round-trip trade statistics from a DataFrame with 'spread' and 'signal' columns."""
    fee = fee_bps / 10000
    df = df.copy()
    df["spread_return"] = df["spread"].diff()
    df["gross_ret"] = df["signal"].shift(1) * df["spread_return"]
    df["trade_trigger"] = df["signal"].diff().fillna(0).abs()
    total_fees = df["trade_trigger"].sum() * fee
    n_trades = int(df["trade_trigger"].sum() / 2)
    gross_pnl = df["gross_ret"].sum()
    net_pnl = gross_pnl - total_fees
    avg_ret = (gross_pnl / n_trades) if n_trades > 0 else 0
    return {
        "Total Trades": n_trades,
        "Gross PnL": round(gross_pnl, 5),
        "Net PnL": round(net_pnl, 5),
        "Avg Profit/Trade (Gross)": round(avg_ret, 5),
        "Fee (Round-trip)": fee * 2,
    }


__all__ = [
    "PAIR_Y",
    "PAIR_X",
    "PROJECT_ROOT",
    "DATA_RAW_PATH",
    "DATA_PATH",
    "RESULTS_FIGURES_PATH",
    "RESULTS_TABLES_PATH",
    "PROJECT_DIRS",
    "START_DATE",
    "END_DATE",
    "BAR_INTERVAL",
    "BAR_INTERVAL_MINUTES",
    "ROLLING_WINDOW",
    "ENTRY_Z",
    "EXIT_Z",
    "WALK_FORWARD_WINDOW_TYPE",
    "VALID_WALK_FORWARD_WINDOW_TYPES",
    "WARMUP_BARS",
    "TRADING_HOURS_PER_DAY",
    "VALID_INTERVALS",
    "INTRADAY_INTERVAL_MINUTES",
    "HIGHER_INTERVALS_PERIODS_PER_YEAR",
    "BARS_PER_TRADING_DAY",
    "PERIODS_PER_YEAR",
    "WALK_FORWARD_INITIAL_TRAIN_BARS",
    "KALMAN_ALPHA_STATE_VAR",
    "KALMAN_BETA_STATE_VAR",
    "KALMAN_INIT_STATE_VAR",
    "KALMAN_OBS_VAR_START",
    "SLEEVES",
    "UNIVERSE",
    "interval_to_minutes",
    "interval_to_bars_per_trading_day",
    "interval_to_periods_per_year",
    "ensure_project_dirs",
    "make_position",
    "get_trade_stats",
]
