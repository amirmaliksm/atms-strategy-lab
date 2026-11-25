import json
import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd


class ResearchDB:
    def __init__(self, db_path: str = "atms_research.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_hash TEXT UNIQUE,
                    symbol TEXT,
                    timeframe TEXT,
                    generation_type TEXT,
                    genome_json TEXT,
                    profit_factor REAL,
                    win_rate REAL,
                    max_drawdown REAL,
                    expectancy REAL,
                    trade_count INTEGER,
                    oos_profit_factor REAL,
                    composite_score REAL,
                    created_at TEXT
                )
            """)
            conn.commit()

    def exists(self, strategy_hash: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT 1 FROM experiments WHERE strategy_hash = ? LIMIT 1",
                (strategy_hash,),
            )
            return cur.fetchone() is not None

    def save_result(
        self,
        strategy_hash: str,
        symbol: str,
        timeframe: str,
        generation_type: str,
        genome: dict,
        metrics: dict,
        oos_pf: float,
        score: float,
    ) -> bool:
        if self.exists(strategy_hash):
            return False
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO experiments (
                    strategy_hash, symbol, timeframe, generation_type, genome_json,
                    profit_factor, win_rate, max_drawdown, expectancy, trade_count,
                    oos_profit_factor, composite_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    strategy_hash,
                    symbol,
                    timeframe,
                    generation_type,
                    json.dumps(genome, sort_keys=True),
                    float(metrics.get("profit_factor", 0.0)),
                    float(metrics.get("win_rate", 0.0)),
                    float(metrics.get("max_drawdown", 0.0)),
                    float(metrics.get("expectancy", 0.0)),
                    int(metrics.get("trade_count", 0)),
                    float(oos_pf),
                    float(score),
                    datetime.utcnow().isoformat(timespec="seconds"),
                ),
            )
            conn.commit()
        return True

    def get_top_strategies(self, limit: int = 20, symbol: str | None = None) -> pd.DataFrame:
        query = "SELECT * FROM experiments"
        params = []
        if symbol:
            query += " WHERE symbol = ?"
            params.append(symbol)
        query += " ORDER BY composite_score DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_stats(self) -> dict:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
            best = conn.execute("SELECT MAX(composite_score) FROM experiments").fetchone()[0]
        return {"total_tested": total, "best_score": round(best or 0.0, 2)}
