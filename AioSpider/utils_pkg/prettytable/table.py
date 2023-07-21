from typing import List
from AioSpider.utils_pkg.prettytable import wcwidth


def print_format(string, way, width, fill=' '):
    count = wcwidth.wcswidth(string) - len(string)
    width = width - count if width >= count else 0
    return '{0:{1}{2}{3}}'.format(string, fill, way, width)


class PrettyTable:

    def __init__(self, item: List[dict]):
        self.item = item
        self.title = list(item[0].keys())
        self.width = self.make_width()
        self.string = self.create_table()

    def make_width(self):
        item = {}
        data_list = []
        for i in self.title:
            data = [str(j[i]) for j in self.item]
            data.insert(0, i)
            data_list.append(data)
        for i in data_list:
            length = [len(str(j)) for j in i]
            item[i[0]] = int(max(length) * 2.5) if max(length) * 2.5 >= 10 else 12
        return item

    def create_table(self):
        string = ''

        # 表头第一行
        string += self.first_line()
        # 表头
        string += self.table_headers()
        # 表头第三行
        string += self.first_line()
        # 表格
        string += self.table_body()
        # 结尾
        string += self.first_line()

        return string[:-1]

    def first_line(self):
        string = ''
        for i in self.title:
            string += '+' + print_format('', '^', self.width[i], '-')
        string += '+\n'
        return string

    def table_headers(self):
        string = ''
        for i in self.title:
            string += '|' + print_format(i, '^', self.width[i])
        string += '|\n'
        return string

    def table_body(self):
        string = ''
        for index, i in enumerate(self.item):
            for j in i:
                string += '|' + print_format(str(i[j]), '^', self.width[j])
            string += '|\n'
        return string

    def __str__(self):
        return self.string

    def __repr__(self):
        return str(self)
