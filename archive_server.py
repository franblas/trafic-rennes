import os
import json
from datetime import datetime
from flask import Flask, send_from_directory, render_template, request, jsonify

ARCHIVES_DIR = "archives"
STARTING_YEAR = 2023

def get_years():
    current_year = datetime.now().strftime("%Y")
    years = [str(y) for y in range(STARTING_YEAR, int(current_year)+1)]
    return years,current_year

def get_config():
    conf = dict()
    with open("config.json", "r") as f:
        conf = json.load(f)
    return conf

def load_troncon_ref():
    result = dict()
    with open("troncon_rva_support_fcd.json", "r") as f:
        raw_troncon_ref = json.load(f)
        for ref in raw_troncon_ref:
            troncon_id = ref["id_troncon"]
            result[troncon_id] = [x[::-1] for x in ref["geo_shape"]["geometry"]["coordinates"]]
    return result

def status_to_color(status):
    if status == "unknown":
        return "#7f8c8d"
    elif status == "freeflow":
        return "#27ae60"
    elif status == "heavy":
        return "#f39c12"
    elif status == "congested":
        return "#c0392b"
    elif status == "impossible":
        return "#2c3e50"
    else:
        return "#7f8c8d"

def load_trafic_data():
    path= datetime.now().date().strftime("%Y-%m-%d")
    paths = [os.path.join(path, basename) for basename in os.listdir(path)]
    latest_file = max(paths, key=os.path.getctime)
    trafic_data = list()
    with open(f"{latest_file}", "r") as f:
        raw_trafic_data = json.load(f)["elaboratedData"]
        for d in raw_trafic_data:
            trafic_data.append({
                "coordinates": TRONCON_REF[d["predefinedLocationReference"]],
                "color": status_to_color(d["trafficStatus"].lower())
            })
    return trafic_data


app = Flask(__name__)

SERVER_CONFIG = get_config()
app.config['SECRET_KEY'] = SERVER_CONFIG["SECRET_KEY"]

TRONCON_REF = load_troncon_ref()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/trafic", methods=["GET"])
def trafic():
    trafic_data = load_trafic_data()
    return jsonify(trafic_data)

@app.route("/archives", methods=["GET"])
def list_archives():
    years, current_year = get_years()
    year_param = request.args.get("year", default=current_year, type=str)
    if year_param not in years or not os.path.exists(ARCHIVES_DIR):
        files = []
        year_param = ""
    else:
        files = sorted([f for f in os.listdir(f"{ARCHIVES_DIR}/{year_param}") if f.endswith(".zip")])
    return render_template("archives.html", files=files, years=years, selected_year=year_param)

@app.route("/archives/<year>/<filename>", methods=["GET"])
def download_archive(year, filename):
    years, _ = get_years()
    if not filename.endswith(".zip") or year not in years:
        return "Forbidden", 403
    return send_from_directory(f"{ARCHIVES_DIR}/{year}", filename, as_attachment=True)
