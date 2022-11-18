from AioSpider import tools, GlobalConstant

from .field import Field, AutoIntField, BoolField, DateTimeField


class FieldItem(dict):

    db = 'DEFAULT'
    table = None


class Model:

    encoding = None
    order = None
    commit_size = None
    db = 'DEFAULT'

    def __init__(self, item=None):
        if item is not None:
            for f in self._get_field():
                setattr(self, f, item.get(f))

    def __setattr__(self, key, value):

        if key.startswith('_') or key.endswith('_'):
            return

        o = getattr(self, key, Field)
        o._value = value
        o.db_column = key
        o._check_value()

    @property
    def __name__(self) -> str:

        name_type = getattr(GlobalConstant().settings, 'MODEL_NAME_TYPE', None)
        if name_type == 'lower':
            name = self.__class__.__name__.replace('model', '').replace('Model', '')
            return name.lower()
        elif name_type == 'upper':
            name = self.__class__.__name__.replace('model', '').replace('Model', '')
            return name.upper()
        else:
            name = self.__class__.__name__.replace('model', '').replace('Model', '')
            name = tools.re(regx='[A-Z][^A-Z]*', text=name)
            name = [i.lower() for i in name]
            return '_'.join(name)

    def _order(self):
        if self.order is None:
            self.order = [i for i in dir(self) if isinstance(getattr(self, i), Field)]
        return self.order

    def _get_field(self):
        """获取模型字段"""

        attr = [i for i in dir(self) if isinstance(getattr(self, i), Field)]

        if self._order() and hasattr(self._order(), '__iter__'):
            order = self._order()
            for i in attr:
                if i not in order:
                    order.append(i)
            attr = order

        if 'id' in attr:
            attr.remove('id')
            attr.insert(0, 'id')

        return attr

    def _make_item(self):

        item = FieldItem()
        item.db = self.db
        item.table = self.__name__

        for f in self._get_field():
            field_obj = getattr(self, f, None)
            if isinstance(field_obj, Field) and field_obj.is_save:
                item[f] = getattr(getattr(self, f, None), '_value', None)
            else:
                item[f] = None

        if 'id' in item:
            item.pop('id')

        return item

    async def save(self):

        if GlobalConstant.database is None:
            return None

        await GlobalConstant().datamanager.commit(self)


class ABCModel(Model):

    is_delete = BoolField(name='逻辑删除')
    create_time = DateTimeField(name='创建时间')
    update_time = DateTimeField(name='更新时间')


class SQLiteModel(Model):
    id = AutoIntField(name='id', db_index=True)


class SQLiteModelICU(ABCModel):
    id = AutoIntField(name='id', db_index=True)


class MySQLModel(Model):
    id = AutoIntField(name='id', db_index=True, auto_field='AUTO_INCREMENT')


class MySQLModelICU(ABCModel):
    id = AutoIntField(name='id', db_index=True, auto_field='AUTO_INCREMENT')


class CSVModel(Model):
    pass


class CSVModelICU(ABCModel):
    pass
