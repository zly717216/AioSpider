import sys
from distutils.core import setup

from pip._internal import main
from setuptools import find_packages


requires = [
    'aiohttp==3.8.3', 'pymongo==4.3.2', 'pymysql==1.0.2', 'redis==4.3.4', 'pandas==1.5.1', 'lxml==4.8.0'
]

if sys.argv and sys.argv[1] == 'install':
    for r in requires:
        main(['install', r])

setup(
    name='AioSpider',           # 包名
    version='V1.0.0',           # 版本号
    description='高并发异步爬虫框架',
    author='zly',
    author_email='zly717216@qq.com',
    install_requires=requires,
    classifiers=[
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: strategy'
      ],
    keywords='robot',
    packages=find_packages('AioSpider'),     # 必填
    package_dir={'': 'AioSpider'},           # 必填
    include_package_data=True,
)

# python setup.py sdist
# python setup.py install
# python setup.py bdist_wheel

