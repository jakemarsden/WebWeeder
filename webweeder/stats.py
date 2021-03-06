from datetime import datetime, timedelta
from logging import getLogger, Logger
from typing import Dict, Optional

import config

_logger = getLogger(__name__)


class StatsMonitor:
    # TODO: ensure class is thread safe
    def __init__(self):
        self.stats: Dict[str, DomainStats] = {}
        self.combined_stats: DomainStats = DomainStats(None)
        self._next_log_time = None

    def on_page_crawled(self, domain: str):
        self._get_stats_for(domain).on_page_crawled()
        self.combined_stats.on_page_crawled()

        self._maybe_log_stats()

    def _maybe_log_stats(self):
        """
        Log statistics if it's time to do so
        """
        log_interval = self._get_log_interval()
        if log_interval is None:
            # Logging is disabled
            return
        now = datetime.utcnow()
        if (self._next_log_time is None) or (now >= self._next_log_time):
            # Time to log now
            self._next_log_time = (now + log_interval)

            for k in sorted(self.stats.keys()):
                self.stats.get(k).log_stats(now, _logger)
            self.combined_stats.log_stats(now, _logger)

    def _get_stats_for(self, domain: str) -> 'DomainStats':
        if domain not in self.stats:
            self.stats[domain] = DomainStats(domain)
        return self.stats.get(domain)

    @staticmethod
    def _get_log_interval() -> Optional[timedelta]:
        """
        :return: How often statistics should be logged, or None if disabled
        """
        interval = config.STATS_INTERVAL
        return timedelta(seconds=interval) if (interval != -1) else None


class DomainStats:
    def __init__(self, domain: Optional[str]):
        """
        :param domain: The domain these stats are for, or None if it represents stats for all domains combined
        """
        label = ('Domain "%s"' % domain) if (domain is not None) else 'Combined:'
        self.fmt = label + ' crawled %d pages in %.2f seconds (avg. %.2f/sec)'
        self.pages_crawled: int = 0
        self.time_started: datetime = datetime.utcnow()

    def on_page_crawled(self):
        self.pages_crawled += 1

    def log_stats(self, now: datetime, logger: Logger):
        elapsed = (now - self.time_started).total_seconds()
        avg = self.pages_crawled / (elapsed if (elapsed != 0) else 1.0)

        logger.info(self.fmt % (self.pages_crawled, elapsed, avg))
