from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='pyopta',
    version='1.0.0',
    description='Parser for OptaF9, OptaF24 and OptaF27 files. It also provides functions for the creation of football pitches, pandas dataframes, heat maps, comparison radar, reports,...',
    license='MIT',
    author='José Barrero',
    author_email='josebarrero@gmail.com',
    url='https://github.com/jbarreroj',
    packages=find_packages(),
    install_requires=requirements,
    package_data={
        'pyopta': ['templates/*.html'],  # include all HTML templates in the 'templates' folder
    },
    classifiers=[
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License'
    ]
)
