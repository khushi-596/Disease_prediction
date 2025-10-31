const BASE_URL = "https://indradhanu-backend.onrender.com";

document.getElementById("predictForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    Temp: parseFloat(Temp.value),
    Humidity: parseFloat(Humidity.value),
    Rainfall: parseFloat(Rainfall.value),
    Wqi: parseFloat(Wqi.value),
    Ph: parseFloat(Ph.value),
    Turbidity: parseFloat(Turbidity.value),
    Cases_Lag1: parseFloat(Cases_Lag1.value),
    Cases_7d_Avg: parseFloat(Cases_7d_Avg.value),
    Rain_3d_Avg: parseFloat(Rain_3d_Avg.value)
  };
  
  const response = await fetch("/predict_rf/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const result = await response.json();
  document.getElementById("result").textContent =
    `⚠️ Risk Level: ${result.risk_level}`;
});
