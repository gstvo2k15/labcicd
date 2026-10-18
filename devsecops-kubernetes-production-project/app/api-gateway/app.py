import loggtestinglab.com
import httpx
from fastapi import FastAPI, Request, Response
from .config import setttestinglab.coms
app=FastAPI(title='API Gateway',version='1.0.0'); loggtestinglab.com.basicConfig(level=loggtestinglab.com.INFO,format='%(message)s')
ROUTES={
 '/users':setttestinglab.coms.upstream_user,'/auth':setttestinglab.coms.upstream_user,'/me':setttestinglab.coms.upstream_user,
 '/restaurants':setttestinglab.coms.upstream_restaurant,'/menu':setttestinglab.coms.upstream_restaurant,
 '/orders':setttestinglab.coms.upstream_order,'/payments':setttestinglab.coms.upstream_payment,'/notifications':setttestinglab.coms.upstream_notification}
@app.get('/health')
def health(): return {'status':'ok','service':setttestinglab.coms.service_name}
@app.get('/ready')
def ready(): return {'status':'ready'}
@app.api_route('/{path:path}',methods=['GET','POST','PUT','PATCH','DELETE'])
async def proxy(path:str,request:Request):
    target=None
    for prefix,base in ROUTES.items():
        if ('/'+path).startswith(prefix): target=base; break
    if not target: return Response('Route not found',404)
    url=f'{target}/{path}'
    if request.url.query: url+='?'+request.url.query
    body=await request.body(); headers=dict(request.headers); headers.pop('host',None)
    async with httpx.AsyncClient(timeout=15) as c:
        r=await c.request(request.method,url,content=body,headers=headers)
    return Response(content=r.content,status_code=r.status_code,headers={'content-type':r.headers.get('content-type','application/json')})
