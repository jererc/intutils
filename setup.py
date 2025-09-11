from setuptools import setup, find_packages

setup(
    name='intutils',
    version='2025.09.11.193813',
    author='jererc',
    author_email='jererc@gmail.com',
    url='https://github.com/jererc/intutils',
    packages=find_packages(exclude=['tests*']),
    python_requires='>=3.10',
    install_requires=[
    ],
    extras_require={
        'dev': ['flake8', 'pytest'],
    },
    entry_points={
        'console_scripts': [
            'cleandrive=intutils.cleandrive:main',
            'cleanfiles=intutils.cleanfiles:main',
            'gitcp=intutils.gitcp:main',
        ],
    },
    include_package_data=True,
)
