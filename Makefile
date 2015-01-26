help:
	@echo "serve - remove build artifacts"
	@echo "test - use testing settings and SQlite3 database"

serve: index stats
	python voseq/manage.py runserver --settings=voseq.settings.local

admin:
	python voseq/manage.py createsuperuser

migrations:
	python voseq/manage.py makemigrations --settings=voseq.settings.local
	python voseq/manage.py migrate --settings=voseq.settings.local

import:
	python voseq/manage.py migrate_db --dumpfile=test_db_dump.xml --settings=voseq.settings.local

index:
	python voseq/manage.py rebuild_index

stats:
	python voseq/manage.py create_stats --settings=voseq.settings.local

coverage: test
	coverage report -m
	coverage html

test:
	python voseq/manage.py makemigrations --settings=voseq.settings.testing
	python voseq/manage.py migrate --settings=voseq.settings.testing
	rm -rf htmlcov .coverage
	coverage run --source voseq voseq/manage.py test -v 2 core public_interface \
	    blast_local blast_local_full blast_ncbi blast_new stats view_genes      \
	    genbank_fasta --settings=voseq.settings.testing
