from distutils.core import setup
from setuptools import find_packages


setup(
    name='AioSpider',              # 包名
    version='V1.0.0',           # 版本号
    description='高并发异步爬虫框架',
    author='zly',
    author_email='zly717216@qq.com',
    install_requires=[
        'aiohttp', 'aiofiles', 'aiocsv', 'aiosqlite', 'aioredis', 'aiomysql',
        'pymongo', 'pymysql', 'redis', 'lxml', 'pyexecjs', 'chardet', 'cchardet', 'w3lib',
    ],
    classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: strategy'
      ],
    keywords='robot',
    packages=find_packages('src'),     # 必填
    package_dir={'': 'src'},           # 必填
    include_package_data=True,
)

# python setup.py sdist
# python setup.py install
