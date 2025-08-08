import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'RC and RL Calculator'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]
autosummary_generate = True
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
