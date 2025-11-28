from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.endpoints import dashboard, resources, broadcast, analytics, inventory, reports

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Configuration
origins = [
    "http://localhost:5173", # React Frontend
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(resources.router, prefix=f"{settings.API_V1_STR}/resources", tags=["resources"])
app.include_router(broadcast.router, prefix=f"{settings.API_V1_STR}/broadcast", tags=["broadcast"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(inventory.router, prefix=f"{settings.API_V1_STR}/inventory", tags=["inventory"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "Welcome to Med Predict AI API"}
