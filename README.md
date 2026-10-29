# 🌊 DWLR Jal Mitra — Backend

Flask backend for the DWLR Jal Mitra groundwater portal.  
Runs locally in VS Code. No database installation needed.

---

## 📁 File Structure

```
dwlr_backend/
├── app.py              ← Flask server + all API routes
├── db.py               ← Mock data + query/write functions
├── requirements.txt    ← pip dependencies
├── api_connector.js    ← Paste into your HTML file
└── README.md           ← This file
```

---

## ⚡ Quick Start (VS Code)

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Start the server
```bash
python app.py
```
You should see:
```
🌊  DWLR Jal Mitra API running at http://localhost:5000
```

### Step 3 — Connect your HTML
Add this line just before `</body>` in `phase2.html`:
```html
<script src="api_connector.js"></script>
```
> If you're opening the HTML directly (file://), keep `api_connector.js`
> in the **same folder** as your HTML file. Flask's CORS is already enabled.

---

## 🔌 Two small HTML changes also needed

In the **Report Issue modal** (`reportModal`), change the submit button:
```html
<!-- BEFORE -->
<button class="btn-submit" onclick="closeModal('reportModal'); showToast(...)">

<!-- AFTER -->
<button class="btn-submit" onclick="submitIssueReport()">📤 Submit Report</button>
```

In the **SMS modal** (`smsModal`), change the submit button:
```html
<!-- BEFORE -->
<button class="btn-submit" onclick="closeModal('smsModal'); showToast(...)">

<!-- AFTER -->
<button class="btn-submit" onclick="submitSmsSubscription()">📲 Activate Alerts</button>
```

---

## 🗺️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stations` | All DWLR stations |
| GET | `/api/stations?state=Karnataka&district=Bengaluru Rural&status=critical` | Filtered stations |
| GET | `/api/stations/<id>` | Single station detail |
| GET | `/api/water-trend?station_id=KA-047&range=30d` | Chart trend data |
| GET | `/api/alerts?district=Bengaluru Rural` | Active alerts |
| GET | `/api/reports?district=Karnataka` | Downloadable reports |
| GET | `/api/advisory?district=Bengaluru Rural` | Farmer advisory cards |
| GET | `/api/districts?state=Karnataka` | Districts for a state |
| POST | `/api/register` | Register a farmer |
| POST | `/api/login` | Login a farmer |
| POST | `/api/send-otp` | Send OTP (mock) |
| POST | `/api/verify-otp` | Verify OTP |
| POST | `/api/report-issue` | Submit water issue report |
| POST | `/api/subscribe-sms` | Subscribe to SMS alerts |

---

## 📦 Sample API Calls (test in browser or Postman)

```
GET  http://localhost:5000/api/stations
GET  http://localhost:5000/api/stations?status=critical
GET  http://localhost:5000/api/stations/KA-047
GET  http://localhost:5000/api/water-trend?station_id=KA-047&range=30d
GET  http://localhost:5000/api/alerts
GET  http://localhost:5000/api/districts?state=Karnataka
```

### Registration (POST)
```json
POST http://localhost:5000/api/register
{
  "fullName":      "Ramesh Kumar",
  "mobile":        "9876543210",
  "state":         "Karnataka",
  "district":      "Bengaluru Rural",
  "password":      "mypassword123",
  "alertLanguage": "Kannada"
}
```

### Login (POST)
```json
POST http://localhost:5000/api/login
{
  "mobile":   "9876543210",
  "password": "mypassword123"
}
```

---

## 🔧 Upgrading from mock data to a real database

All data lives in `db.py`. To swap in SQLite:

```bash
pip install flask-sqlalchemy
```

Then replace the `STATIONS`, `FARMERS`, etc. dicts in `db.py`  
with SQLAlchemy models — the `app.py` routes stay unchanged.

---

## 🔐 OTP Note

The mock OTP is always `123456` and prints to your VS Code terminal.  
To use a real SMS gateway, replace the `send_otp` route in `app.py` with:
- **MSG91** (India) — https://msg91.com
- **Twilio** — https://twilio.com
- **Fast2SMS** (free tier available in India)