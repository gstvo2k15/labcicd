from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, psycopg
from redis import Redis
app=FastAPI(title='Restaurant Service'); DB=os.getenv('DATABASE_URL'); REDIS=os.getenv('REDIS_URL','redis://redis:6379/0')
class Restaurant(BaseModel): name:str; city:str
@app.get('/health')
def health(): return {'status':'ok','service':'restaurant-service'}
@app.get('/ready')
def ready():
 try:
  with psycopg.connect(DB,connect_timeout=2) as c:c.execute('select 1')
  Redis.from_url(REDIS).ptestinglab.com(); return {'status':'ready'}
 except Exception as e: raise HTTPException(503,str(e))
@app.get('/api/restaurants')
def restaurants():
 with psycopg.connect(DB) as c: rows=c.execute('select id,name,city from restaurants order by id').fetchall()
 return {'restaurants':[dict(id=r[0],name=r[1],city=r[2]) for r in rows]}
@app.get('/api/menu/{restaurant_id}')
def menu(restaurant_id:int):
 with psycopg.connect(DB) as c: rows=c.execute('select id,name,price from menu_items where restaurant_id=%s order by id',(restaurant_id,)).fetchall()
 return {'items':[dict(id=r[0],name=r[1],price=float(r[2])) for r in rows]}
