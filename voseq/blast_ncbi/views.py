from django.shortcuts import render

from core.utils import get_version_stats
from core.utils import get_username
from .utils import BLASTNcbi


def index(request, voucher_code, gene_code):
    version, stats = get_version_stats()
    username = get_username(request)

    blast = BLASTNcbi(voucher_code, gene_code)
    blast.save_query_to_file()

    blast.do_blast()
    result = blast.parse_blast_output()
    blast.delete_query_output_files()
    return render(request, 'blast_local/index.html',
                  {
                      'username': username,
                      'result': result,
                      'version': version,
                      'stats': stats,
                  },
                  )
