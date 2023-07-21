__all__ = ['LoadBrowser']

from AioSpider import tools
from AioSpider import GlobalConstant


class LoadBrowser:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance.init_browser(*args, **kwargs)

    def _init_browser_instance(self, browser_config, browser_type):
        headless = browser_config.HeadLess
        executable_path = browser_config.ExecutePath
        binary_path = browser_config.BinaryPath
        log_level = browser_config.LogLevel
        disable_images = browser_config.DisableImages
        disable_javascript = browser_config.DisableJavaScript
        extension_path = browser_config.ExtensionPath
        proxy = browser_config.Proxy
        options = browser_config.Options
        user_agent = browser_config.UserAgent
        download_path = browser_config.DownloadPath
        profile_path = browser_config.ProfilePath

        if browser_type == "chromium":
            return tools.chromium_instance(
                executable_path=executable_path, binary_path=binary_path, headless=headless,
                proxy=proxy, options=options, extension_path=extension_path, user_agent=user_agent,
                download_path=download_path, profile_path=profile_path, disable_images=disable_images,
                disable_javascript=disable_javascript, log_level=log_level
            )
        elif browser_type == "firefox":
            return tools.firefox_instance(
                executable_path=executable_path, binary_path=binary_path, headless=headless,
                proxy=proxy, options=options, extension_path=extension_path, user_agent=user_agent,
                download_path=download_path, profile_path=profile_path, disable_images=disable_images
            )
        else:
            return None

    def init_browser(self, settings):

        if settings.BrowserConfig.Chromium.enabled:
            browser_config = settings.BrowserConfig.Chromium
            browser_type = "chromium"
        elif settings.BrowserConfig.Firefox.enabled:
            browser_config = settings.BrowserConfig.Firefox
            browser_type = "firefox"
        else:
            browser_config = None
            browser_type = None

        if browser_config:
            browser = self._init_browser_instance(browser_config, browser_type)
            GlobalConstant().browser = browser
            return browser
        else:
            return None
