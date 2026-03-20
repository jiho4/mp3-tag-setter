from setuptools import setup, find_packages

setup(
    name="mp3-tag-setter",
    version="1.1.0-SNAPSHOT",
    packages=find_packages(),
    package_data={'': ['*.yaml', '*.yml']},
    include_package_data=True,
)
