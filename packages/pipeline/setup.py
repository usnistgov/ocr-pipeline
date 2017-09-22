from setuptools import setup, find_packages

setup(
    name="pipeline",
    version="1.1.0-alpha3",

    description=("Transform PDF files to clean text files using a distributed architecture",),

    author="Philippe Dessauw",
    author_email="philippe.dessauw@nist.gov",

    packages=find_packages('src'),
    package_dir={
        '': 'src',
    },

    install_requires=[
        'apputils',
        'denoiser',
        'fabric',
        'matplotlib',
        'redis',
        'hiredis',
        'PyPDF2',
    ],
)
