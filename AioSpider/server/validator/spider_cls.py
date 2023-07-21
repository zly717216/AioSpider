from typing import Optional
from fastapi import Form

from utils import CustomHTTPException, ErrorInfo, error_map, StatusTags


def validate_spider_cls_level1_params(cls1: Optional[str] = Form(None)):
    """验证一级分类参数"""

    if cls1 is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.MissingParamsError], StatusTags.MissingParamsError)
        )

    return {"cls1": cls1}


def validate_spider_cls_level1_params1(old_name: Optional[str] = Form(None), new_name: Optional[str] = Form(None)):
    """验证一级分类参数"""

    if old_name is None or new_name is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.MissingParamsError], StatusTags.MissingParamsError)
        )

    return {"old_name": old_name, "new_name": new_name}


def validate_spider_cls_level1_params2(
        old_cls1: Optional[str] = Form(None), new_cls1: Optional[str] = Form(None), cls2: Optional[str] = Form(None)
):
    """验证一级分类参数"""

    if old_cls1 is None or new_cls1 is None or cls2 is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.MissingParamsError], StatusTags.MissingParamsError)
        )

    return {'old_cls1': old_cls1, 'new_cls1': new_cls1, 'cls2': cls2}


def validate_spider_cls_level2_params(cls1: Optional[str] = Form(None), cls2: Optional[str] = Form(None)):
    """验证二级分类参数"""

    if cls1 is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.MissingParamsError], StatusTags.MissingParamsError)
        )

    return {"cls1": cls1, "cls2": cls2 or ''}


def validate_spider_cls_level2_params1(
        cls1: Optional[str] = Form(None), old_name: Optional[str] = Form(None), new_name: Optional[str] = Form(None)
):
    """验证二级分类参数"""

    if cls1 is None or old_name is None or new_name is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.MissingParamsError], StatusTags.MissingParamsError)
        )

    return {"cls1": cls1, "old_name": old_name, 'new_name': new_name}


def validate_spider_cls_create_params(
    name: Optional[str] = Form(None), auto_config: Optional[bool] = Form(None)
):

    if name is None or auto_config is None:
        raise CustomHTTPException(
            ErrorInfo(error_map[StatusTags.MissingParamsError], StatusTags.MissingParamsError)
        )

    return {"auto_config": auto_config, "name": name}
