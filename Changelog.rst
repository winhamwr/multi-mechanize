================
 Change history
================

.. contents::
    :local:

.. _version-1.2.0:

1.2.0
=====
:release-date: TBA
:status: in development
:branch: master

.. _v1-2-0-important:

Important Notes
---------------

* Multi-Mechanize is now pip-installable.
* Project command-line arguments are now all based on the path to your project.
* The HTML output report now uses customizable Jinja2 templates for rendering.

.. _v1-2-0-news:

News
----

* Python package.

    Your favorite python load-testing tool is now installable as a normal
    python package. This means no more mixing your project code in with
    the Multi-Mechanize source.

* Verbosity options.

    Need to debug exactly what Multi-Mechanize is doing? Use the new ``-v``
    flag to get more detailed output.

    .. code-block: bash

        $ multi-mechanize.py path/to/project -v

* Project templates, cloning and a new starter project.

    With a move towards keeping your project data separate from the
    Multi-Mechanize source, it's still important for new users to have
    a good experience. Copy/Pasting a lot of boilerplate is not that.

    A new user (or someone starting a new project) can now use the handy
    ``--start-project`` commandline option to get them started in the
    directory of their choice. Getting a starter project up and running
    is as simple as:

    .. code-block: bash

        $ multi-mechanize.py path/to/project --start-project
        $ multi-mechanize.py path/to/project

* Exceptions in test scripts with no output are now properly caught as errors.

    Previously, if a test script had something like a bare assert:

    .. code-block: python

        class Transaction(object):
            def __init__(self):
                self.custom_timers = {}

            def run(self):
                assert False

    Multi-Mechanize wouldn't recognize that ``AssertionError`` because it didn't
    have an associated error string. Now, that Exception will not only be
    recognized, but the traceback from your test script will be printed to
    stderr.

* Customizable Jinja2 templates are now used for rendering the HTML report.

   HTML reports, now with templating goodness!

   The HTML report generator now looking first in your project's ``templates``
   directory for a template and then defaults to the included template.
   Currently, ``results_template.html`` is the only used template and to change
   your output, simple copy that file to ``your_project/templates/`` and modify
   to your heart's content.


* Added a script to convert Multi-Mechanize CSV output to JMeter's JTL XML
  format.

    Hudson users rejoice! mm-csv-to-jmeter.py lets you turn your CSV in to the
    format that Hudson's PerformancePlugin expects.