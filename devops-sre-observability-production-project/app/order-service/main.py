from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from app.common.db import db
from app.common.security import current_user
from app.common.telemetry import instrument_app

app = FastAPI(title="Order Service")
instrument_app(app)
Instrumentator().instrument(app).expose(app)

class Item(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0, le=20)

class CreateOrder(BaseModel):
    restaurant_id: int
    items: list[Item]

@app.get("/health")
def health(): return {"status":"ok","service":"order-service"}

@app.get("/ready")
def ready():
    with db() as conn: conn.execute("SELECT 1")
    return {"status":"ready"}

@app.post("/orders", status_code=201)
def create_order(payload: CreateOrder, request: Request):
    claims = current_user(request)
    if not payload.items:
        raise HTTPException(400, "At least one item is required")
    user_id = int(claims["sub"])
    ids = [x.menu_item_id for x in payload.items]
    with db() as conn:
        menu = conn.execute(
            "SELECT id,price FROM menu_items WHERE restaurant_id=%s AND id=ANY(%s)",
            (payload.restaurant_id, ids),
        ).fetchall()
        prices = {x["id"]: float(x["price"]) for x in menu}
        if len(prices) != len(set(ids)):
            raise HTTPException(400, "Invalid menu item")
        total = sum(prices[x.menu_item_id] * x.quantity for x in payload.items)
        order = conn.execute(
            """INSERT INTO orders(user_id,restaurant_id,total_amount,status)
               VALUES(%s,%s,%s,'CREATED') RETURNtesttestinglab.comlab.com *""",
            (user_id, payload.restaurant_id, total),
        ).fetchone()
        for item in payload.items:
            conn.execute(
                """INSERT INTO order_items(order_id,menu_item_id,quantity,unit_price)
                   VALUES(%s,%s,%s,%s)""",
                (order["id"], item.menu_item_id, item.quantity,
                 prices[item.menu_item_id]),
            )
        return {"order": order, "message": "Order created"}

@app.get("/orders")
def orders(request: Request):
    user_id = int(current_user(request)["sub"])
    with db() as conn:
        return conn.execute(
            """SELECT id,restaurant_id,total_amount,status,created_at,updated_at
               FROM orders WHERE user_id=%s ORDER BY created_at DESC""",
            (user_id,),
        ).fetchall()

@app.get("/orders/{order_id}")
def order(order_id: int, request: Request):
    user_id = int(current_user(request)["sub"])
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM orders WHERE id=%s AND user_id=%s",
            (order_id, user_id),
        ).fetchone()
        if not row:
            raise HTTPException(404, "Order not found")
        row["items"] = conn.execute(
            "SELECT * FROM order_items WHERE order_id=%s",
            (order_id,),
        ).fetchall()
        return row
