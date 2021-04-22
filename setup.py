import codecs
import os
import sys

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

__version__ = None
exec(open(f"{here}/wyze_sdk/version.py").read())

long_description = ""
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as readme:
    long_description = readme.read()

validate_dependencies = [
    "pytest>=5.4,<6",
]

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setup(
    name='wyze_sdk',
    version=__version__,
    description='The Wyze Labs API Platform SDK for Python.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shauntarves/wyze-sdk",
    author='Shaun Tarves',
    author_email='shaun@tarves.net',
    python_requires=">=3.9.0",
    license="The Unlicense",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        "License :: Public Domain",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9'
    ],
    keywords="",
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
        ]
    ),
    install_requires=[],
    setup_requires=pytest_runner,
    test_suite="tests",
    tests_require=validate_dependencies,
)
