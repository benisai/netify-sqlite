# CONFIG.py
import os

# Router IP Address
ROUTER_IP = os.getenv('ROUTER_IP', '10.0.5.244')
NETIFY_PORT = os.getenv('NETIFY_PORT', '7150')


# URL to fetch NLBW data
nlbw_url = f"http://{ROUTER_IP}/nlbw.txt"


# GeoIP database section and license
DOWNLOAD_NEW_GEOIP_DB = os.getenv('DOWNLOAD_NEW_GEOIP_DB', 'yes') # Set to "yes" to download the new database, set to "no" to skip DB download
maxmind_license_key = os.getenv('maxmind_license_key', 'NO-KEY-CANT-DOWNLOAD')
GEOIP_DB_FILE = "./files/GeoLite2-City.mmdb"


# SQLite database configuration
SQL_DB_FILE = "../database/netifyDB.sqlite"
NETIFY_FLOW_TABLE = "netify_flow"
NETIFY_PURGE_TABLE = "netify_purge"
NETIFY_DATA_TABLE = "netify_data"
NLBW_DATA_TABLE = "nlbw_data"


# Custom DHCP page URL -- On the Router, run this command 'ln -s /tmp/dhcp.leases  /www/dhcp.html'
mac_host_mapping_file = "./files/dhcp_mapping.txt"
dhcp_page_url = f"http://{ROUTER_IP}/dhcp.html"
dhcp_mapping_file = "./files/dhcp_mapping.txt"