from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from AioSpider import tools
from AioSpider.constants import NoticeType
from AioSpider.notice._email import Email
from AioSpider.notice.wechat import GroupRobot


class Drawing:

    def __init__(self, spider, type, level, msg, size: tuple = None, bgc=(255, 255, 255)):

        self.spider = spider
        self.level = level
        self._msg = msg
        self.type = type
        self.width, self.height = size or (620, int(620 / 1.8))
        self.bgc = bgc
        self.line_spacing = 10
        self.font_path = str(Path(__file__).parent.parent / 'tools/font/微软雅黑.ttf')

    def get_msg(self, font):
        msg = ''
        length = 0
        for i in self._msg:
            *_, width, height = font.getbbox(i)
            length += width
            msg += i
            if length >= self.width * 0.6:
                msg += '\n'
                length = 0
                self.height += height + self.line_spacing
        return msg

    def draw_title(self, draw, loc):
        text_color = (0, 0, 0)
        font_size = 30
        font = ImageFont.truetype(self.font_path, font_size)
        draw.text(loc, self.type, font=font, fill=text_color)

    def draw(self):

        # 设置字体
        font_size = 20
        font = ImageFont.truetype(self.font_path, font_size)

        msg = self.get_msg(font)

        # 创建画布
        image = Image.new("RGB", (self.width, self.height), self.bgc)
        draw = ImageDraw.Draw(image)

        cols = ('爬虫', '主机', '时间', '级别')
        text = [
            self.spider,
            tools.get_ipv4(),
            tools.before_day(is_str=True),
            self.level,
        ]

        # 绘制文本
        x, y = 50, 50
        self.draw_title(draw, (x, y))

        y += self.line_spacing * 5

        for m, n in zip(cols, text):
            draw.text((x + 30, y), f"{m}：{n}", font=font, fill=(80, 80, 80))
            y += font_size + self.line_spacing

        for index, i in enumerate(msg.split('\n')):
            if index == 0:
                draw.text((x + 30, y), f"内容：{i}", font=font, fill=(80, 80, 80))
                y += font_size + self.line_spacing
                *_, width, _ = font.getbbox('内容：')
                x += width
            else:
                draw.text((x + 30, y), i, font=font, fill=(80, 80, 80))
                y += font_size + self.line_spacing

        image_binary = BytesIO()
        image.save(image_binary, format='PNG')

        with open(r'd:\\aa.png', 'wb') as f:
            f.write(image_binary.getvalue())

        return image_binary.getvalue()


class EmptyRobot:

    def debug(self, msg, warn: bool = False): ...

    def info(self, msg, warn: bool = False): ...

    def warning(self, msg, warn: bool = False): ...

    def error(self, msg, warn: bool = False): ...

    def critical(self, msg, warn: bool = False): ...


class RobotBase(EmptyRobot):

    def __init__(self, spider, platform, config):

        self.spider = spider
        self.platform = platform

        if platform == NoticeType.wechat:
            self.robot = GroupRobot(config['token'])
        elif platform == NoticeType.dingding:
            self.robot = GroupRobot(token)
        elif platform == NoticeType.email:
            self.robot = Email(
                smtp=config['smtp'], port=config['port'], from_email=config['sender'], token=config['token'],
                receiver=config['receiver']
            )
        else:
            raise TypeError('robot platform type error')

    def send(self, level, msg, warn: bool = False):

        if warn:
            notice_type = '预警'
        else:
            notice_type = '通知'

        content = Drawing(self.spider, notice_type, level, msg).draw()

        if self.platform == NoticeType.wechat:
            self.robot.send_image(content=content)
        elif self.platform == NoticeType.dingding:
            ...
        elif self.platform == NoticeType.email:
            self.robot.send_email(subject=self.spider, body=msg, attach=content)
        else:
            raise TypeError('robot platform type error')

    def debug(self, msg, warn: bool = False):
        self.send('调试', msg, warn=warn)

    def info(self, msg, warn: bool = False):
        self.send('信息', msg, warn=warn)

    def warning(self, msg, warn: bool = False):
        self.send('警告', msg, warn=warn)

    def error(self, msg, warn: bool = False):
        self.send('异常', msg, warn=warn)

    def critical(self, msg, warn: bool = False):
        self.send('崩溃', msg, warn=warn)


class Robot:

    def __init__(self):
        self.robots = {
            'aioSpiderRobot': EmptyRobot(),
        }

    def __getitem__(self, item):
        if item not in self.robots:
            return self.robots['aioSpiderRobot']
        return self.robots[item]

    def add_robot(self, nmae, spider, config):
        self.robots[nmae] = RobotBase(spider, config['type'], {k: v for k, v in config.items() if k != 'type'})

    def remove_robot(self, nmae):
        self.robots.pop(nmae)

    def debug(self, msg, warn: bool = False):
        self['system'].debug(msg, warn=warn)

    def info(self, msg, warn: bool = False):
        self['system'].info(msg, warn=warn)

    def warning(self, msg, warn: bool = False):
        self['system'].warning(msg, warn=warn)

    def error(self, msg, warn: bool = False):
        self['system'].error(msg, warn=warn)

    def critical(self, msg, warn: bool = False):
        self['system'].critical(msg, warn=warn)
