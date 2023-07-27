from pathlib import Path
from csapptools import librariesiolib
from csapptools import pypilib
import os
import csv
import time
from datetime import datetime
import argparse
import textwrap
from bs4 import BeautifulSoup
import requests

def get_args():
    parser = argparse.ArgumentParser(
        description="Collect, store, and update Pypi package data in a CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Examples:
        py pypi_data_harvest.py
        py pypi_data_harvest.py --update "pypi_info_db.csv"
        ''')
    )

    parser.add_argument('-u', '--update', action='store', type=str, required=False, help="file to update")

    args = parser.parse_args() # parse arguments

    args_dict = vars(args)

    return args_dict

def main():
    start_time = time.time()
    args = get_args()
    update = args['update']

    # check update file is given
    if update:
        pypi_db_csv_file = update
        # read already worked pypi projects
        collected_packages = get_current_package_list(pypi_db_csv_file)
    
    else:
        #date_today = datetime.now().strftime('%m-%d-%Y')
        #pypi_db_csv_file = f'{date_today}_pypi_info_db.csv' # new csv file
        pypi_db_csv_file = 'pypi_info_db.csv' # new csv file
        collected_packages = []
    
    # get libraries.io api key
    api_key = get_api_key()
    librariesio_obj = librariesiolib.librariesiolib(api_key)

    # get list of pypi projects
    pypilib_obj = pypilib.pypilib()
    pypi_packages_list = pypilib_obj.get_simple()

    api_count = 1
    new_packages_collected = 0

    librarisio_packages_info = [] # package data to out file
    
    limit = 60
    for pypi_package in pypi_packages_list:
        
        # eval if we have already collected the package before making a request
        if pypi_package['name'] in collected_packages:
            #print(f"already collected: {pypi_package['name']}")
            continue # already collected.. skip package

        print(f"working project: {pypi_package['name']}")
        package_info_json, failure = librariesio_obj.get_pypi_package(pypi_package['name'])

        # handle request failures
        while failure:
            if failure == 'json':
                #one_hour_failures += 1
                print("libraries.io connection error.. sleeping for one hour..")
                time.sleep(3600)
                print(f"trying package {pypi_package['name']} again...")
                package_info_json, failure = librariesio_obj.get_pypi_package(pypi_package['name'])
            else:
                print("sleeping for 60 seconds...")
                time.sleep(60)
                package_info_json, failure = librariesio_obj.get_pypi_package(pypi_package['name'])

        if failure == False and package_info_json == None:
            print(f"skipping project: {pypi_package['name']}")
            continue

        # enrich data collected
        #######################
        # add field total_versions
        package_info_json['total_versions'] = {}
        try:
            package_info_json['total_versions'] = len(package_info_json['versions'])
        except:
            package_info_json['total_versions'] = 0
        
        # limit 'licenses' field to 120 characters
        if package_info_json['licenses']:
            if len(package_info_json['licenses']) > 120:
                package_info_json['licenses'] = package_info_json['licenses'][:120]

        # remove 'versions' field
        del package_info_json['versions']

        # remove 'contributions_count' field
        # this field was recently added to libraries.io
        del package_info_json['contributions_count']

        # get additional metadata from pypi
        metadata_dict = get_pypi_metadata(pypi_package['name'])
        
        # add maintainers
        maintainers = metadata_dict['maintainers']
        maintainers = str(maintainers).replace('[','')
        maintainers = str(maintainers).replace(']','')
        package_info_json['maintainers'] = {}
        package_info_json['maintainers'] = maintainers

        # add latest_upload_date and latest_upload_time
        upload_date, upload_time = format_date_time(package_info_json['latest_release_published_at'])
        package_info_json['latest_upload_date'] = {}
        package_info_json['latest_upload_time'] = {}
        package_info_json['latest_upload_date'] = upload_date
        package_info_json['latest_upload_time'] = upload_time

        # add first_upload_date
        first_upload_date = metadata_dict['first_upload_date']
        package_info_json['first_upload_date'] = {}
        package_info_json['first_upload_date'] = first_upload_date

        # either libraries.io or pypi indicates package was removed
        if package_info_json['status'] == "Removed" or package_info_json['first_upload_date'] == 'none':
            print(f"skipping project; removed: {pypi_package['name']}")
            continue

        # add package data 
        librarisio_packages_info.append(package_info_json)
        api_count += 1
        new_packages_collected += 1

        # save data collected
        if api_count == limit:
            out_csv_file(librarisio_packages_info, pypi_db_csv_file) # save each batch to file
            librarisio_packages_info = [] # reset list
            api_count = 1 # reset request count
            
            print("api count limit")
            print("sleeping for 60 seconds...")
            time.sleep(60)
    
    # save remaining data collected
    if librarisio_packages_info:
        out_csv_file(librarisio_packages_info, pypi_db_csv_file)

    print(f"--- Completed in {time.time() - start_time} seconds ---")
    print(f"total new pypi projects collected: {new_packages_collected}")

def get_api_key():
    """read in libraries.io api key

    return:
    -------
    api_key : str
        libraries.io api key
    """
    
    user_home_path = Path.home()
    api_key_path = os.path.join(user_home_path, '.librariesio', 'api_key.txt')

    with open(api_key_path, 'r') as file:
        api_key = file.read()
    
    return api_key

def get_current_package_list(csv_filepath):
    """read already collected pypi project names

    Parameters:
    -----------
    csv_filepath : str
        pypi data csv file path

    Returns:
    --------
    packages : list
        pypi project names
    """
    
    with open(csv_filepath, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader) # skip headers
        
        packages = []
        for row in csv_reader:
            package_name = row[15]
            packages.append(package_name)
        
    return packages

def get_pypi_metadata(package_name):
    """extract metadata from pypi package url html response

    Parameters:
    -----------
    package_name : str
        package name
    
    Returns:
    --------
    maintainers : list
        contains strings of names
    """

    package_url = f"https://pypi.org/project/{package_name}/"
    
    response = requests.get(package_url)

    maintainers = []
    if not response.status_code == 404:
        soup = BeautifulSoup(response.text, 'lxml')

        # extract all maintiners
        maintainer_usernames = soup.find_all("span", class_="sidebar-section__user-gravatar-text")
        for maintainer in maintainer_usernames:
            username = maintainer.text.strip()
            if not username in maintainers:
                maintainers.append(username)

        # extract first upload date
        version_dates = soup.find_all("p", class_="release__version-date")
        first_release_date = version_dates[-1].text.strip()
        first_release_date_dt = datetime.strptime(first_release_date, '%b %d, %Y')
        first_upload_date = first_release_date_dt.strftime('%Y-%m-%d')

    else:
        print(f"package not found {package_url}")
        maintainers = 'none'
        first_upload_date = 'none'

    metadata = {'maintainers': maintainers, 'first_upload_date': first_upload_date}

    return metadata

def format_date_time(date_time):
    """splits str date/time into seperate fields

    Parameters:
    -----------
    date_time : str
        pypi db field 'latest_release_published_at' - 2022-05-29T11:20:53.000Z
    
    Returns:
    --------
    date : str
        yyyy-mm-dd
    time : str
        HH:MM:SS
    """
    
    parts = date_time.split('T')
    date = parts[0].strip()
    time = parts[1].split('.')[0].strip() 

    return date, time

def out_csv_file(data, csv_file):
    """save pypi data to csv file

    Parameters:
    -----------
    data : dict
        csv rows
    csv_file : str
        csv file
    """

    file_name = csv_file
    field_names = ['dependent_repos_count', 
                   'dependents_count', 
                   'deprecation_reason',
                   'description',
                   'forks',
                   'homepage',
                   'keywords',
                   'language',
                   'latest_download_url',
                   'latest_release_number',
                   'latest_release_published_at',
                   'latest_stable_release_number',
                   'latest_stable_release_published_at',
                   'license_normalized',
                   'licenses',
                   'name',
                   'normalized_licenses',
                   'package_manager_url',
                   'platform',
                   'rank',
                   'repository_license',
                   'repository_status',
                   'repository_url',
                   'stars',
                   'status',
                   'total_versions',
                   'maintainers',
                   'latest_upload_date',
                   'latest_upload_time',
                   'first_upload_date']
    
    file_exists = os.path.isfile(file_name)

    with open(file_name, 'a', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(data)

    print(f"file saved: {file_name}")

if __name__ == "__main__":
    main()