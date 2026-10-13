import numpy as np,pandas as pd,math
def n(v):
 try:v=float(v);return v if math.isfinite(v) else np.nan
 except:return np.nan
def extract(i,p):
 g=lambda k:n(i.get(k));m=g('marketCap');fcf=g('freeCashflow');cash=g('totalCash');debt=g('totalDebt');target=g('targetMeanPrice');return {'market_cap':m,'trailing_pe':g('trailingPE'),'forward_pe':g('forwardPE'),'peg_ratio':g('pegRatio'),'revenue_growth':g('revenueGrowth'),'earnings_growth':g('earningsGrowth'),'profit_margin':g('profitMargins'),'operating_margin':g('operatingMargins'),'return_on_equity':g('returnOnEquity'),'fcf_yield':fcf/m if m>0 else np.nan,'net_cash':cash-debt if pd.notna(cash) and pd.notna(debt) else np.nan,'debt_to_equity':g('debtToEquity'),'target_upside':target/p-1 if p>0 else np.nan}
def score(d):
 def rank(c,hi=True,valid=None):
  s=pd.to_numeric(d[c],errors='coerce');s=s.where(valid(s)) if valid else s;r=s.rank(pct=True)*100;return r if hi else 100-r+100/max(1,s.notna().sum())
 q=[('revenue_growth',.2,1,None),('earnings_growth',.2,1,None),('profit_margin',.15,1,None),('operating_margin',.1,1,None),('return_on_equity',.1,1,lambda x:(x>-1)&(x<3)),('fcf_yield',.15,1,None),('net_cash',.05,1,None),('debt_to_equity',.05,0,lambda x:x>=0)];v=[('trailing_pe',.25,0,lambda x:x>0),('forward_pe',.3,0,lambda x:x>0),('peg_ratio',.15,0,lambda x:(x>0)&(x<10)),('fcf_yield',.2,1,None),('target_upside',.1,1,lambda x:(x>-.8)&(x<2))]
 def calc(spec):
  num=pd.Series(0.,index=d.index);den=pd.Series(0.,index=d.index)
  for c,w,h,f in spec:s=rank(c,bool(h),f);ok=s.notna();num+=s.fillna(0)*w;den+=ok*w
  return (num/den.replace(0,np.nan)).fillna(50),den*100/sum(x[1] for x in spec)
 d['fundamental_score'],a=calc(q);d['valuation_score'],b=calc(v);d['coverage']=np.minimum(a,b);return d
