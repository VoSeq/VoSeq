#!/bin/bash

# Script to set up dependencies for Django on Vagrant.

PGSQL_VERSION=9.3

# Need to fix locale so that Postgres creates databases in UTF-8
cp -p /vagrant_data/etc-bash.bashrc /etc/bash.bashrc
locale-gen en_GB.UTF-8
dpkg-reconfigure locales

export LANGUAGE=en_GB.UTF-8
export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8

# Install essential packages from Apt
apt-get update -y
# Python dev packages
apt-get install -y build-essential python python3-dev python-setuptools python-pip
# Dependencies for image processing with Pillow (drop-in replacement for PIL)
# supporting: jpeg, tiff, png, freetype, littlecms
apt-get install -y libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev
# Git (we'd rather avoid people keeping credentials for git commits in the repo, but sometimes we need it for pip requirements that aren't in PyPI)
apt-get install -y git

apt-get install -y nginx
service nginx start

# Postgresql
if ! command -v psql; then
    apt-get install -y postgresql-$PGSQL_VERSION libpq-dev
    cp /vagrant_data/pg_hba.conf /etc/postgresql/$PGSQL_VERSION/main/
    /etc/init.d/postgresql reload
    echo "alter role postgres with password 'hu8jmn3'" | psql -U postgres
    echo "create database voseq" | psql -U postgres
fi

# elasticsearch
apt-get install -y openjdk-7-jdk openjdk-7-jre
if [[ ! -f /etc/init.d/elasticsearch ]]; then
    wget -q https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.6.0.deb && \
        dpkg -i elasticsearch-1.6.0.deb
fi

if [[ ! -e /var/run/elasticsearch ]]; then
    mkdir -p /var/run/elasticsearch && /etc/init.d/elasticsearch start
fi
/etc/init.d/elasticsearch start

# virtualenv global setup
if ! command -v pip; then
    easy_install -U pip
fi

if [[ ! -f /usr/local/bin/virtualenv ]]; then
    easy_install virtualenv virtualenvwrapper stevedore virtualenv-clone
fi

# bash environment global setup
cp -p /vagrant_data/bashrc /home/vagrant/.bashrc

# Cleanup
apt-get clean


# Virtualenv for VoSeq
if [[ ! -e /home/vagrant/.virtualenvs/voseq ]]; then
    su - vagrant -c "source /usr/local/bin/virtualenvwrapper.sh &&            \
        mkvirtualenv -p /usr/bin/python3 voseq && \
        source /home/vagrant/.virtualenvs/voseq/bin/activate && \
        pip install pip --upgrade && \
        pip install -r /vagrant/requirements/base.txt && \
        pip install gunicorn && \
        pip install setproctitle "
fi

# config.json file for VoSeq
if [[ ! -f /vagrant/config.json ]]; then
    echo '{
        "SECRET_KEY": "create_a_secret_key",
        "DB_USER": "postgres",
        "DB_PASS": "hu8jmn3",
        "DB_NAME": "voseq",
        "DB_PORT": "5432",
        "DB_HOST": "localhost",
        "GOOGLE_MAPS_API_KEY": "get_a_google_map_api_key",
        "PHOTOS_REPOSITORY": "local"
    }
    ' >  /vagrant/config.json
fi

# setup server using gunicorn
if [[ ! -e /home/vagrant/run ]]; then
    mkdir /home/vagrant/run && mkdir /home/vagrant/logs && \
        touch /home/vagrant/logs/gunicorn_supervisor.log
fi

if [[ ! -e /home/vagrant/bin ]]; then
    mkdir /home/vagrant/bin
fi

echo '#!/bin/bash

NAME="voseq"                                  # Name of the application
DJANGODIR=/vagrant/voseq                      # Django project directory
SOCKFILE=/home/vagrant/run/gunicorn.sock           # we will communicte using this unix socket
USER=vagrant                                        # the user to run as
GROUP=vagrant                                     # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=voseq.settings.production             # which settings file should Django use
DJANGO_WSGI_MODULE=voseq.wsgi                     # WSGI module name

# Activate the virtual environment
cd $DJANGODIR
source /home/vagrant/.virtualenvs/voseq/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesnt exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /home/vagrant/.virtualenvs/voseq/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --bind=unix:$SOCKFILE \
    --log-level=debug \
    --log-file=-
' > /home/vagrant/bin/gunicorn_start

chmod u+x /home/vagrant/bin/gunicorn_start
chown vagrant:vagrant -R /home/vagrant
apt-get install -y supervisor

sudo echo '
[program:voseq]
command = /home/vagrant/bin/gunicorn_start                    ; Command to start app
user = vagrant                                                          ; User to run as
stdout_logfile = /home/vagrant/logs/gunicorn_supervisor.log   ; Where to write log messages
redirect_stderr = true                                                ; Save stderr in the same log
environment=LANG=en_GB.UTF-8,LC_ALL=en_GB.UTF-8                       ; Set UTF-8 as default encoding
' > /etc/supervisor/conf.d/voseq.conf

if [[ /var/run/supervisor.sock ]]; then
    unlink /var/run/supervisor.sock
fi

sudo supervisord -c /etc/supervisor/supervisord.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart voseq

# nginx configuration
echo '
    upstream voseq_app_server {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response (in case the Unicorn master nukes a
    # single worker for timing out).
    
    server unix:/home/vagrant/run/gunicorn.sock fail_timeout=0;
    }
    
    server {
    
        listen   80;
        server_name example.com;
    
        client_max_body_size 1G;
    
        access_log /home/vagrant/logs/nginx-access.log;
        error_log /home/vagrant/logs/nginx-error.log;
    
        location /static/ {
            alias   /var/www/VoSeq/static/;
        }
        
        location /media/ {
            alias   /vagrant/www/VoSeq/media/;
        }
    
        location / {
            # an HTTP header important enough to have its own Wikipedia entry:
            #   http://en.wikipedia.org/wiki/X-Forwarded-For
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
            # enable this if and only if you use HTTPS, this helps Rack
            # set the proper protocol for doing redirects:
            # proxy_set_header X-Forwarded-Proto https;
    
            # pass the Host: header from the client right along so redirects
            # can be set properly within the Rack application
            proxy_set_header Host $http_host;
    
            # we dont want nginx trying to do something clever with
            # redirects, we set the Host: header above already.
            proxy_redirect off;
    
            # set "proxy_buffering off" *only* for Rainbows! when doing
            # Comet/long-poll stuff.  Its also safe to set if youre
            # using only serving fast clients with Unicorn + nginx.
            # Otherwise you _want_ nginx to buffer responses to slow
            # clients, really.
            # proxy_buffering off;
    
            # Try to serve static files from nginx, no point in making an
            # *application* server like Unicorn/Rainbows! serve static files.
            if (!-f $request_filename) {
                proxy_pass http://voseq_app_server;
                break;
            }
        }
    
        # Error pages
        error_page 500 502 503 504 /500.html;
        location = /500.html {
            root /var/www/VoSeq/static/;
        }
    }
' > /etc/nginx/sites-available/voseq

ln -s /etc/nginx/sites-available/voseq /etc/nginx/sites-enabled/voseq
rm -rf /etc/nginx/sites-enabled/default
rm -rf /etc/nginx/sites-available/default

if [[ ! -e /var/www ]]; then
    mkdir /var/www &&  chown vagrant:vagrant -R /var/www
fi

