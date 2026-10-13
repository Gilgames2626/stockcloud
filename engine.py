import json,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import pandas as pd,yfinance as yf
from dotenv import load_dotenv
from store import get,put
from indicators import metrics
from fundamentals import extract,score
from news import collect,assess,deep,news_score
from events import earnings
load_dotenv();ROOT=Path(__file__).parent
def hist(t,cfg):
 k='price:'+t;x=get(k)
 if x:d=pd.DataFrame(x);d.Date=pd.to_datetime(d.Date);return d.set_index('Date'),True
 d=yf.Ticker(t).history(period=cfg['history_period'],auto_adjust=True);q=d.reset_index();q.Date=q.Date.astype(str);put(k,q.to_dict('records'),.5);return d,False
def one(t,name,cfg,mode):
 started=time.perf_counter();times={};z=time.perf_counter();d,ph=hist(t,cfg);times['price_seconds']=time.perf_counter()-z;m=metrics(d);z=time.perf_counter();fk='fund:'+t;f=get(fk);fh=bool(f)
 if not f:f={k:(None if pd.isna(v) else float(v)) for k,v in extract(yf.Ticker(t).info or {},m['price']).items()};put(fk,f,24)
 times['fundamental_seconds']=time.perf_counter()-z;z=time.perf_counter();items,feedstats=collect(t,name,cfg,mode);times['feed_seconds']=time.perf_counter()-z;z=time.perf_counter();heads,hstats=assess(items);times['headline_seconds']=time.perf_counter()-z;z=time.perf_counter();dr,ds=deep(items,heads,t,cfg) if mode=='deep' else ([],{'selected':0,'calls':0,'result_cache_hits':0,'content_cache_hits':0,'downloads':0,'fails':0,'input_tokens':0,'output_tokens':0});times['deep_seconds']=time.perf_counter()-z;ns=news_score(items,heads,dr);ev=earnings(t,cfg);stop=max(0,m['price']-cfg['stop_atr_multiple']*m['atr14']);target=m['price']+cfg['reward_risk']*(m['price']-stop);stats={'price_cache':ph,'fund_cache':fh,**feedstats,**{f'headline_{k}':v for k,v in hstats.items()},**{f'deep_{k}':v for k,v in ds.items()},**{k:round(v,3) for k,v in times.items()},'total_seconds':round(time.perf_counter()-started,3)};return {'ticker':t,'company':name,**m,**f,**ev,'news_score':ns,'stop_loss':stop,'take_profit':target},items,stats
def run(mode='quick'):
 total=time.perf_counter();cfg=json.loads((ROOT/'config.json').read_text());rows=[];news={};perf={};errors=[]
 with ThreadPoolExecutor(max_workers=cfg['max_workers']) as ex:
  fs={ex.submit(one,t,n,cfg,mode):t for t,n in cfg['watchlist'].items()}
  for f in as_completed(fs):
   try:r,x,p=f.result();rows.append(r);news[r['ticker']]=x;perf[r['ticker']]=p
   except Exception as e:errors.append({'ticker':fs[f],'error':str(e)})
 d=score(pd.DataFrame(rows));w=cfg['weights'];d['raw_score']=d.fundamental_score*w['fundamental']+d.valuation_score*w['valuation']+d.technical_score*w['technical']+d.news_score*w['news']+d.momentum_score*w['momentum']+d.risk_score*w['risk'];d['total_score']=(d.raw_score-d.earnings_penalty).clip(0,100);d=d.sort_values('total_score',ascending=False).reset_index(drop=True)
 sums={'total_seconds':round(time.perf_counter()-total,3),'companies':len(d),'price_cache_hits':sum(p['price_cache'] for p in perf.values()),'fund_cache_hits':sum(p['fund_cache'] for p in perf.values()),'feed_cache_hits':sum(p['feed_cache_hit'] for p in perf.values()),'google_articles':sum(p['google_count'] for p in perf.values()),'ir_articles':sum(p['ir_count'] for p in perf.values()),'headline_calls':sum(p['headline_calls'] for p in perf.values()),'headline_cache_hits':sum(p['headline_cache_hit'] for p in perf.values()),'headline_input_tokens':sum(p['headline_input_tokens'] for p in perf.values()),'headline_output_tokens':sum(p['headline_output_tokens'] for p in perf.values()),'deep_selected':sum(p['deep_selected'] for p in perf.values()),'deep_calls':sum(p['deep_calls'] for p in perf.values()),'deep_result_cache_hits':sum(p['deep_result_cache_hits'] for p in perf.values()),'deep_content_cache_hits':sum(p['deep_content_cache_hits'] for p in perf.values()),'deep_downloads':sum(p['deep_downloads'] for p in perf.values()),'deep_fails':sum(p['deep_fails'] for p in perf.values()),'deep_input_tokens':sum(p['deep_input_tokens'] for p in perf.values()),'deep_output_tokens':sum(p['deep_output_tokens'] for p in perf.values()),'headline_modes':sorted(set(p['headline_mode'] for p in perf.values()))}
 return d,news,perf,errors,sums
