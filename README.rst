=============================================================
 Multi-Mechanize - Web Performance and Load Testing Framework
=============================================================

:Version: 1.2.0dev
:Web: http://code.google.com/p/multi-mechanize/
:Source: http://code.google.com/p/multi-mechanize/source/

--

View the presentation:

`Performance and Scalability Testing with Python and Multi-Mechanize`_

What is Multi-Mechanize? (the framework)
========================================

Multi-Mechanize is an open source framework for API performance and load
testing. It allows you to run simultaneous python scripts to generate load
(synthetic transactions) against a web site or API/service.

In your scripts, you have the convenience of mechanize along with the power of
the full Python programming language at your disposal. You programmatically
create test scripts to simulate virtual user activity. Your scripts will then
generate HTTP requests to intelligently navigate a web site or send requests to
a web service.

Multi-Mechanize uses a multi-process, multi-threaded engine to replay your
scripts and generate concurrent virtual users.

Results are saved in CSV format along with an HTML report containing stats and
graphs.

* Sample Results Reports: `report_1`_, `report_2`_, `report_3`_
* `Sample Graphs`_

Optionally, results can be stored in a database:

* `Database Storage for Test Data and Results`_


You should be proficient with Python, HTTP, and performance/load testing to use
multi-mechanize successfully.

What is python-mechanize? (scripting language: python + mechanize)
==================================================================

`Mechanize`_ is a Python module for stateful programmatic web browsing, used for
automating interaction with websites. It is similar to `WWW::Mechanize`_ for
Perl.

Test scripts are written in python using `Mechanize`_ or any other Python
web/network module (httplib, urllib, socket, twill, etc).

Features include:

* HTTP methods
* High-level hyperlink and HTML form support
* SSL support
* Automatic cookies
* Custom headers
* Redirections
* Proxies
* HTTP authentication

Installation
============

Multi-Mechanize is available for install via Pip, but on most systems you'll
need to install `matplotlib`_ first.

Installing matplotlib
---------------------

Installing `matplotlib`_ on Ubuntu::

    $ sudo apt-get install python-matplotlib

Methods for installing matplotlib are included in the `matplotlib documentation`_.

Installing Multi-Mechanize
--------------------------

A Pypi package might be forthcoming, but installation from source is easy via
Pip::

    $ pip install git+git://github.com/winhamwr/multi-mechanize.git#egg=multi-mechanize


Quick Getting-Started
==================

Multi-Mechanize comes packaged with a test project that you can clone to see
what can be done out of the box. To clone and run that project ::

    $ multi-mechanize.py --clone-test-project /path/to/my_test_project
    $ multi-mechanize.py /path/to/my_test_project

Detailed Getting-Started
========================

Creating Your Project
--------------------

Multi-Mechanize provides a ``--start-project`` command line option to create a
default configuration and directory structure for your project ::

    $ multi-mechanize.py --start-project path/to/my_project

This command simply copies across several things for you.

config.cfg
  Your project's configuration file. This file controls your test parameters.

test_scripts/
  This directory is where your python test scripts live.

results/
  This directory will contain the results of your tests after they're completed.
  Each run will have a timestamped directory with raw CSV data, and HTML summary
  report and PNG files containing graphs.

Configuring Your Project
------------------------

Your project's ``config.cfg`` file defines what will happen in your test run.
You'll set how long the tests should last, how many threads should be used, and
what test scripts should be run, along with various other parameters.

For details, see the `Configuration File Format`_ documentation.

Developing Test Scripts
-----------------------

Test scripts are what define the actions your virtual users should perform on
a test run. They also define what timers you should measure. At the core, these
are just python scripts containing a ``Transaction`` class and that stores any
timers in a ``self.custom_timers`` dictionary.

To get started, you can simply copy some of the example scripts from the test
project.

For instructions on developing your own scripts see the `Developing Scripts`_
documentation and the `Advanced Script Examples`_.

Getting Help
============

Discussion Group
----------------

Feel free to post a message to the `multi-mechanize users`_ discussion group.
questions, bugs, patches, collaboration, comments, welcome...

Bug Tracker
-----------

If you have any suggestions, bug reports or annoyances please report them
to the `Multi-Mechanize Bug Tracker`_.

License
=======

This software is licensed under the `GNU LGPL v3`_. See the ``LICENSE``
file in the top distribution directory for the full license text.

.. _`Performance and Scalability Testing with Python and Multi-Mechanize`: http://www.slideshare.net/coreygoldberg/performance-and-scalability-testing-with-python-and-multimechanize
.. _`report_1`: http://goldb.org/multi-mechanize/sample_results/results_2010.02.17_12.48.07/results.html
.. _`report_2`: http://goldb.org/multi-mechanize/sample_results/django_dev_server_results_2010.02.20_18.53.17/results.html
.. _`report_3`: http://www.goldb.org/multi-mechanize/sample_results/membase_results_280thread_30min_2010.07.26_14.42.19/results.html
.. _`Sample Graphs`: http://code.google.com/p/multi-mechanize/wiki/SampleGraphs
.. _`Database Storage for Test Data and Results`: http://code.google.com/p/multi-mechanize/wiki/DatabaseStorage
.. _`matplotlib`: http://matplotlib.sourceforge.net/
.. _`matplotlib documentation`: http://matplotlib.sourceforge.net/users/installing.html
.. _`Configuration File Format`: http://code.google.com/p/multi-mechanize/wiki/ConfigFile
.. _`Developing Scripts`: http://code.google.com/p/multi-mechanize/wiki/DevelopingScripts
.. _`Advanced Script Examples`: http://code.google.com/p/multi-mechanize/wiki/AdvancedScripts
.. _`multi-mechanize users`: http://groups.google.com/group/multi-mechanize
.. _`Multi-Mechanize Bug Tracker`: http://code.google.com/p/multi-mechanize/issues/list
.. _`GNU LGPL v3`: http://www.gnu.org/copyleft/lesser.html