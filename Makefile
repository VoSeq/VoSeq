.PHONY: docs serve test migrations import index collectstatic admin

help:
	@echo "docs - build documentation in HTML format"
	@echo "serve - runserver for development"
	@echo "test - use testing settings and SQlite3 database"
	@echo "migrations - prepare database for Django based on models"
	@echo "import - import a MySQL database dump in XML format"
	@echo "index - rebuild the database index. Required. Speeds up data retrieval"
	@echo "admin - create administrator user for your VoSeq installation"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

docs:
	# rm -f docs/voseq.*
	# rm -f docs/modules.rst
	rm -rf docs/_build
	# sphinx-apidoc -o docs/ voseq
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

serve: index stats
	python voseq/manage.py runserver --settings=voseq.settings.local

admin:
	python voseq/manage.py createsuperuser --settings=voseq.settings.local

migrations:
	python voseq/manage.py makemigrations --settings=voseq.settings.local
	python voseq/manage.py migrate --settings=voseq.settings.local

import:
	python voseq/manage.py migrate_db --dumpfile=dump.xml --settings=voseq.settings.local

test_import:
	python voseq/manage.py migrate_db --dumpfile=test_db_dump.xml --settings=voseq.settings.local

index:
	python voseq/manage.py rebuild_index --settings=voseq.settings.local

stats:
	python voseq/manage.py create_stats --settings=voseq.settings.local

collectstatic:
	python voseq/manage.py collectstatic --settings=voseq.settings.production

coverage: travis_test
	coverage report -m
	coverage html

test:
	python voseq/manage.py makemigrations --settings=voseq.settings.testing
	python voseq/manage.py migrate --settings=voseq.settings.testing
	rm -rf htmlcov .coverage
	coverage run --source voseq voseq/manage.py test -v 2 blast_local blast_local_full blast_ncbi blast_new \
	    core create_dataset genbank_fasta public_interface stats view_genes genbank_fasta gene_table \
	    voucher_table gbif overview_table \
	    --settings=voseq.settings.testing

travis_test:
	python voseq/manage.py makemigrations --settings=voseq.settings.testing
	python voseq/manage.py migrate --settings=voseq.settings.testing
	rm -rf htmlcov .coverage
	coverage run --source voseq voseq/manage.py test -v 2 blast_local blast_local_full blast_ncbi blast_new \
	    core create_dataset genbank_fasta public_interface stats view_genes genbank_fasta gene_table \
	    voucher_table gbif overview_table \
	    --settings=voseq.settings.travis
