from setuptools import setup, find_packages

setup(
    name='mara-campaign-tree-editor',
    version='2.0.0',

    description="Flask based Mara UI for correcting wrong UTM parameters or changing campaign structure",

    install_requires=[
        'mara-page>=1.2.3',
        'mara-db>=2.0.0'
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={
    }
)
