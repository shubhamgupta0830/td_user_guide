# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Tabsdata'
copyright = '2024, Tabs Data'
author = 'Tabsdata'
release = 'v0.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'myst_parser',
    "sphinx_design",
    "pydata_sphinx_theme",
    # "custom_builder"
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True
}

source_suffix = ['.rst', '.md']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

myst_enable_extensions = ["colon_fence"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    # Navbar configuration
    # "navbar_start": ["navbar-logo"],  # Leave the left section empty (or add logo if desired)
    "logo": {
        "image_light": "_static/tabsdata.png",  # Logo for light theme
        "image_dark": "_static/tabsdata.png",   # Logo for dark theme (optional)
        # "text": "Tabsdata",  # Optional: Text next to the logo
        "link": "https://td-draft.webflow.io/",
    },
    # "navbar_center": ["custom_navbar.html"],  # Use external links in the center
    # "navbar_end": ["custom_navbar.html","custom_docs_nav.html"],  # Optional: Add social media icons on the right
     # Second navbar: Docs navigation (API Reference, Guide, Tutorials)
    # "navbar_end": ["custom_docs_nav.html"],  # Optional: Add social media icons on the right
    "home_page_in_toc": False,       # Optional
}

html_logo = "_static/tabsdata.png"

# html_theme_options = {
#     "navbar_start": ["navbar-logo"],
#     "navbar_center": [],
#     "navbar_end": ["navbar-icon-links"],
#         # Add external links (custom links for the navbar)
#     "external_links": [
#         {"name": "Twitter", "url": "https://twitter.com/your-handle"},
#         {"name": "GitHub", "url": "https://github.com/your-repo"},
#     ],
#         # Optional: Add social media icons for GitHub, Twitter, etc.
#     "icon_links": [
#         {
#             "name": "GitHub",
#             "url": "https://github.com/your-repo",
#             "icon": "fab fa-github",  # FontAwesome icon for GitHub
#         },
#         {
#             "name": "Twitter",
#             "url": "https://twitter.com/your-handle",
#             "icon": "fab fa-twitter",  # FontAwesome icon for Twitter
#         },
#     ],
#     # "navbar_start": [],
#     # "navbar_center": [],
#     # "navbar_end": [],
#     # # "primary_sidebar_end": ["sidebar-nav-bs"],
#     "show_nav_level": 4,  # Adjust levels in the sidebar
#     "navigation_depth": -1,  # Depth of sidebar navigation
#     # "collapse_navigation": True,
#     "show_toc_level": 2  # Show subsection navigation in the right sidebar
# }

# html_sidebars = {
#     "**": ["sidebar-nav-bs", "sidebar-ethical-ads"]
# }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['custom.css']
html_copy_source = False
html_show_sourcelink = False
html_show_sphinx = False