import time

from fastapi import Request

from app.core.logger import logger


async def add_process_time_handler(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    logger.info(f"Request process time: {process_time} ")
    return response
