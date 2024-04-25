from datetime import datetime
import requests
import geoip2.database
import tarfile
import os
from CONFIG import * # This will import shared variables from the CONFIG.py file.

database_type = "GeoLite2-City"
download_url = f"https://download.maxmind.com/app/geoip_download?edition_id={database_type}&license_key={maxmind_license_key}&suffix=tar.gz"
output_folder = "files"
GEOIP_DB_FILE = "./files/GeoLite2-City.mmdb"


if DOWNLOAD_NEW_GEOIP_DB == "yes":
    # Send a GET request to the download URL
    response = requests.get(download_url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the filename from the response headers
        content_disposition = response.headers.get("content-disposition")
        filename = content_disposition.split("filename=")[1].strip('\"')

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Open a file for writing in binary mode
        with open(filename, "wb") as f:
            # Iterate over the response content in chunks and write to file
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract only the GeoLite2-City.mmdb file to the output folder
        with tarfile.open(filename, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith("GeoLite2-City.mmdb"):
                    member.name = os.path.basename(member.name)
                    tar.extract(member, path=output_folder)

        print(f"Download and extraction complete. Database saved to {output_folder}/GeoLite2-City.mmdb")

        # Delete the .tar.gz file
        os.remove(filename)

        print(f"Deleted {filename} file.")
    else:
        print("Failed to download the database. Please check your license key.")
else:
    print("Skipping GeoLite2-City.mmdb database download.")


