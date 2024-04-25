import os
from datetime import datetime
import subprocess
import json
import sqlite3
import geoip2.database
import socket
from CONFIG import * # This will import shared variables from the CONFIG.py file.

#---------- Check if GeoLite2-City.mmdb, dhcp_mapping or netifyDB.db exists ----------#

# Check if the file GeoLite2-City.mmdb exists
if not os.path.exists(GEOIP_DB_FILE):
    print("GeoLite2-City.mmdb file missing. Running get-geolite2-db.py...")
    subprocess.run(['python3', 'get-geolite2-db.py'])
else:
    print("GeoLite2-City.mmdb file found. No need to run get-geolite2-db.py.")

# Check if the file dhcp_mapping exists
if not os.path.exists(mac_host_mapping_file):
    print("dhcp_mapping.txt file missing. Running get-dhcp.py...")
    subprocess.run(['python3', 'get-dhcp.py'])
else:
    print("dhcp_mapping.txt file found. No need to run get-dhcp.py.")

# Check if the file netifyDB.db exists
if not os.path.exists(SQL_DB_FILE):
    print("netifyDB.db file missing. Running create-sqlite.py...")
    subprocess.run(['python3', 'create-sqlite.py'])
else:
    print("netifyDB.db file found. No need to run create-sqlite.py.")

#----------- END Check GeoLite2-City.mmdb, dhcp_mapping or netifyDB.db exists ----------#
    

# Initialize mac_host_mapping
mac_host_mapping = {}

# Read mac_host_mapping.txt and create mapping dictionary
mac_host_mapping = {}
with open(mac_host_mapping_file, "r") as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            mac, hostname, ip = line.split(" ", 2)
            mac_host_mapping[mac] = (hostname, ip)


# Read GeoIP Database
geoip_reader = geoip2.database.Reader(GEOIP_DB_FILE)

# Create SQLite database connection
db = sqlite3.connect(SQL_DB_FILE)
cursor = db.cursor()

#----------------------------------------------------------------------------------------------------------------------------
# Function to establish socket connection with retry logic
def run_socket():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port = int(NETIFY_PORT)
            sock.connect((ROUTER_IP, port))
            sock.settimeout(None)  # Optional: set to None for blocking mode
            print(f"Socket connection established to {ROUTER_IP} on port {NETIFY_PORT}")
            return sock
        except socket.error as e:
            print(f"Failed to establish socket connection to {ROUTER_IP}:{NETIFY_PORT}: {e}")
            time.sleep(5)  # Wait for a few seconds before retrying

# Establish socket connection
sock = run_socket()
stream = sock.makefile('r')

# Process the data stream for Netify_Flow
try:
    for line in stream:

        # Check if the line contains both "established" or "flow" and "local_ip"
        if "established" in line or "flow" in line and "local_ip" in line:
            # Parse JSON data
            data = json.loads(line)

            flow_data = data.get("flow", {})
            detected_protocol_name = flow_data.get("detected_protocol_name", "Unknown")
            first_seen_at = flow_data.get("first_seen_at", 0)
            first_update_at = flow_data.get("first_update_at", 0)
            ip_version = flow_data.get("ip_version", 0)
            last_seen_at = flow_data.get("last_seen_at", 0)
            local_ip = flow_data.get("local_ip", "Unknown")
            local_mac = flow_data.get("local_mac", "Unknown")
            local_port = flow_data.get("local_port", 0)
            dest_ip = flow_data.get("other_ip", "Unknown")
            dest_mac = flow_data.get("other_mac", "Unknown")
            dest_port = flow_data.get("other_port", 0)
            dest_type = flow_data.get("other_type", "Unknown")
            vlan_id = flow_data.get("vlan_id", 0)
            interface = data.get("interface", "Unknown")
            internal = data.get("internal", False)
            type = data.get("type", "Unknown")
            detected_app_name = flow_data.get("detected_application_name", "Unknown")
            digest = flow_data.get("digest", "Unknown")

            # Check the structure of 'risks_data'
            risks_data = flow_data.get("risks", {})

            # Extract risk scores
            risk_score = risks_data.get("ndpi_risk_score", 0)
            risk_score_client = risks_data.get("ndpi_risk_score_client", 0)
            risk_score_server = risks_data.get("ndpi_risk_score_server", 0)



            # Check if 'host_server_name' exists in the data
            fqdn = flow_data.get("host_server_name", local_ip)
            #print(f"Here is the fqdn: {fqdn}")

            ssl_data = flow_data.get("ssl", {})
            client_sni = ssl_data.get("client_sni", "no_ssl")
            # Check if SSL field exists and has the 'client_sni' attribute, set the FQDN to the SNI
            if "client_sni" in ssl_data:
                fqdn = ssl_data["client_sni"]
                client_sni = ssl_data["client_sni"]
                #print(f"Here is the client_sni set for the fqdn: {fqdn}")

            # Check if local_mac exists in mac_host_mapping
            hostname, _ = mac_host_mapping.get(local_mac, (local_ip, ""))

            # Retrieve location information using GeoIP (You can uncomment this once you have the GeoIP functionality set up)
            try:
                response = geoip_reader.city(dest_ip)
                dest_country = response.country.name
                dest_state = response.subdivisions.most_specific.name
                dest_city = response.city.name
            except geoip2.errors.AddressNotFoundError:
                dest_country = "Unknown"
                dest_state = "Unknown"
                dest_city = "Unknown"

            # Get current timestamp
            time_insert = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # SQL query to insert data into the table
            insert_query = f"""
            INSERT INTO {NETIFY_FLOW_TABLE} (
                timeinsert, hostname, local_ip, local_mac, local_port, fqdn, dest_ip, dest_mac, dest_port, dest_type,
                detected_protocol_name, detected_app_name, digest, first_seen_at, first_update_at, vlan_id, interface, internal, ip_version,
                last_seen_at, type, dest_country, dest_state, dest_city, risk_score, risk_score_client, risk_score_server
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """

            # Execute the SQL query
            cursor.execute(insert_query, (
                time_insert, hostname, local_ip, local_mac, local_port, fqdn, dest_ip, dest_mac, dest_port, dest_type,
                detected_protocol_name, detected_app_name, digest, first_seen_at, first_update_at, vlan_id, interface, internal, ip_version,
                last_seen_at, type, dest_country, dest_state, dest_city, risk_score, risk_score_client, risk_score_server
            ))
            db.commit()



    # Check if the line contains both "digest" and "flow_purge" This is only available in Netify Agent 4.x
        if "digest" in line and "flow_purge" in line:
            data = json.loads(line)
            flow_data = data["flow"]  # Extract the flow data

            detection_packets = flow_data.get("detection_packets", 0)
            last_seen_at = flow_data.get("last_seen_at", 0)
            local_bytes = flow_data.get("local_bytes", 0)
            local_packets = flow_data.get("local_packets", 0)
            other_bytes = flow_data.get("other_bytes", 0)
            other_packets = flow_data.get("other_packets", 0)
            total_bytes = flow_data.get("total_bytes", 0)
            total_packets = flow_data.get("total_packets", 0)
            interface = data["interface"]
            internal = data["internal"]
            reason = data.get("reason", "Unknown")
            detected_app_name = flow_data.get("detected_application_name", "Unknown")
            digest = flow_data.get("digest", "Unknown")
            type = data["type"]

            # Get current timestamp
            time_insert = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # SQL query to insert data into the table
            insert_query = f"""
            INSERT INTO netify_purge (
                timeinsert, detection_packets, digest, last_seen_at, local_bytes, local_packets,
                other_bytes, other_packets, total_bytes, total_packets,
                interface, internal, reason, type
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """

            # Prepare the data for insertion
            insert_data = (
                time_insert, detection_packets, digest, last_seen_at, local_bytes, local_packets,
                other_bytes, other_packets, total_bytes, total_packets,
                interface, internal, reason, type
            )

            # Execute the SQL query
            cursor.execute(insert_query, insert_data)
            db.commit()


    # Check if the line contains "cpu_cores"
        if "cpu_cores" in line:
            data = json.loads(line.strip())

            # Extract relevant data
            cpu_cores = data.get("cpu_cores", 0)
            cpu_system = data.get("cpu_system", 0)
            cpu_system_prev = data.get("cpu_system_prev", 0)
            cpu_user = data.get("cpu_user", 0)
            cpu_user_prev = data.get("cpu_user_prev", 0)
            dhc_size = data.get("dhc_size", 0)
            dhc_status = data.get("dhc_status", False)
            flows = data.get("flows", 0)
            flows_prev = data.get("flows_prev", 0)
            maxrss_kb = data.get("maxrss_kb", 0)
            maxrss_kb_prev = data.get("maxrss_kb_prev", 0)
            sink_queue_max_size_kb = data.get("sink_queue_max_size_kb", 0)
            sink_queue_size_kb = data.get("sink_queue_size_kb", 0)
            sink_resp_code = data.get("sink_resp_code", 0)
            sink_status = data.get("sink_status", False)
            sink_uploads = data.get("sink_uploads", False)
            timestamp = data.get("timestamp", 0)
            type = data.get("type", "Unknown")
            update_imf = data.get("update_imf", 0)
            update_interval = data.get("update_interval", 0)
            uptime = data.get("uptime", 0)

            # Get current timestamp
            time_insert = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert the data into the SQLite database
            cursor.execute('''INSERT INTO netify_data (
                                timeinsert, cpu_cores, cpu_system, cpu_system_prev, cpu_user, cpu_user_prev,
                                dhc_size, dhc_status, flows, flows_prev, maxrss_kb,
                                maxrss_kb_prev, sink_queue_max_size_kb, sink_queue_size_kb,
                                sink_resp_code, sink_status, sink_uploads, timestamp,
                                type, update_imf, update_interval, uptime, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (time_insert, cpu_cores, cpu_system, cpu_system_prev,
                            cpu_user, cpu_user_prev, dhc_size,
                            dhc_status, flows, flows_prev,
                            maxrss_kb, maxrss_kb_prev,
                            sink_queue_max_size_kb, sink_queue_size_kb,
                            sink_resp_code, sink_status,
                            sink_uploads, timestamp, type,
                            update_imf, update_interval, uptime,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            # Commit the transaction
            db.commit()




#----------------------------------------------------------------------------------------------------------------------------The End

finally:
    stream.close()
    sock.close()
    geoip_reader.close()
    cursor.close()
    db.close()
