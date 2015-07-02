from setuptools import setup, find_packages

setup(
    name="denoiser",
    version="1.0.0",

    description=("Provide objects to curate text files from garbage strings",),

    author="Philippe Dessauw",
    author_email="philippe.dessauw@nist.gov",

    packages=find_packages('src'),
    package_dir={
        '': 'src',
    },

    install_requires=[
        'apputils',
        'nltk',
        'numpy',
        'unidecode',
        'scikit-learn==0.15.2',
        'scipy',
    ],
)
