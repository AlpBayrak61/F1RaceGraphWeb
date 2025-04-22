import pymysql
import pandas as pd
import random

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

db = pymysql.connect(
    host='localhost',
    user='root',
    password='933662BeanMYSQL!!',
    database='f1'
)

cursor = db.cursor()
# cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'f1'")
# tables = [row[0] for row in cursor.fetchall()]

# --- Iterate through tables and print first row ---
# for table in tables:
#     print(f"\n--- {table} ---")
#     cursor.execute(f"SELECT * FROM `{table}` LIMIT 1")
#     row = cursor.fetchone()
#     if row:
#         columns = [desc[0] for desc in cursor.description]
#         df = pd.DataFrame([row], columns=columns)
#         print(df.to_markdown(index=False))
#         # print(df.to_string(index=False))
#     else:
#         print("No rows found.")

# cursor.close()
# db.close()





# team = pd.read_csv('csv/team.csv')
# f1_team_names = team['team_name'].tolist()

# sponsor = pd.read_csv('csv/sponsor.csv')
# company_names = sponsor['sponsor_name'].tolist()

# num_rows = 500
# # employs has team_name(str), driver_id(int)
# EMPLOYS = {
#     "team_name": [random.choice(f1_team_names) for _ in range(num_rows)],
#     "driver_id": [i for i in range(1, num_rows + 1)],
# }
# df = pd.DataFrame(EMPLOYS)
# df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]

# # Upload to MySQL (will create table if not exists)
# df.to_sql("employs", con=engine, if_exists='replace', index=False)

# num_rows = 500
# # team_sponsor_pair has team_name(str), sponsor_name(str)
# TEAM_SPONSOR_PAIR = {
#     "team_name": [random.choice(f1_team_names) for _ in range(num_rows)],
#     "sponsor_name": [random.choice(company_names) for _ in range(num_rows)],
# }
# df = pd.DataFrame(TEAM_SPONSOR_PAIR)

# df.to_sql("team_sponsor_pair", con=engine, if_exists='replace', index=False)



num_rows = 10000
# race_event has race_id(int), start_date(date), temp(float between 20 and 40), precipitation(float between 0 and 100), wind_speed(float between 0 and 20)
from datetime import datetime, timedelta
import random
RACE_EVENT = {
    "race_id": [i for i in range(1, num_rows + 1)],
    # start date is random date between 1900 jan 1 midnight and 2025 jan 1 midnight
    "start_date": [datetime(1900, 1, 1) + timedelta(days=random.randint(0, (datetime(2025, 1, 1) - datetime(1900, 1, 1)).days)) for _ in range(num_rows)],
    # "start_date": [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_rows)],
    "temp": [round(random.uniform(20.0, 40.0), 2) for _ in range(num_rows)],
    "precipitation": [round(random.uniform(0.0, 100.0), 2) for _ in range(num_rows)],
    "wind_speed": [round(random.uniform(0.0, 20.0), 2) for _ in range(num_rows)],
}

df = pd.DataFrame(RACE_EVENT)
df.to_sql("race_event", con=engine, if_exists='replace', index=False)