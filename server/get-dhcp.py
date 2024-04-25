import os
import time
import requests
import subprocess
from CONFIG import *

# Decision to generate MAC host mapping from prometheus_url
generate_mac_mapping = "yes"  # Change to "no" if you want to skip the mapping generation

# Path to the lock file
lock_file = "/tmp/main.lock"

# Function to check if main.py is running
def is_main_running():
    return os.path.exists(lock_file)

# Function to start main.py
def start_main():
    if is_main_running():
        with open(lock_file, "w"):
            subprocess.Popen(["python3", "/app/server/main.py"])
            print("main.py processed restarted due to a new dhcp added to dhcp_mapping.txt.")

# Function to kill main.py
def kill_main():
    if is_main_running():
        subprocess.run(["pkill", "-f", "python3 /app/server/main.py"])
        print("main.py processed killed due to a new dhcp added to dhcp_mapping.txt.")

# Function to fetch DHCP lease data from the custom page
def fetch_dhcp_data():
    try:
        response = requests.get(dhcp_page_url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx)
        data = response.text

        dhcp_lease_data = {}
        lines = data.split("\n")
        for line in lines:
            line = line.strip()
            if line:
                fields = line.split(" ")
                mac_address = fields[1]
                hostname = fields[3] if fields[3] != "*" else mac_address.replace(":", "")
                ip_address = fields[2]
                dhcp_lease_data[mac_address] = (hostname, ip_address)

        return dhcp_lease_data

    except requests.RequestException as e:
        print("An error occurred while fetching DHCP data from the {ROUTER_IP}/dhcp.html page:")
        print(e)
        return {}

# Function to update the MAC host mapping file
def update_mac_mapping():
    dhcp_data = fetch_dhcp_data()

    # Read existing DHCP data from the file
    existing_dhcp_data = {}
    if os.path.exists(dhcp_mapping_file):
        with open(dhcp_mapping_file, "r") as file:
            for line in file:
                fields = line.strip().split(" ")
                mac_address = fields[0]
                hostname = fields[1]
                ip_address = fields[2]
                existing_dhcp_data[mac_address] = (hostname, ip_address)

    # Compare fetched DHCP data with existing data
    if dhcp_data == existing_dhcp_data:
        print("No changes detected in DHCP data. Skipping update.")
        return

    # Save DHCP lease data to the file
    with open(dhcp_mapping_file, "w") as file:
        for mac_address, (hostname, ip_address) in dhcp_data.items():
            file.write(f"{mac_address} {hostname} {ip_address}\n")
            print(f"Updated MAC host mapping file: Host={hostname}, MAC={mac_address}, IP={ip_address}")

    # Kill the existing main.py process
    kill_main()

    # Restart main.py
    start_main()

# Main loop
while True:
    # Check if MAC host mapping generation is required
    if generate_mac_mapping == "yes":
        # Update the MAC host mapping file
        update_mac_mapping()

    # Sleep for 15 seconds
    time.sleep(15)
