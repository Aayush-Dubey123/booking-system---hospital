from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from core.apis.routes.doctor_router import doctor_router
from core.apis.routes.auth_router import auth_router
from core.apis.routes.user_router import user_router
from core.apis.routes.hospital_router import hospital_router
from core.apis.routes.superadmin_router import superadmin_router
from core.apis.routes.chatbot_router import chatbot_router
from core.apis.routes.prescription_router import prescription_router
from core.database.database import (
    connect_to_mongo,
    close_mongo_connection,
    get_engine,
)
from core.models.user_model import User
from common.auth import encrypt_password
from core.mcp import mcp

mcp_app = mcp.http_app(path="/")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    
    engine = get_engine()

    # ── Auto-seed superadmin ───────────────────────────────────────────────
    existing_admin = await engine.find_one(User, User.email == "superadmin@citycare.com")
    if not existing_admin:
        superadmin = User(
            first_name="Super",
            last_name="Admin",
            email="superadmin@citycare.com",
            password=encrypt_password("admin1234"),
            role="superadmin",
            status="active"
        )
        await engine.save(superadmin)

    # ── Auto-seed doctor1@example.com → citycare-ngp hospital ─────────────
    from core.models.hospital_model import Hospital
    existing_doctor = await engine.find_one(User, User.email == "doctor1@example.com")
    if not existing_doctor:
        # Find the hospital whose name contains 'ngp' (case-insensitive)
        all_hospitals = await engine.find(Hospital)
        target_hospital = next(
            (h for h in all_hospitals if "ngp" in h.name.lower()), None
        )
        if target_hospital:
            doctor = User(
                first_name="Doctor",
                last_name="One",
                email="doctor1@example.com",
                password=encrypt_password("pass-ADAYUSH1"),
                role="doctor",
                status="active",
                hospital_id=str(target_hospital.id),
            )
            await engine.save(doctor)
    else:
        # If doctor exists but hospital_id is missing, assign to ngp hospital
        if not existing_doctor.hospital_id:
            from core.models.hospital_model import Hospital
            all_hospitals = await engine.find(Hospital)
            target_hospital = next(
                (h for h in all_hospitals if "ngp" in h.name.lower()), None
            )
            if target_hospital:
                existing_doctor.hospital_id = str(target_hospital.id)
                await engine.save(existing_doctor)

    async with mcp_app.router.lifespan_context(mcp_app):
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
app.include_router(hospital_router, tags=["Hospital"])
app.include_router(superadmin_router, tags=["Superadmin"])
app.include_router(chatbot_router, tags=["Chatbot"])
app.include_router(prescription_router, tags=["Prescription"])

app.mount("/mcp", mcp_app)

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
