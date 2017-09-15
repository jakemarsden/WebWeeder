from datetime import datetime, timedelta
from logging import getLogger, Logger
from typing import Dict, Optional

_logger = getLogger(__name__)


class StatsMonitor:
    # TODO: ensure class is thread safe
    def __init__(self, log_period: Optional[timedelta]):
        """
        :param log_period: How often statistics should be logged, or None to disable logging
        """
        self.stats: Dict[str, DomainStats] = {}
        self.log_period: Optional[timedelta] = log_period
        self._next_log_time = None

    def on_page_crawled(self, domain: str):
        stats = self._get_stats_for(domain)
        stats.on_page_crawled()

        self._maybe_log_stats()

    def _maybe_log_stats(self):
        """
        Log statistics if it's time to do so
        """
        if self.log_period is None:
            # Logging is disabled
            return
        now = datetime.utcnow()
        if (self._next_log_time is None) or (now >= self._next_log_time):
            # Time to log now
            self._next_log_time = (now + self.log_period)

            for (domain, stats) in self.stats.items():
                stats.log_stats(now, _logger)

    def _get_stats_for(self, domain: str) -> 'DomainStats':
        if domain not in self.stats:
            self.stats[domain] = DomainStats(domain)
        return self.stats.get(domain)


class DomainStats:
    def __init__(self, domain: str):
        self.domain: str = domain
        self.pages_crawled: int = 0
        self.time_started: datetime = datetime.utcnow()

    def on_page_crawled(self):
        self.pages_crawled += 1

    def log_stats(self, now: datetime, logger: Logger):
        elapsed = (now - self.time_started).total_seconds()
        avg = self.pages_crawled / (elapsed if (elapsed != 0) else 1.0)

        msg = 'Domain "%s" crawled %d pages in %.2f seconds (avg. %.2f/sec)' \
              % (self.domain, self.pages_crawled, elapsed, avg)
        logger.info(msg)
