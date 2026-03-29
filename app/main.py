from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.execution import router as execution_router
from app.sankalp import router as sankalp_router  # ✅ ADD THIS

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(execution_router)
app.include_router(sankalp_router)  # ✅ ADD THIS

# Health
@app.get("/")
def root():
    return {"message": "Manthan running"}