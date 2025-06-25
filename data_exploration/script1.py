
# %%
import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("../data/jobs_ref.db")

# Run a SQL query and load the result into a DataFrame
df = pd.read_sql_query("SELECT * FROM jobs", conn)

# Display the DataFrame
print(df)

# Don't forget to close the connection
conn.close()

# %%
