# -*- coding: utf-8 -*-

import os.path
import sys

from setuptools import find_packages, setup

def get_version():
  """Get version."""

  sys.path.append("src/qwatson")
  import _version # type: ignore
  return _version.__version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if __name__ == '__main__':
  setup(
    version         =get_version(),
    name            ='qwatson',
    url             ='https://github.com/phlummox-patches/qwatson',
    description     ='A simple PyQt-GUI for the Watson time-tracker CLI',
    packages        =find_packages(where='src'),
    package_dir     ={'': 'src'},
    python_requires = '>=3.6',
    install_requires=('arrow',
                      'click',
                      'pyqt5==5.10.1',
                      'qtawesome',
                      'td-watson < 2.2',
    ),
    author='Jean-Sébastien Gosselin',
    #author_email='',
    license         ='GPL',
    license_files   =('LICENSE',),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    classifiers     =[
        "Development Status :: 3 - Alpha",
    ],
    #include_package_data=True,
    entry_points={
          'console_scripts': [
                # thin wrapper around bbquiz.main
                'qwatson = qwatson.mainwindow:main'
           ] },
  )

