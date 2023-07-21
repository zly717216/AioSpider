import os
import base64
import hashlib
from pathlib import Path
from typing import Optional, List, Union

import requests
import pandas as pd
import dataframe_image as dfi


class Source:
    """
    卡片来源样式信息，不需要来源样式可不填写
    Args:
        icon: 来源图片的 url，非必填项
        desc: 来源图片的描述，建议不超过13个字，非必填项
        color: 来源文字的颜色，目前支持：0 灰色，1 黑色，2 红色，3 绿色，非必填项，默认为0
    """

    def __init__(self, icon: str = None, desc: str = None, color: int = 0):
        self.icon = icon or ''
        self.desc = desc or ''
        self.color = color

    @property
    def to_dict(self):
        return {"icon_url": self.icon, "desc": self.desc, "desc_color": self.color}


class MainTitle:
    """
    模版卡片的主要内容，包括一级标题和标题辅助信息
    Args:
        title: 一级标题，建议不超过26个字，非必填项
        desc: 标题辅助信息，建议不超过30个字，非必填项
    """

    def __init__(self, title: str = None, desc: str = None):
        self.title = title or ''
        self.desc = desc or ''

    @property
    def to_dict(self):
        return {"title": self.title, "desc": self.desc}


class HorizonContent:
    """
    嵌套字典二级标题+文本列表
    Args:
        type: 链接类型，非必填项
            0: 普通文本
            1: 跳转url
            2: 下载附件
            3: @员工
        key: 二级标题，建议不超过5个字，必填项
        url: 链接跳转的url，type是1时必填，非必填项
        value: 二级文本，如果type是2，该字段代表文件名称（要包含文件类型），建议不超过26个字，非必填项
        media_id: 附件的media_id，type是2时必填，非必填项
        user_id: 被@的成员的userid，type是3时必填，非必填项
    """

    def __init__(self, type: int = 0, key: str = None, **kwargs):

        self.type = type
        self.key = key or ''
        self.url = ''
        self.value = ''
        self.media_id = ''
        self.user_id = ''

        if type == 1:
            if 'url' in kwargs:
                self.url = kwargs['url']
            else:
                raise Exception('type 参数为1时，必填出入url参数')
        elif type == 2:
            if 'value' in kwargs:
                self.value = kwargs['value']
            else:
                raise Exception('type 参数为2时，必填出入value和media_id参数')
            if 'media_id' in kwargs:
                self.media_id = kwargs['media_id']
            else:
                raise Exception('type 参数为2时，必填出入value和media_id参数')
        if type == 3:
            if 'user_id' in kwargs:
                self.user_id = kwargs['user_id']
            else:
                raise Exception('type 参数为3时，必填出入user_id参数')
        else:
            pass

    @property
    def to_dict(self):
        return {
            "type": self.type, "keyname": self.key, "value": self.value, "url": self.url,
            "media_id": self.media_id, "userid": self.user_id
        }


class Jump:
    """
    跳转指引样式的列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过3
    Args:
        type: 跳转链接类型
            0: 不跳转
            1: 跳转url
            2: 跳转小程序，非必填项
        title: 文案内容，建议不超过13个字，必填项
        url: 跳转链接的url，type是1时必填
        appid: 跳转链接的小程序的appid，type是2时必填
        page_path: 跳转链接的小程序的page_path，type是2时选填
    """

    def __init__(self, type: int = 0, title: str = None, **kwargs):

        self.type = type
        self.title = title or ''
        self.url = ''
        self.appid = ''
        self.page_path = ''

        if type == 1:
            if 'url' in kwargs:
                self.url = kwargs['url']
            else:
                raise Exception('type 参数为1时，必填出入url参数')
        elif type == 2:
            if 'appid' in kwargs:
                self.appid = kwargs['appid']
            else:
                raise Exception('type 参数为2时，必填出入appid参数')

            if 'page_path' in kwargs:
                self.page_path = kwargs['page_path']
        else:
            pass

    @property
    def to_dict(self):
        return {
            "type": self.type, "title": self.title, "url": self.url,
            "appid": self.appid, "pagepath": self.page_path
        }


class CardAction:
    """
    点击卡片的跳转事件
    Args:
        type: 片跳转类型, 必填项
            1: 跳转url
            2: 打开小程序
        url: 跳转url，type是1时必填
        appid: 跳转小程序的appid，type是2时必填
        page_path: 跳转的小程序的pagepath，type是2时选填，非必填项
    """

    def __init__(self, type: int, **kwargs):

        self.type = type
        self.url = ''
        self.appid = ''
        self.page_path = ''

        if type == 1:
            if 'url' in kwargs:
                self.url = kwargs['url']
            else:
                raise Exception('type 参数为1时，必填出入url参数')
        elif type == 2:
            if 'appid' in kwargs:
                self.appid = kwargs['appid']
            else:
                raise Exception('type 参数为2时，必填出入appid参数')

            if 'page_path' in kwargs:
                self.page_path = kwargs['page_path']
        else:
            raise Exception('type 参数错误，type 取值 1、2')

    @property
    def to_dict(self):
        return {
            "type": self.type, "url": self.url, "appid": self.appid, "pagepath": self.page_path
        }


class EmphasisContent:
    """
    关键数据样式
    Args:
        title: 内容，建议不超过10个字，非必填项
        desc: 关键数据样式的数据描述内容，建议不超过15个字，非必填项
    """

    def __init__(self, title: str = None, desc: str = None):
        self.title = title or ''
        self.desc = desc or ''

    @property
    def to_dict(self):
        return {"title": self.title, "desc": self.desc}


class QuoteText:
    """
    关键数据样式
    Args:
        type: 引用文献样式区域点击事件，默认为0
            0: 没有点击事件
            1: 跳转 url
            2: 跳转小程序
        title: 标题，非必填项
        quote_text: 引用文案，非必填项
        url: 点击跳转的 url，type是1时必填
        appid: 点击跳转的小程序的 appid，type是2时必填
        page_path: 点击跳转的小程序的 page_path，type是2时选填
    """

    def __init__(self, *, type: int = 0, title: str = None, quote_text: str = None, **kwargs):

        self.type = type
        self.title = title or ''
        self.quote_text = quote_text or ''
        self.url = ''
        self.appid = ''
        self.page_path = ''

        if type == 1:
            if 'url' in kwargs:
                self.url = kwargs['url']
            else:
                raise Exception('type 参数为1时，必填出入url参数')
        elif type == 2:
            if 'appid' in kwargs:
                self.appid = kwargs['appid']
            else:
                raise Exception('type 参数为2时，必填出入appid参数')

            if 'page_path' in kwargs:
                self.page_path = kwargs['page_path']
        else:
            pass

    @property
    def to_dict(self):
        return {
            "type": self.type, "url": self.url, "appid": self.appid, "pagepath": self.page_path,
            "title": self.title, "quote_area": self.quote_text,
        }


class Article:
    """
    图文消息列表
    Args:
        title：标题，不超过512个字节，超过会自动截断
        description：描述，不超过128个字节，超过会自动截断
        url：点击后跳转的链接
        pic_url：图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图1068 * 455，小图150 * 150
    """

    def __init__(self, title: str, url: str, description: str = None, pic_url: str = None):
        self.title = title
        self.url = url
        self.description = description or ''
        self.pic_url = pic_url or ''

    @property
    def to_dict(self):
        return {
            "title": self.title, "description": self.description, "url": self.url, "picurl": self.pic_url
        }


class CardImage:
    """
    图片样式
    Args:
        url：图片的url
        aspect_ratio：图片的宽高比，宽高比要小于2.25，大于1.3，不填该参数默认1.3
    """

    def __init__(self, url: str, aspect_ratio: float = 1.3):
        self.url = url
        self.aspect_ratio = aspect_ratio

    @property
    def to_dict(self):
        return {
            "url": self.url, "aspect_ratio": self.aspect_ratio
        }


class ImageText:
    """
    左图右文样式
    Args:
        type: 左图右文样式区域点击事件
            0: 没有点击事件
            1: 跳转url
            2: 跳转小程序
        url: 图片的宽高比，点击跳转的url，type是1时必填
        appid: 点击跳转的小程序的appid，必须是与当前应用关联的小程序，type是2时必填
        page_path: 点击跳转的小程序的page_path，type是2时选填
        title: 标题
        desc: 描述
        image_url: 图片url
    """

    def __init__(self, *, image_url, type: int = 0, title: str = None, desc: str = None, **kwargs):

        self.image_url = image_url
        self.type = type
        self.desc = desc
        self.title = title or ''
        self.url = ''
        self.appid = ''
        self.page_path = ''

        if type == 1:
            if 'url' in kwargs:
                self.url = kwargs['url']
            else:
                raise Exception('type 参数为1时，必填出入url参数')
        elif type == 2:
            if 'appid' in kwargs:
                self.appid = kwargs['appid']
            else:
                raise Exception('type 参数为2时，必填出入appid参数')

            if 'page_path' in kwargs:
                self.page_path = kwargs['page_path']
        else:
            pass

    @property
    def to_dict(self):
        return {
            "type": self.type, "url": self.url, "appid": self.appid, "pagepath": self.page_path,
            "title": self.title, 'image_url': self.image_url,
            'desc': self.desc
        }


class VerticalContent:
    """
    卡片二级垂直内容
    Args:
        title: 卡片二级标题，建议不超过26个字
        desc: 二级普通文本，建议不超过112个字
    """

    def __init__(self, *, title: str = None, desc: str = None):
        self.desc = desc or ''
        self.title = title or ''

    @property
    def to_dict(self):
        return {"title": self.title, 'desc': self.desc}


class GroupRobot:

    domain = 'https://qyapi.weixin.qq.com'
    api = '/cgi-bin/webhook/send'

    def __init__(self, token):
        self.token = token

    def _request(self, data: dict):

        res = requests.post(
            url=self.domain + self.api,
            params={'key': self.token},
            json=data
        )

        if res.status_code == 200 and res.json().get('errcode') == 0:
            return True
        else:
            print('企业微信群聊机器人消息发送失败，原因：', res.json())

    def send_text(self, content: str, mentioned_list: list = None, mentioned_mobile_list: list = None):
        """
        发送文本消息
        Args:
            content: 消息内容
            mentioned_list: userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人。如：['zhangsan', '@all']
            mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        Return:
            content | False
        """

        data = {
            "msgtype": "text",
            "text": {
                "content": content, "mentioned_list": mentioned_list,
                "mentioned_mobile_list": mentioned_mobile_list
            }
        }

        return content if self._request(data) else False

    def send_text_card(
            self, *, main_title: MainTitle, action: CardAction, horizon_contents: Optional[List[HorizonContent]] = None,
            jump_list: Optional[List[Jump]] = None, source: Source = None, emphasis_content: EmphasisContent = None,
            quote_text: QuoteText = None, sub_title: str = None
    ):
        """
        发送模板消息卡片
        Args:
            main_title:	模版卡片的主要内容，包括一级标题和标题辅助信息，
            horizon_contents: 二级标题 + 文本列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过6
            action: 点击卡片的跳转事件
            jump_list: 跳转指引样式的列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过3
            source: 卡片来源，非必填项
            emphasis_content: 关键数据
            quote_text:	引用文献样式，建议不与关键数据共用
            sub_title:	二级普通文本，建议不超过112个字。模版卡片主要内容的一级标题main_title.title和二级普通文本sub_title_text必须有一项填写
        """

        main_title = main_title.to_dict
        action = action.to_dict
        jump_list = [i.to_dict for i in jump_list]

        if horizon_contents is None:
            horizon_contents = {}
        else:
            horizon_contents = [i.to_dict for i in horizon_contents]

        if source is None:
            source = {}
        else:
            source = source.to_dict

        if emphasis_content is None:
            emphasis_content = {}
        else:
            emphasis_content = emphasis_content.to_dict

        if quote_text is None:
            quote_text = {}
        else:
            quote_text = quote_text.to_dict

        if sub_title is None:
            sub_title = ''

        data = {
            "msgtype": "template_card",
            "template_card": {
                "card_type": "text_notice", "source": source, "main_title": main_title,
                "emphasis_content": emphasis_content, "quote_area": quote_text, "sub_title_text": sub_title,
                "horizontal_content_list": horizon_contents, "jump_list": jump_list, "card_action": action
            }
        }

        return True if self._request(data) else False

    def send_image_card(
            self, main_title: MainTitle, action: CardAction, card_image: CardImage = None,
            horizon_contents: Optional[List[HorizonContent]] = None, jump_list: Optional[List[Jump]] = None,
            source: Source = None, quote_text: QuoteText = None, image_text_area: ImageText = None,
            vertical_contents: List[VerticalContent] = None
    ):
        """
        发送模板图片卡片
        Args:
            main_title:	模版卡片的主要内容，包括一级标题和标题辅助信息，
            action: 点击卡片的跳转事件
            card_image: 图片样式
            horizon_contents: 二级标题 + 文本列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过6
            jump_list: 跳转指引样式的列表，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过3
            source: 卡片来源，非必填项
            quote_text:	引用文献样式，建议不与关键数据共用
            image_text_area: 左图右文样式
            vertical_contents: 卡片二级垂直内容，该字段可为空数组，但有数据的话需确认对应字段是否必填，列表长度不超过4
        """

        main_title = main_title.to_dict
        action = action.to_dict
        card_image = card_image.to_dict
        jump_list = [i.to_dict for i in jump_list]

        if horizon_contents is None:
            horizon_contents = {}
        else:
            horizon_contents = [i.to_dict for i in horizon_contents]

        if source is None:
            source = {}
        else:
            source = source.to_dict

        if image_text_area is None:
            image_text_area = {}
        else:
            image_text_area = image_text_area.to_dict

        if vertical_contents is None:
            vertical_contents = {}
        else:
            vertical_contents = [i.to_dict for i in vertical_contents]

        if quote_text is None:
            quote_text = {}
        else:
            quote_text = quote_text.to_dict

        data = {
            "msgtype": "template_card",
            "template_card": {
                "card_type": "news_notice", "source": source, "main_title": main_title,
                "card_image": card_image, "image_text_area": image_text_area, "quote_area": quote_text,
                "vertical_content_list": vertical_contents, "horizontal_content_list": horizon_contents,
                "jump_list": jump_list, "card_action": action
            }
        }

        return True if self._request(data) else False

    def send_markdown(self, content: str):
        """
        发送markdown文本消息
        Args:
            content: 消息内容
        Attr:
            标题:
                # 标题一
                ## 标题二
                ### 标题三
                #### 标题四
                ##### 标题五
                ###### 标题六
            加粗: **hello**
            行内代码段: `hello`
            引用: > 引用文字
            字体颜色(只支持3种内置颜色):
                <font color="info">绿色</font>
                <font color="comment">灰色</font>
                <font color="warning">橙红色</font>
        """

        data = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }

        return content if self._request(data) else False

    def send_image(self, path: Union[str, Path] = None, content: bytes = None):
        """
        发送图片
        Args:
            path: 图片路径
            content: 图片内容
        """

        if isinstance(path, str):
            path = Path(path)

        if path is not None and content is None:
            txt = path.read_bytes()
        elif path is None and content is not None:
            txt = content
        else:
            return False

        txt_md5 = hashlib.md5(txt).hexdigest()

        data = {
            "msgtype": "image",
            "image": {"base64": base64.b64encode(txt).decode(), "md5": txt_md5}
        }

        return True if self._request(data) else False

    def send_image_text(self, article_list: List[Article]):
        """
        发送图文消息
        Args:
            article_list: 图文消息，一个图文消息支持1到8条图文
        Return:
            True | False
        """

        article_list = [i.to_dict for i in article_list]

        data = {
            "msgtype": "news", "news": {"articles": article_list}
        }

        return True if self._request(data) else False

    def upload_file(self, path: Union[str, Path]):
        """
        上传文件
        Args:
            path: 文件路径
        Return:
            media_id
        """

        if isinstance(path, str):
            path = Path(path)

        data = {
            'Content-Type': 'application/octet-stream',
            'name': path.stem,
            'filename': path.name,
            'filelength': len(path.read_bytes())
        }

        res = requests.post(
            url='https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media',
            params={'key': self.token, 'type': 'file'},
            files={'file': path.read_bytes()},
            data=data,
        )

        return res.json()['media_id']

    def send_file(self, path: Union[str, Path]):
        """
        发送文件
        Args:
            path: 文件路径
        """

        data = {
            "msgtype": "file",
            "file": {"media_id": self.upload_file(path)}
        }
        return True if self._request(data) else False

    def send_table(self, data: Union[List[dict], pd.DataFrame], fontsize: int = 15, dpi: int = 600):
        """
        发送图片表格
        Args:
            data: 鸟哥数据
            fontsize: 字体大小
            dpi: 每英寸点数
        """

        if isinstance(data, list):
            df = pd.DataFrame([
                {'name': 'chal', 'age': '23', 'country': '中国', 'city': 'Shanghai'},
                {'name': 'charle', 'age': '29', 'country': 'China', 'city': 'Xuzhou'},
                {'name': 'jack', 'age': '32', 'country': 'United States', 'city': 'Washington'},
            ])
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise Exception('data参数必须为 list 或 DataFrame 类型')

        dfi.export(df, 'table.png', fontsize=fontsize, dpi=dpi)
        self.send_image('table.png')
        os.remove('table.png')


if __name__ == '__main__':
    # robot = GroupRobot('66b6eb15-fc45-40f9-b07c-81cf8ee900c5')
    robot = GroupRobot('b0ced49e-ee5a-4e9b-ab1f-e00124731076')
    # robot.send_text('世界，你好')
    # robot.send_text_card(
    #     main_title=MainTitle(title='预警通知', desc='爬虫结束预警通知'),
    #     action=CardAction(type=1, url="http://47.101.219.184:8887"),
    #     horizon_contents=[
    #         HorizonContent(key='爬虫名称', value='融资融券'),
    #         HorizonContent(key='预警等级', value='融资融券'),
    #         HorizonContent(key='入库数量', value='20000条'),
    #     ],
    #     jump_list=[
    #         Jump(type=0, title='查看详情')
    #     ],
    #     emphasis_content=EmphasisContent(title='INFO', desc='一般等级通知'),
    #     source=Source(
    #         icon="http://47.101.219.184:8887/static/main/tarkin-logo.gif?imageView2/1/w/80/h/80",
    #         desc='踏金数据',
    #         color=0
    #     )
    # )
    # robot.send_file(r'D:\companyspider\spider\新浪公告\baidu.py')
    robot.send_image(r'D:\companyspider\spider\新浪公告\微信截图_20230308132347.png')
