import os
import shutil
import base64

from fastapi import APIRouter, Depends
from AioSpider import tools
from AioSpider.cmd import CreateCommand, OptionsEn, OptionsS, OptionsT

from validator import *
from utils import to_json, WorkSpace, StatusTags, error_map


router = APIRouter()


@router.post("/spider/create-cls1")
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


@router.post("/spider/create-cls2")
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


@router.post("/spider/remove-cls2")
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


@router.get("/spider/dir/get")
async def get_spider_path():
    """获取爬虫分类"""

    data = [
        (cls.name, x.name, y.name, [z.name for z in y.iterdir() if z.is_file()])
        for cls in WorkSpace.iterdir() if cls.is_dir()
        for x in cls.iterdir() if x.is_dir()
        for y in (x / 'spider').iterdir() if y.is_dir()
    ]

    return to_json(data=data)


@router.post("/spider/create")
async def create_spider(params: dict = Depends(validate_spider_params1)):

    path = WorkSpace / params['cls1'] / params['cls2'] / 'spider' / params['site'] / (params['name'] + '.py')

    if not path.parent.exists():
        return to_json(msg=StatusTags.SpiderCreateError, status=error_map[StatusTags.SpiderCreateError])

    with open(path, 'wb') as f:
        f.write(base64.b64decode(params['content']))

    return to_json(data={'name': params['name']})


@router.post("/spider/delete")
async def delete_spider(params: dict = Depends(validate_spider_params2)):

    path = WorkSpace / params['cls1'] / params['cls2'] / 'spider' / params['site'] / params['name']

    if path.exists():
        path.unlink(missing_ok=True)

    return to_json(data={'name': params['name']})


@router.post("/spider/run")
async def run_spider(params: dict = Depends(validate_spider_params2)):

    work_path = WorkSpace / params['cls1'] / params['cls2']
    path = work_path.__class__('spider') / params['site'] / (params['name'] + '.py')

    cwd = os.getcwd()

    if not work_path.exists():
        return to_json(error_map[StatusTags.CreateProjectError], StatusTags.CreateProjectError)

    # 切换工作路径
    os.chdir(work_path)

    if not path.exists():
        return to_json(msg=StatusTags.SpiderNotFoundError, status=error_map[StatusTags.SpiderNotFoundError])

    tools.start_python_in_background(path, close=False)

    # 切回工作路径
    os.chdir(cwd)

    return to_json(data={'name': params['name']})
