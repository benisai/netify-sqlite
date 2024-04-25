import os
from datetime import datetime
import requests
import sqlite3
import subprocess
from CONFIG import * # This will import shared variables from the CONFIG.py file.

# Check if the file netifyDB.db exists
if not os.path.exists(SQL_DB_FILE):
    print("netifyDB.db file missing. Running create-sqlite.py...")
    subprocess.run(['python3', 'create-sqlite.py'])


# Function to fetch NLBW data from the custom page
def fetch_nlbw_data():
    try:
        response = requests.get(nlbw_url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx)
        data = response.text

        nlbw_data = []
        lines = data.split("\n")
        for line in lines:
            line = line.strip()
            if line:
                fields = line.split("\t")
                mac_address = fields[0]
                ip_address = fields[1]
                conns = int(fields[2])
                rx_bytes = int(fields[3])
                rx_pkts = int(fields[4])
                tx_bytes = int(fields[5])
                tx_pkts = int(fields[6])
                nlbw_data.append((time_insert, mac_address, ip_address, conns, rx_bytes, rx_pkts, tx_bytes, tx_pkts))

        return nlbw_data

    except requests.RequestException as e:
        print("An error occurred while fetching NLBW data from the nlbw_url:")
        print(e)
        return []

# Connect to the SQLite database
conn = sqlite3.connect(SQL_DB_FILE)
cursor = conn.cursor()

# Get current timestamp
time_insert = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Fetch NLBW data from the custom page
nlbw_data = fetch_nlbw_data()

# Insert NLBW data into the SQLite database
for entry in nlbw_data:
    cursor.execute('''INSERT INTO nlbw_data (timeinsert, mac, ip, conns, rx_bytes, rx_pkts, tx_bytes, tx_pkts)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', entry)

# Commit changes and close connection
conn.commit()
conn.close()
