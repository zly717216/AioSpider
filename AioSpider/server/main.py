from fastapi import FastAPI

from routers.spider_cls import router as spiders_router
from routers.site import router as site_router
from routers.spider import router as spider_router
from utils import (
    error_info_exception_handler, validation_exception_handler, CustomHTTPException,
    RequestValidationError
)


app = FastAPI()

app.include_router(spiders_router)
app.include_router(site_router)
app.include_router(spider_router)
app.exception_handler(CustomHTTPException)(error_info_exception_handler)
app.exception_handler(RequestValidationError)(validation_exception_handler)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', port=10086, host='0.0.0.0')

