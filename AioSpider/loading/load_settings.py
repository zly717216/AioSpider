__all__ = ['LoadSettings']

from AioSpider import GlobalConstant
from AioSpider.exceptions import SystemConfigError


class LoadSettings:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.read_settings(*args, **kwargs)
        instance.sts_check()
        return instance.settings

    def disable_exclusive_configs(self, attr):
        """禁用配置中的互斥项"""

        for i in [i for i in dir(attr) if not i.startswith('__')]:
            config = getattr(attr, i, {})
            if isinstance(config, dict) and 'enabled' in config:
                config['enabled'] = False

    def merge_config_attrs(self, new_config, old_config):
        """合并新旧配置属性"""

        if new_config is None:
            return
        for k in [i for i in dir(new_config) if not i.startswith('__')]:
            if not hasattr(old_config, k):
                setattr(old_config, k, getattr(new_config, k))
            elif isinstance(getattr(old_config, k), dict):
                getattr(old_config, k).update(getattr(new_config, k))
            elif callable(getattr(old_config, k)):
                self.merge_config_attrs(getattr(new_config, k), getattr(old_config, k))
            else:
                setattr(old_config, k, getattr(new_config, k))

    def merge_browser_configs(self, new_config, old_config):
        """合并浏览器配置"""

        if new_config is None:
            return old_config

        for browser_name in ('Chromium', 'Firefox'):
            if hasattr(new_config, browser_name):
                new_browser = getattr(new_config, browser_name)
                old_browser = getattr(old_config, browser_name)

                # 如果启用了一个浏览器，则禁用另一个
                if getattr(new_browser, 'enabled', False):
                    setattr(getattr(old_config, self.other_browser_name(browser_name)), 'enabled', False)

                self.merge_config_attrs(new_browser, old_browser)

        return old_config

    def other_browser_name(self, browser_name):
        """获取另一个浏览器的名称"""

        return 'Firefox' if browser_name == 'Chromium' else 'Chromium'

    def cover_gts(self, sts):
        """覆盖系统配置"""

        gts = GlobalConstant().settings
        self.merge_config_attrs(sts, gts)
        return gts

    def cover_sts(self, spider, gts):
        """覆盖项目配置"""

        config_classes = [
            'SpiderRequestConfig', 'ConcurrencyStrategyConfig', 'ConnectPoolConfig',
            'DataFilterConfig', 'RequestFilterConfig', 'RequestProxyConfig'
        ]

        for config_cls_name in config_classes:
            spider_config_cls = getattr(spider, config_cls_name)
            if not [i for i in dir(spider_config_cls) if not i.startswith('__') and not i.endswith('__')]:
                continue

            gts_config_cls = getattr(gts, config_cls_name)
            if hasattr(gts_config_cls, 'exclusive'):
                self.disable_exclusive_configs(gts_config_cls)
            self.merge_config_attrs(spider_config_cls, gts_config_cls)

        gts.BrowserConfig = self.merge_browser_configs(getattr(spider, 'BrowserConfig'), gts.BrowserConfig)

        return gts

    def read_settings(self, spider):
        """读取配置"""

        self.settings = None

        # 项目settings
        sts = __import__('settings')

        # 爬虫配置优先级：爬虫settings > 项目settings > 系统settings
        sts = self.cover_gts(sts)
        sts = self.cover_sts(spider, sts)

        if not hasattr(sts.SystemConfig, 'AioSpiderPath'):
            raise Exception('settings.SystemConfig 中未配置 AioSpiderPath 工作路径')

        GlobalConstant().settings = sts
        self.settings = sts

    def sts_check(self):
        """检查配置"""

        # 检查系统配置
        cnf = self.settings.SystemConfig

        if not hasattr(cnf, 'AioSpiderPath'):
            raise SystemConfigError(flag=1)

        if not hasattr(cnf, 'BackendCacheEngine'):
            raise SystemConfigError(flag=2)
