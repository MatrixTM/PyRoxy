from setuptools import setup

with open('requirements.txt').open("r+") as f:
    required = f.read().splitlines()

setup(
    name='PyRoxy',
    version="1.0 BETA",
    packages=['PyRoxy', 'PyRoxy.GeoIP', 'PyRoxy.Tools', 'PyRoxy.Exceptions'],
    url='https://github.com/MHProDev/PyRoxy',
    license='',
    author="MH_ProDev",
    author_email='',
    install_requires=required,
    include_package_data=True,
    description=''
)
