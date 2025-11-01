const BASE_URL =
  window.location.hostname.includes("onrender.com")
    ? "https://indradhanu.onrender.com"
    : "http://127.0.0.1:8000";

/* ============================
   CITIZEN FORM HANDLER
============================ */
document.getElementById("citizenForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const ward = document.getElementById("Ward").value;
  const date = document.getElementById("Date").value;

  if (!ward || !date) {
    alert("Please select both ward and date!");
    return;
  }

  const payload = {
    Temp: 30,
    Humidity: 70,
    Rainfall: 12,
    Wqi: 65,
    Ph: 7.1,
    Turbidity: 3.4,
    Cases_Lag1: 4,
    Cases_7d_Avg: 6,
    Rain_3d_Avg: 10
  };

  try {
    const response = await fetch(`${BASE_URL}/predict_rf/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await response.json();
    const riskLevel = result.risk_level || "UNKNOWN";

    const resultBox = document.getElementById("result");
    resultBox.textContent = `⚠️ Risk in ${ward} on ${date}: ${riskLevel}`;
    resultBox.className = `result-box ${riskLevel.toLowerCase()}`;

    const tips = document.getElementById("tips");
    tips.innerHTML = "";

    if (riskLevel === "LOW") {
      tips.innerHTML = `
        <li>✅ Risk is low. Continue healthy habits.</li>
        <li>Maintain cleanliness around your home.</li>`;
    } else if (riskLevel === "MEDIUM") {
      tips.innerHTML = `
        <li>⚠️ Moderate risk in ${ward}. Drink clean water and use repellents.</li>
        <li>Stay alert for fever or chills.</li>`;
    } else if (riskLevel === "HIGH") {
      tips.innerHTML = `
        <li>🚨 High risk in ${ward}!</li>
        <li>Visit your nearest health center if you feel unwell.</li>
        <li>Follow preventive advisories.</li>`;
    } else {
      tips.innerHTML = `<li>❌ Unable to fetch risk level. Try again later.</li>`;
    }
  } catch (err) {
    document.getElementById("result").textContent =
      "❌ Server unreachable or backend offline.";
    console.error(err);
  }
});

/* ============================
   ADMIN DASHBOARD FUNCTIONS
============================ */
async function loadWardAnalytics() {
  const content = document.getElementById("admin-content");
  try {
    const res = await fetch(`${BASE_URL}/admin_summary`);
    if (!res.ok) throw new Error("Summary not found");
    const data = await res.json();

    content.innerHTML = `
      <h3>📊 Ward Analytics Summary</h3>
      <table>
        <tr><th>Ward</th><th>Cases</th><th>Rainfall</th><th>Temp</th><th>Humidity</th><th>WQI</th><th>Risk</th></tr>
        ${data.wards
          .map(
            (w) => `
            <tr>
              <td>${w.ward}</td>
              <td>${w.reported_cases}</td>
              <td>${w.rainfall}</td>
              <td>${w.temp}</td>
              <td>${w.humidity}</td>
              <td>${w.wqi}</td>
              <td class="${w.risk_level.toLowerCase()}">${w.risk_level}</td>
            </tr>`
          )
          .join("")}
      </table>`;
  } catch (err) {
    content.innerHTML = `<p>❌ Unable to load analytics: ${err.message}</p>`;
  }
}


async function loadAIPrediction() {
  const container = document.getElementById("admin-content");
  container.innerHTML = "🤖 Running AI prediction...";
  try {
    const response = await fetch(`${BASE_URL}/admin/predict_all`);
    if (!response.ok) throw new Error("Prediction failed");
    const data = await response.json();

    let html = "<h3>AI Predictions</h3><ul>";
    data.forEach((item) => {
      html += `<li>${item.ward}: ${item.prediction}</li>`;
    });
    html += "</ul>";
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = "❌ Unable to load AI predictions.";
    console.error(err);
  }
}

function showHealthTips() {
  const container = document.getElementById("admin-content");
  container.innerHTML = `
    <h3>💬 Health Tips</h3>
    <ul>
      <li>💧 Drink boiled or filtered water.</li>
      <li>🧴 Use mosquito repellents regularly.</li>
      <li>🥗 Maintain hygiene in food preparation.</li>
      <li>🏠 Keep your surroundings clean and dry.</li>
    </ul>
  `;
}
