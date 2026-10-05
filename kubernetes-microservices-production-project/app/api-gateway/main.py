from fastapi import FastAPI, HTTPException, Request
import os, httpx
app=FastAPI(title='API Gateway')
ROUTES={
 'users':os.getenv('USER_SERVICE_URL','http://user-service:8000'),
 'restaurants':os.getenv('RESTAURANT_SERVICE_URL','http://restaurant-service:8000'),
 'orders':os.getenv('ORDER_SERVICE_URL','http://order-service:8000'),
 'payments':os.getenv('PAYMENT_SERVICE_URL','http://payment-service:8000'),
 'notifications':os.getenv('NOTIFICATION_SERVICE_URL','http://notification-service:8000')}
@app.get('/health')
def health(): return {'status':'ok','service':'api-gateway'}
@app.get('/ready')
async def ready():
 try:
  async with httpx.AsyncClient(timeout=2) as c:
   r=await c.get(ROUTES['users']+'/health'); r.raise_for_status()
  return {'status':'ready'}
 except Exception as e: raise HTTPException(503,str(e))
@app.api_route('/api/{service}/{path:path}',methods=['GET','POST','PUT','DELETE'])
async def proxy(service,path,request:Request):
 if service not in ROUTES: raise HTTPException(404,'unknown service')
 body=await request.body(); url=f"{ROUTES[service]}/api/{path}"
 async with httpx.AsyncClient(timeout=10) as c:
  r=await c.request(request.method,url,content=body,headers={'content-type':request.headers.get('content-type','application/json')})
 return r.json() if 'application/json' in r.headers.get('content-type','') else r.text
