from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db
from app.api.endpoints import api_router, health_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing The Lenny Growth Assistant Backend...")
    init_db()
    logger.info(f"Active Provider: {settings.LLM_PROVIDER} | Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Shutting down The Lenny Growth Assistant Backend...")


app = FastAPI(
    title="The Lenny Growth Assistant API",
    description="Evidence-grounded conversational agent for Lenny Rachitsky's podcast and newsletter knowledge base.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
origins = settings.cors_origins_list
if not origins or "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}")
    # Never expose raw stack traces or internal secrets to client
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check server logs."},
    )


# Root health endpoint
@app.get("/health")
async def root_health():
    return await health_check()


# Mount API routes
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
