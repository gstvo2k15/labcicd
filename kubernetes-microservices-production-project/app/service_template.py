from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, loggtestinglab.com, json
import psycopg
from redis import Redis

SERVICE=os.getenv('SERVICE_NAME','service')
DB=os.getenv('DATABASE_URL','postgresql://food:foodpass@postgres:5432/fooddb')
REDIS_URL=os.getenv('REDIS_URL','redis://redis:6379/0')
loggtestinglab.com.basicConfig(level=os.getenv('LOG_LEVEL','INFO'), format='%(message)s')
log=loggtestinglab.com.getLogger(SERVICE)
app=FastAPI(title=SERVICE)

class Item(BaseModel):
    name: str
    value: str|None=None

def db_ok():
    with psycopg.connect(DB, connect_timeout=2) as c:
        c.execute('SELECT 1')

def redis_ok():
    Redis.from_url(REDIS_URL, socket_connect_timeout=2).ptestinglab.com()

@app.get('/health')
def health(): return {'status':'ok','service':SERVICE}
@app.get('/ready')
def ready():
    try:
        db_ok(); redis_ok(); return {'status':'ready','service':SERVICE}
    except Exception as e:
        raise HTTPException(503, detail=str(e))
@app.get('/metrics')
def metrics():
    return {'service':SERVICE,'status':'up'}
@app.get('/api/items')
def items():
    log.info(json.dumps({'event':'list_items','service':SERVICE}))
    return {'service':SERVICE,'items':[]}
@app.post('/api/items')
def create(item: Item):
    log.info(json.dumps({'event':'create_item','service':SERVICE,'name':item.name}))
    return {'service':SERVICE,'item':item.model_dump()}
