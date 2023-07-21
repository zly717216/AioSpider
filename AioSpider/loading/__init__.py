from AioSpider.loading.load_settings import LoadSettings
from AioSpider.loading.load_log import LoadLogger
from AioSpider.loading.load_browser import LoadBrowser
from AioSpider.loading.load_middleware import LoadMiddleware
from AioSpider.loading.load_database import LoadDatabase
from AioSpider.loading.load_models import LoadModels
from AioSpider.loading.load_notice import LoadNotice


class BootLoader:

    def reload_settings(self, spider):
        return LoadSettings(spider)

    def reload_logger(self, spider_name, settings):
        if hasattr(settings, 'LoggingConfig'):
            config = settings.LoggingConfig
        else:
            from AioSpider import settings
            config = settings.LoggingConfig
        LoadLogger(spider_name, config)
    
    def reload_middleware(self, spider, settings, request_pool):
        return LoadMiddleware(spider, settings, request_pool)
    
    async def reload_connection(self, settings):
        return await LoadDatabase(settings)
    
    def reload_driver(self, settings):
        return LoadBrowser(settings)
    
    def reload_models(self, spider, settings):
        return LoadModels(spider, settings.DataBaseConfig)

    def reload_notice(self, spider, settings):
        return LoadNotice(spider, settings.MessageNotifyConfig)
