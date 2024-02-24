"""Configuration file for the Sphinx documentation builder.

Notes
-----
- `Sphinx configuration`_

.. _Sphinx configuration: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

from project_release import __version__

project = "project_release"
copyright = "2022, Jean-Marie Lemetayer"  # noqa: A001
author = "Jean-Marie Lemetayer"

version = __version__
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["templates"]

html_theme = "sphinx_rtd_theme"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/devdocs/", None),
    "gitpython": ("https://gitpython.readthedocs.io/en/stable/", None),
}
