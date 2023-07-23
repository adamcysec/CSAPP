# CSAPP - The Collection, Storage, and Analysis of Python Packages Tool

## Synposis

CSAPP (*c-sap*) is a suite of tools for Collecting, Storing, and Analyzing Python Packages in PyPI to assist with threat hunting for malicious packages. 

## Description

CSAPP uses Streamlit to host a local Web App for querying and exploring the data witin a CSV file containing Python package information for every project on [PyPI.org](https://pypi.org/).

CSAPP also comes with several other scripts for managing the pypi_info_main_db.csv file:


## Dependencies
pypi_streamlit.py requires the following dependencies:
- [streamlit](https://pypi.org/project/streamlit/)
  - `pip install streamlit` 
- [duckdb](https://pypi.org/project/duckdb/)
  - `pip install duckdb` 

pypi_data_harvest.py requires the following dependencies:
- librariesio (included in repo)
- pypilib (included in repo)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
  - `pip install beautifulsoup4`
- [requests](https://pypi.org/project/requests/)
  - `pip install requests`

pypi_package_validator.py requires the following dependencies:
- [argparse](https://pypi.org/project/argparse/)
  - `pip install argparse`

## Installation

1. git clone repo:
   
`git clone https://github.com/adamcysec/CSAPP.git`

3. Pip install any missing dependencies 

4. Download the PyPI data CSV file: [pypi_info_main_db.csv](https://drive.google.com/file/d/1KXrtPr2qzZ91F6DLiPbZEwpIV0S6eGjR)
   - Due to the file size being about 166 MB, i have to host the file on Google Drive.

5. Store the CSV file in the CSAPP directory 


<br/>
<br/>

## Usage

**Example 1**

`streamlit run pypi_streamlist.py`
