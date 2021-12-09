import setuptools
from setuptools import find_packages

with open('README.md',"r",encoding='utf-8') as rm:
    long_description = rm.read()

setuptools.setup(
    name="Covid_dashboard-pkg-rt539",
    version="1.0.1",
    author="Ryan Toffoletti",
    author_email="rt539@exeter.ac.uk",
    description="Lightweight covid dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Toffoh/Covid-Dashboard",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",],
    packages=find_packages(
         where='Application'),
    package_dir={"":"Application"},
    python_requires=">=3.10",
    install_requires = [
          'Flask',
          'requests',
          'pytest',
          'sched'],
    )

