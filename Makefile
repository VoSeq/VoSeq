.PHONY: docs serve test migrations import index collectstatic admin test_installation

help:
	@echo "docs - build documentation in HTML format"
	@echo "serve - runserver for development"
	@echo "test - use testing settings and SQlite3 database"
	@echo "test_migrations - prepare SQLite3 database for testing based on models"
	@echo "test_import - import test data to our SQLite3 database for testing"
	@echo "migrations - prepare database for Django based on models"
	@echo "import - import a MySQL database dump in XML format"
	@echo "index - rebuild the database index. Required. Speeds up data retrieval"
	@echo "update_index - update the database index. Required. Syncs the data and its index"
	@echo "update_index_production - update the production (deployed) database index. Required. Syncs the data and its index"
	@echo "admin - create administrator user for your VoSeq installation"
	@echo "test_installation - additional configuration steps for test installation"

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

serve: stats
	python manage.py runserver --settings=voseq.settings.local

admin:
	python manage.py createsuperuser --settings=voseq.settings.production

migrations:
	python manage.py makemigrations --settings=voseq.settings.local
	python manage.py migrate --settings=voseq.settings.local

import:
	python manage.py migrate_db --dumpfile=dump.xml --settings=voseq.settings.local

test_migrations:
	python manage.py makemigrations --settings=voseq.settings.testing
	python manage.py migrate --settings=voseq.settings.testing

test_import:
	python manage.py migrate_db --dumpfile=run/media/test_db_dump.xml --settings=voseq.settings.local

index:
	python manage.py rebuild_index --settings=voseq.settings.local

update_index:
	python manage.py update_index --age=1 --remove --settings=voseq.settings.local

update_index_production:
	python manage.py update_index --age=$(age) --remove --settings=voseq.settings.local

stats:
	python manage.py create_stats --settings=voseq.settings.local

collectstatic:
	python manage.py collectstatic --noinput --settings=voseq.settings.production

coverage_travis: test_travis
	coverage report -m
	coverage html

test_travis:
	python manage.py makemigrations --settings=voseq.settings.testing
	python manage.py migrate --settings=voseq.settings.testing
	rm -rf htmlcov .coverage
	coverage run --source . manage.py test -v 2 blast_local blast_local_full blast_ncbi blast_new \
	    core create_dataset genbank_fasta public_interface stats view_genes genbank_fasta gene_table \
	    voucher_table gbif overview_table \
	    --settings=voseq.settings.testing

coverage_local: test_local
	coverage report -m
	coverage html

test_local:
	python manage.py makemigrations --settings=voseq.settings.local_testing
	python manage.py migrate --settings=voseq.settings.local_testing
	rm -rf htmlcov .coverage
	coverage run --source . manage.py test -k -v 2 blast_local blast_local_full blast_ncbi blast_new \
	    core create_dataset genbank_fasta public_interface stats view_genes genbank_fasta gene_table \
	    voucher_table gbif overview_table \
	    --settings=voseq.settings.local_testing
test_installation: migrations test_import stats
	sed -i 's/<\/h1>/<br \/><small>Write <b>user<\/b> and <b>pass<\/b> as username and password<\/small><\/h1>/g' public_interface/templates/registration/login.html
	make collectstatic
	cp -r /var/www/VoSeq/static/media/* /var/www/VoSeq/media/.
