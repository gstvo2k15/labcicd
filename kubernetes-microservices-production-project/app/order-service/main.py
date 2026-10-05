from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, psycopg
from redis import Redis
app=FastAPI(title='Order Service'); DB=os.getenv('DATABASE_URL'); REDIS=os.getenv('REDIS_URL','redis://redis:6379/0')
class Order(BaseModel): user_id:int; restaurant_id:int; item_id:int; quantity:int=1
@app.get('/health')
def health(): return {'status':'ok','service':'order-service'}
@app.get('/ready')
def ready():
 try:
  with psycopg.connect(DB,connect_timeout=2) as c:c.execute('select 1')
  Redis.from_url(REDIS).ping(); return {'status':'ready'}
 except Exception as e: raise HTTPException(503,str(e))
@app.post('/api/orders')
def create(o:Order):
 with psycopg.connect(DB) as c:
  r=c.execute('insert into orders(user_id,restaurant_id,status,total) select %s,%s,\'CREATED\',price*%s from menu_items where id=%s returning id,status,total',(o.user_id,o.restaurant_id,o.quantity,o.item_id)).fetchone()
  if not r: raise HTTPException(400,'menu item not found')
  c.execute('insert into order_items(order_id,menu_item_id,quantity) values(%s,%s,%s)',(r[0],o.item_id,o.quantity)); c.commit()
 Redis.from_url(REDIS).setex(f'order:{r[0]}',3600,r[1]); return {'id':r[0],'status':r[1],'total':float(r[2])}
@app.get('/api/orders/{order_id}')
def get(order_id:int):
 with psycopg.connect(DB) as c:r=c.execute('select id,status,total from orders where id=%s',(order_id,)).fetchone()
 if not r: raise HTTPException(404,'order not found')
 return {'id':r[0],'status':r[1],'total':float(r[2])}
