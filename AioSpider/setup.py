import os
import sys
from pathlib import Path

from pip._internal import main
from setuptools import setup, find_packages


if sys.version_info < (3, 7, 0):
    raise SystemExit("Sorry! AioSpider requires python 3.7.0 or later.")

version = (Path(__file__).parent / '__version__').read_text()


requires = [
    'aiohttp>=3.8.0', 'pymongo>=4.3.0', 'pymysql>=1.0.0', 'redis>=4.3.0', 'pandas>=1.3.0', 'lxml>=4.8.0',
    'bitarray', 'chardet', 'cchardet', 'aiosqlite', 'aioredis', 'requests', 'selenium', 'loguru', 'pypiwin32',
    'rsa', 'motor', 'Beautifulsoup4', 'pypinyin'
]

if sys.platform == 'win32':
    try:
        import Crypto
    except Exception:
        from pycryptodome import setup as _
        os.chdir(Path(__file__).parent)
else:
    requires.append('pycrypto')

if sys.argv and sys.argv[1] == 'install':
    for r in requires:
        main(['install', r])

packages = find_packages()
packages.extend(
    [
        "AioSpider",
        "AioSpider.utils_pkg",
        "AioSpider.utils_pkg.aiomysql",
        "AioSpider.utils_pkg.aiomysql.sa",
        "AioSpider.utils_pkg.aioredis",
        "AioSpider.utils_pkg.execjs",
        "AioSpider.utils_pkg.pydash",
        "AioSpider.utils_pkg.w3lib",
        "AioSpider.utils_pkg.prettytable",
        "AioSpider.utils_pkg.bs4",
    ]
)

setup(
    name='AioSpider',           # 包名
    version=version,            # 版本号
    # py_modules=['hello'],
    # entry_points={'console_scripts': ['pyhello = hello:main']},
    description='高并发异步爬虫框架',
    author='zly',
    maintainer='zly',
    author_email='zly717216@qq.com',
    url="https://github.com/zly717216/AioSpider",
    install_requires=requires,
    classifiers=[
        'Framework :: AioSpider',
        'Development Status :: 5 - Developing',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'aioSpider = AioSpider.aioSpider:main'
        ]
    }
)

# python setup.py sdist
# python setup.py install
# python setup.py bdist_wheel

# from setuptools import setup, find_packages
# from codecs import open
# from os import path
# 
# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()
# 
# # 获取当前文件夹路径
# here = path.abspath(path.dirname(__file__))
# 
# # 在这里添加项目的依赖项
# install_requires = []
# with open("requirements.txt") as f:
#     install_requires = f.read().splitlines()
# 
# # 获取__version__属性
# with open(path.join(here, "aioSpider", "__version__")) as version_file:
#     version = version_file.read().strip()
# 
# setup(
#     name="AioSpider",
#     version=version,
#     description="AioSpider - An async web scraping framework",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/your_username/AioSpider",
#     author="Your Name",
#     author_email="your.email@example.com",
#     license="MIT",
#     classifiers=[
#         "Development Status :: 3 - Alpha",
#         "Intended Audience :: Developers",
#         "License :: OSI Approved :: MIT License",
#         "Programming Language :: Python :: 3",
#         "Programming Language :: Python :: 3.6",
#         "Programming Language :: Python :: 3.7",
#         "Programming Language :: Python :: 3.8",
#     ],
#     keywords="web scraping async aiohttp spider",
#     packages=find_packages(exclude=["contrib", "docs", "tests"]),
#     install_requires=install_requires,
#     python_requires=">=3.6, <4",
#     package_data={
#         "aioSpider": [
#             "tools/Chromium/*",
#             "tools/Firefox/*",
#             "template/*.tpl",
#             # 如果有其他非.py文件需要打包，请将它们添加到这里
#         ]
#     },
#     entry_points={"console_scripts": ["aiospider=aiospider.cmd.cmd:main"]},
# )