from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'radix',
    entry_points={
        'console_scripts': [
            'radix=radix.__main__:entrypoint',
        ],
    },
    packages=['radix'],
    version = '1.1.0',
    description = 'CLI tool for doing data joining',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'KJ',
    author_email = 'jdotpy@users.noreply.github.com',
    url = 'https://github.com/jdotpy/radix',
    download_url = 'https://github.com/jdotpy/radix/tarball/master',
    keywords = ['tools'],
    install_requires=['tree-sitter'],
    extras_require={
        'dev': ['pytest', 'twine'],
    },
    classifiers = [
        "Programming Language :: Python :: 3",
    ],
)
