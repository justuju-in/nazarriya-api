from fastapi import FastAPI
from server.routers import chat

app = FastAPI(title="Nazariya Backend")

# Include routes
app.include_router(chat.router)
