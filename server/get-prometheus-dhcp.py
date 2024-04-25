from datetime import datetime
import requests
from CONFIG import * # This will import shared variables from the CONFIG.py file.

# Decision to generate MAC host mapping from prometheus_url
generate_mac_mapping = "no"  # Change to "no" if you want to skip the mapping generation

#------#
# Initialize mac_host_mapping
#mac_host_mapping = {}

# Prometheus metrics URL
prometheus_url = f"http://{ROUTER_IP}:9100/metrics"
mac_host_mapping_file = "./files/dhcp_mapping.txt"


if generate_mac_mapping == "yes":
    # Fetch metrics data and generate mac_host_mapping.txt
    def generate_mac_host_mapping():
        try:
            response = requests.get(prometheus_url)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx)
            data = response.text

            mac_host_mapping = {}
            lines = data.split("\n")
            for line in lines:
                if line.startswith('dhcp_lease{'):
                    mac_start = line.find('mac="') + len('mac="')
                    mac_end = line.find('"', mac_start)
                    mac = line[mac_start:mac_end]

                    name_start = line.find('name="') + len('name="')
                    name_end = line.find('"', name_start)
                    name = line[name_start:name_end]

                    ip_start = line.find('ip="') + len('ip="')
                    ip_end = line.find('"', ip_start)
                    ip = line[ip_start:ip_end]

                    mac_host_mapping[mac] = (name, ip)

            with open(mac_host_mapping_file, "w") as file:
                for mac, (hostname, ip) in mac_host_mapping.items():
                    file.write(f"{mac.lower()} {hostname} {ip}\n")

        except requests.RequestException as e:
            print("An error occurred while fetching data from Prometheus:")
            print(e)
            # Create a blank file in case of HTTP request errors
            open(mac_host_mapping_file, "w").close()

    # Generate mac_host_mapping.txt
    generate_mac_host_mapping()

    # Read mac_host_mapping.txt and create mapping dictionary
    mac_host_mapping = {}
    with open(mac_host_mapping_file, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line:
                mac, hostname, ip = line.split(" ", 2)
                mac_host_mapping[mac] = (hostname, ip)

elif generate_mac_mapping == "no":
    print("Skipping MAC host mapping generation.")
else:
    print("Skipping MAC host mapping generation.")

