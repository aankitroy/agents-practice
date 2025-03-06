import gspread
import psycopg2
from psycopg2.extras import execute_values
from google.oauth2.service_account import Credentials

def fetch_sheet_and_upload(sheet_url, pg_config, table_names, credentials_path):
    """
    Fetches data from a Google Sheet and uploads it to multiple PostgreSQL tables based on sheet tabs.
    
    Parameters:
    - sheet_url: URL of the Google Sheet.
    - pg_config: A dictionary with PostgreSQL connection parameters (e.g., dbname, user, password, host, port).
    - table_names: A list of table names in PostgreSQL where the data will be inserted, corresponding to each sheet tab.
    - credentials_path: File path to your Google service account credentials JSON.
    
    Note: The PostgreSQL tables should already exist with columns matching the sheet headers.
    """
    # Set up Google Sheets API credentials and client
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
    client = gspread.authorize(creds)
    
    # Open the sheet by URL
    sheet = client.open_by_url(sheet_url)
    
    # Iterate through each worksheet (tab) in the sheet
    for i, worksheet in enumerate(sheet.worksheets()):
        # Fetch all records from the sheet as a list of dictionaries
        records = worksheet.get_all_records()
        if not records:
            print(f"No data found in the sheet tab: {worksheet.title}.")
            continue
        
        # Extract column names from the first record (assuming headers in the first row)
        columns = list(records[0].keys())
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table_names[i]} ({columns_str}) VALUES ({placeholders})"
        print(insert_query)
        
        # Connect to PostgreSQL and insert data one record at a time
        try:
            conn = psycopg2.connect(**pg_config)
            cur = conn.cursor()
            for record in records:
                data = tuple(record[col] for col in columns)
                print(data)
                cur.execute(insert_query, data)
            conn.commit()
            print(f"Successfully inserted {len(records)} records into {table_names[i]}.")
        except Exception as e:
            print(f"Error while inserting data into {table_names[i]}:", e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

# Example usage:
if __name__ == "__main__":
    # URL of the Google Sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1TpyF0qQ158TETFOJNdANTCXarqww-H1mcJMF8FwG_vg/edit"
    
    # PostgreSQL connection configuration
    pg_config = {
        "dbname": "ai",
        "user": "aankitroy",
        "password": "xyzpassword",
        "host": "localhost",
        "port": 5432
    }
    
    # List of table names corresponding to each sheet tab
    table_names = ["Online_Sales", "Marketing_Spend", "Discount_Coupon", "Customer_Data", "Tax"]
    credentials_path = "/Users/aankitroy/Downloads/prefab-hangout-149209-41838eff7034.json"
    
    fetch_sheet_and_upload(sheet_url, pg_config, table_names, credentials_path)
