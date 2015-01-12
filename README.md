Thumbtack Simple Database Challenge
==========================

See http://www.thumbtack.com/challenges/simple-database


Dependencies/Environment
============

This toy depends on Python 2.7.  It was tested on Python 2.7.6 on OS X 10.10.1 (Yosemite).
It probably runs fine on other versions of Python and other versions of unix/linux.


Running the server
============

Clone a copy of this source repo

    % git clone git@github.com:eedeebee/tt-simple-db-fun

Then 

    % cd tt-simple-db-fun
    % ./server.py

You can type at the server's standard input stream.  To end the server, type ```END``` or hit ^D or ^C.

Running the tests
============

    % ./tests.sh

A successful run will look like this:

    Running test tests/test-01.input
    Passed
    Running test tests/test-02.input
    Passed
    Running test tests/test-03.input
    Passed
    Running test tests/test-04.input
    Passed
    Running test tests/test-05.input
    Passed
    Running test tests/test-06.input
    Passed

Status
==========

Limited testing, use at your own risk :)
