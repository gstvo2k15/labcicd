from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
app=FastAPI(title='Order Service',version='1.0.0')
orders={}
class Item(BaseModel): sku:str=Field(min_length=2); quantity:int=Field(gt=0,le=100)
class Order(BaseModel): customer_id:str=Field(min_length=2); items:list[Item]=Field(min_length=1)
@app.get('/health')
def health(): return {'status':'healthy','service':'order-service'}
@app.get('/ready')
def ready(): return {'status':'ready','service':'order-service'}
@app.get('/orders')
def list_orders(): return list(orders.values())
@app.post('/orders',status_code=201)
def create_order(p:Order):
 i=str(uuid4()); o={'id':i,'customer_id':p.customer_id,'items':[x.model_dump() for x in p.items],'status':'CREATED','created_at':datetime.now(timezone.utc).isoformat()}; orders[i]=o; return o
@app.get('/orders/{order_id}')
def get_order(order_id:str):
 if order_id not in orders: raise HTTPException(404,'order not found')
 return orders[order_id]
