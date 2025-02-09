import traceback

from fastapi import FastAPI
from starlette.responses import JSONResponse

from .. import err


def handler(fastapi: FastAPI):
    @fastapi.exception_handler(err.ErrorIdException)
    async def exception_handler(request, exc: err.ErrorIdException):
        return JSONResponse(
            content=exc.to_error_res().dict(),
            status_code=exc.error_id.value.status_code
        )

    @fastapi.exception_handler(Exception)
    async def exception_handler(request, exc: Exception):
        print(traceback.format_exc())
        return JSONResponse(
            content=err.ErrorRes.create_by_exception(
                exc,
            ).dict(),
            status_code=err.ErrorIds.INTERNAL_ERROR.value.status_code
        )

    @fastapi.exception_handler(401)
    async def exception_handler(request, exc: Exception):
        return JSONResponse(
            content=err.ErrorRes.create_by_exception(
                exc, error_ids=err.ErrorIds.UNAUTHORIZED
            ).dict(),
            status_code=err.ErrorIds.UNAUTHORIZED.value.status_code
        )
