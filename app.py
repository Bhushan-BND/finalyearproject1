# ╔══════════════════════════════════════════════════════════╗
# ║  DWLR Jal Mitra — Flask Backend  (LIVE version)         ║
# ║  File: app.py                                           ║
# ║  Local: python app.py  →  http://localhost:5000         ║
# ║  Live:  deployed on Render.com via Procfile             ║
# ╚══════════════════════════════════════════════════════════╝

# Load .env file if present (for local dev with API keys)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed — fine on Render, uses env vars directly

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import uuid, hashlib, json, os

from db import (
    get_all_stations, get_station_by_id, get_stations_by_district,
    get_water_trend, get_alerts, get_reports,
    register_farmer, login_farmer,
    submit_issue_report, subscribe_sms,
    get_advisory, get_districts_by_state
)

app = Flask(__name__)

# Allow all origins — needed for Netlify frontend → Render backend
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ─────────────────────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────────────────────
@app.route("/")
def index():
    return jsonify({
        "app": "DWLR Jal Mitra API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "GET  /api/stations",
            "GET  /api/stations/<station_id>",
            "GET  /api/stations?state=Karnataka&district=Bengaluru Rural&status=critical",
            "GET  /api/water-trend?station_id=KA-047&range=30d",
            "GET  /api/alerts?district=Bengaluru Rural",
            "GET  /api/reports?district=Karnataka",
            "GET  /api/advisory?district=Bengaluru Rural",
            "GET  /api/districts?state=Karnataka",
            "POST /api/register",
            "POST /api/login",
            "POST /api/report-issue",
            "POST /api/subscribe-sms",
        ]
    })

# ─────────────────────────────────────────────────────────
# STATIONS
# ─────────────────────────────────────────────────────────
@app.route("/api/stations", methods=["GET"])
def stations():
    state    = request.args.get("state")
    district = request.args.get("district")
    status   = request.args.get("status")

    data = get_all_stations()

    if state:
        data = [s for s in data if s["state"].lower() == state.lower()]
    if district:
        data = [s for s in data if s["district"].lower() == district.lower()]
    if status:
        data = [s for s in data if s["status"].lower() == status.lower()]

    return jsonify({"success": True, "count": len(data), "stations": data})


@app.route("/api/stations/<station_id>", methods=["GET"])
def station_detail(station_id):
    station = get_station_by_id(station_id.upper())
    if not station:
        return jsonify({"success": False, "error": "Station not found"}), 404
    return jsonify({"success": True, "station": station})


# ─────────────────────────────────────────────────────────
# WATER LEVEL TREND
# ─────────────────────────────────────────────────────────
@app.route("/api/water-trend", methods=["GET"])
def water_trend():
    station_id = request.args.get("station_id", "KA-047").upper()
    range_val  = request.args.get("range", "30d")

    data = get_water_trend(station_id, range_val)
    if data is None:
        return jsonify({"success": False, "error": "Station not found"}), 404

    return jsonify({"success": True, "station_id": station_id, "range": range_val, "trend": data})


# ─────────────────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────────────────
@app.route("/api/alerts", methods=["GET"])
def alerts():
    district = request.args.get("district")
    severity = request.args.get("severity")

    data = get_alerts()
    if district:
        data = [a for a in data if district.lower() in a["district"].lower()]
    if severity:
        data = [a for a in data if a["severity"].lower() == severity.lower()]

    return jsonify({"success": True, "count": len(data), "alerts": data})


# ─────────────────────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────────────────────
@app.route("/api/reports", methods=["GET"])
def reports():
    district = request.args.get("district")
    data = get_reports()
    if district:
        data = [r for r in data if district.lower() in r["district"].lower() or r["district"] == "All India" or r["district"] == "All Karnataka"]
    return jsonify({"success": True, "count": len(data), "reports": data})


# ─────────────────────────────────────────────────────────
# ADVISORY
# ─────────────────────────────────────────────────────────
@app.route("/api/advisory", methods=["GET"])
def advisory():
    district = request.args.get("district", "Bengaluru Rural")
    lang     = request.args.get("lang", "en")
    data = get_advisory(district, lang)
    return jsonify({"success": True, "district": district, "advisory": data})


# ─────────────────────────────────────────────────────────
# DISTRICTS
# ─────────────────────────────────────────────────────────
@app.route("/api/districts", methods=["GET"])
def districts():
    state = request.args.get("state", "")
    if not state:
        return jsonify({"success": False, "error": "state param required"}), 400
    data = get_districts_by_state(state)
    return jsonify({"success": True, "state": state, "districts": data})


# ─────────────────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}

    required = ["fullName", "mobile", "state", "district", "password"]
    missing  = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    mobile = body["mobile"].replace(" ", "").replace("+91", "")
    if not mobile.isdigit() or len(mobile) != 10:
        return jsonify({"success": False, "error": "Invalid mobile number"}), 400

    result = register_farmer(body)
    if not result["success"]:
        return jsonify(result), 409

    return jsonify(result), 201


# ─────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    mobile   = body.get("mobile", "").replace(" ", "").replace("+91", "")
    password = body.get("password", "")

    if not mobile or not password:
        return jsonify({"success": False, "error": "mobile and password required"}), 400

    result = login_farmer(mobile, password)
    if not result["success"]:
        return jsonify(result), 401

    return jsonify(result)


# ─────────────────────────────────────────────────────────
# REPORT ISSUE
# ─────────────────────────────────────────────────────────
@app.route("/api/report-issue", methods=["POST"])
def report_issue():
    body = request.get_json(silent=True) or {}

    required = ["issueType", "village", "mobile"]
    missing  = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    result = submit_issue_report(body)
    return jsonify(result), 201


# ─────────────────────────────────────────────────────────
# SUBSCRIBE SMS
# ─────────────────────────────────────────────────────────
@app.route("/api/subscribe-sms", methods=["POST"])
def subscribe_sms_route():
    body = request.get_json(silent=True) or {}

    mobile = body.get("mobile", "").replace(" ", "").replace("+91", "")
    lang   = body.get("language", "English")
    freq   = body.get("frequency", "Weekly Summary")

    if not mobile or not mobile.isdigit() or len(mobile) != 10:
        return jsonify({"success": False, "error": "Valid 10-digit mobile number required"}), 400

    result = subscribe_sms(mobile, lang, freq)
    return jsonify(result), 201


# ─────────────────────────────────────────────────────────
# OTP (mock)
# ─────────────────────────────────────────────────────────
_otp_store = {}

@app.route("/api/send-otp", methods=["POST"])
def send_otp():
    body   = request.get_json(silent=True) or {}
    mobile = body.get("mobile", "").replace(" ", "").replace("+91", "")
    if not mobile.isdigit() or len(mobile) != 10:
        return jsonify({"success": False, "error": "Invalid mobile number"}), 400

    otp = "123456"  # Mock — replace with MSG91 / Twilio in production
    _otp_store[mobile] = otp
    print(f"[OTP] Mobile: {mobile}  OTP: {otp}")
    return jsonify({"success": True, "message": f"OTP sent to +91{mobile} (mock: {otp})"})


@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    body   = request.get_json(silent=True) or {}
    mobile = body.get("mobile", "").replace(" ", "").replace("+91", "")
    otp    = body.get("otp", "")
    if _otp_store.get(mobile) == otp:
        del _otp_store[mobile]
        return jsonify({"success": True, "message": "OTP verified"})
    return jsonify({"success": False, "error": "Invalid or expired OTP"}), 401


# ─────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🌊  DWLR Jal Mitra API running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", debug=False, port=port)
