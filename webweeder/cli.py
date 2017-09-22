import getpass
import os
import socket
from datetime import date, datetime
from glob import glob
from logging import getLogger, DEBUG
from logging.handlers import RotatingFileHandler
from typing import List, Optional

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import get_scrapy_root_handler, configure_logging

import config
from webweeder import cli_vars
from webweeder import configutils
from webweeder.spiders.monster import MonsterSpider
from webweeder.stats import StatsMonitor
from webweeder.utils import delete_directory, find_duplicates, MEGABYTES
from webweeder.weeders.monster import MonsterWeeder

_logger = getLogger(__name__)


@click.command()
@click.argument('domains', nargs=-1)
@click.option('--alldomains', is_flag=True, help=cli_vars.HELP_ALLDOMAINS)
@click.option('--clean', is_flag=True, help=cli_vars.HELP_CLEAN_CRAWL)
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

    msg = 'crawl: domains=%r, alldomains=%r, clean=%r, outdir=%r, useragent=%r, statsinterval=%r, parser=%r, ' \
          'logfile=%r, logdir=%r' \
          % (domains, alldomains, clean, outdir, useragent, statsinterval, parser, loglevel, logdir)

    _configure(outdir, useragent, statsinterval, parser, loglevel, logdir)
    _log_system_info()
    _logger.debug(msg)
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
        MonsterSpider.next_instance_domain = configutils.get_config_for_domain(domain)
        MonsterSpider.next_instance_callback = stats.on_page_crawled
        process.crawl(MonsterSpider)
    process.start()  # Blocks until the spiders finish


@click.command()
@click.option('--clean', is_flag=True, help=cli_vars.HELP_CLEAN_WEED)
@click.option('--outdir', default=config.OUTPUT_DIRECTORY, type=click.Path(file_okay=False), help=cli_vars.HELP_OUTDIR)
@click.option('--parser', default=config.HTML_PARSER, type=click.Choice(cli_vars.CHOICE_PARSERS),
              help=cli_vars.HELP_PARSER)
@click.option('--loglevel', default=config.LOG_LEVEL, type=click.Choice(cli_vars.CHOICE_LOGLEVEL),
              help=cli_vars.HELP_LOGLEVEL)
@click.option('--logdir', default=config.LOG_DIRECTORY, type=click.Path(file_okay=False), help=cli_vars.HELP_LOGDIR)
def weed(clean, outdir, parser, loglevel, logdir):
    # TODO: docstring for command-line help and example usage

    msg = 'weed: clean=%r, outdir=%r, parser=%r, logfile=%r, logdir=%r' \
          % (clean, outdir, parser, loglevel, logdir)

    _configure(outdir, config.USER_AGENT, config.STATS_INTERVAL, parser, loglevel, logdir)
    _log_system_info()
    _logger.debug(msg)
    click.echo()

    # Clean the output directory if necessary
    if clean:
        click.echo(cli_vars.MSG_CLEANING)
        file_pattern = os.path.join(config.OUTPUT_DIRECTORY, '**', 'plaintext_article.txt')
        for file in glob(file_pattern, recursive=True):
            _logger.debug('Cleaning file: %s' % file)
            os.remove(file)
        click.echo()

    weeder = MonsterWeeder()

    _logger.info('Collecting pages to weed...')
    metadatas: List[str] = weeder.find_page_metadatas(config.OUTPUT_DIRECTORY)
    metadatas.sort()

    # Confirm that the user wants to start weeding
    click.echo('You are about to weed %d pages' % len(metadatas))
    click.confirm('Continue weeding %d pages?' % len(metadatas), abort=True)
    click.echo()

    for (i, metadata) in enumerate(metadatas):
        log_info = (_out_of_str(i + 1, len(metadatas)), metadata)
        _logger.info('Weeding page %s: %s' % log_info)
        try:
            weeder.weed_page(config.OUTPUT_DIRECTORY, metadata)
        except Exception:
            # Just log the failure with its stack trace
            _logger.exception('Failed to weed page %s: %s\n' % log_info)


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
        domain_config = configutils.get_config_for_domain(domain)
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


def _out_of_str(n1: int, n2: int) -> str:
    """
    :return A string in the format [n1 / n2], where "n1" and "n2" are the passed integers padded to the same length
    """
    width = len(str(max(n1, n2)))
    return '[%s / %s]' % (str(n1).rjust(width), str(n2).rjust(width))
