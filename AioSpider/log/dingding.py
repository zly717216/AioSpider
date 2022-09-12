from datetime import datetime
import json

import requests

from Frame.log import logger


def send_dingding_msg(content=None):
    robot_id_list = [
        # 'a5d1fdb05382fb7ffe118285ceaee21bfc526d6e0768c0f02eff8f82a8e5c48d',
        # '63b322cad1e45bbf4dceefcba5848591b32f5e6a74b7a62bd2745633dcf1c7c3',
        'f89e4fd00cb8ba7b1f33003b748b6c7882acc64d630eb6f703b800e261be3ef3',
    ]

    if content is None:
        content = '空空如也'

    msg = {
        "msgtype": "text",
        "text": {"content": datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t\t' + content}
    }
    headers = {"Content-Type": "application/json;charset=utf-8"}

    for robot_id in robot_id_list:
        url = 'https://oapi.dingtalk.com/robot/send?access_token=' + robot_id

        body = json.dumps(msg)
        res = requests.post(url, data=body, headers=headers)

        if res.json()['errcode'] == 0:
            logger.info('钉钉发送成功')
        else:
            print(res.text)
            logger.warning('钉钉发送失败')


if __name__ == '__main__':

    # content = 'Hello，我是韭菜收割机'
    content = '000411   英特集团\n001202	炬申股份\n002605	姚记科技\n600557	康缘药业\n600833	第一医药'
    send_dingding_msg(content)
