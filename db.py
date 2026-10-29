# ╔══════════════════════════════════════════════════════════╗
# ║  DWLR Jal Mitra — Mock Database Layer                   ║
# ║  File: db.py                                            ║
# ║  Uses in-memory Python dicts (no DB install needed).    ║
# ║  Swap the dicts for SQLite / PostgreSQL when ready.     ║
# ╚══════════════════════════════════════════════════════════╝

import hashlib, uuid
from datetime import datetime, timedelta
import random

# ═══════════════════════════════════════════════
# MOCK DATA — DWLR STATIONS
# ═══════════════════════════════════════════════
STATIONS = [
    {
        "id": "KA-047",
        "village": "Doddaballapur",
        "taluk": "Doddaballapur",
        "district": "Bengaluru Rural",
        "state": "Karnataka",
        "lat": 13.2946,
        "lng": 77.5374,
        "depth_mbgl": 8.2,
        "ph": 7.1,
        "tds_mg_l": 480,
        "nitrate_mg_l": 12,
        "ec_ds_m": 1.1,
        "status": "safe",
        "recharge_rate_mm": 72,
        "last_updated": "2026-05-11T14:15:00",
        "trend": "stable",
        "bore_well_advisory": "Safe to use",
        "drinking_suitability": True,
        "irrigation_suitability": True,
    },
    {
        "id": "KA-052",
        "village": "Nelamangala",
        "taluk": "Nelamangala",
        "district": "Bengaluru Rural",
        "state": "Karnataka",
        "lat": 13.0979,
        "lng": 77.3938,
        "depth_mbgl": 11.4,
        "ph": 7.8,
        "tds_mg_l": 820,
        "nitrate_mg_l": 48,
        "ec_ds_m": 1.8,
        "status": "moderate",
        "recharge_rate_mm": 55,
        "last_updated": "2026-05-11T14:15:00",
        "trend": "declining",
        "bore_well_advisory": "Use with caution",
        "drinking_suitability": False,
        "irrigation_suitability": True,
    },
    {
        "id": "KA-089",
        "village": "Devanahalli",
        "taluk": "Devanahalli",
        "district": "Bengaluru Rural",
        "state": "Karnataka",
        "lat": 13.2479,
        "lng": 77.7117,
        "depth_mbgl": 14.6,
        "ph": 8.3,
        "tds_mg_l": 1240,
        "nitrate_mg_l": 82,
        "ec_ds_m": 2.6,
        "status": "critical",
        "recharge_rate_mm": 28,
        "last_updated": "2026-05-11T13:45:00",
        "trend": "declining",
        "bore_well_advisory": "Do NOT drill new bore-wells",
        "drinking_suitability": False,
        "irrigation_suitability": False,
    },
    {
        "id": "KA-033",
        "village": "Hoskote",
        "taluk": "Hoskote",
        "district": "Bengaluru Rural",
        "state": "Karnataka",
        "lat": 13.0704,
        "lng": 77.7980,
        "depth_mbgl": 9.8,
        "ph": 7.2,
        "tds_mg_l": 560,
        "nitrate_mg_l": 18,
        "ec_ds_m": 1.2,
        "status": "safe",
        "recharge_rate_mm": 68,
        "last_updated": "2026-05-11T14:15:00",
        "trend": "improving",
        "bore_well_advisory": "Safe to use",
        "drinking_suitability": True,
        "irrigation_suitability": True,
    },
    {
        "id": "KA-071",
        "village": "Anekal",
        "taluk": "Anekal",
        "district": "Bengaluru Rural",
        "state": "Karnataka",
        "lat": 12.7122,
        "lng": 77.6957,
        "depth_mbgl": 12.1,
        "ph": 7.6,
        "tds_mg_l": 760,
        "nitrate_mg_l": 35,
        "ec_ds_m": 1.6,
        "status": "moderate",
        "recharge_rate_mm": 48,
        "last_updated": "2026-05-11T13:00:00",
        "trend": "stable",
        "bore_well_advisory": "Use with caution",
        "drinking_suitability": True,
        "irrigation_suitability": True,
    },
    {
        "id": "MH-012",
        "village": "Nashik East",
        "taluk": "Nashik",
        "district": "Nashik",
        "state": "Maharashtra",
        "lat": 20.0059,
        "lng": 73.7898,
        "depth_mbgl": 6.4,
        "ph": 7.0,
        "tds_mg_l": 320,
        "nitrate_mg_l": 8,
        "ec_ds_m": 0.9,
        "status": "safe",
        "recharge_rate_mm": 90,
        "last_updated": "2026-05-11T14:00:00",
        "trend": "improving",
        "bore_well_advisory": "Safe to use",
        "drinking_suitability": True,
        "irrigation_suitability": True,
    },
    {
        "id": "RJ-041",
        "village": "Jodhpur North",
        "taluk": "Jodhpur",
        "district": "Jodhpur",
        "state": "Rajasthan",
        "lat": 26.2946,
        "lng": 73.0169,
        "depth_mbgl": 18.3,
        "ph": 8.6,
        "tds_mg_l": 2200,
        "nitrate_mg_l": 120,
        "ec_ds_m": 4.2,
        "status": "critical",
        "recharge_rate_mm": 12,
        "last_updated": "2026-05-11T12:30:00",
        "trend": "declining",
        "bore_well_advisory": "Do NOT drill. Extreme water scarcity zone.",
        "drinking_suitability": False,
        "irrigation_suitability": False,
    },
]

# ═══════════════════════════════════════════════
# ALERTS
# ═══════════════════════════════════════════════
ALERTS = [
    {
        "id": "ALT-001",
        "severity": "critical",
        "district": "Bengaluru Rural",
        "taluk": "Devanahalli",
        "station_id": "KA-089",
        "title": "Critical: Devanahalli Taluk",
        "message": "Station KA-089 reports 14.6 mbgl – critically low. Restrict bore-well usage. Switch to rainwater harvesting immediately.",
        "issued_date": "2026-05-10",
        "active": True,
    },
    {
        "id": "ALT-002",
        "severity": "warning",
        "district": "Bengaluru Rural",
        "taluk": "Nelamangala",
        "station_id": "KA-052",
        "title": "Warning: Nelamangala – High Nitrate",
        "message": "Nitrate levels elevated (48 mg/L). Do not use groundwater for drinking. Use for irrigation only until further notice.",
        "issued_date": "2026-05-08",
        "active": True,
    },
    {
        "id": "ALT-003",
        "severity": "info",
        "district": "Bengaluru Rural",
        "taluk": "Hoskote",
        "station_id": "KA-033",
        "title": "Update: Hoskote – Improved",
        "message": "Water levels recovered by 1.2 m after check-dam construction. Bore-well drilling restrictions lifted as of April 30, 2026.",
        "issued_date": "2026-05-01",
        "active": True,
    },
    {
        "id": "ALT-004",
        "severity": "critical",
        "district": "Jodhpur",
        "taluk": "Jodhpur",
        "station_id": "RJ-041",
        "title": "Critical: Jodhpur – Extreme Scarcity",
        "message": "Water table at 18.3 mbgl. No new bore-wells permitted. Emergency water tankers deployed by district administration.",
        "issued_date": "2026-05-09",
        "active": True,
    },
]

# ═══════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════
REPORTS = [
    {
        "id": "RPT-001",
        "name": "Monthly Groundwater Bulletin – April 2026",
        "district": "Bengaluru Rural",
        "period": "Apr 2026",
        "format": "PDF",
        "file_size_kb": 1240,
        "download_url": "/api/reports/RPT-001/download",
    },
    {
        "id": "RPT-002",
        "name": "Pre-Monsoon Water Level Report 2026",
        "district": "All Karnataka",
        "period": "Jan–Apr 2026",
        "format": "PDF + Excel",
        "file_size_kb": 3870,
        "download_url": "/api/reports/RPT-002/download",
    },
    {
        "id": "RPT-003",
        "name": "DWLR Station Data (Raw CSV)",
        "district": "All Karnataka",
        "period": "Custom Range",
        "format": "CSV",
        "file_size_kb": 890,
        "download_url": "/api/reports/RPT-003/download",
    },
    {
        "id": "RPT-004",
        "name": "Annual Groundwater Status Report 2025",
        "district": "All India",
        "period": "2025",
        "format": "PDF",
        "file_size_kb": 8200,
        "download_url": "/api/reports/RPT-004/download",
    },
]

# ═══════════════════════════════════════════════
# DISTRICTS BY STATE
# ═══════════════════════════════════════════════
DISTRICTS = {
    "Karnataka":       ["Bengaluru Rural","Bengaluru Urban","Raichur","Bidar","Mysuru","Tumkur","Kolar","Chitradurga","Dharwad","Belagavi","Vijayapura","Ballari","Hassan","Mandya","Shivamogga"],
    "Maharashtra":     ["Pune","Nashik","Aurangabad","Kolhapur","Nagpur","Solapur","Jalgaon","Amravati","Latur","Nanded"],
    "Rajasthan":       ["Jaipur","Jodhpur","Barmer","Bikaner","Udaipur","Kota","Ajmer","Sikar","Chittorgarh","Alwar"],
    "Punjab":          ["Amritsar","Ludhiana","Jalandhar","Patiala","Bathinda","Gurdaspur","Ferozepur","Moga"],
    "Uttar Pradesh":   ["Lucknow","Agra","Varanasi","Kanpur","Allahabad","Mathura","Meerut","Gorakhpur","Bareilly"],
    "Madhya Pradesh":  ["Bhopal","Indore","Jabalpur","Gwalior","Ujjain","Sagar","Rewa","Satna"],
    "Gujarat":         ["Ahmedabad","Surat","Vadodara","Rajkot","Bhavnagar","Junagadh","Anand","Gandhinagar"],
    "Telangana":       ["Hyderabad","Warangal","Nizamabad","Karimnagar","Khammam","Mahbubnagar","Nalgonda"],
    "Andhra Pradesh":  ["Vijayawada","Visakhapatnam","Tirupati","Guntur","Nellore","Kurnool","Kadapa"],
    "Tamil Nadu":      ["Chennai","Coimbatore","Madurai","Salem","Tiruchirappalli","Tirunelveli","Vellore"],
    "Kerala":          ["Thiruvananthapuram","Kochi","Kozhikode","Thrissur","Palakkad","Alappuzha","Kollam"],
    "West Bengal":     ["Kolkata","Howrah","Darjeeling","Murshidabad","Bardhaman","Nadia","North 24 Parganas"],
    "Odisha":          ["Bhubaneswar","Cuttack","Sambalpur","Rourkela","Puri","Berhampur","Balasore"],
    "Bihar":           ["Patna","Gaya","Muzaffarpur","Bhagalpur","Darbhanga","Purnia","Begusarai"],
    "Assam":           ["Guwahati","Dibrugarh","Silchar","Jorhat","Tezpur","Nagaon","Kamrup"],
}

# ═══════════════════════════════════════════════
# FARMER STORE (in-memory — replace with DB)
# ═══════════════════════════════════════════════
_farmers = {}        # { mobile: farmer_dict }
_issues  = []        # list of submitted issues
_sms_subs = {}       # { mobile: subscription_dict }

# ═══════════════════════════════════════════════
# HELPER — password hash
# ═══════════════════════════════════════════════
def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ═══════════════════════════════════════════════
# QUERY FUNCTIONS
# ═══════════════════════════════════════════════

def get_all_stations():
    return STATIONS

def get_station_by_id(sid: str):
    return next((s for s in STATIONS if s["id"] == sid), None)

def get_stations_by_district(district: str):
    return [s for s in STATIONS if s["district"].lower() == district.lower()]

def get_water_trend(station_id: str, range_val: str = "30d"):
    """Generate mock daily readings going back N days."""
    station = get_station_by_id(station_id)
    if not station:
        return None

    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map.get(range_val, 30)

    base_depth  = station["depth_mbgl"]
    today       = datetime.today()
    readings    = []
    last_year   = []

    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        # Slight random variation ± 0.3 m
        noise  = round(random.uniform(-0.3, 0.3), 2)
        noise2 = round(random.uniform(-0.3, 0.3), 2)
        readings.append({
            "date": date.strftime("%Y-%m-%d"),
            "depth_mbgl": round(base_depth + noise + (i * 0.01), 2),
        })
        last_year.append({
            "date": (date - timedelta(days=365)).strftime("%Y-%m-%d"),
            "depth_mbgl": round(base_depth + noise2 + (i * 0.012) + 0.8, 2),
        })

    return {"this_year": readings, "last_year": last_year}

def get_alerts():
    return ALERTS

def get_reports():
    return REPORTS

def get_districts_by_state(state: str):
    return DISTRICTS.get(state, [])

def get_advisory(district: str, lang: str = "en"):
    """Returns crop/water advisory cards for a district."""
    return [
        {
            "type": "crops",
            "icon": "🌾",
            "title": "Recommended Crops",
            "body": "With current water level at 8.2 mbgl, grow millets, pulses, or drip-irrigated tomatoes. Avoid paddy and sugarcane this Kharif season.",
            "badge": "✅ Suitable for your area",
            "badge_color": "green",
        },
        {
            "type": "irrigation",
            "icon": "💦",
            "title": "Irrigation Schedule",
            "body": "Limit bore-well irrigation to 5–8 AM. Use drip/sprinkler to save 40% water. Avoid irrigation during 11 AM–3 PM.",
            "badge": "💡 Save water",
            "badge_color": "blue",
        },
        {
            "type": "monsoon",
            "icon": "🌧️",
            "title": "Monsoon Forecast",
            "body": "IMD predicts normal monsoon in Karnataka (June–Sep 2026). Prepare farm ponds and recharge pits. Expected recharge: 180–220 mm.",
            "badge": "🌦️ Jun 2026 arrival",
            "badge_color": "wheat",
        },
        {
            "type": "borewell",
            "icon": "🚜",
            "title": "Bore-well Advisory",
            "body": "Do NOT drill new bore-wells in Devanahalli & Hoskote this season. Water table critically low. Wait till post-monsoon (Oct–Nov 2026).",
            "badge": "⛔ High-risk zone",
            "badge_color": "red",
        },
        {
            "type": "scheme",
            "icon": "🧑‍🤝‍🧑",
            "title": "Community Recharge",
            "body": "Join the Amrit Sarovar scheme. Your Gram Panchayat has 3 active check dams. Contact your local Jal Shakti officer for NREGA-funded pits.",
            "badge": "📞 Scheme available",
            "badge_color": "blue",
        },
        {
            "type": "helpline",
            "icon": "📱",
            "title": "Helpline & SMS Service",
            "body": "Call 1800-180-1551 (toll-free) for groundwater queries. Register for weekly SMS alerts in your language. Available 24/7.",
            "badge": "📞 Toll-free",
            "badge_color": "wheat",
        },
    ]


# ═══════════════════════════════════════════════
# WRITE FUNCTIONS
# ═══════════════════════════════════════════════

def register_farmer(data: dict) -> dict:
    mobile = data["mobile"].replace(" ", "").replace("+91", "")
    if mobile in _farmers:
        return {"success": False, "error": "Mobile number already registered"}

    farmer_id = "JM-" + str(uuid.uuid4())[:8].upper()
    _farmers[mobile] = {
        "farmer_id":    farmer_id,
        "full_name":    data.get("fullName", ""),
        "father_name":  data.get("fatherName", ""),
        "dob":          data.get("dob", ""),
        "gender":       data.get("gender", ""),
        "aadhaar":      data.get("aadhaar", ""),  # Store masked in prod
        "mobile":       mobile,
        "state":        data.get("state", ""),
        "district":     data.get("district", ""),
        "taluk":        data.get("taluk", ""),
        "village":      data.get("village", ""),
        "pincode":      data.get("pincode", ""),
        "land_acres":   data.get("landAcres", 0),
        "water_source": data.get("waterSource", ""),
        "crops":        data.get("crops", ""),
        "bore_depth":   data.get("boreDepth", 0),
        "alert_lang":   data.get("alertLanguage", "English"),
        "password_hash":_hash(data["password"]),
        "registered_at":datetime.now().isoformat(),
    }
    return {
        "success":   True,
        "farmer_id": farmer_id,
        "message":   f"Registration successful! Your Farmer ID is {farmer_id}. It has been sent to +91{mobile}.",
    }


def login_farmer(mobile: str, password: str) -> dict:
    farmer = _farmers.get(mobile)
    if not farmer:
        return {"success": False, "error": "Mobile number not registered"}
    if farmer["password_hash"] != _hash(password):
        return {"success": False, "error": "Incorrect password"}
    return {
        "success":   True,
        "farmer_id": farmer["farmer_id"],
        "full_name": farmer["full_name"],
        "district":  farmer["district"],
        "message":   f"Welcome back, {farmer['full_name']}!",
    }


def submit_issue_report(data: dict) -> dict:
    ticket = "JM-" + str(uuid.uuid4())[:8].upper()
    report = {
        "ticket_id":   ticket,
        "issue_type":  data.get("issueType", ""),
        "village":     data.get("village", ""),
        "description": data.get("description", ""),
        "mobile":      data.get("mobile", ""),
        "submitted_at":datetime.now().isoformat(),
        "status":      "received",
    }
    _issues.append(report)
    return {
        "success":   True,
        "ticket_id": ticket,
        "message":   f"Issue reported! Your ticket ID is {ticket}. We will respond within 48 hours.",
    }


def subscribe_sms(mobile: str, language: str, frequency: str) -> dict:
    _sms_subs[mobile] = {
        "mobile":      mobile,
        "language":    language,
        "frequency":   frequency,
        "subscribed_at": datetime.now().isoformat(),
    }
    return {
        "success":  True,
        "message":  f"SMS alerts activated for +91{mobile} in {language} ({frequency}).",
    }
