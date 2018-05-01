#!/usr/bin/env python3

import io
import os

from setuptools import setup, find_packages

with io.open('about.md', 'r', encoding='utf-8') as f:
    ABOUT = f.read()

NAME = 'Orange3-WONDER'

MAJOR = 0
MINOR = 0
MICRO = 6
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

AUTHOR = 'Alberto Flor, Luca Rebuffi'
AUTHOR_EMAIL = 'alberto.flor@unitn.it'

URL = 'https://github.com/WONDER-project/Orange3-WONDER'
DESCRIPTION = 'Orange3 add-on for image data mining.'
LONG_DESCRIPTION = ABOUT
LICENSE = 'GPL3+'

CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3 :: Only'
]

KEYWORDS = [
    'orange3 add-on',
    'orange3-wonder'
]

PACKAGES = find_packages()

PACKAGE_DATA = {
    'orangecontrib.xrdanalyzer.view.widgets': ['icons/*.*'],
    'orangecontrib.xrdanalyzer.view.widgets': ['icons/*.*'],
    'orangecontrib.xrdanalyzer.controller.fit.data': ['*.*', 'delta_l_files/*.*'],
}

NAMESPACE_PACAKGES = ["orangecontrib",
                      "orangecontrib.xrdanalyzer",
                      "orangecontrib.xrdanalyzer.view",
                      "orangecontrib.xrdanalyzer.view.widgets",
                      "orangecontrib.xrdanalyzer.view.untrusted",
                      ]

INSTALL_REQUIRES = sorted(set(
    line.partition('#')[0].strip()
    for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt'))) - {''})

ENTRY_POINTS = {
    'orange.widgets':
        ('WONDER = orangecontrib.xrdanalyzer.view.widgets',
         'UNTRUSTED = orangecontrib.xrdanalyzer.view.untrusted',
         ),
    'orange3.addon':
        ('Orange3-WONDER = orangecontrib.xrdanalyzer',)



}

if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        namespace_packages=['orangecontrib'],
        entry_points=ENTRY_POINTS,
    )
