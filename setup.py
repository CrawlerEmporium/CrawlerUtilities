from setuptools import setup, find_packages

setup(
    name="CrawlerUtilities",
    version="0.0.50",
    license="MIT",
    author="LordDusk",
    author_email="mail@crawleremporium.com",
    description="Library that all my Crawler bots use, contains functions, cogs, and handlers.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CrawlerEmporium/CrawlerUtilities",
    packages=find_packages(),
    install_requires=open("requirements.txt").readlines(),
    python_requires=">=3.8",
)
