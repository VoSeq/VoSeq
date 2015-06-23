from django.shortcuts import render

from core.utils import get_version_stats
from core.utils import get_username
from .utils import BLAST


def index(request, voucher_code, gene_code):
    version, stats = get_version_stats()
    username = get_username(request)

    blast = BLAST('local', voucher_code, gene_code)
    blast.save_seqs_to_file()

    if blast.is_blast_db_up_to_date() is False:
        blast.create_blast_db()

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
