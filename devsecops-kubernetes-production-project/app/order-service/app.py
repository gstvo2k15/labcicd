import logging
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from .config import settings
from .services.db import fetch_all, fetch_one, execute
from .services.security import decode_token
app=FastAPI(title='Order Service',version='1.0.0'); logging.basicConfig(level=logging.INFO,format='%(message)s')
class Item(BaseModel): menu_item_id:int; quantity:int=Field(gt=0,le=50)
class OrderIn(BaseModel): restaurant_id:int; items:list[Item]
def user_id(auth):
    if not auth or not auth.lower().startswith('bearer '): raise HTTPException(401,'Authorization required')
    return int(decode_token(auth.split(' ',1)[1])['sub'])
@app.get('/health')
def health(): return {'status':'ok','service':settings.service_name}
@app.get('/ready')
def ready(): fetch_one('SELECT 1 AS ok'); return {'status':'ready'}
@app.post('/orders',status_code=201)
def create_order(body:OrderIn, authorization:str|None=Header(default=None)):
    uid=user_id(authorization)
    if not body.items: raise HTTPException(400,'Order must contain items')
    prices=[]
    for i in body.items:
        row=fetch_one('SELECT id,price FROM menu_items WHERE id=%s AND restaurant_id=%s AND available=true',(i.menu_item_id,body.restaurant_id))
        if not row: raise HTTPException(400,f'Menu item {i.menu_item_id} unavailable')
        prices.append((row['price'],i.quantity))
    total=sum(p*q for p,q in prices)
    order=execute('INSERT INTO orders(user_id,restaurant_id,status,total_amount) VALUES(%s,%s,%s,%s) RETURNING *',(uid,body.restaurant_id,'CREATED',total))
    for i in body.items: execute('INSERT INTO order_items(order_id,menu_item_id,quantity) VALUES(%s,%s,%s)',(order['id'],i.menu_item_id,i.quantity))
    return order
@app.get('/orders')
def history(authorization:str|None=Header(default=None)):
    uid=user_id(authorization); return fetch_all('SELECT id,restaurant_id,status,total_amount,created_at FROM orders WHERE user_id=%s ORDER BY created_at DESC',(uid,))
@app.get('/orders/{order_id}')
def get_order(order_id:int,authorization:str|None=Header(default=None)):
    uid=user_id(authorization); r=fetch_one('SELECT * FROM orders WHERE id=%s AND user_id=%s',(order_id,uid))
    if not r: raise HTTPException(404,'Order not found');
    r['items']=fetch_all('SELECT menu_item_id,quantity FROM order_items WHERE order_id=%s',(order_id,)); return r
@app.patch('/orders/{order_id}/status')
def status(order_id:int,status_value:str,authorization:str|None=Header(default=None)):
    uid=user_id(authorization); allowed={'CREATED','PAID','PREPARING','OUT_FOR_DELIVERY','DELIVERED','CANCELLED'}
    if status_value not in allowed: raise HTTPException(400,'Invalid status')
    r=execute('UPDATE orders SET status=%s WHERE id=%s AND user_id=%s RETURNING *',(status_value,order_id,uid))
    if not r: raise HTTPException(404,'Order not found'); return r
