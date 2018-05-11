#!/usr/bin/env python3

import io
import os

from setuptools import setup, find_packages

with io.open('about.md', 'r', encoding='utf-8') as f:
    ABOUT = f.read()

NAME = 'Orange3-WONDER'

MAJOR = 0
MINOR = 0
MICRO = 25
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

AUTHOR = 'Luca Rebuffi, Paolo Scardi, Alberto Flor'
AUTHOR_EMAIL = 'paolo.scardi@unitn.ut'

URL = 'https://github.com/WONDER-project/Orange3-WONDER'
DESCRIPTION = 'Whole POwder PatterN MoDEl in Orange.'
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
         'WONDER - UNTRUSTED = orangecontrib.xrdanalyzer.view.untrusted',
         ),
    'orange3.addon':
        ('Orange3-WONDER = orangecontrib.xrdanalyzer',)



}

import sys

from distutils.core import setup
from distutils.extension import Extension

ext_modules=[
    Extension("orangecontrib.xrdanalyzer.controller.fit.wppm_functions",               ["orangecontrib/xrdanalyzer/controller/fit/wppm_functions.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack",       ["orangecontrib/xrdanalyzer/controller/fit/fitters/fitter_minpack.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack_util",  ["orangecontrib/xrdanalyzer/controller/fit/fitters/fitter_minpack_util.pyx"]),
]

from Orange.canvas.application.addons import PipInstaller

class Package:
    def __init__(self, package_url="", name=""):
        self.package_url = package_url
        self.name = name

if __name__ == '__main__':
    pip = PipInstaller()

    try:
        if not sys.argv[1:][0] == "sdist": pip.upgrade(Package(package_url="pip", name="pip"))
    except:
        try:
            pip.upgrade(Package(package_url="pip", name="pip"))
        except:
            pass

    try:
        from Cython.Distutils import build_ext
    except:
        try:
            pip.arguments.append("--no-warn-script-location")
            pip.install(Package(package_url="Cython"))
        except:
            pass

    from Cython.Distutils import build_ext

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
        cmdclass = {'build_ext': build_ext},
        ext_modules = ext_modules,
    )
