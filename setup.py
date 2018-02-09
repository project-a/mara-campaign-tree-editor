from setuptools import setup, find_packages

setup(
    name='mara-campaign-tree-editor',
    version='1.0.0',

    description="Tool to find and edit marketing campaign names",

    install_requires=[
        'mara-page>=1.2.3',
        'mara-db>=2.0.0'
    ],

    dependency_links=[
        'git+ssh://git@github.com/mara/mara-page.git@1.2.3#egg=mara-page-1.2.3',
        'git+ssh://git@github.com/mara/mara-db.git@2.0.0#egg=mara-db-2.0.0'
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={
    }
)
