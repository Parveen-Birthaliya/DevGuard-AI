
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="DevGuard AI",
    description="AI-Powered Code Review & Security Analysis",
    version="0.1.0")

# Configure CORS (Cross-Origin Resource Sharing)
# This allows your frontend (React) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint 
@app.get("/")
async def root():
    return {
        "message": "DevGuard AI API",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "devguard-ai"
    }


