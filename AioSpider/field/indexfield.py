__all__ = [
    'SpatialIndexField', 'FullTextIndexField', 'UniqueIndexField', 'NormalIndexField',
    'UnionIndexField', 'UniqueUnionIndexField'
]

from typing import Union


class IndexMeta:

    def __init__(self, tb_name: str, field_name: Union[str, list]):
        self.tb_name = tb_name
        self.field_name = field_name


class SpatialIndexField(IndexMeta):
    """空间索引"""

    def index_mysql(self):
        index_name = f'spatial_idx_{self.field_name}'
        return f'SPATIAL INDEX `{index_name}` (`{self.field_name}`)'


class FullTextIndexField(IndexMeta):
    """全文索引"""

    def index_mysql(self):
        index_name = f'fulltext_idx_{self.field_name}'
        return f'FULLTEXT INDEX `{index_name}` (`{self.field_name}`)'


class UniqueIndexField(IndexMeta):

    def index_mysql(self):
        index_name = f'unique_idx_{self.field_name}'
        return f'UNIQUE INDEX `{index_name}` (`{self.field_name}`)'

    def index_sqlite(self):
        index_name = f'unique_idx_{self.tb_name}_{self.field_name}'
        return f'CREATE UNIQUE INDEX IF NOT EXISTS `{index_name}` ON `{self.tb_name}` (`{self.field_name}`)'


class NormalIndexField(IndexMeta):

    def index_mysql(self):
        index_name = f'idx_{self.field_name}'
        return f'INDEX `{index_name}` (`{self.field_name}`)'

    def index_sqlite(self):
        index_name = f'idx_{self.tb_name}_{self.field_name}'
        return f'CREATE INDEX IF NOT EXISTS `{index_name}` ON `{self.tb_name}` (`{self.field_name}`)'


class UnionIndexField(IndexMeta):

    def index_mysql(self):
        index_name = f'union_idx_{"_".join(self.field_name)}'
        columns = ", ".join([f'`{i}`' for i in self.field_name])
        return f'INDEX `{index_name}` ({columns})'

    def index_sqlite(self):
        index_name = f'union_idx_{self.tb_name}_{"_".join(self.field_name)}'
        columns = ", ".join([f'`{i}`' for i in self.field_name])
        return f'CREATE INDEX IF NOT EXISTS `{index_name}` ON `{self.tb_name}` ({columns})'


class UniqueUnionIndexField(IndexMeta):

    def index_mysql(self):
        index_name = f'union_idx_{"_".join(self.field_name)}'
        columns = ", ".join([f'`{i}`' for i in self.field_name])
        return f'UNIQUE INDEX `{index_name}` ({columns})'

    def index_sqlite(self):
        index_name = f'union_idx_{self.tb_name}_{"_".join(self.field_name)}'
        columns = ", ".join([f'`{i}`' for i in self.field_name])
        return f'CREATE UNIQUE INDEX `{index_name}` ON `{self.tb_name}` ({columns})'
