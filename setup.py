import codecs
import os
import re
import sys

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

def find_version(*file_paths):
    with codecs.open(os.path.join(here, *file_paths), 'r', 'utf-8') as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("__version__ not defined in version.py")

long_description = ""
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as readme:
    long_description = readme.read()

validate_dependencies = [
    "pytest>=9.0.3",
    "flake8>=3,<4",
]

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setup(
    name='wyze_sdk',
    version=find_version("wyze_sdk", "version.py"),
    description='The Wyze Labs API Platform SDK for Python.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shauntarves/wyze-sdk",
    author='Shaun Tarves',
    author_email='shaun@tarves.net',
    python_requires=">=3.12,<3.15", # 3.15 due to dependency from imagesize
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
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
    keywords=["wyze", "wyze-labs", "wyze-sdk", "wyze-api", "wyzeapy", "wyze-apy", "smart home", "home automation"],
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
        ]
    ),
    install_requires=["requests", "bbpb", "mintotp", "pycryptodomex"],
    setup_requires=["pytest_runner", "pycryptodomex"],
    test_suite="tests",
    tests_require=validate_dependencies,
)
