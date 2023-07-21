import os
import sys
from pathlib import Path

from pip._internal import main
from setuptools import setup, find_packages


if sys.version_info < (3, 7, 0):
    raise SystemExit("Sorry! AioSpider requires python 3.7.0 or later.")

version = (Path(__file__).parent / 'AioSpider/__version__').read_text()


requires = [
    'aiohttp>=3.8.0', 'pymongo>=4.3.0', 'pymysql>=1.0.0', 'redis>=4.3.0', 'pandas>=1.3.0', 'lxml>=4.8.0',
    'bitarray', 'chardet', 'cchardet', 'aiosqlite', 'aioredis', 'requests', 'selenium', 'loguru', 'pypiwin32',
    'motor'
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

# python setup.py clean --all
# python setup.py sdist
# python setup.py install
# python setup.py bdist_wheel

