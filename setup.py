from setuptools import find_packages, setup

setup(
    name='platform_utils_eai',
    packages=find_packages(include=['platform_utils_eai']),
    version='0.3.0',
    description='Collection of functions and utilities to create annotated libraries to be uploaded on EAI Platform',
    author='Simone Martin Marotta',
    install_requires=["split-folders"],
    setup_requires=[],
    tests_require=['pytest'],
    test_suite='tests',
)