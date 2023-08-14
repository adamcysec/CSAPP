# CSAPP - The Collection, Storage, and Analysis of Python Packages Tool

### Help Book
Read the [Git Book](https://adamcysec.gitbook.io/csapp/) to learn about CSAPP and how adversaries are targeting PyPI

## Synposis

CSAPP (*c-sap*) is a suite of tools for Collecting, Storing, and Analyzing Python Packages in PyPI to assist with threat hunting for malicious packages. 

## Description

CSAPP uses Streamlit to host a local Web App for querying and exploring the data set within a CSV file containing Python package information for every project on [PyPI.org](https://pypi.org/).

Try out the application right now on Streamlit with the sample data set!! --> [csapp-adamcysec.streamlit.app](https://csapp-adamcysec.streamlit.app/)

CSAPP also comes with several other scripts for managing the pypi_info_db.csv data set:

- pypi_package_harvest.py
  - Collects and stores new PyPI records in the data set.
- py_package_validator.py
  - Removes PyPI records from the data set that no longer exist on pypi.org
- audit_pypi_info_db.py
  - Removes errors in records from the data set.

## Dependencies
pypi_streamlit.py requires the following dependencies:
- [streamlit](https://pypi.org/project/streamlit/)
  - `pip install streamlit` 
- [duckdb](https://pypi.org/project/duckdb/)
  - `pip install duckdb` 

pypi_data_harvest.py requires the following dependencies:
- [csapptools](https://pypi.org/project/csapptools/)
  - `pip install csapptools`
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
  - `pip install beautifulsoup4`
- [requests](https://pypi.org/project/requests/)
  - `pip install requests`

pypi_package_validator.py requires the following dependencies:
- [argparse](https://pypi.org/project/argparse/)
  - `pip install argparse`

## Installation

1. git clone repo:

```
git clone https://github.com/adamcysec/CSAPP.git
```

3. Pip install any missing dependencies 

4. Download the full PyPI data set CSV file: [pypi_info_db.csv](https://drive.google.com/file/d/1uYDHmn9lZ7EhrjFIMnhqKr_SpWjDFZqO)
   - Due to the file size being about 160 MB, i have to host the file on Google Drive.

5. Store the data set CSV file in the CSAPP directory

## Updating The Data Set

New PyPI packages are uploaded every day, therefore you will want to update the data set before use.

> 📘 **Note**
>
> **pypi_data_harvest.py requires an API key from [libraries.io](https://libraries.io/)**

### Configure libraries.io API Key

1. Create an account on [libraries.io](https://libraries.io/)
2. Create hidden directory in your user's home folder called `.librariesio`
3. Saved libraries.io api key in a txt file called `api_key.txt`

Or use the `--apikey` parameter to pass in your api key file.

Run tool pypi_data_harvest.py to update the data set:

```
py pypi_data_harvest.py --update "pypi_info_db.csv"

Or

py pypi_data_harvest.py --update "pypi_info_db.csv" -k "C:\\apikey.txt"
```

## Run The Web App Locally

[Streamlit](https://csapp-adamcysec.streamlit.app/) is only hosting the web app with a sample of the data set, therefore you will want to run the app locally to use the full data set:

```
streamlit run pypi_streamlit.py
```

Note: if you have more than one version of python installed you may need to run streamlit like so:

```
python3 -m streamlit run pypi_streamlit.py
```

Download the full PyPI data set CSV file: [pypi_info_db.csv](https://drive.google.com/file/d/1uYDHmn9lZ7EhrjFIMnhqKr_SpWjDFZqO)
