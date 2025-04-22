import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine, text

# --- Configuration ---
MYSQL_USER = 'root'
MYSQL_PASSWORD = '933662BeanMYSQL!!'
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DB = 'f1'
CSV_FOLDER = './csv'

# --- Connect to MySQL ---
engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}')

# --- Process CSV files ---
for filename in os.listdir(CSV_FOLDER):
    if filename.endswith(".csv"):
        filepath = os.path.join(CSV_FOLDER, filename)
        table_name = os.path.splitext(filename)[0].lower().replace(' ', '_')

        print(f"Processing: {filename} -> Table: {table_name}")

        # Read CSV into DataFrame
        df = pd.read_csv(filepath)

        # Replace spaces/special characters in column names
        df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]

        # Upload to MySQL (will create table if not exists)
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print(f"✅ Loaded {len(df)} rows into `{table_name}`.")

print("All CSVs processed.")
