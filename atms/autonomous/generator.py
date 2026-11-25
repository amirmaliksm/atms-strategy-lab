import copy
import hashlib
import json
import random


class StrategyGenerator:
    INDICATORS = ["EMA_CROSS", "RSI_FILTER", "MACD_TREND", "ADX_STRENGTH", "BB_BREAKOUT", "DONCHIAN_BREAKOUT"]

    @staticmethod
    def hash_genome(genome: dict) -> str:
        canonical = json.dumps(genome, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    def random_genome(self) -> dict:
        active_modules = random.sample(self.INDICATORS, k=random.randint(2, 4))
        fast_ema = random.choice([8, 12, 15, 20, 25])
        mid_ema = random.choice([34, 50, 65, 80])
        slow_ema = random.choice([100, 150, 200])

        return {
            "modules": sorted(active_modules),
            "fast_ema": fast_ema,
            "mid_ema": mid_ema,
            "slow_ema": slow_ema,
            "rsi_period": random.choice([7, 10, 14, 21]),
            "rsi_buy": random.choice([40, 45, 50, 55]),
            "rsi_sell": random.choice([45, 50, 55, 60]),
            "macd_fast": random.choice([8, 12]),
            "macd_slow": random.choice([21, 26]),
            "macd_signal": random.choice([7, 9]),
            "adx_period": 14,
            "adx_min": random.choice([18, 20, 25, 30]),
            "bb_period": random.choice([20, 30]),
            "bb_std": random.choice([1.8, 2.0, 2.5]),
            "breakout_lookback": random.choice([10, 20, 30, 50]),
            "atr_period": 14,
            "sl_atr_mult": random.choice([1.0, 1.25, 1.5, 2.0, 2.5]),
            "tp_r_mult": random.choice([1.5, 2.0, 2.5, 3.0, 4.0]),
        }

    def mutate_genome(self, parent: dict) -> dict:
        child = copy.deepcopy(parent)
        tweak_key = random.choice([
            "fast_ema", "mid_ema", "rsi_buy", "rsi_sell",
            "adx_min", "sl_atr_mult", "tp_r_mult", "breakout_lookback"
        ])
        if tweak_key in ("fast_ema", "mid_ema", "breakout_lookback"):
            child[tweak_key] = max(5, int(child[tweak_key] + random.choice([-5, -3, 3, 5])))
        elif tweak_key in ("rsi_buy", "rsi_sell", "adx_min"):
            child[tweak_key] = max(10, min(85, int(child[tweak_key] + random.choice([-4, -2, 2, 4]))))
        elif tweak_key in ("sl_atr_mult", "tp_r_mult"):
            child[tweak_key] = round(max(0.5, child[tweak_key] + random.choice([-0.25, 0.25])), 2)

        if random.random() < 0.25:
            mod = random.choice(self.INDICATORS)
            if mod in child["modules"] and len(child["modules"]) > 2:
                child["modules"].remove(mod)
            elif mod not in child["modules"]:
                child["modules"].append(mod)
            child["modules"] = sorted(child["modules"])

        return child
