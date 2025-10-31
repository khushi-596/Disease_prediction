import React from "react";

export default function RiskCard({ title, value, level, recommendation }) {
  const levelColor = {
    Low: "bg-green-100 text-green-800",
    Medium: "bg-yellow-100 text-yellow-800",
    High: "bg-red-100 text-red-800"
  };

  return (
    <div className="p-4 rounded-lg shadow-md bg-white border border-gray-200 max-w-md">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-xl font-bold mb-1">{value}</p>
      <span className={`px-2 py-1 rounded-full text-sm font-semibold ${levelColor[level] || "bg-gray-100 text-gray-800"}`}>
        {level}
      </span>
      {recommendation && <p className="mt-2 text-gray-600">{recommendation}</p>}
    </div>
  );
}
