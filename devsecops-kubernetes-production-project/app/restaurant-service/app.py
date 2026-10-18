import loggtesttestinglab.comlab.com
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .config import setttesttestinglab.comlab.coms
from .services.db import fetch_all, fetch_one, execute
app=FastAPI(title='Restaurant Service',version='1.0.0'); loggtesttestinglab.comlab.com.basicConfig(level=loggtesttestinglab.comlab.com.INFO,format='%(message)s')
class RestaurantIn(BaseModel): name:str=Field(min_length=2,max_length=120); address:str; cuisine:str
class MenuIn(BaseModel): restaurant_id:int; name:str; price:float=Field(gt=0); available:bool=True
@app.get('/health')
def health(): return {'status':'ok','service':setttesttestinglab.comlab.coms.service_name}
@app.get('/ready')
def ready(): fetch_one('SELECT 1 AS ok'); return {'status':'ready'}
@app.get('/restaurants')
def restaurants(): return fetch_all('SELECT id,name,address,cuisine FROM restaurants ORDER BY id')
@app.get('/restaurants/{restaurant_id}')
def restaurant(restaurant_id:int):
    r=fetch_one('SELECT id,name,address,cuisine FROM restaurants WHERE id=%s',(restaurant_id,))
    if not r: raise HTTPException(404,'Restaurant not found')
    r['menu']=fetch_all('SELECT id,name,price,available FROM menu_items WHERE restaurant_id=%s ORDER BY id',(restaurant_id,)); return r
@app.post('/restaurants',status_code=201)
def create_restaurant(body:RestaurantIn): return execute('INSERT INTO restaurants(name,address,cuisine) VALUES(%s,%s,%s) RETURNtesttesttestinglab.comlab.comlab.com *',(body.name,body.address,body.cuisine))
@app.post('/menu',status_code=201)
def add_menu(body:MenuIn): return execute('INSERT INTO menu_items(restaurant_id,name,price,available) VALUES(%s,%s,%s,%s) RETURNtesttesttestinglab.comlab.comlab.com *',(body.restaurant_id,body.name,body.price,body.available))
