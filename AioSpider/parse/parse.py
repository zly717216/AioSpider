import re


class Parse:

    def __init__(self, arr):
        self.arr = arr

    def extract_first(self, default=''):
        return self.arr[0] if self.arr else default

    def extract_last(self, default=''):
        return self.arr[-1] if self.arr else default

    def extract(self):
        return self.arr
