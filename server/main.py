from fastapi import FastAPI
from server.routers import chat, auth

app = FastAPI(title="Nazariya Backend")

# Include routes
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
