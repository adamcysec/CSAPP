import duckdb
import streamlit as st
import os.path

db = "duck.db"
destination_table_name = "pypi"
filename = "pypi_info_db.csv"

def execute_query(query: str, db: str, return_type: str = "df"):
    with duckdb.connect(db, read_only=True) as con:
        if return_type == "df":
            return con.execute(query).df()
        elif return_type == "arrow":
            return con.execute(query).arrow()
        elif return_type == "list":
            return con.execute(query).fetchall()

@st.cache_data
def export_df(df):
    return df.to_csv(index=False).encode("utf-8")

def load_file(db: str = "duck.db", infile_path: str = "06-04-2023_pypy_info_main_db_audit.csv", table_name: str = "pypi"):
    with duckdb.connect(db) as conn:
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} as SELECT * FROM read_csv_auto('{infile_path}')")
    return True

def main():
    st.set_page_config(
    page_title="Pypi Threat Hunting",
    page_icon="🔍",
    )
    st.title("Pypi Threat Hunting")

    try:
        if not os.path.exists(filename):
            filename = "sample_pypi_info_db.csv"

        load_file(db=db, infile_path=filename, table_name=destination_table_name)

        st.write("## Submit SQL Query")
        default_query = f"SELECT name,rank,description,latest_release_published_at,package_manager_url,repository_url,maintainers,homepage,stars,latest_release_number,forks,total_versions\nFROM {destination_table_name}\nWHERE"
        
        user_query = st.text_area("Enter SQL query", value=default_query, height=200)

        #user_query = st.text_input("SQL Query", value=default_query, key="search_query")
        
        button = st.button(label="Run Query")
        if button:
            result = execute_query(
                    user_query,
                    db=db,
                    return_type="df",
            )
            
            try:
                # Set Date as index.
                result = result.set_index('latest_upload_date')
                result.index = result.index.date
            except:
                pass
            
            total_records_returned = len(result)
            if total_records_returned<=5:
                st.dataframe(result, height=150)
            elif total_records_returned >= 50:
                st.dataframe(result, height=1000)
            elif total_records_returned > 100:
                st.dataframe(result, height=1000)
            else:
                st.dataframe(result, height=200)

            #st.write(f"select * from {destination_table_name} where {filter_option} = '{filter_by}'")
            st.write(f"Total Records: {total_records_returned:,}")
        
            # To download the data we have just selected
            st.write("### Download Data")
            file_name = st.text_input("file name", value="search_results", key="out_file")
            
            if not '.csv' in file_name:
                file_name += '.csv'
            
            st.download_button(
                label="Press to Download",
                data=export_df(result),
                file_name=f"{file_name}.csv",
                mime="text/csv",
                key="download-csv",
            )

    except duckdb.CatalogException:  # Catch exception when the database file don't exist yet
        st.text("Please Click on the above button to start hunting.")

if __name__ == "__main__":
    main()