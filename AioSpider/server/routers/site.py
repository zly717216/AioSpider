import os
import shutil

from fastapi import APIRouter, Depends

from validator import *
from utils import to_json, WorkSpace, StatusTags, error_map


router = APIRouter()


@router.post("/site/create")
async def delete_site(params: dict = Depends(validate_site_params1)):
    """创建站点"""

    path = WorkSpace / params['cls1'] / params['cls2'] / 'spider' / params['site']

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return to_json(data={'site': params['site']})


@router.post("/site/delete")
async def delete_site(params: dict = Depends(validate_site_params1)):

    path = WorkSpace / params['cls1'] / params['cls2'] / 'spider' / params['site']

    if path.exists():
        shutil.rmtree(str(path))

    return to_json(data={'site': params['site']})


@router.get("/site/dir/get")
async def get_site_path():
    """获取爬虫分类"""

    data = [
        (cls.name, i.name, [j.name for j in (i / 'spider').iterdir() if j.is_dir()])
        for cls in WorkSpace.iterdir() if cls.is_dir()
        for i in cls.iterdir() if i.is_dir()
    ]

    return to_json(data=data)
