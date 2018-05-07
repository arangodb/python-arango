from setuptools import setup, find_packages

from arango import version

setup(
    name='python-arango',
    description='Python Driver for ArangoDB',
    version=version.__version__,
    author='Joohwan Oh',
    author_email='joohwan.oh@outlook.com',
    url='https://github.com/joowani/python-arango',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=['requests', 'six'],
    tests_require=['pytest', 'mock', 'flake8'],
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
