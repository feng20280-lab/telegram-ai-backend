from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import accounts, chats, ai

app = FastAPI(title="Telegram AI Reply Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(chats.router, prefix="/chats", tags=["Chats"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])

@app.get("/")
def root():
    return {"status": "Telegram AI Backend is running"}
