from fastapi import FastAPI
from server.routers import chat, auth
from server.utils.logging import LoggingMiddleware

app = FastAPI(title="Nazariya Backend")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routes
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Add root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Nazariya Backend API", "status": "running"}
