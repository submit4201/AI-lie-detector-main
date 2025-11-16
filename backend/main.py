from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routers (use package-qualified imports so `import backend.main` works)
from backend.api.analysis_routes import router as analysis_router
from backend.api.session_routes import router as session_router
from backend.api.general_routes import router as general_router
from backend import config
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app_description = """
The AI Lie Detector API provides endpoints for analyzing audio content to detect potential deception.
It offers features like speech-to-text transcription, emotion analysis, and advanced AI-driven analysis using Google Gemini.
Session management is included to maintain conversation context.

**Key Features**:
- Audio analysis with deception indicators.
- Session-based conversation history and contextual analysis.
- Detailed breakdown of results including emotion, credibility, and linguistic patterns.
"""

app = FastAPI(
    title="AI Lie Detector API",
    version="1.0.1",
    description=app_description,
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Add CORS middleware
# In production, restrict this to the actual frontend domain
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(general_router, tags=["General"])
app.include_router(analysis_router, tags=["Analysis"])
app.include_router(session_router, prefix="/session", tags=["Session Management"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)