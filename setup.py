from setuptools import setup, find_packages
setup(
    name='tourbillon-celery',
    version='0.1',
    packages=find_packages(),
    install_requires=['celery==3.1.8'],
    zip_safe=False,
    namespace_packages=['tourbillon']
)
