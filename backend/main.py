from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =========================================================
# ROUTERS
# =========================================================

from routers.register import router as register_router
from routers.login import router as login_router
from routers.knowledge_base import router as knowledge_base_router
from routers.documents import router as documents_router
from routers.conversations import router as conversations_router


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="KnowledgeAI API",
    description="Backend API for the KnowledgeAI RAG application",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(register_router)
app.include_router(login_router)
app.include_router(knowledge_base_router)
app.include_router(documents_router)
app.include_router(conversations_router)


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def home():
    return {
        "message": "KnowledgeAI Backend is running"
    }