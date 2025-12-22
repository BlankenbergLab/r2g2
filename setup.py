from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="r2g2",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "rpy2>=3.6.1",
        "jinja2",
        "requests",
        "packaging"
    ],
    entry_points={
        'console_scripts': [
            'r2g2-package=r2g2.scripts.r2g2_package:main',
            'r2g2-script=r2g2.scripts.r2g2_script:run_main',
        ],
    },
    include_package_data=True,
    author="Jayadev Joshi, Fabio Cumbo, Daniel Blankenberg",
    description="A tool to convert R scripts and packages to Galaxy wrappers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlankenbergLab/r2g2",
    license="MIT",
    license_files=["LICENSE"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
