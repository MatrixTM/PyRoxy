from pathlib import Path
from setuptools import setup
import PyRoxy

with Path(__file__).with_name('requirements.txt').open("r+") as f:
    required = f.read().splitlines()

setup(
    name='PyRoxy',
    version=PyRoxy.__version__,
    packages=['PyRoxy', 'PyRoxy.GeoIP', 'PyRoxy.Tools', 'PyRoxy.Exceptions'],
    url='https://github.com/MHProDev/PyRoxy',
    license='',
    author=PyRoxy.__auther__,
    author_email='',
    install_requires=required,
    include_package_data=True,
    description=''
)
