"""Setuptools entry point."""
import codecs
import os
from typing import List

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# PYTHON 2.7 compatible version - no typing here because of Python 2.7
package_name = 'fingerprint'   # type: ignore
required = ['chardet',
            'click',
            'python-registry @ git+https://github.com/williballenthin/python-registry.git']     # type: ignore
required_for_tests = list()     # type: ignore
entry_points = dict()           # type: ignore


def get_version(dist_directory):
    # type: (str) -> str
    # PYTHON 2.7 compatible version - lib_registry is needed for lib_platform
    path_version_file = os.path.join(os.path.dirname(__file__), dist_directory, 'version.txt')
    with open(path_version_file, mode='r') as version_file:
        version = version_file.readline()
    return version


def is_travis_deploy() -> bool:
    if 'travis_deploy' in os.environ:
        if os.environ['travis_deploy'] == 'True':
            return True
    return False


def strip_links_from_required(l_required: List[str]) -> List[str]:
    """
    >>> required = ['lib_regexp @ git+https://github.com/bitranox/lib_regexp.git', 'test']
    >>> assert strip_links_from_required(required) == ['lib_regexp', 'test']

    """
    l_req_stripped = list()                                        # type: List[str]
    for req in l_required:
        req_stripped = req.split('@')[0].strip()
        l_req_stripped.append(req_stripped)
    return l_req_stripped


if is_travis_deploy():
    required = strip_links_from_required(required)


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'
]


# PYTHON 2.7 compatible version - lib_registry is needed for lib_platform
long_description = package_name
path_readme = os.path.join(os.path.dirname(__file__), 'README.rst')
if os.path.exists(path_readme):
    # noinspection PyBroadException
    try:
        readme_content = codecs.open(path_readme, encoding='utf-8').read()
        long_description = readme_content
    except Exception:
        pass


setup(name=package_name,
      version=get_version(package_name),
      url='https://github.com/bitranox/{package_name}'.format(package_name=package_name),
      packages=[package_name],
      package_data={package_name: ['version.txt']},
      description=package_name,
      long_description=long_description,
      long_description_content_type='text/x-rst',
      author='Robert Nowotny',
      author_email='rnowotny1966@gmail.com',
      classifiers=CLASSIFIERS,
      entry_points=entry_points,
      # minimally needs to run tests - no project requirements here
      tests_require=['typing',
                     'pathlib',
                     'mypy ; platform_python_implementation != "PyPy" and python_version >= "3.5"',
                     'pytest',
                     'pytest-pep8 ; python_version < "3.5"',
                     'pytest-pycodestyle ; python_version >= "3.5"',
                     'pytest-mypy ; platform_python_implementation != "PyPy" and python_version >= "3.5"'
                     ] + required_for_tests,

      # specify what a project minimally needs to run correctly
      install_requires=['typing', 'pathlib'] + required + required_for_tests,
      # minimally needs to run the setup script, dependencies must not put here
      setup_requires=['typing',
                      'pathlib',
                      'pytest-runner']
      )
