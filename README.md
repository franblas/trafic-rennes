# Rennes Traffic – Data Collection and Archive Consultation

This project automatically collects traffic data from Rennes via an API, archives the results daily, and allows you to consult the archives through a web interface.

## Features

- **Automatic collection**: Queries the [RennesOpenData API](https://fcd.autoroutes-trafic.fr/RennesOpenData/TP_FCD_AT.json) every 5 minutes.
- **Daily archiving**: Stores each response in a JSON file within a date-named folder (`YYYY-MM-DD`). Archives (zips) and deletes the previous day's folder at each day change.
- **Archive server**: Lets you browse the archives through a simple web interface.
- **Logging and error handling**: Errors are managed with retries and logged in `script.log`.

## Installation

### Prerequisites

- Python 3.11+
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```

## Run locally

### 1. Data collection and archiving

Start the collection script:

```bash
python fetch_and_archive.py
```

The script will run continuously, automatically handling storage, archiving, and folder deletion.

### 2. Browse archives via the web server

Start the archive server:

```bash
flask --app archive_server:app run --debug
```

Open your browser at [http://localhost:5000](http://localhost:5000) to access the web interface and browse the archives.

## Run with Docker compose

```bash
# run everything
docker-compose up -d
# run only the data collector
docker-compose up fetch-and-archive -d
# run only the web server
docker-compose up archive-server -d
```

## File organization

- `fetch_and_archive.py`: Data collection and archiving script.
- `archive_server.py`: Web server to browse the archives.
- `archives/`: Folder containing daily archives zip files (`YYYY-MM-DD.zip`).
- `script.log`: Log file.
- `templates/` and `static/`: Files for the web interface.

## License

[MIT](LICENSE)
