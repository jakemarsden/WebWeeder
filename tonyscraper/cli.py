import os
from typing import Optional, List, Set

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

import config
from tonyscraper import cli_vars
from tonyscraper.domainconfig import DomainConfig
from tonyscraper.spiders.monster import MonsterSpider


@click.command()
@click.argument('domains', nargs=-1)
@click.option('--alldomains', is_flag=True, help=cli_vars.HELP_ALLDOMAINS)
@click.option('--outdir', default=config.OUTPUT_DIRECTORY, type=click.Path(file_okay=False), help=cli_vars.HELP_OUTDIR)
@click.option('--useragent', default=config.USER_AGENT, type=str, help=cli_vars.HELP_USERAGENT)
@click.option('--loglevel', default='INFO', type=click.Choice(cli_vars.CHOICE_LOGLEVEL), help=cli_vars.HELP_LOGLEVEL)
def crawl(domains, alldomains, outdir, useragent, loglevel):
    # TODO: docstring for command-line help and example usage

    domains = _validate_domains(domains, alldomains)
    if domains is None:
        return

    config.OUTPUT_DIRECTORY = outdir
    os.makedirs(outdir, exist_ok=True)

    settings = {
        'LOG_LEVEL': loglevel,
        'USER_AGENT': useragent
    }

    configure_logging(settings)

    process = CrawlerProcess(settings)

    for domain in domains:
        MonsterSpider.next_instance_domain = _find_domain_config(domain)
        process.crawl(MonsterSpider)

    process.start()  # Blocks until the crawler finishes


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

    duplicates = _find_duplicates(domains)
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


def _find_duplicates(test_list: List[object]) -> Set[object]:
    duplicates = list(test_list)
    uniques = set(test_list)
    for unique in uniques:
        duplicates.remove(unique)  # Only removes first matching
    return set(duplicates)
