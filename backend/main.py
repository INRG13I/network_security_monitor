from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.device_controller import router as device_router

app = FastAPI()

# Allow frontend (adjust origin in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the device API
app.include_router(device_router, prefix="/api")
