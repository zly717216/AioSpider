import os
import shutil

from fastapi import APIRouter, Depends
from AioSpider.cmd import CreateCommand, OptionsEn, OptionsS, OptionsT

from validator import *
from utils import to_json, WorkSpace, StatusTags, error_map


router = APIRouter()


@router.post("/spider/spider-cls/create-cls1")
async def create_spider_cls1(params: dict = Depends(validate_spider_cls_level1_params)):
    """创建爬虫一级分类"""

    cwd = os.getcwd()

    # 切换工作路径
    os.chdir(WorkSpace)

    # 创建分类
    if not (WorkSpace / params['cls1']).exists():
        (WorkSpace / params['cls1']).mkdir(parents=True, exist_ok=True)

    # 切回工作路径
    os.chdir(cwd)

    return to_json(data={'cls1': params['cls1']})


@router.post("/spider/spider-cls/create-cls2")
async def create_spider_cls2(params: dict = Depends(validate_spider_cls_level2_params)):
    """创建爬虫二级分类"""

    cwd = os.getcwd()

    if not (WorkSpace / params['cls1']).exists():
        return to_json(error_map[StatusTags.CreateProjectError], StatusTags.CreateProjectError)

    # 切换工作路径
    os.chdir(WorkSpace / params['cls1'])

    # 创建分类
    status = CreateCommand().create_project(params['cls2'])

    # 切回工作路径
    os.chdir(cwd)

    if status:
        return to_json(data={'cls2': params['cls2']})
    else:
        return to_json(error_map[StatusTags.CreateProjectError], StatusTags.CreateProjectError)


@router.post("/spider/spider-cls/delete")
async def delete_spider_cls(params: dict = Depends(validate_spider_cls_level2_params)):

    for cls2 in params['cls2'].split(','):
        if not cls2:
            continue
        if not (WorkSpace / params['cls1'] / cls2).exists():
            continue
        try:
            shutil.rmtree(WorkSpace / params['cls1'] / cls2)
        except PermissionError as e:
            print(e)

    if not cls2 or not list((WorkSpace / params['cls1']).iterdir()):
        try:
            shutil.rmtree(WorkSpace / params['cls1'])
        except PermissionError as e:
            print(e)

    return to_json(data={'cls1': params['cls1']})


@router.post("/spider/spider-cls/remove-cls2")
async def move_spider_cls2(params: dict = Depends(validate_spider_cls_level1_params2)):
    """移动爬虫二级分类"""

    if (WorkSpace / params['old_cls1']).exists() and (WorkSpace / params['old_cls1'] / params['cls2']).exists() and \
            (WorkSpace / params['new_cls1']).exists() and not (WorkSpace / params['new_cls1'] / params['cls2']).exists():
        try:
            shutil.move(
                str(WorkSpace / params['old_cls1'] / params['cls2']),
                str(WorkSpace / params['new_cls1'] / params['cls2'])
            )
        except Exception as e:
            print(e)

    return to_json(data={'cls2': params['cls2']})


@router.get("/spider/spider-cls/dir/get")
async def get_spider_cls_path():
    """获取爬虫分类"""

    data = {
        cls.name: [i.name for i in cls.iterdir() if i.is_dir()]
        for cls in WorkSpace.iterdir() if cls.is_dir()
    }

    return to_json(data=data)
