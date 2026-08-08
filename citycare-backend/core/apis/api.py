from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from core.apis.routes.doctor_router import doctor_router
from core.apis.routes.auth_router import auth_router
from core.apis.routes.user_router import user_router
from core.database.database import (
    connect_to_mongo,
    close_mongo_connection,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="CityCare Clinic API",
    version="1.0.0",
    description="Appointment Booking System for CityCare Clinic",
    lifespan=lifespan,
    redoc_url="/documentation",
)
 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["Authentication"])
app.include_router(user_router, tags=["Patient"])
app.include_router(doctor_router, tags=["Doctor"])

@app.get("/")
async def root():
    return {"message": "Welcome to CityCare Clinic API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="CityCare Clinic API",
        version="1.0.0",
        description="Appointment Booking System for CityCare Clinic",
        routes=app.routes,
    )

    # Inject BearerAuth security scheme — no OAuth2, plain HTTP Bearer
    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Paste the access_token returned by POST /v1/users/login",
        }
    }

    # Apply BearerAuth to every route that has an 'authorization' header parameter
    for path_data in openapi_schema.get("paths", {}).values():
        for operation in path_data.values():
            parameters = operation.get("parameters", [])
            has_auth_header = any(
                p.get("name", "").lower() == "authorization"
                and p.get("in") == "header"
                for p in parameters
            )
            if has_auth_header:
                # Remove the raw header param — Swagger will send it via the lock icon
                operation["parameters"] = [
                    p for p in parameters
                    if not (
                        p.get("name", "").lower() == "authorization"
                        and p.get("in") == "header"
                    )
                ]
                operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
