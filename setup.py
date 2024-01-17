#!/usr/bin/env python3
from distutils.core import setup

VERSION = '1.0.0'  # major.minor.fix

with open('README.md', 'r') as f:
    long_description = f.read()

with open('LICENSE', 'r') as f:
    license_text = f.read()

if __name__ == "__main__":
    setup(
        name='nodered-forge',
        version=VERSION,
        description='NodeRedForge is a Python-based tool designed to facilitate the generation of '
                    'custom JSON API nodes for Node-RED. By Khalid Grandi (github.com/xaled).',
        long_description=long_description,
        long_description_content_type='text/markdown',
        keywords='library node-red code-generator',
        author='Khalid Grandi',
        author_email='kh.grandi@gmail.com',
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ],
        license='MIT',
        url='https://github.com/xaled/nodered-forge',
        install_requires=['jinja2'],
        python_requires='>=3',
        packages=['nodered_forge'],
        package_data={
            '': ['LICENSE', 'requirements.txt', 'README.md'],
            'nodered_forge': ['templates/**/*'],
        },
    )
