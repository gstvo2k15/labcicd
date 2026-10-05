from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from app.common.db import db
from app.common.telemetry import instrument_app

app = FastAPI(title="Notification Service")
instrument_app(app)
Instrumentator().instrument(app).expose(app)

class NotificationRequest(BaseModel):
    user_id: int
    order_id: int
    message: str

@app.get("/health")
def health(): return {"status":"ok","service":"notification-service"}

@app.get("/ready")
def ready():
    with db() as conn: conn.execute("SELECT 1")
    return {"status":"ready"}

@app.post("/notifications")
def notify(payload: NotificationRequest):
    with db() as conn:
        return conn.execute(
            """INSERT INTO notifications(user_id,order_id,message,status)
               VALUES(%s,%s,%s,'SENT') RETURNING *""",
            (payload.user_id,payload.order_id,payload.message),
        ).fetchone()

@app.get("/notifications/{user_id}")
def notifications(user_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
