from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from backend.routers.products import router as product_router
from backend.routers.cart import router as cart_router
from backend.routers.wallet import router as wallet_router
from backend.routers.users import router as user_router

app = FastAPI(title="Kiosk Product API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(wallet_router)


# ------------------- OPENAPI SECURITY -------------------

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Kiosk Product API",
        version="1.0",
        description="API with JWT Auth",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path, methods in openapi_schema["paths"].items():
        if path in ["/openapi.json", "/docs", "/redoc"]:
            continue

        for method in methods.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
