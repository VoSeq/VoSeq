import re

from haystack.views import SearchView

from core.utils import get_version_stats


class VoSeqSearchView(SearchView):
    def __init__(self, url_encoded_query, *args, **kwargs):
        self.url_encoded_query = self.get_correct_url_query(url_encoded_query)
        self.simple_query = self.recover_keyword(url_encoded_query)
        super(VoSeqSearchView, self).__init__(*args, **kwargs)

    def get_correct_url_query(self, url_encoded_query):
        this_query = self.strip_page(url_encoded_query)
        return this_query

    def recover_keyword(self, url_encoded_query):
        this_query = re.sub('\w+=Select', ' ', url_encoded_query)
        this_query = re.sub('\w+=', ' ', this_query)
        this_query = this_query.replace('&', ' ')
        this_query = re.sub('\s+', ' ', this_query)
        return this_query.strip()

    def strip_page(self, url_encoded_query):
        this_query = re.sub('page=[0-2]+', '', url_encoded_query)
        this_query = this_query.replace('&&', '&')
        this_query = re.sub('^&', '', this_query)
        this_query = re.sub('&$', '', this_query)
        return this_query

    def extra_context(self):
        version, stats = get_version_stats()
        return {
            'simple_query': self.simple_query,
            'url_encoded_query': self.url_encoded_query,
            'result_count': len(self.searchqueryset),
            'version': version,
            'stats': stats,
        }
