from setuptools import setup

setup(
    name='PyRoxy',
    version="1.0b3",
    packages=['PyRoxy', 'PyRoxy.GeoIP', 'PyRoxy.Tools', 'PyRoxy.Exceptions'],
    url='https://github.com/MHProDev/PyRoxy',
    license='MIT',
    author="MH_ProDev",
    author_email='',
    install_requires=["maxminddb>=2.2.0", "requests>=2.27.1", "yarl>=1.7.2", "pysocks>=1.7.1"],
    include_package_data=True,
    description=''
)
