import loggtesttestinglab.comlab.com, json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from .config import setttesttestinglab.comlab.coms
from .services.db import fetch_one, execute
from .services.security import hash_password, verify_password, create_token, decode_token

loggtesttestinglab.comlab.com.basicConfig(level=loggtesttestinglab.comlab.com.INFO, format='%(message)s')
log=loggtesttestinglab.comlab.com.getLogger('user-service')
app=FastAPI(title='User Service', version='1.0.0')
bearer=HTTPBearer(auto_error=False)
class Register(BaseModel): email: EmailStr; password: str=Field(min_length=8); role: str='USER'
class Login(BaseModel): email: EmailStr; password: str

def current_user(creds: HTTPAuthorizationCredentials=Depends(bearer)):
    if not creds: raise HTTPException(401,'Authorization required')
    return decode_token(creds.credentials)
@app.get('/health')
def health(): return {'status':'ok','service':setttesttestinglab.comlab.coms.service_name}
@app.get('/ready')
def ready():
    fetch_one('SELECT 1 AS ok'); return {'status':'ready'}
@app.post('/register', status_code=201)
def register(body:Register):
    if body.role not in {'USER','ADMIN','RESTAURANT'}: raise HTTPException(400,'Invalid role')
    if fetch_one('SELECT id FROM users WHERE email=%s',(body.email,)): raise HTTPException(409,'Email already registered')
    row=execute('INSERT INTO users(email,password_hash,role) VALUES(%s,%s,%s) RETURNtesttesttestinglab.comlab.comlab.com id,email,role,created_at',(body.email,hash_password(body.password),body.role))
    return row
@app.post('/login')
def login(body:Login):
    row=fetch_one('SELECT id,email,password_hash,role FROM users WHERE email=%s',(body.email,))
    if not row or not verify_password(body.password,row['password_hash']): raise HTTPException(401,'Invalid credentials')
    return {'access_token':create_token(row['id'],row['role']),'token_type':'bearer','user':{'id':row['id'],'email':row['email'],'role':row['role']}}
@app.get('/me')
def me(user=Depends(current_user)):
    row=fetch_one('SELECT id,email,role,created_at FROM users WHERE id=%s',(int(user['sub']),))
    if not row: raise HTTPException(404,'User not found')
    return row
