.PHONY: clean-pyc clean-build docs

help:
	@echo "docs - build documentation in HTML format"
	@echo "serve - runserver for development"
	@echo "test - use testing settings and SQlite3 database"

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
	rm -f docs/voseq.*
	rm -rf docs/_build
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ voseq
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
	python voseq/manage.py migrate_db --dumpfile=test_db_dump.xml --settings=voseq.settings.local

index:
	python voseq/manage.py rebuild_index --settings=voseq.settings.local

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
