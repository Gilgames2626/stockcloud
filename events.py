import pandas as pd,yfinance as yf
from store import get,put
def earnings(ticker,cfg):
 key='earn:'+ticker;cached=get(key)
 if cached:return cached
 date=None
 try:
  x=yf.Ticker(ticker).get_earnings_dates(limit=8)
  if x is not None and not x.empty:
   idx=pd.to_datetime(x.index,utc=True);f=idx[idx>=pd.Timestamp.now(tz='UTC')];date=f.min() if len(f) else None
 except:pass
 days=max(0,(date-pd.Timestamp.now(tz='UTC')).days) if date is not None else None;pen=0
 if days is not None:
  for k,v in sorted((int(k),v) for k,v in cfg['earnings_risk'].items()):
   if days<=k:pen=v;break
 out={'earnings_date':date.isoformat() if date is not None else None,'days_to_earnings':days,'earnings_penalty':pen};put(key,out,12);return out
