import itertools
import numpy as np
import pandas as pd

def prepare_data(raw: pd.DataFrame, timeframe="M15") -> pd.DataFrame:
    df=raw.copy()
    df.columns=[str(c).strip().lower() for c in df.columns]
    aliases={"date":"datetime","time":"datetime","timestamp":"datetime","open_time":"datetime",
             "o":"open","h":"high","l":"low","c":"close"}
    df=df.rename(columns={k:v for k,v in aliases.items() if k in df.columns and v not in df.columns})
    required=["datetime","open","high","low","close"]
    missing=[c for c in required if c not in df.columns]
    if missing: raise ValueError("Missing columns: "+", ".join(missing))
    df["datetime"]=pd.to_datetime(df["datetime"],utc=True,errors="coerce")
    for c in ["open","high","low","close"]:
        df[c]=pd.to_numeric(df[c],errors="coerce")
    df=df.dropna(subset=required).sort_values("datetime").drop_duplicates("datetime").set_index("datetime")
    if df.empty: raise ValueError("No valid OHLC rows found.")
    if (df.high < df[["open","close","low"]].max(axis=1)).any() or (df.low > df[["open","close","high"]].min(axis=1)).any():
        raise ValueError("Invalid OHLC candle detected.")
    if timeframe=="H1":
        agg={"open":"first","high":"max","low":"min","close":"last"}
        if "volume" in df.columns: agg["volume"]="sum"
        df=df.resample("1h",label="right",closed="right").agg(agg).dropna(subset=["open","high","low","close"])
    return df

def _rsi(s, n):
    delta=s.diff()
    gain=delta.clip(lower=0)
    loss=-delta.clip(upper=0)
    avg_gain=gain.ewm(alpha=1/n,adjust=False,min_periods=n).mean()
    avg_loss=loss.ewm(alpha=1/n,adjust=False,min_periods=n).mean()
    rs=avg_gain/avg_loss.replace(0,np.nan)
    out=100-(100/(1+rs))
    return out.fillna(50)

def _indicators(df,p):
    x=df.copy()
    x["ema_fast"]=x.close.ewm(span=p["ema_fast"],adjust=False).mean()
    x["ema_mid"]=x.close.ewm(span=p["ema_mid"],adjust=False).mean()
    x["ema_slow"]=x.close.ewm(span=p["ema_slow"],adjust=False).mean()
    x["rsi"]=_rsi(x.close,p["rsi_len"])
    prev=x.close.shift()
    tr=pd.concat([(x.high-x.low),(x.high-prev).abs(),(x.low-prev).abs()],axis=1).max(axis=1)
    x["atr"]=tr.ewm(alpha=1/p["atr_len"],adjust=False,min_periods=p["atr_len"]).mean()
    x["buy"]=((x.ema_mid>x.ema_slow)&(x.ema_fast>x.ema_mid)&(x.close>x.ema_fast)&
              (x.rsi.shift(1)<=p["buy_level"])&(x.rsi>p["buy_level"]))
    x["sell"]=((x.ema_mid<x.ema_slow)&(x.ema_fast<x.ema_mid)&(x.close<x.ema_fast)&
               (x.rsi.shift(1)>=p["sell_level"])&(x.rsi<p["sell_level"]))
    return x

def run_backtest(df,p,initial_balance=10000,risk_pct=1,spread=0.3,slippage=0.05,commission=0):
    x=_indicators(df,p).dropna(subset=["atr"])
    balance=float(initial_balance); peak=balance; maxdd=0.0
    trades=[]; curve=[]
    position=None
    idx=x.index
    for i in range(1,len(x)-1):
        row=x.iloc[i]; nxt=x.iloc[i+1]
        # Manage existing trade using this candle's OHLC.
        if position:
            hit_sl = row.low <= position["sl"] if position["side"]=="BUY" else row.high >= position["sl"]
            hit_tp = row.high >= position["tp"] if position["side"]=="BUY" else row.low <= position["tp"]
            exit_price=None; reason=None
            if hit_sl:
                exit_price=position["sl"]; reason="STOP" # conservative if both hit
            elif hit_tp:
                exit_price=position["tp"]; reason="TAKE_PROFIT"
            if exit_price is not None:
                direction=1 if position["side"]=="BUY" else -1
                # approximate round-trip spread and slippage in price units
                gross=direction*(exit_price-position["entry"])*position["units"]
                costs=(spread+2*slippage)*position["units"] + commission*position["lots"]
                pnl=gross-costs
                balance+=pnl
                trades.append({"entry_time":position["entry_time"],"exit_time":idx[i],"side":position["side"],
                               "entry":position["entry"],"exit":exit_price,"stop_loss":position["sl"],
                               "take_profit":position["tp"],"units":position["units"],"lots":position["lots"],
                               "risk_cash":position["risk_cash"],"pnl":pnl,"r_multiple":pnl/position["risk_cash"] if position["risk_cash"] else 0,
                               "exit_reason":reason,"balance_after":balance})
                position=None
        peak=max(peak,balance); maxdd=max(maxdd,(peak-balance)/peak*100 if peak else 0)
        curve.append({"datetime":idx[i],"balance":balance})
        # Signal on closed candle i; enter at next candle open, only if flat.
        if position is None and balance>0 and row.atr>0:
            side="BUY" if bool(row.buy) else ("SELL" if bool(row.sell) else None)
            if p.get("allow_side","Both")=="Long only" and side=="SELL": side=None
            if p.get("allow_side","Both")=="Short only" and side=="BUY": side=None
            if side:
                entry=float(nxt.open)+(spread/2 if side=="BUY" else -spread/2)
                stop_dist=float(row.atr)*p["atr_mult"]
                risk_cash=balance*risk_pct/100
                units=risk_cash/stop_dist if stop_dist>0 else 0
                if units>0:
                    direction=1 if side=="BUY" else -1
                    sl=entry-direction*stop_dist
                    tp=entry+direction*stop_dist*p["rr"]
                    position={"side":side,"entry":entry,"entry_time":idx[i+1],"sl":sl,"tp":tp,
                              "units":units,"lots":units/100000,"risk_cash":risk_cash}
    if position:
        last=x.iloc[-1]; exit_price=float(last.close)
        direction=1 if position["side"]=="BUY" else -1
        gross=direction*(exit_price-position["entry"])*position["units"]
        costs=(spread+2*slippage)*position["units"]+commission*position["lots"]
        pnl=gross-costs; balance+=pnl
        trades.append({"entry_time":position["entry_time"],"exit_time":idx[-1],"side":position["side"],
                       "entry":position["entry"],"exit":exit_price,"stop_loss":position["sl"],
                       "take_profit":position["tp"],"units":position["units"],"lots":position["lots"],
                       "risk_cash":position["risk_cash"],"pnl":pnl,"r_multiple":pnl/position["risk_cash"] if position["risk_cash"] else 0,
                       "exit_reason":"END_OF_DATA","balance_after":balance})
    t=pd.DataFrame(trades)
    if len(t):
        wins=t[t.pnl>0]; losses=t[t.pnl<0]
        gross_profit=wins.pnl.sum(); gross_loss=abs(losses.pnl.sum())
        pf=gross_profit/gross_loss if gross_loss else (float("inf") if gross_profit else 0)
        win_rate=len(wins)/len(t)*100
        net=balance-initial_balance
    else:
        pf=0; win_rate=0; net=0
    summary={"trades":len(t),"win_rate":win_rate,"net_profit":net,"return_pct":net/initial_balance*100,
             "profit_factor":pf,"max_drawdown":maxdd,"average_r":float(t.r_multiple.mean()) if len(t) else 0,
             "gross_profit":float(t[t.pnl>0].pnl.sum()) if len(t) else 0,
             "gross_loss":float(abs(t[t.pnl<0].pnl.sum())) if len(t) else 0,
             "ending_balance":balance}
    return summary,t,pd.DataFrame(curve)

def optimize(df,ema_sets,rsi_sets,atr_sets,rr_sets,initial_balance,risk_pct,spread,slippage,commission,min_trades=30):
    rows=[]; details={}
    for eset,rset,atr,rr in itertools.product(ema_sets,rsi_sets,atr_sets,rr_sets):
        ef,em,es=map(int,eset.split("/")); buy,sell=map(float,rset.split("/"))
        if not ef<em<es or buy>=sell: continue
        p={"ema_fast":ef,"ema_mid":em,"ema_slow":es,"rsi_len":14,"buy_level":buy,"sell_level":sell,
           "atr_len":14,"atr_mult":float(atr),"rr":float(rr),"allow_side":"Both"}
        s,t,c=run_backtest(df,p,initial_balance,risk_pct,spread,slippage,commission)
        name=f"EMA {eset} | RSI {rset} | SL {atr} ATR | TP {rr}R"
        rows.append({"strategy":name,**s})
    out=pd.DataFrame(rows)
    if len(out):
        out["rank_score"]=out.apply(lambda r: (r.profit_factor if r.profit_factor<5 else 5) * max(0,1-r.max_drawdown/100) * min(1,r.trades/max(min_trades,1)),axis=1)
        out=out.sort_values(["rank_score","net_profit"],ascending=False).reset_index(drop=True)
    return out,details
