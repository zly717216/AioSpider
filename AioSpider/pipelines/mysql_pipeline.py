from AioSpider.models import models
from AioSpider import GlobalConstant

from .pipeline import Pipeline


class MySQLPipeline(Pipeline):

    is_async = True
    model = None

    def __init__(self, *args, **kwargs):
        super(MySQLPipeline, self).__init__(*args, **kwargs)
        self._models = None

    def spider_open(self):
        pass

    def spider_close(self):
        pass

    async def process_item(self, item):

        if self._models is None:
            self._models = GlobalConstant().models

        if self.model and not hasattr(self._models, self.model):
            return item

        if isinstance(item, dict):
            model = getattr(self._models, self.model)(item)
            for f in model._check_attr_():
                setattr(model, f, item.get(f))

            await model.save()

        if isinstance(item, models.Model) and self.model == item.__class__.__name__:
            await item.save()

        return item

