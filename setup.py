from setuptools import setup, find_packages
setup(
    name="PyKrak",
    version="0.1",
    packages=find_packages(),
    package_data={
        'PyKrak': ['data/*/*.txt'],
    }
)
