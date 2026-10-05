from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from .config import settings
from .services.db import fetch_one, execute
from .services.security import decode_token
app=FastAPI(title='Payment Service',version='1.0.0')
class PaymentIn(BaseModel): order_id:int; amount:float=Field(gt=0); method:str='CARD'
def uid(auth):
    if not auth or not auth.lower().startswith('bearer '): raise HTTPException(401,'Authorization required')
    return int(decode_token(auth.split(' ',1)[1])['sub'])
@app.get('/health')
def health(): return {'status':'ok','service':settings.service_name}
@app.get('/ready')
def ready(): fetch_one('SELECT 1 AS ok'); return {'status':'ready'}
@app.post('/payments',status_code=201)
def pay(body:PaymentIn,authorization:str|None=Header(default=None)):
    user=uid(authorization)
    order=fetch_one('SELECT id,total_amount FROM orders WHERE id=%s AND user_id=%s',(body.order_id,user))
    if not order: raise HTTPException(404,'Order not found')
    if abs(float(order['total_amount'])-body.amount)>0.01: raise HTTPException(400,'Payment amount mismatch')
    p=execute('INSERT INTO payments(order_id,amount,status,method) VALUES(%s,%s,%s,%s) RETURNING *',(body.order_id,body.amount,'SUCCESS','MOCK'))
    execute("UPDATE orders SET status='PAID' WHERE id=%s",(body.order_id,)); return p
@app.get('/payments/{order_id}')
def get_payment(order_id:int,authorization:str|None=Header(default=None)):
    user=uid(authorization)
    if not fetch_one('SELECT id FROM orders WHERE id=%s AND user_id=%s',(order_id,user)): raise HTTPException(404,'Order not found')
    return fetch_one('SELECT * FROM payments WHERE order_id=%s ORDER BY id DESC LIMIT 1',(order_id,))
