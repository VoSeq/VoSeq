[![Build Status](https://travis-ci.org/carlosp420/VoSeq.svg)](https://travis-ci.org/carlosp420/VoSeq)
[![Coverage Status](https://img.shields.io/coveralls/carlosp420/VoSeq.svg)](https://coveralls.io/r/carlosp420/VoSeq?branch=master)

# VoSeq is being rewritten
We are rebuilding VoSeq from scratch. We decided to migrate from PHP to Python
by using the framework Django. We also moved from MySQL to PostgreSQL.

You can still download the old VoSeq v1.7.4 from [here](https://github.com/carlosp420/VoSeq/releases/tag/v1.7.4).
But be aware that we will not be doing major maintenance of that code.

Here is a test installation of the old VoSeq (v1.7.0) <http://www.nymphalidae.net/VoSeq/>

More details about the migration can be found in our [discussion list](https://groups.google.com/forum/#!topic/voseq-discussion-list/wQ-E0Xcimgw).

VoSeq 2.0.0 is the future!

# Configuration
 
Clone/download Voseq to your prefer directory.

You need to install some Python packages as dependencies:

```shell
cd /path/to/VoSeq
pip install -r requirements/dev.txt
```
 
Download and install PostgreSQL. For macOSX users we recommend to do it by downloading the Postgres.app from http://postgresapp.com

Download and install `elasticsearch` from here: http://www.elasticsearch.org/overview/elkdownloads/
You can install the `.deb` file. The bin directory of elasticsearch should be added automatically to your PATH. If not, add the following line to your `.profile` (Linux) or `.bash_profile` (macOSX) file:

```shell
export PATH="$PATH:/path/to/elasticsearch/bin/"
```
 

Create a PostgreSQL database:

```shell
sudo su postgres
psql
postgres=# create database voseq;
```
 
 In macOSX if you are using the Postgres.app, it my be enough to run:
 
 ```shell
 psql
 user.name=# CREATE DATABASE voseq;
 ```
 
Create a `config.json` file to keep the database variables:
```javascript
 {
 "SECRET_KEY": "create_a_secret_key",
 "DB_USER": "user.name", // e.g., postgres or user.name
 "DB_PASS": "create_a_database_password",
 "DB_NAME": "voseq",
 "DB_PORT": "5432",
 "DB_HOST": "localhost",
 "GOOGLE_MAPS_API_KEY": "get_a_google_map_api_key"
 }
```

# Migrate VoSeq database
If you have a previous version of Voseq as server and want to migrate, you need to dump your MySQL database into a XML file:

```shell
cd /path/to/Voseq/
mysqldump --xml voseq_database > dump.xml
```

Then use our script to migrate all your VoSeq data into a PostGreSQL database.

```shell
make migrations
python migrate_db.py dump.xml
```

It might issue a warning message:

```
WARNING:: Could not parse dateCreation properly.
WARNING:: Using empty as date for `time_edited` for code Your_Vocher_Code
```

It means that the creation time for your voucher was probably empty or similar
to `0000-00-00`. In that case the date of creation for your voucher will be
empty. This will not cause any trouble when running VoSeq. You can safely
ignore this message.

Create an index for all the data in your database:

```shell
make index
```

# Test database for development
You can use test data to populate your PostgreSQL database, useful for 
development.


Create tables for the database:

```shell
cd /path/to/Voseq/
make migrations
```

Import test data for your database:

```shell
make import
```

# Start the server
 
 In Linux start elasticsearch as a service and then start the server:
 
 ```shell
 sudo service elasticsearch start
 cd /path/to/Voseq
 make serve
 ```
 
 In macOSX if you do not have the `service` command, run elasticsearch in the background and then start the server:
 
 ```shell
 elasticsearch -d
 cd /path/to/Voseq
 make serve
 ```
*Note that if you did not check to Start Postgres automatically after login, you first have to go to Applications and start it manually from there by clicking on the app.*


Finally, open this URL in your web browser and you are ready to start using VoSeq:  `http://127.0.0.1:8000/`

