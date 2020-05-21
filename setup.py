import setuptools

with open('README.md', mode='r', encoding='utf-8') as readme_file:
    long_description = readme_file.read()


setuptools.setup(
    name="eml-analyzer",
    version="1.0.0",
    author="Florian Wahl",
    author_email="florian.wahl.developer@gmail.com",
    description="A cli script to analyze an E-Mail in the eml format for viewing the header, extracting attachments etc.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wahlflo/eml_analyzer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
       'cli-formatter>=1.2.0'
    ],
    entry_points={
        "console_scripts": [
            "emlAnalyzer=eml_analyzer.cli_script:main"
        ],
    }
)