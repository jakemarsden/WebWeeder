import getpass
import os
import socket
from datetime import date, datetime
from logging import getLogger, DEBUG
from logging.handlers import RotatingFileHandler
from typing import List, Optional

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import get_scrapy_root_handler, configure_logging

import config
from webweeder import cli_vars
from webweeder.domainconfig import DomainConfig
from webweeder.spiders.monster import MonsterSpider
from webweeder.stats import StatsMonitor
from webweeder.utils import delete_directory, find_duplicates, MEGABYTES

_logger = getLogger(__name__)


@click.command()
@click.argument('domains', nargs=-1)
@click.option('--alldomains', is_flag=True, help=cli_vars.HELP_ALLDOMAINS)
@click.option('--clean', is_flag=True, help=cli_vars.HELP_CLEAN)
@click.option('--outdir', default=config.OUTPUT_DIRECTORY, type=click.Path(file_okay=False), help=cli_vars.HELP_OUTDIR)
@click.option('--useragent', default=config.USER_AGENT, type=str, help=cli_vars.HELP_USERAGENT)
@click.option('--statsinterval', default=config.STATS_INTERVAL, type=click.IntRange(min=-1),
              help=cli_vars.HELP_STATSINTERVAL)
@click.option('--parser', default=config.HTML_PARSER, type=click.Choice(cli_vars.CHOICE_PARSERS),
              help=cli_vars.HELP_PARSER)
@click.option('--loglevel', default=config.LOG_LEVEL, type=click.Choice(cli_vars.CHOICE_LOGLEVEL),
              help=cli_vars.HELP_LOGLEVEL)
@click.option('--logdir', default=config.LOG_DIRECTORY, type=click.Path(file_okay=False), help=cli_vars.HELP_LOGDIR)
def crawl(domains, alldomains, clean, outdir, useragent, statsinterval, parser, loglevel, logdir):
    # TODO: docstring for command-line help and example usage

    _configure(outdir, useragent, statsinterval, parser, loglevel, logdir)
    _log_system_info()
    click.echo()

    # Clean the output directory if it's the ONLY thing we need to do
    if clean:
        if len(domains) == 0 and (not alldomains):
            click.echo(cli_vars.MSG_CLEANING_AND_EXITING)
            delete_directory(outdir, preserve_dir=True)
            return

    # Ensure the user has entered valid domains to crawl
    domains = _validate_domains(domains, alldomains)
    if domains is None:
        return

    # Clean the output directory if necessary
    if clean:
        click.echo(cli_vars.MSG_CLEANING)
        delete_directory(outdir, preserve_dir=True)
        click.echo()

    # Confirm that the user wants to start crawling
    click.echo('You are about to crawl these domains: %r' % domains)
    click.confirm('Continue crawling %d domains?' % len(domains), abort=True)
    click.echo()

    # Keeps track of statistics
    stats = StatsMonitor()

    # Create and start the spiders specified by the user
    process = CrawlerProcess(config.SCRAPY_SETTINGS)
    for domain in domains:
        MonsterSpider.next_instance_domain = _find_domain_config(domain)
        MonsterSpider.next_instance_callback = stats.on_page_crawled
        process.crawl(MonsterSpider)
    process.start()  # Blocks until the spiders finish


def _configure(outdir, useragent, statsinterval, parser, loglevel, logdir):
    config.OUTPUT_DIRECTORY = outdir
    config.USER_AGENT = useragent
    config.STATS_INTERVAL = statsinterval
    config.HTML_PARSER = parser
    config.LOG_LEVEL = loglevel
    config.LOG_DIRECTORY = logdir
    config.SCRAPY_SETTINGS = {
        'BOT_NAME': 'WebWeeder',
        'ROBOTSTXT_OBEY': True,
        'LOG_LEVEL': loglevel,
        'USER_AGENT': useragent
    }

    os.makedirs(outdir, exist_ok=True)
    os.makedirs(logdir, exist_ok=True)

    configure_logging(config.SCRAPY_SETTINGS)

    log_file_path = os.path.join(config.LOG_DIRECTORY, date.today().strftime('%Y-%m-%d.log'))
    file_handler = RotatingFileHandler(filename=log_file_path, maxBytes=(50 * MEGABYTES), backupCount=100)
    file_handler.setFormatter(get_scrapy_root_handler().formatter)
    file_handler.setLevel(DEBUG)
    getLogger().addHandler(file_handler)


def _find_domain_config(name: str) -> Optional[DomainConfig]:
    for domain_config in config.DOMAINS:
        if domain_config.name == name:
            return domain_config
    return None


def _validate_domains(domains: List[str], alldomains: bool) -> Optional[List[str]]:
    """
    :param domains: List of domains the user has specified to crawl
    :param alldomains True if the user is trying to crawl every configured domain
    :return: A list of valid domains to crawl, or "None" if there was a validation problem
    """
    if alldomains:
        if len(domains) != 0:
            click.echo(cli_vars.ERROR_ALLDOMAINS_WITH_LIST)
            return None
        domains = [domain_config.name for domain_config in config.DOMAINS]

    if len(domains) == 0:
        click.echo(cli_vars.ERROR_NO_DOMAIN_SPECIFIED)
        return None

    domains = sorted(domains)

    duplicates = find_duplicates(domains)
    for duplicate in duplicates:
        click.echo(cli_vars.ERROR_DUPLICATE_DOMAINS % duplicate)
    if len(duplicates) != 0:
        return None

    all_configured = True
    for domain in domains:
        domain_config = _find_domain_config(domain)
        if domain_config is None:
            click.echo(cli_vars.ERROR_UNCONFIGURED_DOMAIN % domain)
            all_configured = False
    if not all_configured:
        return None

    return domains


def _log_system_info():
    try:
        hostname = socket.gethostname()
    except:
        hostname = ''
    try:
        username = getpass.getuser()
    except:
        username = ''
    _logger.debug('')
    _logger.debug('        ------------------------------------')
    _logger.debug('        |    APPLICATION LAUNCH            |')
    _logger.debug('        |    %s    |' % datetime.now().isoformat())
    _logger.debug('        ------------------------------------')
    _logger.debug('        Hostname:  %s' % hostname)
    _logger.debug('        Username:  %s' % username)
    _logger.debug('        Directory: %s' % os.getcwd())
    _logger.debug('')
