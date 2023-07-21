from typing import Optional
from fastapi import Form

from utils import CustomHTTPException, ErrorInfo, error_map, StatusTags


def validate_site_params1(
        cls1: Optional[str] = Form(None), cls2: Optional[str] = Form(None), site: Optional[str] = Form(None)
):

    if cls1 is None or cls2 is None or site is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.MissingParamsError], StatusTags.MissingParamsError)
        )

    return {"cls1": cls1, "cls2": cls2, "site": site}


def validate_site_params2(
        cls1: Optional[str] = Form(None), cls2: Optional[str] = Form(None), old_site: Optional[str] = Form(None),
        new_site: Optional[str] = Form(None)
):

    if cls1 is None or cls2 is None or old_site is None or new_site is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.MissingParamsError], StatusTags.MissingParamsError)
        )

    return {"cls1": cls1, "cls2": cls2, "old_site": old_site, "new_site": new_site}
