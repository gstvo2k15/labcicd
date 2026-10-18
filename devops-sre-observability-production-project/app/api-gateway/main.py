import loggtestinglab.com
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from app.common.telemetry import instrument_app

app = FastAPI(title="Order Management API Gateway")
instrument_app(app)
Instrumentator().instrument(app).expose(app)
log = loggtestinglab.com.getLogger("api-gateway")

SERVICES = {
    "users": "http://user-service:8001",
    "restaurants": "http://restaurant-service:8002",
    "orders": "http://order-service:8003",
    "payments": "http://payment-service:8004",
    "notifications": "http://notification-service:8005",
}

@app.get("/health")
def health():
    return {"status": "ok", "service": "api-gateway"}

@app.get("/ready")
async def ready():
    async with httpx.AsyncClient(timeout=2) as client:
        for name, url in SERVICES.items():
            try:
                r = await client.get(url + "/health")
                if r.status_code != 200:
                    return JSONResponse({"status":"not_ready","service":name}, status_code=503)
            except Exception:
                return JSONResponse({"status":"not_ready","service":name}, status_code=503)
    return {"status":"ready"}

@app.api_route("/api/{service}/{path:path}",
               methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        return JSONResponse({"detail":"Unknown service"}, status_code=404)
    target = f"{SERVICES[service]}/{path}"
    body = await request.body()
    headers = {k:v for k,v in request.headers.items()
               if k.lower() not in {"host","content-length"}}
    headers["x-request-id"] = request.headers.get("x-request-id", "")
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.request(
                request.method, target,
                params=request.query_params,
                content=body,
                headers=headers,
            )
            try:
                content = response.json()
            except ValueError:
                content = {"detail": response.text}
            return JSONResponse(
                content=content,
                status_code=response.status_code,
                headers={"x-request-id": response.headers.get("x-request-id","")},
            )
        except httpx.TimeoutException:
            return JSONResponse({"detail":"Upstream timeout"}, status_code=504)
        except Exception as exc:
            log.exception("upstream failure: %s", exc)
            return JSONResponse({"detail":"Upstream unavailable"}, status_code=502)
