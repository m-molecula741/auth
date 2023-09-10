import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.config import config
from app.core.logger import logger
from app.core.middleware import add_process_time_handler
from app.routers.routers import router_private, router_public
from redis import asyncio as aioredis
from app.pages.router import router as router_pages
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


def get_app() -> FastAPI:
    app = FastAPI(
        title=config.project_name,
        debug=config.debug,
        version=config.version,
        default_response_class=ORJSONResponse,
    )

    app.middleware("http")(add_process_time_handler)

    @app.on_event("startup")
    async def startup():
        app.state.redis = aioredis.from_url(config.redis_cache_url)
        FastAPICache.init(RedisBackend(app.state.redis), prefix="cache")
        logger.info("Conected to redis")

    @app.on_event("shutdown")
    async def shutdown():
        await app.state.redis.close()
        FastAPICache.reset()
        logger.info("Redis connection close")

    origins = [
        "http://127.0.0.1:8000"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
        allow_headers=[
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Authorization",
            "Access-Control-Allow-Credentials"
        ],
    )

    app.include_router(router_private, prefix="/private")
    app.include_router(router_public, prefix="/public")
    app.include_router(router_pages)
    app.mount("/static", StaticFiles(directory="app/static"), "static")

    return app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
