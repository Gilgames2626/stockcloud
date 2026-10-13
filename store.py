import json,sqlite3,threading,hashlib
from datetime import datetime,timezone,timedelta
from pathlib import Path
DB=Path(__file__).parent/'data'/'cache.db';LOCK=threading.Lock()
def con():
 c=sqlite3.connect(DB,timeout=30);c.row_factory=sqlite3.Row;c.execute('PRAGMA journal_mode=WAL');c.execute('CREATE TABLE IF NOT EXISTS cache(k TEXT PRIMARY KEY,v TEXT,exp TEXT)');return c
def get(k):
 with con() as c:r=c.execute('SELECT v,exp FROM cache WHERE k=?',(k,)).fetchone()
 if not r:return None
 if datetime.fromisoformat(r['exp'])<=datetime.now(timezone.utc):return None
 return json.loads(r['v'])
def put(k,v,hours):
 exp=(datetime.now(timezone.utc)+timedelta(hours=hours)).isoformat()
 with LOCK,con() as c:c.execute('INSERT INTO cache VALUES(?,?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v,exp=excluded.exp',(k,json.dumps(v,ensure_ascii=False),exp))
def h(text):return hashlib.sha256(text.encode()).hexdigest()
def clear(prefix=None):
 with LOCK,con() as c:
  n=c.execute('SELECT COUNT(*) n FROM cache'+(' WHERE k LIKE ?' if prefix else ''),((prefix+'%',) if prefix else ())).fetchone()['n'];c.execute('DELETE FROM cache'+(' WHERE k LIKE ?' if prefix else ''),((prefix+'%',) if prefix else ()))
 return n
