from datetime import datetime


class PageMetadata:
    def __init__(self):
        self.domain: str = None
        self.url: str = None
        self.url_date: datetime = None
        self.page_title: str = None
        self.article_title: str = None
        self.article_date: datetime = None
        self.directory: str = None
        self.file_metadata: str = None
        self.file_raw_html: str = None
        self.file_article_plaintext: str = None
