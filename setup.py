from setuptools import setup, find_packages

setup(
    name="dataclasses-dict",
    version="0.0.1",
    packages=find_packages(exclude=("tests*",)),
    author="lidatong",
    author_email="charles.dt.li@gmail.com",
    description="Easily convert dataclasses to and from dicts",
    url="https://github.com/lidatong/dataclasses-dict",
    license="Unlicense",
    keywords="dataclasses dict",
    install_requires=[
        "dataclasses==0.5"
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": ["pytest"]
    },
    include_package_data=True
)

