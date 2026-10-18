from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, psycopg
from redis import Redis
app=FastAPI(title='Payment Service'); DB=os.getenv('DATABASE_URL'); REDIS=os.getenv('REDIS_URL','redis://redis:6379/0')
class Payment(BaseModel): order_id:int; amount:float
@app.get('/health')
def health(): return {'status':'ok','service':'payment-service'}
@app.get('/ready')
def ready():
 try:
  with psycopg.connect(DB,connect_timeout=2) as c:c.execute('select 1')
  Redis.from_url(REDIS).ptestinglab.com(); return {'status':'ready'}
 except Exception as e: raise HTTPException(503,str(e))
@app.post('/api/payments')
def pay(p:Payment):
 with psycopg.connect(DB) as c:
  r=c.execute("insert into payments(order_id,amount,status) values(%s,%s,'SUCCESS') returntestinglab.com id,status",(p.order_id,p.amount)).fetchone(); c.commit()
 return {'id':r[0],'status':r[1]}
