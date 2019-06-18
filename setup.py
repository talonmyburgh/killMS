#!/usr/bin/python
'''
DDFacet, a facet-based radio imaging package
Copyright (C) 2013-2017  Cyril Tasse, l'Observatoire de Paris,
SKA South Africa, Rhodes University

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import subprocess
import os
import warnings
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.sdist import sdist
from distutils.command.build import build
from os.path import join as pjoin
import sys

pkg='killMS'
__version__ = "2.7.0.0"
build_root=os.path.dirname(__file__)

def backend(compile_options):

    if compile_options is not None:
        print >> sys.stderr, "Compiling extension libraries with user defined options: '%s'"%compile_options
    path = pjoin(build_root, pkg, 'cbuild')
    try:
        subprocess.check_call(["mkdir", path])
    except:
        warnings.warn("%s already exists in your source folder. We will not create a fresh build folder, but you "
                      "may want to remove this folder if the configuration has changed significantly since the "
                      "last time you run setup.py" % path)
    subprocess.check_call(["cd %s && cmake %s .. && make" %
                           (path, compile_options if compile_options is not None else ""), ""], shell=True)

class custom_install(install):
    install.user_options = install.user_options + [
        ('compopts=', None, 'Any additional compile options passed to CMake')
    ]
    def initialize_options(self):
        install.initialize_options(self)
        self.compopts = None

    def run(self):
        backend(self.compopts)
        install.run(self)

class custom_build(build):
    build.user_options = build.user_options + [
        ('compopts=', None, 'Any additional compile options passed to CMake')
    ]
    def initialize_options(self):
        build.initialize_options(self)
        self.compopts = None

    def run(self):
        backend(self.compopts)
        build.run(self)

class custom_sdist(sdist):
    def run(self):
        bpath = pjoin(build_root, pkg, 'cbuild')
        if os.path.isdir(bpath):
            subprocess.check_call(["rm", "-rf", bpath])
        sdist.run(self)

def define_scripts():
    #these must be relative to setup.py according to setuputils
    killms_scripts = [os.path.join(pkg, script_name) for script_name in ['kMS.py']]
    return killms_scripts

def readme():
    """ Return README contents """
    with open('README.md') as f:
        return f.read()

def requirements():
    # TODO - same as in latest DDFacet, need to systemically work out what is needed @cyriltasse
    # but this the safest assumption for now
    requirements = [("nose >= 1.3.7", "nose >= 1.3.7"),
                    ("Cython >= 0.25.2", "Cython >= 0.25.2"),
                    ("numpy>=1.15.1", "numpy>=1.15.1"), # Ubuntu 18.04
                    ("sharedarray @ git+https://gitlab.com/bennahugo/shared-array.git@master", "sharedarray @ git+https://gitlab.com/bennahugo/shared-array.git@master"),
                    ("Polygon2 >= 2.0.8", "Polygon2 >= 2.0.8"),
                    ("pyFFTW >= 0.10.4", "pyFFTW >= 0.10.4"),
                    ("astropy >= 3.0", "astropy >= 2.0.11"),
                    ("deap >= 1.0.1", "deap >= 1.0.1"),
                    ("ptyprocess>=0.5", "ptyprocess<=0.5"), #workaround for ipdb on py2
                    ("ipdb >= 0.10.3", "ipdb <= 0.10.3"),
                    ("python-casacore <= 3.0.0", "python-casacore <= 3.0.0"),
                    ("pyephem >= 3.7.6.0", "pyephem >= 3.7.6.0"),
                    ("numexpr >= 2.6.2", "numexpr >= 2.6.2"),
                    ("matplotlib >= 2.0.0", "matplotlib >= 2.0.0"),
                    ("scipy >= 0.16.0", "scipy >= 0.16.0"),
                    ("astLib >= 0.8.0", "astLib >= 0.8.0"),
                    ("psutil >= 5.2.2", "psutil >= 5.2.2"),
                    ("py-cpuinfo >= 3.2.0", "py-cpuinfo >= 3.2.0"),
                    ("tables >= 3.3.0", "tables >= 3.3.0"),
                    ("prettytable >= 0.7.2", "prettytable >= 0.7.2"),
                    ("pybind11 >= 2.2.2", "pybind11 >= 2.2.2"),
                    ("pyfits >= 3.5", "pyfits >= 3.5"), #kittens dependency, do not remove
                    ("configparser >= 3.7.1", "configparser <= 3.5.0"),
                    ("pandas <=0.23.3", "pandas >=0.23.3"),
                    ("ruamel.yaml >= 0.15.92", "ruamel.yaml >= 0.15.92"),
                    ("DDFacet >= 0.3.0", "DDFacet >= 0.3.0")] 
    try:
        import six
    except ImportError, e:
        raise ImportError("Six not installed. Please install Python 2.x compatibility package six before running KillMS install. "
                          "You should not see this message unless you are not running pip install -- run pip install!")

    py3_requirements, py2_requirements = zip(*requirements)
    install_requirements = py2_requirements if six.PY2 else py3_requirements

    return install_requirements

setup(name=pkg,
      version=__version__,
      description='A Wirtinger-based direction-dependent radio interferometric calibration package',
      long_description = readme(),
      url='http://github.com/saopicc/killMS',
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Astronomy"],
      author='Cyril Tasse',
      author_email='cyril.tasse@obspm.fr',
      license='GNU GPL v2',
      cmdclass={'install': custom_install,
                'build': custom_build,
                'sdist': custom_sdist,
               },
      python_requires='<3.0',
      packages=[pkg],
      install_requires=requirements(),
      include_package_data=True,
      zip_safe=False,
      long_description_content_type='text/markdown',
      scripts=define_scripts()
)
