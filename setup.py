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
    "flake8>=3,<4",
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
    python_requires=">=3.8.0",
    include_package_data=True,
    license="The Unlicense",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Communications :: Chat",
        "License :: Public Domain",
        "License :: Free for non-commercial use",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Topic :: Home Automation",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords=["wyze", "wyze-labs", "wyze-sdk", "wyze-api", "wyzeapy", "wyze-apy", "smart home", "home automation"],
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
        ]
    ),
    install_requires=["requests", "blackboxprotobuf", "mintotp", "pycryptodomex"],
    setup_requires=pytest_runner,
    test_suite="tests",
    tests_require=validate_dependencies,
)
