from setuptools import setup, find_packages

version = {}
with open('./arango/version.py') as fp:
    exec(fp.read(), version)

setup(
    name='python-arango',
    description='Python Driver for ArangoDB',
    version=version['VERSION'],
    author='Joohwan Oh',
    author_email='joohwan.oh@outlook.com',
    url='https://github.com/joowani/python-arango',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests', 'six']
)
