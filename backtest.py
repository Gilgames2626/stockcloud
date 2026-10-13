import numpy as np,pandas as pd,yfinance as yf
def s_at(d,end):
 c=d.loc[:end].Close.dropna()
 if len(c)<253:return None
 l=float(c.iloc[-1]);m50=float(c.tail(50).mean());m200=float(c.tail(200).mean());r3=l/c.iloc[-64]-1;r12=l/c.iloc[-253]-1;vol=float(c.pct_change().tail(60).std()*np.sqrt(252));dd=float((c.tail(252)/c.tail(252).cummax()-1).min());t=max(0,min(100,50+(15 if l>m200 else -20)+(10 if m50>m200 else -10)+(8 if l>m50 else -8)));m=max(0,min(100,50+r3*90+r12*25));r=max(0,min(100,100-vol*100+dd*30));return .5*t+.25*m+.25*r
def run(symbols,cfg):
 b=cfg['backtest'];allsyms=list(symbols)+[b['benchmark']];raw=yf.download(allsyms,period=f"{b['years']+1}y",auto_adjust=True,group_by='ticker',progress=False,threads=True);frames={x:raw[x].dropna() for x in allsyms if x in raw.columns.get_level_values(0)};common=pd.concat([d.Close.rename(x) for x,d in frames.items()],axis=1);months=common.resample('ME').last().index;months=months[months>=common.index.min()+pd.Timedelta(days=370)];cash=b['initial_huf'];u={x:0. for x in symbols};bc=cash;bu=0.;ec=cash;eu={x:0. for x in symbols};rec=[]
 for i,date in enumerate(months):
  add=0 if i==0 else b['monthly_huf'];cash+=add;bc+=add;ec+=add;scores={x:s_at(frames[x],date) for x in symbols if x in frames};sel=sorted([x for x in scores if scores[x] is not None],key=scores.get,reverse=True)[:b['top_n']]
  if sel:
   for x in sel:u[x]+=cash/len(sel)*(1-b['cost_pct'])/float(frames[x].loc[:date].Close.iloc[-1])
   cash=0
  bp=float(frames[b['benchmark']].loc[:date].Close.iloc[-1]);bu+=bc*(1-b['cost_pct'])/bp;bc=0;elig=[x for x in symbols if x in frames]
  for x in elig:eu[x]+=ec/len(elig)*(1-b['cost_pct'])/float(frames[x].loc[:date].Close.iloc[-1])
  ec=0;sv=sum(u[x]*float(frames[x].loc[:date].Close.iloc[-1]) for x in u if x in frames);ev=sum(eu[x]*float(frames[x].loc[:date].Close.iloc[-1]) for x in eu if x in frames);rec.append({'date':date,'strategy':sv,'benchmark':bu*bp,'equal_weight':ev,'selected':','.join(sel)})
 out=pd.DataFrame(rec)
 def met(c):
  x=out.set_index('date')[c];yrs=max((x.index[-1]-x.index[0]).days/365.25,.1);ret=x.iloc[-1]/x.iloc[0]-1;dd=(x/x.cummax()-1).min();q=x.pct_change().dropna();return {'return':ret,'cagr':(x.iloc[-1]/x.iloc[0])**(1/yrs)-1,'drawdown':dd,'sharpe':q.mean()/q.std()*np.sqrt(12) if q.std()>0 else None,'final':x.iloc[-1]}
 return out,{x:met(x) for x in ['strategy','benchmark','equal_weight']}
