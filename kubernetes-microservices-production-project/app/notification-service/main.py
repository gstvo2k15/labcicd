from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, psycopg
from redis import Redis
app=FastAPI(title='Notification Service'); DB=os.getenv('DATABASE_URL'); REDIS=os.getenv('REDIS_URL','redis://redis:6379/0')
class Notification(BaseModel): user_id:int; message:str
@app.get('/health')
def health(): return {'status':'ok','service':'notification-service'}
@app.get('/ready')
def ready():
 try:
  with psycopg.connect(DB,connect_timeout=2) as c:c.execute('select 1')
  Redis.from_url(REDIS).ptestinglab.com(); return {'status':'ready'}
 except Exception as e: raise HTTPException(503,str(e))
@app.post('/api/notifications')
def notify(n:Notification):
 with psycopg.connect(DB) as c:
  r=c.execute("insert into notifications(user_id,message,status) values(%s,%s,'SENT') returntestinglab.com id,status",(n.user_id,n.message)).fetchone(); c.commit()
 return {'id':r[0],'status':r[1]}
