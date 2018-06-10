#!/usr/bin/env python3

import io
import os

from setuptools import setup, find_packages

with io.open('about.md', 'r', encoding='utf-8') as f:
    ABOUT = f.read()

NAME = 'Orange3-WONDER'

MAJOR = 0
MINOR = 1
MICRO = 26
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
    'orangecontrib.xrdanalyzer.view.widgets'           : ['icons/*.*'], # to be removed
    'orangecontrib.xrdanalyzer.view.initialization'    : ['icons/*.*', 'data/*.*'],
    'orangecontrib.xrdanalyzer.view.ipf_and_background': ['icons/*.*'],
    'orangecontrib.xrdanalyzer.view.thermal_properties': ['icons/*.*'],
    'orangecontrib.xrdanalyzer.view.microstructure'    : ['icons/*.*'],
    'orangecontrib.xrdanalyzer.view.fitting'           : ['icons/*.*'],
    'orangecontrib.xrdanalyzer.view._untrusted'        : ['icons/*.*'],

    'orangecontrib.xrdanalyzer.controller.fit.data': ['*.*', 'delta_l_files/*.*'],
}

NAMESPACE_PACAKGES = ["orangecontrib",
                      "orangecontrib.xrdanalyzer",
                      "orangecontrib.xrdanalyzer.view",
                      "orangecontrib.xrdanalyzer.view.widgets",
                      "orangecontrib.xrdanalyzer.view.initialization",    
                      "orangecontrib.xrdanalyzer.view.ipf_and_background",
                      "orangecontrib.xrdanalyzer.view.thermal_properties",
                      "orangecontrib.xrdanalyzer.view.microstructure",    
                      "orangecontrib.xrdanalyzer.view.fitting",           
                      "orangecontrib.xrdanalyzer.view._untrusted",
                      ]

INSTALL_REQUIRES = sorted(set(
    line.partition('#')[0].strip()
    for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt'))) - {''})

ENTRY_POINTS = {
    'orange.widgets':
        (#'OLD STRUCTURE! = orangecontrib.xrdanalyzer.view.widgets',
         'Initialization = orangecontrib.xrdanalyzer.view.initialization',
         'Instrument and Background = orangecontrib.xrdanalyzer.view.ipf_and_background',
         'Thermal Properties = orangecontrib.xrdanalyzer.view.thermal_properties',
         'Microstructure = orangecontrib.xrdanalyzer.view.microstructure',
         'Fitting = orangecontrib.xrdanalyzer.view.fitting',
         #'Untrusted = orangecontrib.xrdanalyzer.view._untrusted',
         ),
    'orange3.addon':
        ('Orange3-WONDER = orangecontrib.xrdanalyzer',)



}

import shutil, sys

from distutils.core import setup
from distutils.extension import Extension

ext_modules=[
    Extension("orangecontrib.xrdanalyzer.util.congruence",                                           ["orangecontrib/xrdanalyzer/util/congruence.pyx"]),
    Extension("orangecontrib.xrdanalyzer.util.general_functions",                                    ["orangecontrib/xrdanalyzer/util/general_functions.pyx"]),
    Extension("orangecontrib.xrdanalyzer.util.test_recovery",                                        ["orangecontrib/xrdanalyzer/util/test_recovery.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.fit_parameter",                              ["orangecontrib/xrdanalyzer/controller/fit/fit_parameter.pyx"]),
    Extension("orangecontrib.xrdanalyzer.model.atom",                                                ["orangecontrib/xrdanalyzer/model/atom.pyx"]),
    Extension("orangecontrib.xrdanalyzer.model.diffraction_pattern",                                 ["orangecontrib/xrdanalyzer/model/diffraction_pattern.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure",                     ["orangecontrib/xrdanalyzer/controller/fit/init/crystal_structure.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure_symmetry",            ["orangecontrib/xrdanalyzer/controller/fit/init/crystal_structure_symmetry.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters",                        ["orangecontrib/xrdanalyzer/controller/fit/init/fft_parameters.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization",                    ["orangecontrib/xrdanalyzer/controller/fit/init/fit_initialization.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.init.thermal_polarization_parameters",       ["orangecontrib/xrdanalyzer/controller/fit/init/thermal_polarization_parameters.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.instrument.background_parameters",           ["orangecontrib/xrdanalyzer/controller/fit/instrument/background_parameters.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.instrument.instrumental_parameters",         ["orangecontrib/xrdanalyzer/controller/fit/instrument/instrumental_parameters.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.microstructure.constrast_factor",            ["orangecontrib/xrdanalyzer/controller/fit/microstructure/constrast_factor.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.microstructure.size",                        ["orangecontrib/xrdanalyzer/controller/fit/microstructure/size.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.microstructure.strain",                      ["orangecontrib/xrdanalyzer/controller/fit/microstructure/strain.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters",                      ["orangecontrib/xrdanalyzer/controller/fit/fit_global_parameters.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities",                         ["orangecontrib/xrdanalyzer/controller/fit/util/fit_utilities.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack",                     ["orangecontrib/xrdanalyzer/controller/fit/fitters/fitter_minpack.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack_util",                ["orangecontrib/xrdanalyzer/controller/fit/fitters/fitter_minpack_util.pyx"]),
    Extension("orangecontrib.xrdanalyzer.controller.fit.wppm_functions",                             ["orangecontrib/xrdanalyzer/controller/fit/wppm_functions.pyx"]),
]

from Orange.canvas.application.addons import PipInstaller

class Package:
    def __init__(self, package_url="", name=""):
        self.package_url = package_url
        self.name = name

def create_recovery():

    recovered_paths = [os.path.join("orangecontrib", "xrdanalyzer", "controller"),
                       os.path.join("orangecontrib", "xrdanalyzer", "model"),
                       os.path.join("orangecontrib", "xrdanalyzer", "util")]

    root_path = os.path.join("orangecontrib", "xrdanalyzer")
    recovery_root_path = os.path.join(root_path, "recovery")

    if os.path.exists(recovery_root_path): shutil.rmtree(recovery_root_path)
    os.makedirs(recovery_root_path)
    open(os.path.join(recovery_root_path,  "__init__.py"), 'a').close()

    for path, dirs, files in os.walk(root_path):
        do_recovery = False
        for recovered_path in recovered_paths:
            if path.startswith(recovered_path):
                do_recovery = True
                break

        if do_recovery:
            recovery_path = os.path.join(recovery_root_path, path[26:])
            if not recovery_path.endswith("__pycache__"):
                if not os.path.exists(recovery_path):
                    os.makedirs(recovery_path)

                    if os.path.exists(os.path.join(path, "__init__.py")):
                        shutil.copyfile(os.path.join(path, "__init__.py"), os.path.join(os.path.join(recovery_path,  "__init__.py")))

                for file in files:
                    if file.endswith(".pyx") and not file.endswith("test_recovery.pyx"):
                        shutil.copyfile(os.path.join(path, file), os.path.join(recovery_path,  file[:-1]))
                    elif file.endswith(".c") or file.endswith(".so"):
                        os.remove(os.path.join(path, file))

if __name__ == '__main__':

    is_sdist = False
    is_develop = False
    for arg in sys.argv:
        if arg == 'sdist':
            is_sdist = True
        elif arg == "develop":
            is_develop = True

    if is_sdist and not is_develop: #to prevent creating recovery as sudoer
        create_recovery()

    #########################################################
    # check if Chyton is present, in case it install it
    #########################################################

    if not is_sdist:
        try:
            from Cython.Distutils import build_ext
        except:
            try:
                pip = PipInstaller()
                pip.arguments.append("--no-warn-script-location")
                pip.install(Package(package_url="Cython"))
            except:
                pass


    try:
        if is_develop: raise Exception("to go in the other installation protocol")

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
    except:
        #########################################################
        # in case of problems: restore full python installation
        # not cython files are replaced by recovery files generated
        # during sdist
        #########################################################

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
            entry_points=ENTRY_POINTS
        )
