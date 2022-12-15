Welcome to the project_release package documentation
====================================================

.. image:: https://img.shields.io/pypi/v/project-release
   :target: https://pypi.org/project/project-release
.. image:: https://img.shields.io/readthedocs/project-release
   :target: https://project-release.readthedocs.io/en/latest
.. image:: https://img.shields.io/github/license/jmlemetayer/project-release
   :target: https://github.com/jmlemetayer/project-release/blob/main/LICENSE.md
.. image:: https://img.shields.io/github/actions/workflow/status/jmlemetayer/project-release/build-and-publish.yml?branch=main
   :target: https://github.com/jmlemetayer/project-release/actions
.. image:: https://img.shields.io/github/actions/workflow/status/jmlemetayer/project-release/pytest-and-coverage.yml?branch=main&label=test
   :target: https://github.com/jmlemetayer/project-release/actions
.. image:: https://results.pre-commit.ci/badge/github/jmlemetayer/project-release/main.svg
   :target: https://results.pre-commit.ci/latest/github/jmlemetayer/project-release/main
.. image:: https://img.shields.io/codecov/c/gh/jmlemetayer/project-release/main
   :target: https://codecov.io/gh/jmlemetayer/project-release

*A tool to help releasing projects.*

Installation
------------

Using ``pip``::

    pip install project-release

Usage
-----

 - Inside your project, create a file ``.project-release-config.yaml``.
 - A very basic configuration can be generated with ``project-release sample-config``.
 - All options are documented in the :ref:`Configuration` page.
 - Once configured, a project can be released by executing ``project-release``.

License
-------

The :obj:`project_release` module is released under the `MIT License`_.

.. _`MIT License`: https://github.com/jmlemetayer/project-release/blob/main/LICENSE.md

.. toctree::
   :hidden:

   Home <self>
   Configuration <config>
   Advanced usage <advanced>
   API <api>
