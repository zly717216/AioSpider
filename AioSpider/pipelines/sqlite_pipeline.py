import os
import asyncio
from importlib import import_module

from .pipeline import Pipeline
from AioSpider.models import SQLiteModel


class SqlitePipeline(Pipeline):

    is_async = True
    model = None

    def __init__(self, *args, **kwargs):
        super(SqlitePipeline, self).__init__(*args, **kwargs)
        self._models = import_module(os.getcwd().split('\\')[-1] + '.models')

    def spider_open(self):
        pass

    def spider_close(self):
        asyncio.create_task(getattr(self._models, self.model).close())

    async def process_item(self, item):

        if self.model and not hasattr(self._models, self.model):
            return item

        if isinstance(item, dict):
            model = getattr(self._models, self.model)(item)
            for f in model._check_attr_():
                setattr(model, f, item.get(f))

            await model.save()

        if isinstance(item, getattr(self._models, self.model)):
            await item.save()

        return item

