class Connector:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._connector = dict()

    def __getitem__(self, name):
        return getattr(self, name, None)

    def __setitem__(self, name, connect):
        setattr(self, name, connect)
        self._connector[name] = connect

    def __str__(self):
        return f'Connector({self._connector})'

    def __repr__(self):
        return f'Connector({self._connector})'

    def items(self):
        return [(k, v) for k, v in self._connector.items()]
