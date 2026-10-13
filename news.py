import os,re,feedparser,requests
from urllib.parse import quote_plus,urlparse
from pydantic import BaseModel,Field
from store import get,put,h
class Head(BaseModel):
 sentiment:int=Field(ge=-100,le=100);importance:int=Field(ge=0,le=100);reason:str
class Heads(BaseModel):assessments:list[Head]
class Deep(BaseModel):
 event_type:str;sentiment:int=Field(ge=-100,le=100);importance:int=Field(ge=0,le=100);horizon:str;risk_flags:list[str];confidence:int=Field(ge=0,le=100);summary:str

def feed(query,kind,limit):
 url=f'https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en';f=feedparser.parse(url);out=[]
 for e in f.entries[:limit]:
  src=e.get('source',{}).get('title','') if isinstance(e.get('source',{}),dict) else ''
  if e.get('title'):out.append({'title':e['title'],'link':e.get('link',''),'published':e.get('published',''),'source':src,'source_type':kind,'weight':1.3 if kind=='investor_relations' else 1.0})
 return out
def collect(ticker,company,cfg,mode):
 key=f'feeds:{mode}:{ticker}';cached=get(key)
 if cached is not None:return cached,{'feed_cache_hit':True,'google_count':sum(x['source_type']=='google_news' for x in cached),'ir_count':sum(x['source_type']=='investor_relations' for x in cached)}
 general=feed(f'({company} OR {ticker}) stock when:{cfg["news_days"]}d','google_news',cfg['news_limit']);ir=[]
 if mode=='deep' and cfg['ir_domains'].get(ticker):ir=feed(f'site:{cfg["ir_domains"][ticker]} ({company} OR {ticker}) when:30d','investor_relations',cfg['news_limit'])
 seen={}
 for x in general+ir:seen.setdefault(re.sub(r'[^a-z0-9]','',x['title'].lower()),x)
 result=list(seen.values());put(key,result,.5);return result,{'feed_cache_hit':False,'google_count':len(general),'ir_count':len(ir)}
def lexical(items):
 pos={'growth','record','beats','upgrade','profit','approval','raises'};neg={'loss','miss','probe','lawsuit','warning','cuts','downgrade'};out=[]
 for x in items:w=set(re.findall('[a-z]+',x['title'].lower()));out.append(Head(sentiment=max(-100,min(100,18*(len(w&pos)-len(w&neg)))),importance=45,reason='Fallback'))
 return out
def assess(items):
 key='head:'+h('|'.join(x['title'] for x in items))+'|'+os.getenv('GEMINI_MODEL','');cached=get(key)
 if cached:return [Head(**x) for x in cached],{'calls':0,'cache_hit':True,'mode':'Gemini cache','input_tokens':0,'output_tokens':0}
 calls=0;it=ot=0;mode='Kulcsszo'
 if os.getenv('GEMINI_API_KEY'):
  try:
   from google import genai
   cl=genai.Client(api_key=os.environ['GEMINI_API_KEY']);prompt='Classify each financial headline in order. Use only title. sentiment -100..100, importance 0..100, short reason.\n'+'\n'.join(f'{i+1}. {x["title"]}' for i,x in enumerate(items));r=cl.models.generate_content(model=os.getenv('GEMINI_MODEL','gemini-3.5-flash-lite'),contents=prompt,config={'response_mime_type':'application/json','response_schema':Heads});a=r.parsed.assessments;calls=1;mode='Gemini';u=getattr(r,'usage_metadata',None);it=getattr(u,'prompt_token_count',0) or 0;ot=getattr(u,'candidates_token_count',0) or 0
  except Exception:a=lexical(items);mode='Tartalek / kulcsszo'
 else:a=lexical(items)
 put(key,[x.model_dump() for x in a],24*365);return a,{'calls':calls,'cache_hit':False,'mode':mode,'input_tokens':it,'output_tokens':ot}
def content(item,cfg):
 key='content:'+h(item['link']);cached=get(key)
 if cached:return cached,True
 headers={'User-Agent':os.getenv('SEC_USER_AGENT','AlphaHunter research tool') if 'sec.gov' in urlparse(item['link']).netloc else 'AlphaHunter research tool'};r=requests.get(item['link'],headers=headers,timeout=cfg['deep_news']['timeout'],allow_redirects=True);r.raise_for_status();from trafilatura import extract;text=re.sub(r'\s+',' ',extract(r.text,url=r.url,output_format='txt',include_comments=False,include_tables=True) or '').strip()
 if len(text)<500:raise ValueError('Too little article text')
 data={'text':text[:cfg['deep_news']['max_chars']],'url':r.url,'chars':len(text)};put(key,data,cfg['deep_news']['cache_hours']);return data,False
def deep(items,heads,ticker,cfg):
 chosen=sorted([(x,a) for x,a in zip(items,heads) if x['source_type']=='investor_relations' or a.importance>=cfg['deep_news']['importance']],key=lambda z:z[1].importance,reverse=True)[:cfg['deep_news']['max_docs']];results=[];stats={'selected':len(chosen),'calls':0,'result_cache_hits':0,'content_cache_hits':0,'downloads':0,'fails':0,'input_tokens':0,'output_tokens':0}
 for item,_ in chosen:
  try:
   c,ch=content(item,cfg);stats['content_cache_hits']+=int(ch);stats['downloads']+=int(not ch);cachekey='deep:'+h(c['text']+cfg['deep_news']['model']+'v1');cached=get(cachekey)
   if cached:d=Deep(**cached);stats['result_cache_hits']+=1
   else:
    from google import genai
    cl=genai.Client(api_key=os.environ['GEMINI_API_KEY']);prompt=f'Analyze this public financial document for {ticker}. Use only text. Return event type, sentiment, importance, horizon, risks, confidence, concise summary.\n{c["text"]}';r=cl.models.generate_content(model=cfg['deep_news']['model'],contents=prompt,config={'response_mime_type':'application/json','response_schema':Deep});d=r.parsed;put(cachekey,d.model_dump(),24*365);stats['calls']+=1;u=getattr(r,'usage_metadata',None);stats['input_tokens']+=getattr(u,'prompt_token_count',0) or 0;stats['output_tokens']+=getattr(u,'candidates_token_count',0) or 0
   item['deep']=d.model_dump();results.append((item,d))
  except Exception as e:item['deep_error']=str(e);stats['fails']+=1
 return results,stats
def news_score(items,heads,deep_results):
 hw=[max(1,a.importance)*x['weight'] for x,a in zip(items,heads)];hs=50+sum(a.sentiment*w for a,w in zip(heads,hw))/sum(hw)/2 if hw else 50
 if not deep_results:return max(0,min(100,hs))
 dw=[max(1,d.importance)*x['weight']*max(.25,d.confidence/100) for x,d in deep_results];ds=sum((50+d.sentiment/2)*w for (_,d),w in zip(deep_results,dw))/sum(dw);return max(0,min(100,.7*ds+.3*hs))
