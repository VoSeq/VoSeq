Recommendations for developers
==============================

There are many issues to tackle, some of them marked as
`easy <https://github.com/carlosp420/VoSeq/issues>`_.

Recommended workflow
--------------------

1. fork the VoSeq repository into your github account.
2. create a new branch: ``git checkout -b patch-1``
3. write code.
4. push to your repo: ``git push origin patch-1``
5. create a pull request
6. profit!

Before doing additional pull requests
-------------------------------------

1. Go to your master branch: ``git checkout master``
2. Add the upstream repo URL: ``git remote add upstream https://github.com/carlosp420/VoSeq.git``
3. Update your repo: ``git fetch upstream``
4. ``git merge upstream/master``
5. Repeat the instructions above from step 2.
