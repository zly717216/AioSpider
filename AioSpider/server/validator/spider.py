from typing import Optional
from fastapi import Form

from utils import CustomHTTPException, ErrorInfo, error_map, StatusTags


def validate_spider_params1(
        cls1: Optional[str] = Form(None), cls2: Optional[str] = Form(None),
        site: Optional[str] = Form(None), name: Optional[str] = Form(None),
        content: Optional[str] = Form(None)
):

    if cls1 is None or cls2 is None or site is None or name is None or content is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.InvalidParamsError], StatusTags.InvalidParamsError)
        )

    return {"cls1": cls1, "cls2": cls2, "site": site, "name": name, "content": content}


def validate_spider_params2(
        cls1: Optional[str] = Form(None), cls2: Optional[str] = Form(None),
        site: Optional[str] = Form(None), name: Optional[str] = Form(None)
):
    if cls1 is None or cls2 is None or site is None or name is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.InvalidParamsError], StatusTags.InvalidParamsError)
        )

    return {"cls1": cls1, "cls2": cls2, "site": site, "name": name}
