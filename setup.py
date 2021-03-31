from setuptools import setup, find_packages, Extension

#########
# Setup #
#########


setup(
    name='tjbioarticles',
    version='1.0.0',
    description='Multiple keywords combinations, Pubmed articles extractions',
    url='',
    authors='Tatiana Rijoff',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.0',
        ]
    )
