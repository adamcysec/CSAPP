import csv
from datetime import datetime

import argparse
import textwrap

def get_args():
    parser = argparse.ArgumentParser(
        description="Removes errors in records from the data set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Examples:
        py audit_pypi_info_db.py -f "pypi_info_db.csv"
        ''')
    )

    parser.add_argument('-f', '--file', action='store', type=str, required=True, help="path to data set CSV file")

    args = parser.parse_args() # parse arguments

    args_dict = vars(args)

    return args_dict

def main():
    args = get_args()
    pypi_db_file = args['file']
    
    new_csv_file_name = 'new_pypi_info_main_db.csv'


    with open(pypi_db_file, 'r', encoding='utf-8') as input_csv_file:
        with open(new_csv_file_name, 'w', encoding='utf-8') as new_csv_file:
            csv_reader = csv.reader(input_csv_file)
            csv_writer = csv.writer(new_csv_file, lineterminator='\n')

            row_count = 1
            skipped_rows = 0
            all = []

            for row in csv_reader:
                if row_count == 1:
                    modified_row = eval_headers(row)
                    all.append(modified_row) # add headers to new file
        
                else:
                    # work csv rows
                    
                    # skip rows with incorrect number of items on row
                    modified_row = eval_rows(row)
                    if modified_row == 'error':
                        skipped_rows += 1
                        continue # skip row
                    else:
                        # evaluate row values
                        error = False
                        
                        modified_row, error = eval_dependent_repos_count(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row, error = eval_dependents_count(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_deprecation_reason(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_description(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row, error = eval_forks(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_homepage(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_keywords(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_language(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_latest_download_url(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_latest_release_number(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_latest_release_published_at(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_latest_stable_release_number(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_latest_stable_release_published_at(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_license_normalized(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_licenses(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_name(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_normalized_licenses(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_package_manager_url(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_platform(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row, error = eval_rank(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_repository_license(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_repository_status(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_repository_url(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row, error = eval_stars(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row, error = eval_total_versions(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        modified_row = eval_maintainers(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        error = eval_latest_upload_date(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        error = eval_latest_upload_time(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row

                        error = eval_first_upload_date(modified_row)
                        if error == True:
                            skipped_rows += 1
                            continue # skip row


                        all.append(modified_row) # add new data for new csv file
                
                row_count += 1
            
            csv_writer.writerows(all) # write new csv file
            print(f"file saved: {new_csv_file_name}")
    
    print(f"skipped {skipped_rows} rows")
  

def eval_headers(row):
    # count columns
    colum_count = len(row)
    if colum_count != 30:
        print(f"number of columns: {colum_count} not equal to 30")
        print(row)

    return row

def eval_rows(row):
    row_count = len(row)

    if row_count != 30:
        print(f"number of rows: {row_count} not equal to 30")
        print(row)

        row = 'error' # mark row as in error and skip it

    return row

def eval_string(string):
    # value should be a string
    if string == "" or string == None:
        string = 'none'

    if type(string) != str:
        string = str(string)

    return string

def eval_num(num):
    # value should be an int as a string
    if num == '' or num == None:
        num = '0'

    error = False
    try:
        # value should be an int
        test = int(num)
    except:
        error = True

    num = str(num)

    return num, error

def eval_url(url):
    if url == '' or url == None:
        url = 'none'

    if type(url) != str:
        url = str(url)
    
    return url

def eval_list(check_list):
    check_list = check_list.replace('[', '')
    check_list = check_list.replace(']', '')
    
    if check_list == '' or check_list == None:
        check_list = 'none'

    # return comma seperated values
    return check_list

def eval_date(date):
    
    error = False
    try:
        date_df = datetime.strptime(date, '%Y-%m-%d')
    except:
        error = True
    
    return error

###########################

def eval_dependent_repos_count(row):
    dependent_repos_count = row[0]
    
    dependent_repos_count, error = eval_num(dependent_repos_count)
    row[0] = dependent_repos_count

    return row, error

def eval_dependents_count(row):
    dependents_count = row[1]

    dependents_count, error = eval_num(dependents_count)
    row[1] = dependents_count

    return row, error

def eval_deprecation_reason(row):
    deprecation_reason = row[2]

    deprecation_reason = eval_string(deprecation_reason)
    row[2] = deprecation_reason

    return row

def eval_description(row):
    description = row[3]

    description = eval_string(description)
    row[3] = description

    return row

def eval_forks(row):
    forks = row[4]

    forks, error = eval_num(forks)
    row[4] = forks

    return row, error

def eval_homepage(row):
    url = row[5]
    
    url = eval_url(url)
    row[5] = url

    return row

def eval_keywords(row):
    keywords = row[6]

    keywords = eval_list(keywords)
    row[6] = keywords

    return row

def eval_language(row):
    language = row[7]

    language = eval_string(language)
    row[7] = language

    return row

def eval_latest_download_url(row):
    latest_download_url = row[8]

    latest_download_url = eval_url(latest_download_url)
    row[8] = latest_download_url
    
    return row

def eval_latest_release_number(row):
    latest_release_number = row[9]

    latest_release_number = eval_string(latest_release_number)
    row[9] = latest_release_number

    return row

def eval_latest_release_published_at(row):
    latest_release_published_at = row[10]

    latest_release_published_at = eval_string(latest_release_published_at)
    row[10] = latest_release_published_at

    return row

def eval_latest_stable_release_number(row):
    latest_stable_release_number = row[11]

    latest_stable_release_number = eval_string(latest_stable_release_number)
    row[11] = latest_stable_release_number

    return row

def eval_latest_stable_release_published_at(row):
    latest_stable_release_published_at = row[12]

    latest_stable_release_published_at = eval_string(latest_stable_release_published_at)
    row[12] = latest_stable_release_published_at

    return row

def eval_license_normalized(row):
    license_normalized = row[13]

    license_normalized = eval_string(license_normalized)
    row[13] = license_normalized

    return row

def eval_licenses(row):
    licenses = row[14]

    licenses = eval_string(licenses)
    row[14] = licenses

    return row

def eval_name(row):
    name = row[15]

    name = eval_string(name)
    row[15] = name

    return row

def eval_normalized_licenses(row):
    normalized_licenses = row[16]

    normalized_licenses = eval_list(normalized_licenses)
    row[16] = normalized_licenses

    return row

def eval_package_manager_url(row):
    package_manager_url = row[17]
    
    package_manager_url = eval_url(package_manager_url)
    row[17] = package_manager_url

    return row

def eval_platform(row):
    platform = row[18]

    platform = eval_string(platform)
    row[18] = platform

    return row

def eval_rank(row):
    rank = row[19]

    rank, error = eval_num(rank)
    row[19] = rank

    return row, error

def eval_repository_license(row):
    repository_license = row[20]

    repository_license = eval_string(repository_license)
    row[20] = repository_license

    return row

def eval_repository_status(row):
    repository_status = row[21]

    repository_status = eval_string(repository_status)
    row[21] = repository_status

    return row

def eval_repository_url(row):
    repository_url = row[22]

    repository_url = eval_url(repository_url)
    row[22] = repository_url

    return row

def eval_stars(row):
    stars =  row[23]
    
    stars, error = eval_num(stars)
    row[23] = stars

    return row, error

def eval_status(row):
    status = row[24]

    status = eval_string(status)
    row[24] = status

    return row

def eval_total_versions(row):
    total_versions = row[25]

    total_versions, error = eval_num(total_versions)
    row[25] = total_versions

    return row, error

def eval_maintainers(row):
    maintainers = row[26]

    maintainers =  eval_list(maintainers)
    row[26] = maintainers

    return row

def eval_latest_upload_date(row):
    latest_upload_date = row[27]

    error = eval_date(latest_upload_date)

    return error

def eval_latest_upload_time(row):
    latest_upload_time = row[28]

    parts =  latest_upload_time.split(':')
    if len(parts) == 3:
        error = False
    else:
        error = True

    return error

def eval_first_upload_date(row):
    latest_upload_date = row[29]

    error = eval_date(latest_upload_date)
    
    return error

if __name__ == "__main__":
    main()