from fastapi import APIRouter,UploadFile,File,FastAPI

import RAG_APP.RAG
from RAG_APP.sql_analyst import router as sql_analyst_router
from RAG_APP.main import router as authentication_router
from RAG_APP.bill_generated import router as bill_router
from RAG_APP.chatbot import router as chatbot_router
from RAG_APP.today_insight import router as today_insight_router

api=FastAPI()

# Initialize database on startup


from fastapi.middleware.cors import CORSMiddleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(RAG_APP.RAG.router,prefix="/rag",tags=["RAG"])
api.include_router(sql_analyst_router,prefix="/sql_analyst",tags=["SQL Analyst"])
api.include_router(authentication_router,prefix="/auth",tags=["Authentication"])
api.include_router(bill_router,prefix="/bill",tags=["Bill Generation"])
api.include_router(chatbot_router,prefix="",tags=["Chatbot"])
api.include_router(today_insight_router,prefix="",tags=["Today's Insight"])
@api.get("/")
async def root():
    return {"status": "operational", "message": "RAG API is running"}

@api.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "ok"}