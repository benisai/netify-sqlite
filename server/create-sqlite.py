import os
from datetime import datetime
import sqlite3
from CONFIG import * # This will import shared variables from the CONFIG.py file.

# Create SQLite database connection
db = sqlite3.connect(SQL_DB_FILE)
cursor = db.cursor()

# Create Netify Flow table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS netify_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timeinsert TEXT,
    hostname TEXT,
    local_ip TEXT,
    local_mac TEXT,
    local_port INTEGER,
    fqdn TEXT,    
    dest_ip TEXT,
    dest_mac TEXT,
    dest_port INTEGER,
    dest_type TEXT,
    detected_protocol_name TEXT,
    detected_app_name TEXT,
    digest INTEGER,
    first_seen_at INTEGER,
    first_update_at INTEGER,
    vlan_id INTEGER,
    interface TEXT,
    internal INTEGER,
    ip_version INTEGER,
    last_seen_at INTEGER,
    type TEXT,
    dest_country TEXT,
    dest_state TEXT,
    dest_city TEXT,
    risk_score TEXT,
    risk_score_client TEXT,
    risk_score_server TEXT
);
"""
cursor.execute(create_table_query)
db.commit()



# Create Netify purge table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS netify_purge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timeinsert TEXT,
    digest INTEGER,
    detection_packets INTEGER,
    last_seen_at INTEGER,
    local_bytes INTEGER,
    local_packets INTEGER,
    other_bytes INTEGER,
    other_packets INTEGER,
    total_bytes INTEGER,
    total_packets INTEGER,
    interface TEXT,
    internal INTEGER,
    reason TEXT,
    type TEXT
);
"""
cursor.execute(create_table_query)
db.commit()



# Create netify_data table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS netify_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timeinsert TEXT,
    cpu_cores INTEGER,
    cpu_system REAL,
    cpu_system_prev REAL,
    cpu_user REAL,
    cpu_user_prev REAL,
    dhc_size INTEGER,
    dhc_status INTEGER,
    flows INTEGER,
    flows_prev INTEGER,
    maxrss_kb INTEGER,
    maxrss_kb_prev INTEGER,
    sink_queue_max_size_kb INTEGER,
    sink_queue_size_kb INTEGER,
    sink_resp_code INTEGER,
    sink_status INTEGER,
    sink_uploads INTEGER,
    timestamp INTEGER,
    type TEXT,
    update_imf INTEGER,
    update_interval INTEGER,
    uptime INTEGER,
    created_at TEXT
);
"""
cursor.execute(create_table_query)
db.commit()



# Create the table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS nlbw_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timeinsert TEXT,
    ip TEXT,
    mac TEXT,
    conns INTEGER,
    rx_bytes INTEGER,
    rx_pkts INTEGER,
    tx_bytes INTEGER,
    tx_pkts INTEGER
);
"""
cursor.execute(create_table_query)
db.commit()




