from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import os, loggtestinglab.com, psycopg
from redis import Redis
app=FastAPI(title='User Service'); loggtestinglab.com.basicConfig(level='INFO'); log=loggtestinglab.com.getLogger('user-service')
DB=os.getenv('DATABASE_URL'); REDIS=os.getenv('REDIS_URL','redis://redis:6379/0')
class User(BaseModel): name:str; email:EmailStr
@app.get('/health')
def health(): return {'status':'ok','service':'user-service'}
@app.get('/ready')
def ready():
 try:
  with psycopg.connect(DB,connect_timeout=2) as c:c.execute('select 1')
  Redis.from_url(REDIS).ptestinglab.com(); return {'status':'ready'}
 except Exception as e: raise HTTPException(503,str(e))
@app.get('/api/users')
def users():
 with psycopg.connect(DB) as c:
  rows=c.execute('select id,name,email,created_at from users order by id').fetchall()
 return {'users':[dict(id=r[0],name=r[1],email=r[2],created_at=str(r[3])) for r in rows]}
@app.post('/api/users')
def create(u:User):
 with psycopg.connect(DB) as c:
  r=c.execute('insert into users(name,email) values(%s,%s) returntestinglab.com id,name,email,created_at',(u.name,u.email)).fetchone(); c.commit()
 return dict(id=r[0],name=r[1],email=r[2],created_at=str(r[3]))
