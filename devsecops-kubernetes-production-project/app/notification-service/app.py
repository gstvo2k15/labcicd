from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from .config import settings
from .services.db import fetch_one, fetch_all, execute
from .services.security import decode_token
app=FastAPI(title='Notification Service',version='1.0.0')
class NotificationIn(BaseModel): order_id:int; channel:str='EMAIL'; message:str=Field(min_length=1,max_length=500)
def uid(auth):
    if not auth or not auth.lower().startswith('bearer '): raise HTTPException(401,'Authorization required')
    return int(decode_token(auth.split(' ',1)[1])['sub'])
@app.get('/health')
def health(): return {'status':'ok','service':settings.service_name}
@app.get('/ready')
def ready(): fetch_one('SELECT 1 AS ok'); return {'status':'ready'}
@app.post('/notifications',status_code=201)
def notify(body:NotificationIn,authorization:str|None=Header(default=None)):
    user=uid(authorization)
    if not fetch_one('SELECT id FROM orders WHERE id=%s AND user_id=%s',(body.order_id,user)): raise HTTPException(404,'Order not found')
    return execute('INSERT INTO notifications(order_id,channel,message,status) VALUES(%s,%s,%s,%s) RETURNING *',(body.order_id,body.channel,body.message,'SENT'))
@app.get('/notifications')
def notifications(authorization:str|None=Header(default=None)):
    user=uid(authorization); return fetch_all('SELECT n.* FROM notifications n JOIN orders o ON o.id=n.order_id WHERE o.user_id=%s ORDER BY n.created_at DESC',(user,))
