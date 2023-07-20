import duckdb
import streamlit as st

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

def load_file(db: str = "duck.db", infile_path: str = "pypi_info_db.csv", table_name: str = "pypi"):
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
        #button = st.button(label="Get Started")
        #if button:
        load_file(db=db, infile_path=filename, table_name=destination_table_name)

        data = execute_query(f"select * from {destination_table_name}", db=db, return_type="df")
        ###########  section 1  ###########  
        st.write("## Data Sample")
        st.dataframe(data.head(10), height=300)

        ###########  section 2  ###########
        st.write("## Visualization")
        option = st.selectbox("Select a dimension", ["rank", "stars", "dependent_repos_count", "dependents_count", "forks", "total_versions"], key="option")
        if option:
            #st.write(f"### Bar Chart: {option} x Quantity")
            #st.bar_chart(data[option], x=option, y="total_versions")

            #st.write(f"### Bar Chart: {option} x Amount")
            #st.bar_chart(data[option], x=option, y="amount")

            st.write(f"### Bar Chart: {option} x Count")
            st.bar_chart(data[option].value_counts())

        ###########  section 3  ###########
        st.write("## Filters ##")
        filter_option = st.selectbox("Select a filter", ["rank", "licenses", "normalized_licenses"], key="filter_option")
        st.write(f"### Filters (by {filter_option})")
        value_list = [
            row[0]
            for row in execute_query(
                f"select distinct({filter_option}) from {destination_table_name}", db=db, return_type="list"
            )
        ]
        value_list.sort()
        
        filter_by = st.selectbox(label="Select a Value", options=value_list, key="rank_filter")
        
        if filter_by != "--":
            
            if type(filter_by) == str:
                # check for ' in string values
                if "'" in filter_by:
                    # sql escape '
                    filter_by = filter_by.replace("'", "''")

            result = execute_query(
                f"select * from {destination_table_name} where {filter_option} = '{filter_by}'",
                db=db,
                return_type="df",
            )
            st.dataframe(result, height=400)

            #st.write(f"select * from {destination_table_name} where {filter_option} = '{filter_by}'")
            st.write(f"Total Records: {len(result):,}")


            # To download the data we have just selected
            st.write("#### Download Data")
            st.download_button(
                label="Press to Download",
                data=export_df(result),
                file_name=f"pypi - rank='{filter_by}'.csv",
                mime="text/csv",
                key="download-csv",
            )
    except duckdb.CatalogException:  # Catch exception when the database file don't exist yet
        st.text("Please Click on the above button to start hunting.")

if __name__ == "__main__":
    main()