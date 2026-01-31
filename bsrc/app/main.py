# app/app.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger
from app.web.router import router as captcha_router
from app.utils import config

def create_app() -> FastAPI:
    my_app = FastAPI(
        title="ChemCaptcha Service",
        description="A dynamic, plugin-based chemical captcha service.",
        version="1.0.0"
    )

    my_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    my_app.include_router(captcha_router, prefix="/api")

    @my_app.get("/")
    async def root():
        return {
            "message": "ChemCaptcha Service is running",
            "mode": "DEV" if config.DEV_MOD else "PROD",
            "registered_plugins": list(config.PLUGINS.keys()) if hasattr(config, "PLUGINS") else "Loaded dynamically"
        }

    return my_app

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting server in {'DEV' if config.DEV_MOD else 'PROD'} mode...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=config.DEV_MOD)