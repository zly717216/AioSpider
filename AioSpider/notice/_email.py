from typing import Union, List

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from AioSpider import logger


class Email:

    def __init__(self, smtp: str, port: int, from_email: str, token: str, receiver: Union[str, List[str]]):

        self.smtp = smtp
        self.port = port
        self.from_email = from_email
        self.token = token

        if isinstance(receiver, str):
            self.receiver = [receiver]
        else:
            self.receiver = receiver

        self._server = None

    @property
    def server(self):
        if self._server is None:
            try:
                self._server = smtplib.SMTP(self.smtp, self.port, timeout=3)
                # 开启TLS加密，确保邮件内容安全传输
                self._server.starttls()
                self._server.login(self.from_email, self.token)
            except Exception:
                raise ConnectionError('邮箱服务器连接失败')
        return self._server

    def close(self):
        self.server.quit()

    def send_email(self, subject, body, attach: Union[bytes, List[bytes]] = None):

        # 构建邮件内容
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ','.join(self.receiver)
        msg['Subject'] = subject

        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain'))

        if isinstance(attach, bytes):
            attach = [attach]

        if attach is not None:
            for x in attach:
                image_mime = MIMEImage(x)
                msg.attach(image_mime)

        self.server.sendmail(self.from_email, self.receiver, msg.as_string())
        logger.info("邮件发送成功")
