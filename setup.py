from setuptools import find_packages, setup

setup(
    name='TonyScraper',
    version='0.0.1',
    author='Jake Marsden',
    author_email='jakemarsdenjm@gmail.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ],
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'bs4',
        'click',
        'html5lib',
        'lxml',
        'pathvalidate',
        'python-dateutil',
        'scrapy'
    ],
    entry_points="""
        [console_scripts]
        tonycrawl=webweeder.cli:crawl
    """
)
