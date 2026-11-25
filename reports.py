import io
import pandas as pd

def _strip_tz_df(df):
    if df is None or not hasattr(df, "columns"):
        return df
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64tz_dtype(out[col].dtype):
            out[col] = out[col].dt.tz_localize(None)
    return out


def build_excel(summary,trades,curve,params,symbol,timeframe,optimizer=None):
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as w:
        pd.DataFrame([summary]).to_excel(w,index=False,sheet_name="Summary")
        if len(trades): _strip_tz_df(trades).to_excel(w,index=False,sheet_name="Trade History")
        if len(curve): _strip_tz_df(curve).to_excel(w,index=False,sheet_name="Equity Curve")
        if params: pd.DataFrame([params]).to_excel(w,index=False,sheet_name="Settings")
        if optimizer is not None: _strip_tz_df(optimizer).to_excel(w,index=False,sheet_name="Optimization")
        for ws in w.book.worksheets:
            ws.freeze_panes="A2"
            ws.auto_filter.ref=ws.dimensions
            for col in ws.columns:
                letter=col[0].column_letter
                maxlen=max((len(str(c.value)) if c.value is not None else 0) for c in col)
                ws.column_dimensions[letter].width=min(max(maxlen+2,12),32)
    return buf.getvalue()
