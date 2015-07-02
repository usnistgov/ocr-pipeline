from setuptools import setup, find_packages

setup(
    name="apputils",
    version="0.1.0",

    description=("A set of useful functions for your Python software",),

    author="Philippe Dessauw",
    author_email="philippe.dessauw@nist.gov",

    packages=find_packages('src'),
    package_dir={'': 'src'},

    install_requires=[
        'pyyaml',
    ],
)
