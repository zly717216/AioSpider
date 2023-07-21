__all__ = ['LoadModels']

import inspect
from typing import List, Type

from AioSpider import tools
from AioSpider.models import Model
from AioSpider.models import models


class LoadModels:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        instance.load_models()
        instance.update_models_from_db()
        return instance.models

    def __init__(self, spider, db_config):
        self.spider = spider
        self.db_config = db_config
        self.models = []

    def load_models(self) -> List[Type[Model]]:
        """加载所有非抽象类的模型"""

        try:
            models_module = __import__(self.spider.__module__)
        except Exception:
            models_module = __import__('models')

        self.models = [
            obj for obj in models_module.__dict__.values()
            if inspect.isclass(obj) and issubclass(obj, Model) and not obj.Meta.abstract
        ]

    def update_model_bases(self, name, model_list, db_type):

        for model_name in model_list:
            model = getattr(models, model_name)
            if db_type == 'Sqlite':
                base_model = models.SQLiteModel
            else:
                base_model = models.MySQLModel
            model.__bases__ = (base_model,)
            model.Meta = type(
                'Meta', (model.Meta,), {
                    k: v for k, v in base_model.Meta.__dict__.items() if v is not None and k != 'tb_name'
                })
            model.Meta.db = name
            self.models.append(model)

    def update_models_from_db(self):

        db_types = ['Sqlite', 'Csv', 'Mysql', 'Mongodb', 'File']

        for db_type in db_types:
            if hasattr(self.db_config, db_type) and getattr(self.db_config, db_type)['enabled']:
                for name, model_list in getattr(self.db_config, db_type)['installs'].items():
                    self.update_model_bases(name, model_list, db_type)
