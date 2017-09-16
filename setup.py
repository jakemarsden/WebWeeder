from setuptools import find_packages, setup

setup(
    name='WebWeeder',
    version='0.0.1',
    author='Jake Marsden',
    author_email='jakemarsdenjm@gmail.com',
    url='https://github.com/jakemarsden/WebWeeder',
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
        webcrawl=webweeder.cli:crawl
    """
)
