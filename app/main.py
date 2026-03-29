from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.execution import router as execution_router

app = FastAPI()

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(execution_router)

@app.get("/")
def root():
    return {"message": "Manthan running"}