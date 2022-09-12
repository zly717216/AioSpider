import sys
from pathlib import Path
from AioSpider.template import create_project as cpj
from AioSpider.template import gen_spider as gs


argv = sys.argv
# aioSpider options value [-argv]


# 创建项目 aioSpider createProject project
def create_project(name):

    items = cpj(name)

    for item in items:
        if item['type'] == 'dir' and not item['path'].exists():
            item['path'].mkdir(parents=True, exist_ok=True)

    for item in items:
        if item['type'] == 'file' and not item['path'].exists():
            item['path'].write_text(item['text'], encoding='utf-8')


# 创建项目 aioSpider genSpider spider
def gen_spider(args):

    name = args[2]
    if len(args) == 4:
        start_url = args[3]
    else:
        start_url = None

    spider_text = gs(name, start_url)
    path = Path().cwd() / f'spider/{name}.py'
    if not path.exists():
        path.write_text(spider_text, encoding='utf-8')


if argv[1] == 'createProject':
    create_project(argv[2])

elif argv[1] == 'genSpider':
    gen_spider(argv)
