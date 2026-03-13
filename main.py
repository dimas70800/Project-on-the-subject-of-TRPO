import logging

import uvicorn
from fastapi import FastAPI

from src.controllers.products import router as products_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="File Processing API",
    description="API для онлайн-магазина",
    version="1.0.0",
)

app.include_router(products_router)

@app.get("/")
async def root():
    return {
        "message": "Это API для онлайн-магазина",
    }

def main():
    logger.info('Started')
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

if __name__ == "__main__":
    main()