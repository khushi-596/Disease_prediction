import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="text-center mt-20">
      <h1 className="text-4xl font-bold mb-4 text-blue-600">Welcome to Indradhanu</h1>
      <p className="text-gray-700 mb-6">Predict disease risk and visualize reported cases in your wards.</p>
      <Link to="/dashboard" className="px-6 py-3 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-500 transition">Go to Dashboard</Link>
    </div>
  );
}
