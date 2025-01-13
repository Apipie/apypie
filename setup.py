"""
setup.py for apypie
"""
from os import path
from io import open
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# Get the long description from the README file
with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='apypie',
    version='0.6.2',
    description='Apipie bindings for Python',
    license='MIT',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/Apipie/apypie',
    author='Evgeni Golov',
    author_email='evgeni@golov.de',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='api apipie bindings',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'requests>=2.4.2',
    ],
)
