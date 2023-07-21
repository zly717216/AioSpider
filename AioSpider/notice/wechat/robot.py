from typing import Optional

import requests


class Robot:
    """
    企业微信自定义应用机器人
    Args:
        eid: 企业ID
        secret: 应用的凭证密钥
    """

    def __init__(self, eid: str, secret: str):
        self.eid = eid
        self.secret = secret
        self._token = None

    @property
    def token(self):
        if self._token is None:
            self._token = self.get_token()
        return self._token

    def _request(self, url: str, params: dict) -> Optional[dict]:

        res = requests.get(url, params=params)

        if res.status_code == 200 and res.json()['errcode'] == 0:
            return res.json()
        else:
            print(f'请求失败，错误码：{res.json()["errcode"]}，错误原因：{res.json()["errmsg"]}')
            return None

    def get_token(self):
        """
        获取应用的access_token
        Returns:
            access_token
        """

        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        params = {
            'corpid': self.eid, 'corpsecret': self.secret
        }
        json_data = self._request(url, params=params)

        if json_data is not None:
            return json_data['access_token']
        else:
            return ''

    def get_user(self):
        """
        获取配置了客户联系功能的企业成员列表
        权限说明:
            企业需要使用“客户联系”secret或配置到“可调用应用”列表中的自建应用secret所获取的accesstoken来调用
            accesstoken如何获取:
                第三方应用需具有“企业客户权限->客户基础信息”权限
                第三方/自建应用只能获取到可见范围内的配置了客户联系功能的成员。
        Returns:
            配置了客户联系功能的成员userid列表
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get_follow_user_list'
        params = {'access_token': self.token}
        json_data = self._request(url, params=params)

        if json_data is not None:
            return json_data['follow_user']
        else:
            return []

    def get_customer(self, user_id: str):
        """
        获取客户列表
        Args:
            user_id: 用户ID
        Returns:
            外部联系人的userid列表
        """

        url = 'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/list'
        params = {
            'access_token': self.token, 'userid': user_id
        }
        json_data = self._request(url, params=params)

        if json_data is not None:
            return json_data['external_userid']
        else:
            return []

    def get_customer_info(self, user_id: str):
        """
        获取客户详情
        Args:
            user_id: 外部联系人的userid，注意不是企业成员的帐号
        Returns:
            客户详情
        """

        url = 'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get'
        params = {
            'access_token': self.token, 'external_userid': user_id
        }
        json_data = self._request(url, params=params)

        if json_data is not None:
            return json_data
        else:
            return {}

    def send(self, user_list):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_msg_template'
        params = {
            'access_token': self.token
        }
        data = {
            "chat_type": "single",
            "external_userid": user_list,
            "sender": "zhangliyuan",
            "allow_select": True,
            "text": {
                "content": "文本消息内容"
            },
            "attachments": []
        }
        res = requests.post(url, params=params, json=data)
        print(res.json())


if __name__ == '__main__':
    # robot = Robot('wwe69f36449bc17aa1', 'A94tFIxS44EVfdz5yxFmuGUkjpos63WQABBDlsU8WxE')
    robot = Robot('wwe69f36449bc17aa1', 'z8SjEuisVKG3gyNbd42fzZPJleUA5JZfK_nWP12Xuq0')
    # print(robot.get_customer(user_id='Zhangliyuan'))
    print(robot.get_customer_info(user_id='wmvecUMwAAcP4bQIM8NDkFwxFCflJkeQ'))
    robot.send(['wmvecUMwAAcP4bQIM8NDkFwxFCflJkeQ'])
    # robot.get_user()
