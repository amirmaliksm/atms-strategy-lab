import json
import random
import threading
import time
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

from .database import ResearchDB
from .generator import StrategyGenerator


class AutonomousResearchEngine:
    def __init__(self, db_path: str = "atms_research.db", export_dir: str = "research_exports", spread_points: float = 0.20, slippage_points: float = 0.10, min_trades: int = 30):
        self.db = ResearchDB(db_path)
        self.generator = StrategyGenerator()
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self.status = "STOPPED"  # RUNNING | PAUSED | STOPPED
        self.duplicates_skipped = 0
        self.session_tested = 0
        self.last_message = "Idle"
        self.spread_points = float(spread_points)
        self.slippage_points = float(slippage_points)
        self.min_trades = int(min_trades)

    def _compute_signals(self, df: pd.DataFrame, g: dict) -> pd.Series:
        close = df["close"]
        high = df["high"]
        low = df["low"]

        ema_f = close.ewm(span=g["fast_ema"], adjust=False).mean()
        ema_m = close.ewm(span=g["mid_ema"], adjust=False).mean()
        ema_s = close.ewm(span=g["slow_ema"], adjust=False).mean()

        delta = close.diff()
        gain = delta.clip(lower=0).rolling(g["rsi_period"]).mean()
        loss = (-delta.clip(upper=0)).rolling(g["rsi_period"]).mean().replace(0, np.nan)
        rsi = 100 - (100 / (1 + (gain / loss)))

        buy_cond = pd.Series(True, index=df.index)
        sell_cond = pd.Series(True, index=df.index)

        mods = g["modules"]
        if "EMA_CROSS" in mods:
            buy_cond &= (ema_f > ema_m) & (close > ema_s)
            sell_cond &= (ema_f < ema_m) & (close < ema_s)
        if "RSI_FILTER" in mods:
            buy_cond &= rsi > g["rsi_buy"]
            sell_cond &= rsi < g["rsi_sell"]
        if "MACD_TREND" in mods:
            macd = close.ewm(span=g["macd_fast"]).mean() - close.ewm(span=g["macd_slow"]).mean()
            sig = macd.ewm(span=g["macd_signal"]).mean()
            buy_cond &= macd > sig
            sell_cond &= macd < sig
        if "BB_BREAKOUT" in mods:
            ma = close.rolling(g["bb_period"]).mean()
            std = close.rolling(g["bb_period"]).std()
            buy_cond &= close > (ma + g["bb_std"] * std)
            sell_cond &= close < (ma - g["bb_std"] * std)
        if "DONCHIAN_BREAKOUT" in mods:
            lb = g["breakout_lookback"]
            buy_cond &= close > high.shift(1).rolling(lb).max()
            sell_cond &= close < low.shift(1).rolling(lb).min()

        signal = pd.Series(0, index=df.index)
        signal[buy_cond] = 1
        signal[sell_cond] = -1
        return signal

    def _quick_backtest(self, df: pd.DataFrame, g: dict) -> dict:
        tr = pd.concat([
            df["high"] - df["low"],
            (df["high"] - df["close"].shift(1)).abs(),
            (df["low"] - df["close"].shift(1)).abs(),
        ], axis=1).max(axis=1)
        atr = tr.rolling(g["atr_period"]).mean().bfill()
        sig = self._compute_signals(df, g)

        closes = df["close"].to_numpy()
        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        atrs = atr.to_numpy()
        sigs = sig.to_numpy()

        r_results = []
        i = 50
        n = len(df) - 1
        while i < n:
            if sigs[i] == 0 or np.isnan(atrs[i]) or atrs[i] <= 0:
                i += 1
                continue
            direction = sigs[i]
            entry = closes[i]
            sl_dist = atrs[i] * g["sl_atr_mult"]
            tp_dist = sl_dist * g["tp_r_mult"]
            sl = entry - direction * sl_dist
            tp = entry + direction * tp_dist

            outcome = 0.0
            for j in range(i + 1, min(i + 96, n)):
                if direction == 1:
                    if lows[j] <= sl:
                        outcome = -1.0
                        i = j
                        break
                    if highs[j] >= tp:
                        outcome = float(g["tp_r_mult"])
                        i = j
                        break
                else:
                    if highs[j] >= sl:
                        outcome = -1.0
                        i = j
                        break
                    if lows[j] <= tp:
                        outcome = float(g["tp_r_mult"])
                        i = j
                        break
            total_cost = float(self.spread_points + self.slippage_points)
            if outcome != 0.0:
                cost_in_r = total_cost / max(sl_dist, 1e-9)
                r_results.append(round(outcome - cost_in_r, 4))
            i += 1

        trades = len(r_results)
        if trades < self.min_trades:
            return {"profit_factor": 0.0, "win_rate": 0.0, "max_drawdown": 100.0, "expectancy": -1.0, "trade_count": trades}

        arr = np.array(r_results)
        wins = arr[arr > 0]
        losses = arr[arr < 0]
        gross_profit = float(wins.sum()) if len(wins) else 0.0
        gross_loss = float(abs(losses.sum())) if len(losses) else 1e-6
        pf = gross_profit / gross_loss
        win_rate = (len(wins) / trades) * 100.0
        expectancy = float(arr.mean())
        equity = np.cumsum(arr)
        peak = np.maximum.accumulate(equity)
        max_dd = float(np.max(peak - equity)) if len(equity) else 0.0

        return {
            "profit_factor": round(pf, 3),
            "win_rate": round(win_rate, 2),
            "max_drawdown": round(max_dd, 2),
            "expectancy": round(expectancy, 3),
            "trade_count": trades,
        }

    def evaluate_candidate(self, df: pd.DataFrame, symbol: str, timeframe: str, genome: dict, gen_type: str):
        h = self.generator.hash_genome(genome)
        if self.db.exists(h):
            self.duplicates_skipped += 1
            return

        # 70% In-Sample / 30% Out-of-Sample Walk-Forward Split
        split_idx = int(len(df) * 0.70)
        is_df = df.iloc[:split_idx].reset_index(drop=True)
        oos_df = df.iloc[split_idx:].reset_index(drop=True)

        is_metrics = self._quick_backtest(is_df, genome)
        oos_metrics = self._quick_backtest(oos_df, genome)

        # Overfitting penalty if OOS fails
        oos_pf = oos_metrics["profit_factor"]
        if is_metrics["trade_count"] < self.min_trades or is_metrics["profit_factor"] < 1.05 or oos_pf < 1.0:
            score = 0.0
        else:
            score = (
                (is_metrics["profit_factor"] * 25.0)
                + (oos_pf * 35.0)
                + (is_metrics["expectancy"] * 20.0)
                - (is_metrics["max_drawdown"] * 1.5)
            )

        self.db.save_result(
            strategy_hash=h,
            symbol=symbol,
            timeframe=timeframe,
            generation_type=gen_type,
            genome=genome,
            metrics=is_metrics,
            oos_pf=oos_pf,
            score=round(max(0.0, score), 2),
        )
        self.session_tested += 1
        self.last_message = f"[{timeframe}] Tested {h} ({gen_type}) | Score: {max(0.0, score):.2f} | OOS PF: {oos_pf:.2f}"

    def export_top_excel(self, symbol: str | None = None) -> Path:
        top_df = self.db.get_top_strategies(limit=100, symbol=symbol)
        out_file = self.export_dir / f"ATMS_Top_Leaderboard_{symbol or 'ALL'}.xlsx"
        with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
            top_df.head(10).to_excel(writer, index=False, sheet_name="Top 10")
            top_df.head(20).to_excel(writer, index=False, sheet_name="Top 20")
            top_df.to_excel(writer, index=False, sheet_name="Top 100")
        return out_file

    def _worker_loop(self, datasets: dict[str, pd.DataFrame], symbol: str):
        timeframes = list(datasets.keys())
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                self.status = "PAUSED"
                time.sleep(0.5)
                continue

            self.status = "RUNNING"
            tf = random.choice(timeframes)
            df = datasets[tf]

            # 35% Evolutionary mutation from Top 20, 65% Fresh Discovery
            top_df = self.db.get_top_strategies(limit=20, symbol=symbol)
            if len(top_df) >= 3 and random.random() < 0.35:
                parent_row = top_df.sample(1).iloc[0]
                parent_genome = json.loads(parent_row["genome_json"])
                genome = self.generator.mutate_genome(parent_genome)
                gen_type = "EVOLUTION"
            else:
                genome = self.generator.random_genome()
                gen_type = "DISCOVERY"

            try:
                self.evaluate_candidate(df, symbol, tf, genome, gen_type)
            except Exception as exc:
                self.last_message = f"Worker warning: {exc}"

            if self.session_tested > 0 and self.session_tested % 25 == 0:
                try:
                    self.export_top_excel(symbol=symbol)
                except Exception:
                    pass

            time.sleep(0.05)

        self.status = "STOPPED"

    def start(self, datasets: dict[str, pd.DataFrame], symbol: str):
        if self._thread and self._thread.is_alive():
            self._pause_event.clear()
            self.status = "RUNNING"
            return
        self._stop_event.clear()
        self._pause_event.clear()
        self._thread = threading.Thread(
            target=self._worker_loop, args=(datasets, symbol), daemon=True
        )
        self._thread.start()
        self.status = "RUNNING"

    def pause(self):
        self._pause_event.set()
        self.status = "PAUSED"

    def resume(self):
        self._pause_event.clear()
        self.status = "RUNNING"

    def stop(self):
        self._stop_event.set()
        self._pause_event.clear()
        self.status = "STOPPED"
