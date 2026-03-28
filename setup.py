from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'radixcodemap',
    entry_points={
        'console_scripts': [
            'radix=radix.__main__:entrypoint',
        ],
    },
    packages=['radix', 'radix.handlers'],
    version = '0.4.0',
    description = 'Summarize code repositories quickly and (soon) with multiple verbosity levels',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'KJ',
    author_email = 'jdotpy@users.noreply.github.com',
    url = 'https://github.com/jdotpy/radix-map',
    download_url = 'https://github.com/jdotpy/radix-map/tarball/master',
    keywords = ['tools'],
    install_requires=['tree-sitter'],
    extras_require={
        'dev': ['pytest', 'twine'],
    },
    classifiers = [
        "Programming Language :: Python :: 3",
    ],
)
