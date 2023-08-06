import csv
import argparse
import os
import textwrap
import requests
import time
import concurrent.futures

CONNECTIONS = 100
TIMEOUT = 5

def get_args():
    parser = argparse.ArgumentParser(
        description="Removes PyPI records from the data set that no longer exist on pypi.org",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Examples:
        pypi_package_validator.py -f "pypi_info_main_db.csv"
        pypi_package_validator.py -f 'pypi_info_main_db.csv' -tmp
        ''')
    )

    parser.add_argument('-f', '--file', action='store', type=str, required=True, help="CSV filepath")
    parser.add_argument('-o', '--output', action='store', type=str, required=False, help="New CSV file name")
    parser.add_argument('-tmp', '--tmpfile', action='store_true', required=False, help="Use this if progress was stopped and you need to resume progress")

    args = parser.parse_args() # parse arguments

    args_dict = vars(args)

    return args_dict


def main():
    start_time = time.time()
    
    args = get_args()
    input_csv = args['file']
    new_csv_file_name = args['output']
    tmp_validator_file = args['tmpfile']

    validated_out_rows = []
    work_num_urls = 10000 # the number of urls to work at one time

    # get all urls from pypi DB
    all_urls = get_urls_from_csvfile(input_csv)

    # if progress was stopped, then read in the previously worked urls
    if tmp_validator_file:
        total_elements = read_validator_tmp_file()
        del all_urls[:total_elements] # remove urls previously worked

    validated_batches = 1

    # validate urls
    while len(all_urls) > 0:
        first_10000_urls = all_urls[:work_num_urls] # grab urls to work
        del all_urls[:work_num_urls] # remove urls we worked

        batch_time = time.time()
        # start concurrent work
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
            future_to_url = (executor.submit(resolve_package, url) for url in first_10000_urls)

            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    data = future.result()
                except Exception as exc:
                    print(str(type(exc)))
                finally:
                    validated_out_rows.append(data)
        
        print(f"--- Validated Batch Num {validated_batches} Completed in {time.time() - batch_time} seconds ---")
        validated_batches += 1

        # save project urls we worked to file
        save_worked_urls(validated_out_rows)
        validated_out_rows = []

    # yay we validated all the urls!
    print(f"--- Validated Urls Completed in {time.time() - start_time} seconds ---")
    # read in the pypi urls that no longer exist
    invalid_urls = read_validated_non_existent_urls()

    # save new csv with only valid urls
    save_valid_urls(input_csv, invalid_urls, new_csv_file_name)

    # remove the tmp file.. no longer needed
    if os.path.exists("validator_worked_urls.tmp"):
        os.remove("validator_worked_urls.tmp")

    print(f"--- Script Completed in {time.time() - start_time} seconds ---")
   

def resolve_package(pypi_url):
    """Resolves the pypi package url
    
    Concurrent will run this function. 
    
    Parameters:
    -----------
    pypi_url : str
        pypi package url

    Returns:
    --------
    pypi_package_data : dict
        contains pypi package url and whether the package still exists
    """
    package_exists = True
    
    response = requests.head(pypi_url)

    if response.status_code == 404:
        package_exists = False
    
    pypi_package_data = {'pypi_url': pypi_url, 'package_exists': package_exists}

    return pypi_package_data

def get_urls_from_csvfile(csv_filepath):
    """Reads in all pypi urls from the CSV DB to be validated

    Parameters:
    -----------
    csv_filepath : str
        file path to CSV file

    Returns:
    --------
    all_urls : list
        contains pypi package urls
    """
    
    all_urls = []
    with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader) # skip headers

        for row in csv_reader:
            url = row[17]
            all_urls.append(url)

    return all_urls

def save_worked_urls(data):
    """Saves validated pypi urls to file

    Keeps track of urls worked to prevent double work 
    if script execution stops in the middle of work.

    Parameters:
    --------
    data : list
        contains a dict of urls validated
    """
    
    file_name = "validator_worked_urls.tmp"
    file_exists = os.path.exists(file_name)
    field_names = ['pypi_url', 'package_exists']
    with open(file_name, 'a', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(data)
    
    print(f"tmp urls saved: {file_name}")

def read_validator_tmp_file():
    """Reads in the tmp file of urls already worked to prevent double work

    Returns:
    --------
    total_elements : int
        total number of rows containing a url
    """
    
    tmp_validator_file = 'validator_worked_urls.tmp'
    with open(tmp_validator_file, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader) # skip headers

        total_rows = 0
        for row in csv_reader:
            if row != '':
                total_rows += 1

        total_elements = total_rows - 1
    
    return total_elements

def read_validated_non_existent_urls():
    """Reads in the tmp file of invalid urls to be removed from the pypi db

    Returns:
    --------
    invalid_urls : list
        list of invalid urls
    """
    
    tmp_validator_file = 'validator_worked_urls.tmp'
    invalid_urls = []
    
    with open(tmp_validator_file, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader) # skip headers

        for row in csv_reader:
            url = row[0]
            exists = row[1]
            if exists == 'False':
                invalid_urls.append(url)
    
    return invalid_urls

def save_valid_urls(input_csv, invalid_urls, new_csv_file_name):
    """Removes non existent pypi urls from the pypi DB

    Compares the pypi urls from the pypi Db to the invalid_urls.
    If url does not exist, then discard it.
    Saves new CSV with only valid pypi urls.

    Parameters:
    -----------
    input_csv : str
        pypi Db file
    invalid_urls : list
        list of invalid urls
    new_csv_file_name : str
        new pypi Db file
    """
    
    with open(input_csv, 'r', encoding='utf-8') as input_csv_file:
        with open(new_csv_file_name, 'w', encoding='utf-8') as new_csv_file:
            csv_reader = csv.reader(input_csv_file)
            csv_writer = csv.writer(new_csv_file, lineterminator='\n')

            row_count = 1
            skipped_rows = 0
            out = []

            for row in csv_reader:
                if row_count == 1:
                    out.append(row) # add headers to new file
                else:
                    # work csv rows
                    pypi_url = row[17]

                    if pypi_url not in invalid_urls:
                        out.append(row)
                    else:
                        skipped_rows += 1
                        print(f"package no longer exists: {pypi_url}")
                
                row_count += 1
            
            csv_writer.writerows(out) # write new csv file
            print(f"file saved: {new_csv_file_name}")
            print(f"total rows validated: {row_count}")
            print(f"total invalid pypi urls removed: {skipped_rows}")

if __name__ == "__main__":
    main()