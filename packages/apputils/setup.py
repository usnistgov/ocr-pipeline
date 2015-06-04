from setuptools import setup, find_packages

setup(
    name="apputils",
    version="0.1.0",

    description=("A set of useful functions meant to be reused",),

    author="Philippe Dessauw",
    author_email="pdessauw@gmail.com",

    packages=find_packages('src'),
    package_dir={'': 'src'},

    install_requires=[
        'pyyaml',
    ],
)