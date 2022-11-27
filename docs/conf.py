"""Configuration file for the Sphinx documentation builder.

Notes
-----
- `Sphinx configuration`_

.. _Sphinx configuration: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# pylint: disable=invalid-name
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

from project_release import (  # noqa: E402 # pylint: disable=wrong-import-position
    __version__,
)

project = "project_release"
copyright = "2022, Jean-Marie Lemetayer"  # pylint: disable=redefined-builtin
author = "Jean-Marie Lemetayer"

version = __version__
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["templates"]

html_theme = "sphinx_rtd_theme"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/devdocs/", None),
}
