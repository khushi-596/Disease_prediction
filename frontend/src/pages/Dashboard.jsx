import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import 'chart.js/auto';
import RiskCard from "../components/RiskCard";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [ward, setWard] = useState("Ward-1");
  const [last7, setLast7] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${API}/data?n=200`);
        setData(res.data);

        const wardRows = res.data.filter(r => r.ward === ward).slice(-14);
        setLast7(wardRows.map(r => r.reported_cases).slice(-7));
      } catch (err) {
        console.error("Failed to fetch data:", err);
      }
    };
    fetchData();
  }, [ward]);

  const wards = [...new Set(data.map(d => d.ward))].slice(0, 20);

  const handleWardChange = (e) => {
    setWard(e.target.value);
    const wardRows = data.filter(r => r.ward === e.target.value).slice(-14);
    setLast7(wardRows.map(r => r.reported_cases).slice(-7));
  };

  const handlePredict = async () => {
    const wardRows = data.filter(r => r.ward === ward).sort((a, b) => new Date(a.date) - new Date(b.date));
    if (!wardRows.length) return alert("No data for this ward!");
    const last = wardRows[wardRows.length - 1];

    const payload = {
      temp: last.temp || 0,
      rainfall: last.rainfall || 0,
      wqi: last.wqi || 0,
      cases_lag1: last.cases_lag1 || 0,
      cases_7d_avg: last.cases_7d_avg || 0,
      last_7_cases: last7.length ? last7 : Array(7).fill(0)
    };

    try {
      setLoading(true);
      const res = await axios.post(`${API}/predict`, payload);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: data.filter(d => d.ward === ward).map(d => d.date),
    datasets: [{
      label: "Reported cases",
      data: data.filter(d => d.ward === ward).map(d => d.reported_cases),
      tension: 0.3,
      borderColor: "#3B82F6",
      backgroundColor: "rgba(59, 130, 246, 0.2)"
    }]
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>

      <div className="flex flex-wrap gap-4 items-center">
        <select value={ward} onChange={handleWardChange} className="border p-2 rounded">
          {wards.map(w => <option key={w} value={w}>{w}</option>)}
        </select>
        <button onClick={handlePredict} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500">
          {loading ? "Predicting..." : "Predict Risk"}
        </button>
        <button onClick={async()=>{ await axios.post(`${API}/alert?ward=${ward}&message=Demo alert`); alert("Demo alert triggered") }} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-500">
          Trigger Demo Alert
        </button>
      </div>

      <div className="bg-white p-4 rounded shadow">
        <Line data={chartData} />
      </div>

      {result && (
        <RiskCard 
          title="Next-day Prediction" 
          value={result.predicted_cases?.toFixed(2)} 
          level={result.level} 
          recommendation={result.recommendation} 
        />
      )}
    </div>
  );
}
