HISTORY
-------

2.5.0 (2021-04-02)
++++++++++++++++++
- Added bankit format for dataset creation.

2.4.0 (2021-03-14)
++++++++++++++++++
- allow batch upload of vouchers with Flickr photos urls.

2.3.1 (2021-03-13)
++++++++++++++++++
- updated the flickrapi dependency
- allow users to add voucher photos by pasting URLs of photos in Flickr
- added max requests to gunicorn workers

2.3.0 (2020-12-06)
++++++++++++++++++
- use Genes in Sequences model as foreign key
- implement celery queue to generate datasets
- added login required to run blast
- added warning to avoid batch upload of sequences with no gene column

2.2.5 (2020-11-15)
++++++++++++++++++
- serve css files over https

2.2.4 (2020-11-01)
++++++++++++++++++
- implement script to handle several voseq installations running in the same server
- implemented celery queue
- dataset creation is done asynchronously

2.2.3 (2020-08-17)
++++++++++++++++++
- upgraded Dockerfile to use debian-stretch

2.2.2 (2020-08-16)
++++++++++++++++++
- fixed usage of django-suit for admin interface.
- allow partial match to voucher code, genus, species, accession numbers, gene_codes
  when searching for Vouchers or Sequences in the admin interface. Eg. searching
  for "Meli" will return matches to Melitaea, Melinaea, etc.
- References to vouchers from Sequence objects will show voucher code, genus and
  species.
- dropped support for python 3.5
- added config.json for initial deployment.

2.2.1 (2020-06-28)
++++++++++++++++++
- upgraded dataset-creator dependency to allow generating datasets with full taxon
  names even if names are longer than 54 characters.

2.2.0 (2020-06-27)
++++++++++++++++++
- dropped support for vagrant
- start using docker
- fix 500 error when creating report selecting altitude. Now you can select either
  max or min altitude.

2.1.6 (2018-02-03)
++++++++++++++++++
- Fixed error when doing simple search fro voucher code that does not exist in
  the database. issue #381.

2.1.5 (2018-01-15)
++++++++++++++++++
- Voucher table can include type_species.
- Genbank fasta files do not include those with accession numbers.
- Translation of triples with missing codons do not raise exception.
- Lineage included in genbank fasta files.

2.1.4 (2017-11-06)
++++++++++++++++++
- Fixed bug when generating datasets with certain codon positions.

2.1.3 (2017-08-28)
++++++++++++++++++

- Create log for django in tmp directory.
- Install ncbi-blast+ when provisioning in vagrant.

2.1.2 (2017-08-28)
++++++++++++++++++

- Strip sequences of line breaks before creating database for BLAST. This was
  causing error 500.

2.1.1 (2017-08-26)
++++++++++++++++++

- Avoid error 500 when doing BLAST and there are no sequences in database to
  create the BLAST database.

2.1.0 (2017-05-07)
++++++++++++++++++

- Datasets now include taxon names if required.
- Dropped using Haystack for advanced search results, but autosuggestion still using haystack.
- Added indexes to speed up queries.

2.0.5 (2016-12-21)
++++++++++++++++++

- Fixed that did not allow batch upload of sequences.

2.0.4 (2016-10-04)
++++++++++++++++++

- Fixed bug when validating coordinates during import. Fixes #357

2.0.3 (2016-10-03)
++++++++++++++++++

- Upgraded dependency Django to version 1.10.2

2.0.2 (2016-09-29)
++++++++++++++++++

- Permanent fix for django-import-export. Overriding method `self.save_instance`
  needed to be updated to new signature of django-import-export.

2.0.1 (2016-09-28)
++++++++++++++++++

- Temporal fix for django-import-export that issued errors for the function
  `self.save_instance` when importing vouchers.


2.0 (2016-09-26)
++++++++++++++++

Fixed bugs
""""""""""
- Create_dataset tool will produce gene partitions sorted regardless of letter case.
  The same for Phylip charset_block.
- Creating Phylip datasets for charset_block partitioned by codon position and
  1st2nd_3rd.
  The same for Phylip charset_block.
- Fixed bugs for creation of Nexus files using partitions.
  The same for Phylip charset_block.
- Characters not in IUPAC (except '?-') will not be accepted when importing or
  saving sequences.
- Added tool for batch import of sequences in admin interface.
- Added tool to add genes in admin interface.
- In dataset creation, moved warnings to bottom of page. There will be only a big
  warning message on top.
- Dataset creation tool will issue error messages when users wants datasets
  containing only codons 1,3 and 2,3.
- Dataset creation tool, genes will be sorted alphabetically, regardless of case.
- Fixed version on footer.
- MEGA datasets.
- Refactoring of ``create_dataset`` module.
- Editing vouchers in Admin interface: adding photos is optional not mandatory.
- Error message will be shown when attempting to translate bad codon such as "N--".
- Shown error message if sequence is longer than specified nchar value.
- Show message that FASTA datasets have all the sequences concatenated.
- Sorted list of gene codes in voucher page.
- Corrected path for media files in nginx so uploaded images will be shown in
  voucher pages.
- Convert symbols and white spaces of code and taxon names to underscore to
  avoid choking Biopython when creating datasets.
- Fixed method to import flickr images.
- Fixed template to show thumbnail of flickr images.

Features
""""""""
- date collection is flexible. Added a start and end collection dates which
  can be complete (YYYY-mm-dd) or incomplete (only year, or only year and month).
- added alert message when user attempts to generate voucher table without
  specifying the gene codes or taxon sets.
- added optional deployment for test installations.
  

pre-release v2.0.0-beta (2015-08-06)
++++++++++++++++++++++++++++++++++++

- **Interactive overview table** to browse taxa and the genes sequenced for them.
- **Easy instalation** and deployment using Vagrant virtual machines. Install
  and configure VoSeq and all its dependencies with the command ``vagrant up``.
- **Fixed search unnecessary spelling suggestions** in search results due to
  capital and lower cases of the same word.
- **Added interactive overview table** for vouchers and genes using `dataTables`.
- **Added taxonset creation** by adding lists of taxon codes.
- **Importing voucher images to Flickr** (optional, by default it keeps all the
  image files in the local server).
- **Added batch upload of voucher** data. It will show a diff between fields that
  could be updated and will also show a confirmation page before execution of
  changes.
- **Added Zwick et al. method** to degenerate DNA sequences for create_dataset tool.
- **Implemented ``get_updated_field``** for haystack so it would be quicker to update
  our database index as the option ``age=number of hours`` can be used.

pre-release v2.0.0-alpha-3 (2015-06-12)
+++++++++++++++++++++++++++++++++++++++

- **Getting correct VoSeq version number** from ``HISTORY.rst``.
- **Importing voucher image files** to database and new VoSeq package.

pre-release v2.0.0-alpha-2 (2015-06-02)
+++++++++++++++++++++++++++++++++++++++

- **Note** that it still needs the ability to generate datasets using
  the degenerated translations by Zwick et al, 2012.

New features
""""""""""""

- **Create dataset** in MEGA format.
- Search results show a text box with the full list of vouchers so that they can be copied in order
  to create new taxonsets.

pre-release v2.0.0-alpha-1 (2015-05-28)
+++++++++++++++++++++++++++++++++++++++

Re-written features
"""""""""""""""""""

-  **Browse page** for vouchers recently modified/added to the database.
-  **Blast new sequence** tool for blasting any sequence against all or
   a subset of sequences kept in VoSeq.
-  **View genes** tool to quickly see what genes are currently in the
   database. **New:** there is a badge for each gene showing the number
   of voucher records that have sequences for that particular gene.
-  **Create dataset** tool to generate ready-to-run datasets in commonly
   used phylogenetic software such as TNT, PAUP, MrBayes, BEAST, RaXML.
-  **Create voucher table** tool that generates a ready for publication
   CSV table (importable in MS Excel) with information for each voucher
   record, such as: Code, Genus, Species, Locality, Sequences present or
   not for each gene, etc.
-  **Create gene table** tool that generates a CSV table with statistics
   about particular DNA alignments (constructed with the vouchers and
   gene codes that you can select) such as gene type, sequences length,
   dataset completion, percentage of variable sites, parsimony
   informative, conserved sites, and frequency of each nucleotide in
   your alignment.
-  **Create GenBank FASTA file** tool that generates FASTA file with
   most of the required info ready for submission to GenBank using their
   Sequin software.
-  **Share data with GBIF** tool that creates a data dump of the
   information from all vouchers into a CSV table (that can be imported
   in MS Excel) ready for being used with GBIF's tool IPT.
-  **Advanced search** tool for searching voucher or sequences using
   combination of data fields.
-  **Batch modification of voucher data** tool in the Administration
   interface.

New features
""""""""""""

-  **Faster generation of datasets** due to the use of more efficient
   algorithms.
-  **Faster advanced searches** due to the indexing of the database
   using the backend elasticsearch.
-  **General search** tool in the navegation bar that accepts taxonomic
   keywords to search for voucher records.
-  **Keyword suggestions** tool for the general search. If users
   misspell a taxonomic name when they use this tool, they will be shown
   the possible correct spelling of the query with the message "Did you
   mean:".
-  **Pagination** tool for searches, so that up to 20 results are shown
   per page along with links to **next** and **previous** pages.
-  **Fine grained** permissions to upload and look at the sequences.
-  **Login accounts**. Only users with a working account will be able to
   look/retrieve any DNA sequence. They will not be able to create
   datasets. However, they will still be able to look at voucher
   information, search for vouchers and sequences and perform BLASTs.
-  **Superuser account**. Only the Superuser/Administrator will be able
   to create login accounts, change passwords, add user email. Also
   users can be given specific permission to most of components in VoSeq
   such as: adding genes, gene sets, members, vouchers, primers,
   sequences, etc.
-  **Users can be grouped** for better management of permissions.
-  **Batch deletion** tools for vouchers and sequences.

Version 1.7.X
+++++++++++++
- 2014-11-13 Carlos Peña:

  * When making voucher tables there were many repetitive columns, fixed.

- 2014-08-19 Carlos Peña:

  * Updated flickr_upload_from_directory file to batch upload photos into
  * Flickr from local directory. One file at a time.
  * Updated phpflickr api file to use CURLFile when uploading files using
    curl. @file in curl_set_opt is deprecated.

Version 1.7.4
+++++++++++++
- 2014-08-01 Carlos Peña:

  * Updating phpFlickr to deal with the change in Flickr's API (all
    connections to Flickr are now using https).

Version 1.7.3
+++++++++++++
- 2013-11-07 Carlos Peña:

  * Fixing bugs when creating degenerated datasets
  * The codon ATG was converted to ??? due to a typo (an extra white
    space). Codon with lower case letters in the sequences were converted
    to ???. Fixed by converting the whole sequence to uppercase before
    processing.

Version 1.7.2
+++++++++++++
- 2013-11-01 Tobias Malm:

  * Fixed the GenBank fasta file creator to work for introned genes. Now
    creates an extra protein alignment to upload together with the
    nucleotide one. Also removes sequences that already are associated with
    an accession number.

- 2013-10-10 Tobias Malm:

  * Implemented degenerate coding for retrieval of datasets and
    restructured the dataset creator a bit. Degenerate (Degen) coding
    translates possible synonymous change sites to IUPAC codes to minimize
    heterogeneity problems. It is implemented in some different flavours
    (at least for standard genetic code.) Read more in Zwick etal. (2012)
    and Regier et al. (2010). - Thanks to Andreas Zwick for the translation
    code base.
  * Fixed a bug in taxon/gene set creator trying empty names when using
    list mode. - Thanks to Rasa Bukontaite
  * Some other small bugs and layout stuff.

Version 1.7.1
+++++++++++++
- 2013-10-09 Carlos Peña mycalesis@gmail.com:

  * Scripts to MySQL import and merge Do not remove the placeholder file
    index.html in uploads folder.
  * Tools to import and merge databases
    It is possible to merge databases. All data that is not already in the
    current database will be incorporated. If there are conflicts, the
    changes will not be made, and warning messages will be issued.
  * MySQL dump was not working
    It couldn't find the right path for ``mysqldump``. Fixed, works for now.
  * File was missing
  * Adding more files from Tobias
    MySQL database import, export, merge and new dataset tools creation.

- 2013-09-28 Carlos Peña mycalesis@gmail.com:

  * Added Tobias's code

- Tobias 2013-10-01:

  * Fixed a small bug in data set creator apparently adding "unit
    separator" codes in taxon names under some circumstances.

- Tobias 2013-09-11:

  * Included a merge databases option under admin, that let you add values
    from a database backup to your existing database. This will not
    overwrite anything in your old database and will only add
    non-problematic information to your current db. E.g. if a genecode or
    voucher already exist but is specified differently between databases,
    these and their related values (sequences/primers) will not be added.
  * After the merge you will recieve an output stating what was and what
    was not added to the database (and why).
  * Fixed a bug in the import database script that didnt check for prefix
    names, resulting in wrongly named new database tables.

- Tobias 2013-08-30:

  * Included functions to store aligned morphological data as a
    gene/alignment (i.e. a string of numbers,e.g. 01100110) representing
    character states for a voucher. A morphology alignment need to be
    aligned!! Multistate characters can be introduced within brackets, i.e.
    (),{},[] as well as with or without separating comma. E.g. [01] as in
    TNT or {0,1,2} as in MrBayes. These will be reformed when creating
    datasets.
  * Datasets, gene/alignment tables and so on can now be made to include
    morpholocical data.
  * Fixed a bug in local blast for windows, that tried to read from the
    wrong database file.

Version 1.7.0
+++++++++++++

- Tobias 2013-04-24:

  * Added a geneset creator in similar style as for taxonsets. Genesets can
    be now used for creating tables and datasets.

- Tobias 2013-04-24:

  * Fixed a bug in the taxonset creator that unchecked taxa when filtering
    records with a text string.

- Tobias 2013-04-24:

  * Added an update account page where user information and passwords may
    be changed. This may be used for the account in use, but admin status
    can not be changed. This allows for a database manager to create
    temporal account names for new users, who themselves can change their
    info later.

- Tobias 2013-04-24:

  * Layout fixes. E.g. mainpage gene viewer.

- Carlos 2013-04-11:

  * Fixing installation script 4. No need to check for writeable dojo
    folder. Checking dojo_data instead.

Version 1.6.0
+++++++++++++

- Carlos 2013-03-29:

  * Added button to get a Backup file of the MySQL database.

- Carlos 2013-03-31:

  * Added button, page, js functions to upload big Backup files of the
    MySQL database (using plupload).

Version 1.5.0
+++++++++++++
- [Carlos 2013-03-18] Allowing several photos for each voucher.
- [Carlos 2013-03-18] MySQL table definition for voucher images changed to
  accommodate several strings separated by "|".
- Tobias 2013-03-20] Various layout and smaller bug fixes(e.g. batch
  seq import/update for 'notes').
- Tobias 2013-03-20] Created gene/alignment (xml) table output with
  characteristics for a given alignent, such as variable, conserved,
  parsimony informative sites and nucleotide frequencies. Also
  specified for individual codon positions for protein coding genes.
- Tobias 2013-03-15] Included new gene information in the data set
  retrieval scripts. It ignores introns by default, but if included
  treated as a separate parition block.[Thanks to Seraina Klopfstein]
  Genetic codes for amino acids translations are now set at gene info
  page. "Special" data set now also includes AA, AA partitions and dna
  partitions are now combineable in the same data set and specified as
  such in the output files. AA partitions will not be made if protein
  code is set to no.
- Tobias 2013-03-15] Changed gene information to include more fields,
  including protein coding or not, aligned or not, intron regions and
  gene type. To be used for new features in the create dataset and
  other scripts.
- Tobias 2013-03-11] Included -- ignore of taxa from taxonsetfor table
  output.
- Tobias 2013-03-09] Included -/N/n to be counted as missing for the \*
  and number of bp output in tables.
- Tobias 2013-03-10] Included improved delete button for sequences, as
  well as one for genes/alignments. NOTE! Deleting an alignment/gene
  will delete all accompanying seqs and primers!!! [Thanks to Rasa
  Bukontaite]

Version 1.4.4
+++++++++++++
- [Carlos 2013-03-17] Fixing mask\_url links in BLAST scripts.

Version 1.4.3
+++++++++++++
- [Carlos 2013-02-16] Fixing directory chage for login-form.

Version 1.4.2
+++++++++++++
- [Carlos 2013-02-13] Fixing checkdate bug in files for batch upload/update.
  [Thanks to Marianne Espeland].

Version 1.4.1
+++++++++++++
-  Tobias 2013-02-10] Fixing curl function in Windows [connection to
   Github].

Version 1.4.0
+++++++++++++
- [Carlos 2013-02-03] It is possible to host all voucher photos in local
  server. No need for Flickr then. Add the line
  ``$photos_repository = 'local';`` to your ``conf.php`` file.

Version 1.3.8
+++++++++++++
- [Carlos 2013-02-01] During installation, passwords for MySQL and VoSeq
  administrator go under permissive checks in case they are complex passwords
  [Thanks to Pierre Solbès]
- [Carlos 2013-02-01] During installation, suggest user to check that the
  socket in php.ini points to the same file as in the my.cnf configuration
  file. [Thanks to Pierre Solbès]
- [Carlos 2013-01-31] Users will get a notification in Login page when there
  is a new version of VoSeq available in GitHub.
- [Carlos 2013-01-31] Version is taken from changelog.md file.

Version 1.3.7
+++++++++++++
- [Carlos 2013-01-30] Improved installation script to detect problems during
  connection with MySQL. Error will be shown to user for further inspection.
- [Carlos 2013-01-29] Moved scripts to upgrade mysql schema into file
  mysql_upgrade.php
- [Carlos 2013-01-29] Using changelog.md instead of changelog.txt
- [Carlos 2013-01-28] In tool to create FASTA files for GenBank submissions:
  replace the ?-marks at the beginnings by "N".

Version 1.3.6
+++++++++++++
- Tobias 2013-01-27] Added a checkbox for single gene datasets to
  exclude taxa missing that gene from the dataset (yes/no).
- Tobias 2013-01-27] Also made a box where you enter minimum number of
  genes needed for a taxa to enter your dataset (maximum is the number
  of genes you've chosen) - say you have chosen 9 genes and want each
  taxa in yur dataset to have at least 7 of those - just enter 7 in
  that box and run and it will filter taxa with less than 7 of your
  chosen genes.

Version 1.3.5
+++++++++++++
- Tobias 2012-12-04] Edited some table outputs for dataset and table
  creation and overview table.

Version 1.3.4
+++++++++++++
- [Tobias 2012-11-30] Added automatic update of gene codes in primer
  and sequences tables when updating gene names.
- [Tobias 2012-11-30] Fixed small redirect bug on admin page.
- [Tobias 2012-11-29] Fixed bug in the code+genepair duplicate control
  for upload batch.
- [Tobias 2012-11-29] Added a batch update script allowing insertion of
  new values into empty fields for already existing vouchers, sequences
  and primers. Will not overwrite already existing values.

Version 1.3.3
+++++++++++++
- [Carlos 2012-11-20] Fixing mask_url bug in add.php file.

Version 1.3.2
+++++++++++++
- [Carlos 2012-11-15] Fixing mask_url bug in add_gene.php file.
- [Carlos 2012-11-14] Fixing installation script to consider altenate socket

Version 1.3.1
+++++++++++++
- [Carlos 2012-11-13] Adding remove voucher button. It will delete a record including
  sequences, primers and remove them from taxonlists.
  Fixing adding taxonlist links and behaviour.

Version 1.3.0
+++++++++++++
- [Carlos 2012-10-31] Will issue alert dialogs when sequences blocks have
  no sequences when creating datasets

Version 1.2.8
+++++++++++++
- [Carlos] fixes to take into account tildes and accents when creating users.

Version 1.2.7
+++++++++++++
- [Carlos] fixing bugs for uploading sequences and voucher data. Making sure
  that white spaces are stripped.
- [Carlos] adding citation of PLOS paper to intro page.

Version 1.2.6
+++++++++++++
- [Tobias] Change in form: accept-charset="utf8" in the
  upload\_sequences.php file to allow windows systems to properly
  import all utf8 characters - before it gave error and stopped the
  import process when encountering a special symbol.

Version 1.2.5
+++++++++++++
- [Carlos 2012-09-02] In Mac systems the installation script will prefill the
  url address to ``http://127.0.0.1/yadaya`` For all other systems the default
  is ``http://localhost/yadaya``.
- [Tobias] when you change a voucher code, it should be updated in
  TaxonSets as well.

Version 1.2.4
+++++++++++++
- [Tobias] included "Determined by" and "Auctor" fields to voucher table
  and "notes" to sequence table.
- Changed the handling of dates and integer values in processing of
  vouchers and sequences.

Version 1.2.3
+++++++++++++
- 20120514 (CP) including help text and links to online documentation.

Version 1.2.2
+++++++++++++
- 20120426:

  * (CP) installation script: entering table prefix for MySQL is
    not mandatory now.

- 20120424:

  * (TM, CP) creating genbank fasta file keeps codes in the original case.
    When code is updated or changed for a record, it is also updated for sequences and primers tables.

- 20120405:

  * (CP) admin/add.php file now has mysql\_real\_escape\_string() too all
    variables before inserting or updating to MySQL tables.

- 20120322:

  * (CP) Fixing installation issues. Had to create folder dojo\_data for
    autocomplete boxes.

- 20120319:

  * (TM) Fixes of BLAST scripts to run in Windows.
  * (TM) Improving creating datasets, and aminoacids option.

- 20120308:

  * (CP) Added the use of prefixes for the tables in MySQL so
    that there can be several installations of VoSeq in one MySQL server by
    using different prefixes.
  * (CP) Default prefix is voseq\_ and it is defined in conf.php file during
    installation. Users can change the prefix during installation as well.
  * (CP) Fixing installation issues, with creating the URL path that will go
    into file conf.php

Version 1.1.10
++++++++++++++

- 20120306:

  * (CP) Made it friendlier to get a Token for using Flickr. Had to create an
    App for VoSeq and register ir in Flickr.
  * Now the Api and secret keys will be the same for all Flickr installations,
    and only the Token will be different.
  * Users of VoSeq can get a token from here:
    http://nymphalidae.utu.fi/cpena/VoSeq/
  * (CP) Removing sump and sumt from creating dataset in NEXUS tool. Also
    fixing brlenspr to unconstrained:Exp(10.0);

- 20120302:

  * (CP) Share data with GBIF is now an Excel Sheet.
  * (CP) Fixing issues of blasts scripts.

- 20120227:

  * (CP) Integration with EOL and Flickr. From voucher pages is possible to
    submit a photo to EOL's flickr pool of photos.
  * (CP) For voucher pages, authority and year will be pulled from EOL. A link
    to the EOL page will be shown under the voucher Code.
  * (CP) Create dataset page. Cosmetic fix for selecting codons positions:
    1st-2nd, 3rd
  * (CP) Batch uploading of vouchers. Allowing empty fields for latitude and
    longitude (will not issue error message) and will be inserted into MySQL
    database as NULL fields.
  * (CP) process\_upload\_sequences.php: Removed utf8\_encoding of
    raw\_voucher\_upload data, it is not necessary.

Version 1.1.9
+++++++++++++
- 20120222:

  * (CP) added mysql\_set\_charset to utf8 for all php files.
  * (CP) added template data for fresh install of VoSeq, it includes gene,
    voucher photos and maps with test API key from Yahoo!

- 20120221:

  * (CP) fixed add\_taxonset, it looks nicer now.
  * (CP) creating of blank database during installation includes sample data
    such as two codes and one gene, which are named template and the gene is
    in the list of genes with its reading frame.

Version 1.1.8
+++++++++++++
- 20120219:

  * (CP) fixing blast\_locally\_full\_db.php to work in Windows and Linux.
    Including error files and error messages.
  * (CP) fixing badly shown margins and sidebars in IE.
  * (CP) blast\_vs\_genbank checks for too short sequences before trying to
    blast against Genbank
  * (CP) blast\_locally\_full\_db output processing was a little bit redundant.

Version 1.1.7
+++++++++++++
- 20120217

  * (CP) setting width and height for images
  * (CP) setting .htaccess file with cache control and Leverage browser caching
  * (CP) setting character set for pages using php code header('Content-type:
    text/html; charset=utf8'); before generating any content. included in
    file header.php 20120215
  * (CP) documentation now instructs on how to enable CURL in Windows. It's
    needed to enable Flickr plugin.
  * (CP) fixed install4.php it now creates the field flickr\_id in table voucher
    for MySQL. Intro message.
  * Clean up of make\_footer function
  * search.php file avoids sql injection
  * jquery.js included in /includes
  * file blast\_functions.php created in /includes
  * blast\_vs\_genbank.php heavily modified to include some javascript to make
    a countdown while data is retrieved from NCBI BLAST (using some code from
    Rod Page).
  * setting size of colofon images in footer

Version 1.1.6
+++++++++++++
- 20120214:

  * (CP) admin/add.php?code=PM10-14' prevent sql injection
  * (CP) Installation script writing conf.php file by itself.

- 20120205:

  * (CP) installation/index.php Absolute path to VoSeq.
  * (CP) installation script in Windows, it does not add any more \\\\\\ to
    the local\_folder path.

- 20120202:

  * (CP) file admin/add.php commented UTF8\_encoding functions
    because cause encoding problems. Now seems to be working ok.

- 20120126:

  * (CP) blast\_locally.php lines 238-245
  * (CP) blast\_locally\_full\_db.php line 63: comment set names utf8
  * (CP) blast\_coi\_vs\_genbank.php => blast\_vs\_genbank.php line 107-108 line
    137-142 not BLAST only for COI genes.
  * (CP) markup\_functions.php Make MS Excel table.
  * (CP) sequences.php no utf8.

Version 1.1.5
+++++++++++++
- 20111128:

  * (CP) Fixed "update" primers when there is nothing to update. Now they are
    inserted as new entries.

- 20111110:

  * (CP) Several fixes of the look and feel.
        

Version 1.1.0
+++++++++++++
- 20110725:

  * (TM) Fixed the genbank list retrieval with taxonset, and gene picker.
    Fixed a viewing table in the normal section. Added a in-db data summary at
    footer.

- 20110614:

  * (TM) Added taxonset creator and editor, with display of voucher info and
    existing sequences.
  * Taxonsets may be used for dataset retrieval or table creation together with
    or as separate from the free code field.

- 20110520:

  * (TM) edited dataset retrieval page and functionality, now with support for
    various codon position partitioning, as well as PHYLIP and FASTA formats.

- 20110516:

  * (TM) added batch upload function for vouchers and sequences.
  * (TM) added gene table layout (view/edit/add).
  * (TM) auto update of comboBoxes and auto removal of old search results.
  * (TM) added field choice and value delimitor choice for table and dataset
    generation and fasta format for dataset gen.
  * (TM) some small bug and layout fixes.

- 20110414:

  * (TM) login scripts and password handling.
  * (TM) link refs and URL masking.
  * (TM) some layout fixes and adding of host field.
  * (TM) added record history field, storing changes made to a record and by
    who (user).

Version 1.0.8
+++++++++++++
- 2011-03-15:

  * Some minor modifications on voucher'page.
  * Added tool to do a blast of COI sequences against ncbi genbank, via
    webservice.

Version 1.0.5
+++++++++++++
- 2007-08-24:

  * Included validation of latitude and longitude in admin
    interface, only decimal numbers are accepted now. This was included in
    both, creation of new record and when updated old ones. It was tweaked a
    little to take into account when user doesn't enter coordinates so that
    it will be written in the database as NULL values.

Version 1.0.4
+++++++++++++
- 2007-08-23:

  * Included Yahoo! Maps.
  * Included Tooltips in add.php (add and update records) of admin interface.
    So users can enter latitude and longitude as decimal degrees. Sexagesimal
    degrees has been abandoned.
  * Story.php shows sexagesimal coordinates that are converted in the fly
    from decimal numbers.

Version 1.0.3
+++++++++++++
- Now interfaces show primer number 6, thanks to Julien Leneveu.

Version 1.0.2
+++++++++++++
- 2007-05-03:

  * Included some more dojo.
  * In admin interface, included option to delete sequence records by id.

Version 1.0.1
+++++++++++++
- 2007-03-25:

  * Included creation of thumbnails to avoid showing squashed
    pictures.
  * MySQL database modified, ``alter table add column thumbnail``.

Version 1.0.0
+++++++++++++
- 2007-03-21:

  * Heavy change in makeup.
  * Inclusion of AJAX using dojo: comboBox.

Version 0.0.11
++++++++++++++
- 2007-03-15:

  * In Admin interface, the default geneCode has been
    eliminated, now user if forced to select one.
  * In Admin interface, the handling of sequences is more precise by using ids
    instead of code+geneCode.
  * In Admin interface, number of base pairs and ambiguous base pairs are shown
    for sequences.

Version 0.0.10
++++++++++++++
- 2007-03-13:

  * In Admin interface, updating voucher info was giving "duplicate code"
    errors, fixed now.

Version 0.0.9
+++++++++++++
2007-03-11 - In Admin interface, it is posible to change record's code.

Version 0.0.8
+++++++++++++
2007-03-10 - Fixed searches of genera. "%string%" by "string%".

Version 0.0.7
+++++++++++++
- 2007-03-09:

  * Changed to smaller icons of "voucher picture" and "change picture".
  * Search results are ordered by voucher's code.

Version 0.0.6
+++++++++++++
- 2007-03-02:

  * Improved "Next" and "Previous" arrwos to browse through records when user
    does searches in "User interface"

- 2007-02-28:

  * Lab work in Admin interface correctly aligned now.
  * Added yyyy-mm-dd when user has to enter dates.
  * Added "Next" and "Previous" arrows to browse through records when user does
    searches in "Admin interface"

Version 0.0.5
+++++++++++++
- 2007-02-22 Added "Next" and "Previous" arrows to browse through records when
  user does searches in "User interface"

Version 0.0.4
+++++++++++++
- 2007-02-16:

  * Sequences appear wrapped now.
  * User interface now doesn't show misaligned rows for See sequences.
  * geneCode can be chosen from a selection of pre-stablished geneCodes.

Version 0.0.3
+++++++++++++
- 2007-02-16:

  * Search interface for administration ("admin") expanded in a
    FileMaker's fashion.
  * Searches accept incomplete queries (i.e. typing cladi in Notes field will
    retrieve all records with Cladistics + any additional characters.
  * Added option to change voucher picture.
  * Changelog created.
