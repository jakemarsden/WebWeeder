import os

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

import config
from tonyscraper import cli_vars
from tonyscraper.spiders.clashdaily_com import ClashdailyComSpider


@click.command()
@click.option('--outdir', default=config.OUTPUT_DIRECTORY, type=click.Path(file_okay=False), help=cli_vars.HELP_OUTDIR)
@click.option('--useragent', default=config.USER_AGENT, type=str, help=cli_vars.HELP_USERAGENT)
@click.option('--loglevel', default='INFO', type=click.Choice(cli_vars.CHOICE_LOGLEVEL), help=cli_vars.HELP_LOGLEVEL)
def crawl(outdir, useragent, loglevel):
    config.OUTPUT_DIRECTORY = outdir
    os.makedirs(outdir, exist_ok=True)

    settings = {
        'LOG_LEVEL': loglevel,
        'USER_AGENT': useragent
    }

    configure_logging(settings)

    process = CrawlerProcess(settings)
    process.crawl(ClashdailyComSpider)
    process.start()  # Blocks until the crawler finishes
