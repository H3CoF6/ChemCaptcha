import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger
from app.web.router import router as captcha_router
from app.utils import config
from app.utils.config import DIST_DIR

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

    @my_app.get("/api/health")
    async def root():
        return {
            "message": "ChemCaptcha Service is running",
            "mode": "DEV" if config.DEV_MOD else "PROD",
            "registered_plugins": list(config.PLUGINS.keys()) if hasattr(config, "PLUGINS") else "Loaded dynamically"
        }

    if os.path.exists(DIST_DIR):
        my_app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")

        @my_app.get("/favicon.ico")
        async def favicon():
            return FileResponse(os.path.join(DIST_DIR, "favicon.ico"))

        @my_app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not Found")

            return FileResponse(os.path.join(DIST_DIR, "index.html"))
    else:
        logger.warning(f"Dist directory not found at {DIST_DIR}. Frontend will not be served.")

    return my_app

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting server in {'DEV' if config.DEV_MOD else 'PROD'} mode...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=config.DEV_MOD)