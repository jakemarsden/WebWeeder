from typing import Optional

import config
from webweeder.domainconfig import DomainConfig


def get_config_for_domain(name: str) -> Optional[DomainConfig]:
    """
    :param name:
    :return: The DomainConfig for the domain with the specified name, or None if no domains with the given domain are
    configured.
    """
    for domain_config in config.DOMAINS:
        if domain_config.name == name:
            return domain_config
    return None
