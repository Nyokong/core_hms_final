# filters.py
import logging

class ExcludeHeadersFilter(logging.Filter):
    def filter(self, record):
        return 'Host' not in record.getMessage()