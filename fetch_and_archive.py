import os
import time
import json
import requests
import urllib3
import logging
from datetime import datetime, timedelta
from zipfile import ZipFile, ZIP_DEFLATED

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://fcd.autoroutes-trafic.fr/RennesOpenData/TP_FCD_AT.json"
FETCH_INTERVAL = 300  # 5min
LOG_FILE = "script.log"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def fetch_data():
    try:
        response = requests.get(API_URL, timeout=30, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.warning(f"Error, try again : {e}")
        try:
            response = requests.get(API_URL, timeout=30, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e2:
            logging.error(f"Error : {e2}")
            return None

def save_json(data, folder):
    now = datetime.now()
    filename = now.strftime("%H-%M-%S.json")
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Save response into : {filepath}")
    except Exception as e:
        logging.error(f"Error when saving {filepath} : {e}")

def archive_and_remove_folder(folder, year):
    archives_dir = f"archives/{year}"
    os.makedirs(archives_dir, exist_ok=True)
    zip_filename = os.path.join(archives_dir, f"{folder}.zip")
    try:
        with ZipFile(zip_filename, "w", ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=folder)
                    zipf.write(file_path, arcname)
        logging.info(f"Dossier archivé : {zip_filename}")
        # Remove folder
        for root, dirs, files in os.walk(folder, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(folder)
        logging.info(f"Folder deleted: {folder}")
    except Exception as e:
        logging.error(f"Error when zipping or removing {folder} : {e}")

def main():
    last_day = datetime.now().date()
    folder = last_day.strftime("%Y-%m-%d")
    logging.info("Start script")
    while True:
        now = datetime.now()
        current_day = now.date()
        # If it's a new day, archive data & remove previous folder
        if current_day != last_day:
            old_folder = last_day.strftime("%Y-%m-%d")
            if os.path.exists(old_folder):
                year = last_day.strftime("%Y")
                archive_and_remove_folder(old_folder, year)
            last_day = current_day
            folder = current_day.strftime("%Y-%m-%d")
        # Fetch data
        data = fetch_data()
        if data is not None:
            save_json(data, folder)
        else:
            logging.error("No data found, going to the next step")
        # Wait...
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
