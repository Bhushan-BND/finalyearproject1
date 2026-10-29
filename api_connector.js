/* ═══════════════════════════════════════════════════════════════
   DWLR Jal Mitra — API Connector  (FIXED v3 — Login + Live URL)
   Place this file in the same folder as phase2.html
   Add before </body>:  <script src="api_connector.js"></script>
   ═══════════════════════════════════════════════════════════════

   HOW URL AUTO-DETECTION WORKS:
   ─────────────────────────────
   • Opening phase2.html directly from your computer (file://) → uses localhost
   • Opening via http://localhost:5555 or similar              → uses localhost
   • Opening from Render.com (https://...)                     → uses Render URL

   AFTER DEPLOYING TO RENDER:
   ──────────────────────────
   Replace the LIVE_URL below with your actual Render app URL,
   e.g.  "https://dwlr-jal-mitra-api.onrender.com"
   ═══════════════════════════════════════════════════════════════ */

// ── URL Configuration ────────────────────────────────────────────
const LOCAL_URL = "http://localhost:5000";
const LIVE_URL  = "https://dwlr-jal-mitra-api.onrender.com";  // ← update after deploy

// Auto-detect: use localhost when running locally, live URL when deployed
const API_BASE = (
  window.location.protocol === "file:" ||
  window.location.hostname  === "localhost" ||
  window.location.hostname  === "127.0.0.1"
) ? LOCAL_URL + "/api" : LIVE_URL + "/api";

console.log("🌊 DWLR API Connector v3 | Using API:", API_BASE);

// ─── Loading spinner helpers ─────────────────────────────────────
function showLoader(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = `
    <tr><td colspan="8" style="text-align:center;padding:24px;color:#888;">
      <span style="font-size:1.4rem">⏳</span><br>Loading live data...
    </td></tr>`;
}

function showLoaderGrid(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = `
    <div style="text-align:center;padding:40px;color:#888;grid-column:1/-1;">
      <span style="font-size:2rem">⏳</span><br>Loading...
    </div>`;
}

// ─── Core fetch ──────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(API_BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "API error");
    return data;
  } catch (err) {
    console.error("[API]", path, err.message);
    if (typeof showToast === "function") showToast("⚠️ " + err.message);
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════
// 1. DASHBOARD — water quality table + metric cards
// ═══════════════════════════════════════════════════════════════
async function loadStations(filters = {}) {
  const tbody = document.querySelector("#page-dashboard .table-section tbody");
  if (tbody) showLoader("page-dashboard-tbody-loader");

  const params = new URLSearchParams(filters).toString();
  const data   = await apiFetch("/stations" + (params ? "?" + params : ""));
  if (!data) return;

  // ── water quality table ──
  const tBody = document.querySelector("#page-dashboard .table-section tbody");
  if (tBody) {
    tBody.innerHTML = "";
    data.stations.forEach(s => {
      const badge = {
        safe:     '<span class="status-badge status-safe">✅ Safe</span>',
        moderate: '<span class="status-badge status-warning">⚠️ Moderate</span>',
        critical: '<span class="status-badge status-critical">🚨 Critical</span>',
      }[s.status] || s.status;

      tBody.innerHTML += `
        <tr>
          <td><strong>${s.id}</strong></td>
          <td>${s.village}</td>
          <td>${s.depth_mbgl}</td>
          <td>${s.ph}</td>
          <td>${s.tds_mg_l}</td>
          <td>${s.nitrate_mg_l} mg/L</td>
          <td>${badge}</td>
          <td>${timeSince(new Date(s.last_updated))}</td>
        </tr>`;
    });
  }

  // ── monitoring page table ──
  const monTbody = document.querySelector("#page-monitoring .table-section tbody");
  if (monTbody) {
    monTbody.innerHTML = "";
    data.stations.forEach(s => {
      const badge = {
        safe:     '<span class="status-badge status-safe">✅ Safe</span>',
        moderate: '<span class="status-badge status-warning">⚠️ Moderate</span>',
        critical: '<span class="status-badge status-critical">🚨 Critical</span>',
      }[s.status] || s.status;
      monTbody.innerHTML += `
        <tr>
          <td><strong>${s.id}</strong></td>
          <td>${s.village}</td>
          <td>${s.district}</td>
          <td>${s.depth_mbgl}</td>
          <td>${s.ph}</td>
          <td>${s.tds_mg_l}</td>
          <td>${badge}</td>
          <td>${s.bore_well_advisory}</td>
          <td>${timeSince(new Date(s.last_updated))}</td>
        </tr>`;
    });
  }

  // ── metric cards update with first station ──
  if (data.stations.length > 0) updateDashboardCards(data.stations[0]);

  // ── footer sync timestamp ──
  const syncEl = document.querySelector(".footer-bottom strong");
  if (syncEl) {
    const now = new Date();
    syncEl.textContent = now.toLocaleDateString("en-IN", { day:"2-digit", month:"short", year:"numeric" })
      + " – " + now.toLocaleTimeString("en-IN", { hour:"2-digit", minute:"2-digit" }) + " IST";
  }
}

function updateDashboardCards(s) {
  const cards = document.querySelectorAll("#page-dashboard .dash-card");
  if (!cards.length) return;
  const set = (card, val) => {
    const v = card?.querySelector(".card-value");
    if (v) v.textContent = val;
  };
  set(cards[0], s.depth_mbgl);   // water level
  set(cards[3], s.ph);           // pH
  set(cards[4], s.ec_ds_m);      // EC
  const unit6 = cards[5]?.querySelector(".card-unit");
  if (unit6) unit6.textContent = `${s.village} – Station #${s.id}`;
}

// ═══════════════════════════════════════════════════════════════
// 2. CHART — water level trend
// ═══════════════════════════════════════════════════════════════
async function loadWaterTrend(stationId = "KA-047", range = "30d") {
  const data = await apiFetch(`/water-trend?station_id=${stationId}&range=${range}`);
  if (!data) return;

  const readings  = data.trend.this_year;
  const lastYear  = data.trend.last_year;

  const mapY = (d) => Math.max(20, Math.min(180,
    Math.round(20 + ((d - 4) / (12 - 4)) * 160)
  ));

  const svgWidth = 620;
  const step     = svgWidth / Math.max(readings.length - 1, 1);

  const toPoints = (arr) =>
    arr.map((r, i) => `${Math.round(60 + i * step)},${mapY(r.depth_mbgl)}`).join(" ");

  const svg = document.querySelector(".chart-svg");
  if (!svg) return;

  const lines = svg.querySelectorAll("polyline");
  if (lines.length >= 2) {
    lines[0].setAttribute("points", toPoints(lastYear));
    lines[1].setAttribute("points", toPoints(readings));
  }

  const dot = svg.querySelector("circle:last-of-type");
  if (dot && readings.length) {
    const last = readings[readings.length - 1];
    dot.setAttribute("cx", Math.round(60 + (readings.length - 1) * step));
    dot.setAttribute("cy", mapY(last.depth_mbgl));
  }

  const xLabels = svg.querySelectorAll("text[y='198']");
  if (xLabels.length >= 3 && readings.length) {
    xLabels[0].textContent = readings[0].date.slice(5);
    xLabels[Math.floor(xLabels.length / 2)].textContent =
      readings[Math.floor(readings.length / 2)].date.slice(5);
    xLabels[xLabels.length - 1].textContent = "Today";
  }
}

// ═══════════════════════════════════════════════════════════════
// 3. ALERTS PAGE
// ═══════════════════════════════════════════════════════════════
async function loadAlerts(district = "") {
  const container = document.querySelector("#page-alerts .advisory-grid");
  if (!container) return;

  container.innerHTML = `
    <div style="grid-column:1/-1;text-align:center;padding:30px;color:#888">
      ⏳ Loading alerts...
    </div>`;

  const params = district ? `?district=${encodeURIComponent(district)}` : "";
  const data   = await apiFetch("/alerts" + params);
  if (!data) return;

  const colorMap = {
    critical: { border:"#c0392b", bg:"#fce4ec", color:"#c62828", dot:"🔴", icon:"🚨" },
    warning:  { border:"#e67e22", bg:"#fff3e0", color:"#e65100", dot:"🟡", icon:"⚠️" },
    info:     { border:"#27ae60", bg:"#e8f5e9", color:"#2e7d32", dot:"🟢", icon:"✅" },
  };

  container.innerHTML = "";
  data.alerts.forEach(a => {
    const c = colorMap[a.severity] || colorMap.info;
    container.innerHTML += `
      <div class="advisory-card" style="border-top-color:${c.border}">
        <div class="adv-icon">${c.icon}</div>
        <h4>${a.title}</h4>
        <p>${a.message}</p>
        <span class="adv-badge" style="background:${c.bg};color:${c.color}">
          ${c.dot} Issued: ${a.issued_date}
        </span>
      </div>`;
  });

  if (data.alerts.length === 0) {
    container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:#888">
      ✅ No active alerts for this area.
    </div>`;
  }

  const critical = data.alerts.find(a => a.severity === "critical");
  if (critical) {
    const alertTextEl = document.getElementById("alertText");
    if (alertTextEl) alertTextEl.textContent = critical.message;
  }
}

// ═══════════════════════════════════════════════════════════════
// 4. REPORTS PAGE
// ═══════════════════════════════════════════════════════════════
async function loadReports(district = "") {
  const tbody = document.querySelector("#page-reports tbody");
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:24px;color:#888">
    ⏳ Loading reports...
  </td></tr>`;

  const params = district ? `?district=${encodeURIComponent(district)}` : "";
  const data   = await apiFetch("/reports" + params);
  if (!data) return;

  tbody.innerHTML = "";
  data.reports.forEach(r => {
    tbody.innerHTML += `
      <tr>
        <td>${r.name}</td>
        <td>${r.district}</td>
        <td>${r.period}</td>
        <td>${r.format}</td>
        <td>
          <button class="btn-primary" style="padding:6px 14px;font-size:.75rem"
            onclick="showToast('⬇️ Downloading: ${r.name.replace(/'/g,"")}')">
            ⬇ Download
          </button>
        </td>
      </tr>`;
  });
}

// ═══════════════════════════════════════════════════════════════
// 5. ADVISORY PAGE
// ═══════════════════════════════════════════════════════════════
async function loadAdvisory(district = "Bengaluru Rural") {
  const grid = document.querySelector("#page-advisory .advisory-grid");
  if (!grid) return;

  grid.innerHTML = `
    <div style="grid-column:1/-1;text-align:center;padding:40px;color:#888">
      ⏳ Loading advisory...
    </div>`;

  const data = await apiFetch(`/advisory?district=${encodeURIComponent(district)}`);
  if (!data) return;

  const bgMap    = { blue:"#e3f2fd", wheat:"#fff9c4", green:"#e8f5e9", red:"#fce4ec" };
  const colorMap = { blue:"#1565c0", wheat:"#f57f17", green:"#27ae60", red:"#c62828" };
  const classMap = { blue:"blue", wheat:"wheat", green:"", red:"" };

  grid.innerHTML = "";
  data.advisory.forEach(adv => {
    const cc = adv.badge_color || "green";
    grid.innerHTML += `
      <div class="advisory-card ${classMap[cc] || ""}">
        <div class="adv-icon">${adv.icon}</div>
        <h4>${adv.title}</h4>
        <p>${adv.body}</p>
        <span class="adv-badge"
          style="background:${bgMap[cc]||"#e8f5e9"};color:${colorMap[cc]||"#27ae60"}">
          ${adv.badge}
        </span>
      </div>`;
  });
}

// ═══════════════════════════════════════════════════════════════
// 6. MONITORING — live station table + filter wiring
// ═══════════════════════════════════════════════════════════════
function ensureMonitoringTable() {
  const mon = document.getElementById("page-monitoring");
  if (!mon) return;
  if (mon.querySelector(".table-section")) return;

  const mc = mon.querySelector(".main-content");
  if (!mc) return;

  mc.insertAdjacentHTML("beforeend", `
    <div class="table-section" style="margin-top:20px;">
      <table>
        <thead>
          <tr>
            <th>Station ID</th><th>Village</th><th>District</th>
            <th>Depth (mbgl)</th><th>pH</th><th>TDS (mg/L)</th>
            <th>Status</th><th>Bore-well Advisory</th><th>Updated</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>`);
}

function wireMonitoringFilters() {
  const mon = document.getElementById("page-monitoring");
  if (!mon || mon.dataset.wired) return;
  mon.dataset.wired = "1";

  ensureMonitoringTable();

  const selects = mon.querySelectorAll(".filter-select");
  const [stateSelect, districtSelect, statusSelect] = selects;
  if (!stateSelect) return;

  stateSelect.addEventListener("change", async () => {
    const state = stateSelect.value;
    if (!state) return;
    const data = await apiFetch(`/districts?state=${encodeURIComponent(state)}`);
    if (!data) return;
    if (districtSelect) {
      districtSelect.innerHTML = '<option value="">All Districts</option>';
      data.districts.forEach(d => {
        const o = document.createElement("option");
        o.textContent = d;
        districtSelect.appendChild(o);
      });
    }
    applyMonitoringFilters();
  });

  if (districtSelect) districtSelect.addEventListener("change", applyMonitoringFilters);
  if (statusSelect)   statusSelect.addEventListener("change",   applyMonitoringFilters);
}

function applyMonitoringFilters() {
  const mon = document.getElementById("page-monitoring");
  if (!mon) return;
  const [stateSelect, districtSelect, statusSelect] = mon.querySelectorAll(".filter-select");
  const filters = {};
  if (stateSelect?.value)    filters.state    = stateSelect.value;
  if (districtSelect?.value) filters.district = districtSelect.value;
  if (statusSelect?.value && statusSelect.value !== "All Stations") {
    filters.status = statusSelect.value.toLowerCase().replace(" only","").trim();
  }
  loadStations(filters);
}

// ═══════════════════════════════════════════════════════════════
// 7. OTP — send via backend (REGISTRATION)
// ═══════════════════════════════════════════════════════════════
async function sendOTP() {
  const phoneEl = document.getElementById("regPhone");
  const phone   = phoneEl?.value || "";

  if (phone.replace(/\D/g,"").length < 10) {
    showToast("⚠️ Enter a valid 10-digit mobile number");
    return;
  }

  const data = await apiFetch("/send-otp", {
    method: "POST",
    body:   JSON.stringify({ mobile: phone }),
  });
  if (!data) return;

  const otpSec = document.getElementById("otpSection");
  if (otpSec) otpSec.style.display = "block";
  showToast("📱 " + data.message);
}

// ═══════════════════════════════════════════════════════════════
// 7b. OTP — send via backend (LOGIN)
// ═══════════════════════════════════════════════════════════════
async function sendLoginOTP() {
  const phoneEl = document.getElementById("loginPhone");
  const phone   = phoneEl?.value || "";

  if (phone.replace(/\D/g,"").length < 10) {
    showToast("⚠️ Enter a valid 10-digit mobile number");
    return;
  }

  const data = await apiFetch("/send-otp", {
    method: "POST",
    body:   JSON.stringify({ mobile: phone }),
  });
  if (!data) return;

  showToast("📱 " + data.message + " (OTP: 123456 for testing)");
}

// ═══════════════════════════════════════════════════════════════
// 8. LOGIN — submit to backend
//    Supports: mobile+OTP login  (tab 1)
//    The backend checks /api/login with mobile + otp
// ═══════════════════════════════════════════════════════════════
async function submitLogin() {
  const phone = document.getElementById("loginPhone")?.value?.trim() || "";
  const otp   = document.getElementById("loginOtp")?.value?.trim()   || "";

  if (!phone || phone.replace(/\D/g,"").length < 10) {
    showToast("⚠️ Enter your registered mobile number");
    return;
  }
  if (!otp || otp.length < 4) {
    showToast("⚠️ Enter the OTP sent to your mobile");
    return;
  }

  const data = await apiFetch("/login", {
    method: "POST",
    body:   JSON.stringify({ mobile: phone, otp: otp }),
  });
  if (!data) return;

  // Store farmer info in sessionStorage for the session
  try {
    sessionStorage.setItem("jm_farmer_id",   data.farmer_id   || "");
    sessionStorage.setItem("jm_farmer_name", data.farmer_name || "");
    sessionStorage.setItem("jm_logged_in",   "true");
  } catch(e) {}

  closeModal("loginModal");
  showToast("✅ Welcome back, " + (data.farmer_name || "Farmer") + "! | स्वागत है!");

  // Update nav to show logged-in state
  const loginLink = document.querySelector('.nav-inner a[onclick*="loginModal"]');
  if (loginLink) {
    loginLink.textContent = "👤 " + (data.farmer_name || "My Account");
    loginLink.removeAttribute("onclick");
  }
}

// ═══════════════════════════════════════════════════════════════
// 9. REGISTRATION — submit to backend
// ═══════════════════════════════════════════════════════════════
async function submitRegistration() {
  const g = (id) => document.getElementById(id)?.value?.trim() || "";

  const name  = g("regName");
  const phone = g("regPhone");
  const pass  = g("regPass");
  const pass2 = g("regPass2");
  const terms = document.getElementById("termsCheck")?.checked;

  if (!name || !phone) { showToast("⚠️ Name and mobile are required"); return; }
  if (pass && pass !== pass2) { showToast("⚠️ Passwords do not match"); return; }
  if (!terms) { showToast("⚠️ Please accept Terms & Conditions"); return; }

  const payload = {
    fullName:      name,
    fatherName:    document.querySelectorAll("#regForm input[type=text]")[1]?.value || "",
    dob:           g("regDob"),
    gender:        document.querySelector("#regForm select")?.value || "",
    aadhaar:       g("regAadhaar"),
    mobile:        phone,
    state:         document.getElementById("regState")?.value || "",
    district:      document.getElementById("regDistrict")?.value || "",
    taluk:         document.querySelector("#regForm input[placeholder='Your Taluk']")?.value || "",
    village:       document.querySelector("#regForm input[placeholder='Village name']")?.value || "",
    pincode:       document.querySelector("#regForm input[placeholder='6-digit pincode']")?.value || "",
    landAcres:     parseFloat(document.querySelector("#regForm input[type=number]")?.value) || 0,
    waterSource:   document.querySelectorAll("#regForm select")[2]?.value || "",
    crops:         document.querySelector("#regForm input[placeholder*='Rice']")?.value || "",
    boreDepth:     parseFloat(document.querySelectorAll("#regForm input[type=number]")[1]?.value) || 0,
    alertLanguage: document.querySelectorAll("#regForm select")[3]?.value || "English",
    password:      pass,
  };

  const data = await apiFetch("/register", {
    method: "POST",
    body:   JSON.stringify(payload),
  });
  if (!data) return;

  document.getElementById("regForm").style.display = "none";
  const success = document.getElementById("regSuccess");
  if (success) {
    success.style.display = "block";
    const h4 = success.querySelector("h4");
    const p  = success.querySelector("p");
    if (h4) h4.textContent = "Registration Successful! 🎉";
    if (p)  p.innerHTML = data.message + "<br><br><strong>Your Farmer ID:</strong> " +
      (data.farmer_id || "—");
  }
}

// ═══════════════════════════════════════════════════════════════
// 10. DISTRICT DROPDOWN — state → district
// ═══════════════════════════════════════════════════════════════
async function updateDistricts() {
  const state = document.getElementById("regState")?.value;
  if (!state) return;

  const data = await apiFetch(`/districts?state=${encodeURIComponent(state)}`);
  const sel  = document.getElementById("regDistrict");
  if (!data || !sel) return;

  sel.innerHTML = '<option>Select District</option>';
  data.districts.forEach(d => {
    const o = document.createElement("option");
    o.textContent = d;
    sel.appendChild(o);
  });
}

// ═══════════════════════════════════════════════════════════════
// 11. REPORT ISSUE MODAL
// ═══════════════════════════════════════════════════════════════
async function submitIssueReport() {
  const issueType   = document.querySelector("#reportModal select")?.value || "";
  const village     = document.querySelector("#reportModal input[type=text]")?.value || "";
  const description = document.querySelector("#reportModal textarea")?.value || "";
  const mobile      = document.querySelector("#reportModal input[type=tel]")?.value || "";

  if (!village || !mobile) {
    showToast("⚠️ Village and mobile number are required");
    return;
  }

  const data = await apiFetch("/report-issue", {
    method: "POST",
    body:   JSON.stringify({ issueType, village, description, mobile }),
  });
  if (!data) return;

  closeModal("reportModal");
  showToast("✅ " + data.message);
}

// ═══════════════════════════════════════════════════════════════
// 12. SMS SUBSCRIBE MODAL
// ═══════════════════════════════════════════════════════════════
async function submitSmsSubscription() {
  const mobile   = document.querySelector("#smsModal input[type=tel]")?.value || "";
  const language = document.querySelectorAll("#smsModal select")[0]?.value || "English";
  const frequency= document.querySelectorAll("#smsModal select")[1]?.value || "Weekly Summary";

  if (!mobile || mobile.replace(/\D/g,"").length < 10) {
    showToast("⚠️ Enter a valid 10-digit mobile number");
    return;
  }

  const data = await apiFetch("/subscribe-sms", {
    method: "POST",
    body:   JSON.stringify({ mobile, language, frequency }),
  });
  if (!data) return;

  closeModal("smsModal");
  showToast("✅ " + data.message);
}

// ═══════════════════════════════════════════════════════════════
// 13. UTILITY — time since
// ═══════════════════════════════════════════════════════════════
function timeSince(date) {
  const s = Math.floor((new Date() - date) / 1000);
  if (s < 60)    return s + " sec ago";
  if (s < 3600)  return Math.floor(s / 60) + " min ago";
  if (s < 86400) return Math.floor(s / 3600) + " hr ago";
  return Math.floor(s / 86400) + " days ago";
}

// ═══════════════════════════════════════════════════════════════
// 14. PAGE ROUTER — patches into existing showPage safely
// ═══════════════════════════════════════════════════════════════
(function patchShowPage() {
  const _orig = window.showPage;

  window.showPage = function(page, link) {
    if (typeof _orig === "function") _orig(page, link);

    if (page === "dashboard")  { loadStations(); loadWaterTrend(); }
    if (page === "monitoring") { ensureMonitoringTable(); loadStations(); wireMonitoringFilters(); }
    if (page === "advisory")   { loadAdvisory(); }
    if (page === "reports")    { loadReports(); }
    if (page === "alerts")     { loadAlerts(); }
  };
})();

// ═══════════════════════════════════════════════════════════════
// 15. AUTO-REFRESH every 5 minutes
// ═══════════════════════════════════════════════════════════════
function startAutoRefresh() {
  setInterval(() => {
    const active = document.querySelector(".page-section.active");
    if (!active) return;
    const id = active.id.replace("page-", "");
    if (id === "dashboard")  { loadStations(); loadWaterTrend(); }
    if (id === "monitoring") { loadStations(); }
    if (id === "alerts")     { loadAlerts(); }
  }, 5 * 60 * 1000);
}

// ═══════════════════════════════════════════════════════════════
// 16. INIT — runs once DOM is ready
// ═══════════════════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  console.log("🌊 DWLR API Connector v3 ready →", API_BASE);

  // Load initial dashboard data
  loadStations();
  loadWaterTrend();

  // Pre-wire monitoring filters
  wireMonitoringFilters();

  // Start auto-refresh
  startAutoRefresh();

  // ── Fix modal close buttons (safety net in case onclick wasn't updated) ──
  const reportCloseBtn = document.querySelector("#reportModal .modal-close");
  if (reportCloseBtn) reportCloseBtn.onclick = () => closeModal("reportModal");

  const smsCloseBtn = document.querySelector("#smsModal .modal-close");
  if (smsCloseBtn) smsCloseBtn.onclick = () => closeModal("smsModal");

  const loginCloseBtn = document.querySelector("#loginModal .modal-close");
  if (loginCloseBtn) loginCloseBtn.onclick = () => closeModal("loginModal");

  // ── Fix modal submit buttons (safety net) ──
  const reportSubmitBtn = document.querySelector("#reportModal .btn-submit");
  if (reportSubmitBtn) reportSubmitBtn.onclick = submitIssueReport;

  const smsSubmitBtn = document.querySelector("#smsModal .btn-submit");
  if (smsSubmitBtn) smsSubmitBtn.onclick = submitSmsSubscription;

  const loginSubmitBtn = document.querySelector("#loginModal .btn-submit");
  if (loginSubmitBtn) loginSubmitBtn.onclick = submitLogin;

  console.log("✅ All API hooks wired. Login, Registration, Report, SMS — all connected to backend.");
  console.log("ℹ️  Using API:", API_BASE);
});
