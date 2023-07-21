from pathlib import Path
from AioSpider import tools


def read_sts_tpl():
    path = Path(__file__).parent / 'settings.tpl'
    return path.read_text(encoding='utf-8')


def read_models_tpl():
    path = Path(__file__).parent / 'models.tpl'
    return path.read_text(encoding='utf-8')


def read_middleware_tpl():
    path = Path(__file__).parent / 'middleware.tpl'
    return path.read_text(encoding='utf-8')


def read_spider_tpl():
    path = Path(__file__).parent / f'spider.tpl'
    return path.read_text(encoding='utf-8')


def gen_project(project: str, settings=True) -> list:

    path = Path.cwd() / project

    if path.exists():
        return None
    else:
        path.mkdir(parents=True, exist_ok=True)

    return [
        {'path': path / 'spider', 'type': 'dir'},
        {'path': path / 'settings.py', 'type': 'file', 'text': read_sts_tpl() if settings else ''},
        {'path': path / 'models.py', 'type': 'file', 'text': read_models_tpl()},
        {'path': path / 'middleware.py', 'type': 'file', 'text': read_middleware_tpl()},
    ]


def gen_spider(name, name_en=None, start_urls=None, source=None, target=None):

    text = read_spider_tpl()
    text = text.replace('{{ name }}', name)

    if name_en is not None:
        text = text.replace('{{ name_en }}', name.title())
    else:
        if tools.is_chinese(name):
            text = text.replace('{{ name_en }}', tools.translate(name).title().replace(' ', ''))
        else:
            text = text.replace('{{ name_en }}', name.title())

    if start_urls is None:
        text = text.replace('\n    start_urls = {{ start_urls }}', '')
    else:
        text = text.replace('{{ start_urls }}', str(start_urls))
        
    if source is None:
        text = text.replace('{{ source }}', name)
    else:
        text = text.replace('{{ source }}', source)
        
    if target is None:
        text = text.replace('\n    target = {{ target }}', '')
    else:
        text = text.replace('{{ target }}', str(target))

    return text
