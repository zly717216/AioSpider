from enum import IntEnum
from datetime import datetime, timedelta, time as dtime, date
from typing import Union, Callable, NewType, Optional

from AioSpider import tools
from AioSpider.models import TaskModel
from AioSpider.spider.spider import Spider


username = NewType('username', str)
password = NewType('password', str)
token = NewType('token', str)


class BatchLevel(IntEnum):

    SECOND = 0
    MINUTE = 1
    HOUR = 2
    DAY = 3
    WEEK = 4
    MONTH = 5
    SEASON = 6
    YEAR = 7


class BatchSpider(Spider):
    """
    批次爬虫，支持秒级、分钟级、小时级、天级、月级、年级批次定时
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        level: 爬虫批次级别
            1: 秒级
            2: 分钟级
            3: 小时级
            4: 天级
            5: 周级
            6: 月级
            7: 季级
            8: 年级批次定时
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    INTERVAL_LEVEL = {
        BatchLevel.SECOND: ('seconds', 1),
        BatchLevel.MINUTE: ('minutes', 1),
        BatchLevel.HOUR: ('hours', 1),
        BatchLevel.DAY: ('days', 1),
        BatchLevel.WEEK: ('days', 7),
    }

    def __init__(
            self,
            *,
            time: Union[datetime, str],
            interval: int,
            level: BatchLevel,
            username: str = None,
            password: str = None,
            cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None,
            call_end: Callable[[], bool] = None,
            call_login: Callable[[str, str], str] = None,
    ):

        super(BatchSpider, self).__init__(
            username=username, password=password, cookies=cookies, token=token, call_before=call_before,
            call_end=call_end, call_login=call_login,
        )
        if isinstance(time, str):
            time = tools.strtime_to_time(time, is_time=True)

        self.level = level
        self.interval = interval

        self.time = time
        self.next_time = self._init_next_time()

        self.task: TaskModel = None

        self.id: Optional[int] = None
        self.status: int = 0
        self.count: int = 0
        self.end_time: Optional[datetime] = None
        self.token: Optional[str] = token

    def spider_open(self):

        super(BatchSpider, self).spider_open()

        # # 判断爬虫是否存在，存在更新，不存在创建
        # if not SpiderModel.objects.filter(name=self.name).exists():
        #     spider = SpiderModel(
        #         name=self.name,
        #         site=self.source,
        #         target=self.target,
        #         description=self.description,
        #         dev_status=0,
        #         start_time=self.start_time,
        #         level=self.level,
        #         version=self.version,
        #         interval=self.interval
        #     )
        #     spider.save()
        # else:
        #     pass

    def create_task(self):
        self.task = TaskModel(spider=self.name, start_time=self.next_time)
        self.task.save()

    def is_time_to_run(self):
        return datetime.now().replace(microsecond=0) == self.next_time

    def get_next_time(self):
        return self.next_time + timedelta(**{
                self.INTERVAL_LEVEL[self.level][0]: self.INTERVAL_LEVEL[self.level][-1] * self.interval
            })

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            hour=self.time.hour, minute=self.time.minute,
            second=self.time.second, microsecond=0
        )

        if next_time < now:
            next_time += timedelta(**{
                self.INTERVAL_LEVEL[self.level][0]: self.INTERVAL_LEVEL[self.level][-1] * self.interval
            })

        return next_time


class BatchSecondSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, time: Union[dtime, str], interval: int = 1,
            username: str = None, password: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable[[username, password], token] = None,
    ):
        super().__init__(
            time=time, interval=interval, level=BatchLevel.SECOND, username=username,
            password=password, cookies=cookies, token=token, call_before=call_before,
            call_end=call_end, call_login=call_login
        )


class BatchMiniteSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, time: Union[dtime, str], interval: int = 2,
            username: str = None, password: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable[[username, password], token] = None,
    ):
        super().__init__(
            time=time, interval=interval, level=BatchLevel.MINUTE, username=username,
            password=password, cookies=cookies, token=token, call_before=call_before,
            call_end=call_end, call_login=call_login
        )


class BatchHourSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, time: Union[dtime, str], interval: int = 1, username: str = None, password: str = None,
            cookies: dict = None, token: str = None, call_before: Callable[[], bool] = None,
            call_end: Callable[[], bool] = None, call_login: Callable[[username, password], token] = None,
    ):
        super().__init__(
            time=time, interval=interval, level=BatchLevel.HOUR, username=username, password=password,
            cookies=cookies, token=token, call_before=call_before, call_end=call_end, call_login=call_login
        )


class BatchDaySpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, time: Union[dtime, str], interval: int = 1, username: str = None,
            password: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable[[username, password], token] = None,
    ):
        super(BatchDaySpider, self).__init__(
            time=time, interval=interval, level=BatchLevel.DAY, username=username, password=password,
            cookies=cookies, token=token, call_before=call_before, call_end=call_end, call_login=call_login
        )


class BatchWeekSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, weekday: int, time: Union[dtime, str], interval: int = 1,
            username: str = None, password: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable[[username, password], token] = None,
    ):
        self.weekday = weekday
        super().__init__(
            time=time, interval=interval, username=username, level=BatchLevel.WEEK,
            password=password, cookies=cookies, token=token, call_before=call_before,
            call_end=call_end, call_login=call_login
        )

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            hour=self.time.hour, minute=self.time.minute,
            second=self.time.second, microsecond=0
        )
        while True:
            if next_time.weekday() == self.weekday:
                break
            tmp_date = tools.before_day(now=next_time, before=-1, is_date=True)
            next_time = next_time.replace(
                year=tmp_date.year, month=tmp_date.month, day=tmp_date.day
            )

        if next_time < now:
            next_time += timedelta(**{
                self.INTERVAL_LEVEL[self.level][0]: self.INTERVAL_LEVEL[self.level][-1] * self.interval
            })

        return next_time


class BatchMonthSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, day: int, time: Union[dtime, str], interval: int = 1,
            username: str = None, password: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable[[username, password], token] = None,
    ):

        self.day = day

        super().__init__(
            time=time, interval=interval, level=BatchLevel.MONTH, username=username,
            password=password, cookies=cookies, token=token, call_before=call_before,
            call_end=call_end, call_login=call_login
        )

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            day=self.day, hour=self.time.hour, minute=self.time.minute,
            second=self.time.second, microsecond=0
        )

        if next_time < now:
            next_time = tools.get_next_month_same_day(next_time)

        return next_time

    def get_next_time(self):
        return tools.get_next_month_same_day(self.next_time)


class BatchSeasonSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, *, date: Union[date, str], time: Union[dtime, str], interval: int = 1,
            username: str = None, password: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable[[username, password], token] = None,
    ):

        if isinstance(date, str):
            date = tools.strtime_to_time(date, is_date=True)

        self.date = date

        super().__init__(
            time=time, interval=interval, username=username, level=BatchLevel.SEASON,
            password=password, cookies=cookies, token=token, call_before=call_before,
            call_end=call_end, call_login=call_login
        )

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            year=self.date.year, month=self.date.month, day=self.date.day,
            hour=self.time.hour, minute=self.time.minute, second=self.time.second,
            microsecond=0
        )

        if next_time < now:
            for _ in range(3):
                next_time = tools.get_next_month_same_day(next_time)

        return next_time

    def get_next_time(self):
        next_time = self.next_time
        for _ in range(3):
            next_time = tools.get_next_month_same_day(next_time)
        return next_time


class BatchYearSpider(BatchSpider):
    """
    日级爬虫
    Args:
        time: 爬虫启动时间
        interval: 爬虫批次时间间隔
        username: 登录用户名
        password: 登录密码
        cookies: 登录cookies
        token: 登录token
        call_before: 爬虫单次正式启动前调用
        call_end: 爬虫单次结束前调用
        call_login: 爬虫单次结束前调用，登录逻辑
    """

    def __init__(
            self, date: Union[date], time: Union[dtime, str], interval: int = BatchLevel.YEAR,
            username: str = None, password: str = None, cookies: dict = None, token: str = None,
            call_before: Callable[[], bool] = None, call_end: Callable[[], bool] = None,
            call_login: Callable[[username, password], token] = None,
    ):

        if isinstance(date, str):
            date = tools.strtime_to_time(date, is_date=True)

        self.date = date

        super().__init__(
            time=time, interval=interval, username=username, level=BatchLevel.YEAR,
            password=password, cookies=cookies, token=token, call_before=call_before,
            call_end=call_end, call_login=call_login
        )

    def _init_next_time(self) -> datetime:

        now = datetime.now()

        next_time = now.replace(
            year=self.date.year, month=self.date.month, day=self.date.day,
            hour=self.time.hour, minute=self.time.minute, second=self.time.second,
            microsecond=0
        )

        if next_time < now:
            next_time = now.replace(
                year=self.date.year + 1, month=self.date.month, day=self.date.day,
                hour=self.time.hour, minute=self.time.minute, second=self.time.second,
                microsecond=0
            )

        return next_time

    def get_next_time(self):
        return self.next_time.replace(
            year=self.next_time.year + 1, month=self.next_time.month, day=self.next_time.day,
            hour=self.next_time.hour, minute=self.next_time.minute, second=self.next_time.second,
            microsecond=0
        )
