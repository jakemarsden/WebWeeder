import json
from datetime import datetime
from typing import Dict, Optional

from dateutil.parser import parse as parse_datetime


class PageMetadata:
    def __init__(self):
        self.domain: str = None
        self.url: str = None
        self.url_date: datetime = None
        self.page_title: str = None
        self.article_title: str = None
        self.article_date: str = None
        self.directory: str = None
        self.file_metadata: str = None
        self.file_raw_html: str = None
        self.file_article_plaintext = None


def page_metadata_to_json(meta: PageMetadata, pretty: bool = True) -> str:
    json_obj: Dict[str, object] = meta.__dict__.copy()
    json_obj['url_date'] = _datetime_to_json(meta.url_date)
    json_obj['article_date'] = _datetime_to_json(meta.article_date)

    indent = 4 if pretty else None
    return json.dumps(json_obj, indent=indent, sort_keys=False)


def page_metadata_from_json(json_str: str) -> PageMetadata:
    json_obj = json.loads(json_str)
    meta = PageMetadata()
    meta.__dict__ = json_obj.copy()
    meta.url_date = _datetime_from_json(json_obj['url_date'])
    meta.article_date = _datetime_from_json(json_obj['article_date'])

    return meta


def _datetime_to_json(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if (dt is not None) else None


def _datetime_from_json(json_str: Optional[str]) -> Optional[datetime]:
    if (json_str is None) or (len(json_str) == 0):
        return None
    return parse_datetime(json_str)
