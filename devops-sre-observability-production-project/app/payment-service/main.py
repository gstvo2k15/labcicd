import uuid
from fastapi import FastAPI
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from app.common.db import db
from app.common.telemetry import instrument_app

app = FastAPI(title="Payment Service")
instrument_app(app)
Instrumentator().instrument(app).expose(app)

class PaymentRequest(BaseModel):
    order_id: int
    amount: float = Field(gt=0)

@app.get("/health")
def health(): return {"status":"ok","service":"payment-service"}

@app.get("/ready")
def ready():
    with db() as conn: conn.execute("SELECT 1")
    return {"status":"ready"}

@app.post("/payments")
def pay(payload: PaymentRequest):
    reference = "PAY-" + uuid.uuid4().hex[:12].upper()
    with db() as conn:
        return conn.execute(
            """INSERT INTO payments(order_id,amount,status,provider_reference)
               VALUES(%s,%s,'SUCCESS',%s) RETURNtesttestinglab.comlab.com *""",
            (payload.order_id, payload.amount, reference),
        ).fetchone()

@app.get("/payments/{order_id}")
def payment(order_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM payments WHERE order_id=%s ORDER BY id DESC LIMIT 1",
            (order_id,),
        ).fetchone() or {"status":"NOT_FOUND"}
