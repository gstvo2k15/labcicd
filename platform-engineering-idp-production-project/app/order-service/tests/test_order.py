from fastapi.testclient import TestClient
from main import app
c=TestClient(app)
def test_health(): assert c.get('/health').status_code==200
def test_order():
 r=c.post('/orders',json={'customer_id':'u1','items':[{'sku':'burger-1','quantity':2}]}); assert r.status_code==201
 assert c.get('/orders/'+r.json()['id']).status_code==200
