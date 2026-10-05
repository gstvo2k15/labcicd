from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get('/health').status_code==200
def test_register():
 name='demo-service'
 r=client.post('/services',json={'name':name,'owner':'platform-team','repository':'https://github.com/example/demo-service'})
 assert r.status_code in (201,409)
 assert client.get('/services/'+name).status_code==200
