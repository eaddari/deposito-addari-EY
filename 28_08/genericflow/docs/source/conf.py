# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'genericflow'
copyright = '2025, EY'
author = 'EY'

import os
import sys

# Ensure the application source code is importable by Sphinx. From this file
# (docs/source/conf.py), the project src directory is two levels up.
sys.path.insert(0, os.path.abspath('../../src'))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []

# Support both .rst and .md (via MyST) sources
source_suffix = {
	'.rst': 'restructuredtext',
	'.md': 'markdown',
}

# If certain heavy or optional dependencies are not installed during
# documentation build time, mock them so autodoc can still import modules.
autodoc_mock_imports = [
	'crewai',
	'faiss',
]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
