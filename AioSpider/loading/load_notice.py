__all__ = ['LoadNotice']

from AioSpider import robot


class LoadNotice:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        instance.init_robot()

    def __init__(self, spider, settings):
        self.spider = spider
        self.settings = settings

    def init_robot(self):

        robot_config = {
            i: getattr(self.settings, i) for i in dir(self.settings)
            if not i.startswith('__') and not i.endswith('__')
        }

        for name, config in robot_config.items():
            if not config.get('enabled'):
                continue
            robot.add_robot(
                name,
                self.spider,
                config={k: v for k, v in config.items() if k != 'enabled'}
            )
