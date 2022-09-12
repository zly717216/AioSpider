from pathlib import Path


def create_project(project: str) -> list:

    items = [{'path': Path(project), 'type': 'dir', 'text': ''}]
    path = Path(__file__).parent / 'project'

    for i in path.rglob('*'):
        if i.is_file():
            file = i.read_text(encoding='utf-8').replace('${project.upper}', project.title()).\
                replace('${project}', project)
            item = {
                'path': Path(project) / str(i).split('project\\')[-1].replace('.tpl', '.py'), 'type': 'file', 'text': file
            }
        else:
            item = {
                'path': Path(project) / str(i).split('project\\')[-1], 'type': 'dir', 'text': ''
            }

        items.append(item)

    return items


def gen_spider(spider, start_url=None):

    path = Path(__file__).parent / 'spider/spider.tpl'
    text = path.read_text(encoding='utf-8').replace('${spider.upper}', spider.title())
    text = text.replace('${spider}', spider)
    if start_url is None:
        text = text.replace('${start_urls}', '')
    else:
        text = text.replace('${start_urls}', f'"{start_url}"')

    return text
