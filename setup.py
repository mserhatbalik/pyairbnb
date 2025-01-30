from setuptools import setup

VERSION = '0.0.8'
DESCRIPTION = 'Airbnb scraper in Python'

setup(
    name="pyairbnb",
    version=VERSION,
    author="John (John Balvin)",
    author_email="<johnchristian@hotmail.es>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/johnbalvin/pyairbnb',
    long_description=open('README.md').read(),
    keywords=['airbnb', 'scraper', 'crawler','bot','reviews'],
    install_requires=['curl_cffi','bs4'],
)