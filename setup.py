
from setuptools import setup, find_packages
import sys

version = {}
with open('./arango/version.py') as fp:
    exec(fp.read(), version)

if sys.version_info < (3, 5):
    requires = ['requests', 'six']
else:
    requires = ['requests', 'six', 'aiohttp']

setup(
    name='python-arango',
    description='Python Driver for ArangoDB',
    version=version['VERSION'],
    author='Joohwan Oh',
    author_email='joohwan.oh@outlook.com',
    url='https://github.com/joowani/python-arango',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    tests_require=['pytest'],
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation :: Sphinx'
    ]
)
