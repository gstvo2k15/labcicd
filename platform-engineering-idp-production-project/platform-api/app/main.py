from datetime import datetime, timezone
from pathlib import Path
import sqlite3, uuid
from typtestinglab.com import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB=Path(__file__).resolve().parent.parent/'platform.db'
app=FastAPI(title='Platform Engineertestinglab.com API',version='1.0.0')

def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
 c=conn(); c.execute("CREATE TABLE IF NOT EXISTS services(name TEXT PRIMARY KEY,owner TEXT NOT NULL,lifecycle TEXT NOT NULL,language TEXT NOT NULL,environment TEXT NOT NULL,repository TEXT NOT NULL,created_at TEXT NOT NULL)")
 c.execute("CREATE TABLE IF NOT EXISTS deployments(id TEXT PRIMARY KEY,service TEXT NOT NULL,environment TEXT NOT NULL,image TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL)"); c.commit(); c.close()
init()
class Service(BaseModel):
 name:str=Field(pattern=r'^[a-z0-9-]{2,40}$'); owner:str; lifecycle:str='development'; language:str='python'; environment:str='dev'; repository:str
class Deploy(BaseModel):
 service:str; environment:str; image:str
@app.get('/health')
def health(): return {'status':'healthy','service':'platform-api'}
@app.get('/platform/status')
def status():
 c=conn(); s=c.execute('select count(*) c from services').fetchone()['c']; d=c.execute('select count(*) c from deployments').fetchone()['c']; c.close(); return {'status':'operational','services_registered':s,'deployment_records':d,'timestamp':datetime.now(timezone.utc).isoformat()}
@app.get('/services')
def services(environment:Optional[str]=None):
 c=conn(); q='select * from services'; args=();
 if environment: q+=' where environment=?'; args=(environment,)
 rows=c.execute(q+' order by name',args).fetchall(); c.close(); return [dict(x) for x in rows]
@app.post('/services',status_code=201)
def create(s:Service):
 c=conn(); now=datetime.now(timezone.utc).isoformat()
 try: c.execute('insert into services values(?,?,?,?,?,?,?)',(s.name,s.owner,s.lifecycle,s.language,s.environment,s.repository,now)); c.commit()
 except sqlite3.IntegrityError: c.close(); raise HTTPException(409,'service already exists')
 c.close(); return {'message':'service registered','service':s.model_dump()}
@app.get('/services/{name}')
def get(name:str):
 c=conn(); r=c.execute('select * from services where name=?',(name,)).fetchone(); c.close()
 if not r: raise HTTPException(404,'service not found')
 return dict(r)
@app.post('/deploy',status_code=201)
def deploy(d:Deploy):
 c=conn(); ok=c.execute('select 1 from services where name=?',(d.service,)).fetchone()
 if not ok: c.close(); raise HTTPException(404,'service must be registered first')
 i=str(uuid.uuid4()); now=datetime.now(timezone.utc).isoformat(); c.execute('insert into deployments values(?,?,?,?,?,?)',(i,d.service,d.environment,d.image,'REQUESTED',now)); c.commit(); c.close()
 return {'deployment_id':i,'status':'REQUESTED',**d.model_dump()}
@app.get('/deployments')
def deployments():
 c=conn(); r=c.execute('select * from deployments order by created_at desc').fetchall(); c.close(); return [dict(x) for x in r]
