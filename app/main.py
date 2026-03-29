from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.execution import router as execution_router
from app.sankalp import router as sankalp_router

import os

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
app.include_router(sankalp_router)

# Health
@app.get("/")
def root():
    return {"message": "Manthan running"}


# 🔥 DEBUG (add this)
@app.get("/debug-env")
def debug_env():
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }