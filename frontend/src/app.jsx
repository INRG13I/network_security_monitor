import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Topology from './components/Topology';
import Sidebar from './components/Sidebar';
import DevicePage from './components/DevicePage';
import './App.css';
import axios from 'axios';

function MenuButton({ onTrigger, onRefresh }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleExport = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/devices/export");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "network_data.json";
      a.click();
    } catch (err) {
      alert("Export failed.");
      console.error("Export error:", err);
    }
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("http://localhost:8000/api/devices/import", {
        method: "POST",
        body: formData,
      });
      const result = await res.json();
      alert(`Imported ${result.imported || 0} devices.`);
      if (onRefresh) {
        onRefresh();
      }
    } catch (err) {
      alert("Import failed.");
      console.error("Import error:", err);
    }
  };

  return (
    <div>
      <button
        onClick={() => setMenuOpen(prev => !prev)}
        className="absolute top-4 right-4 z-50 bg-gray-800 text-white border border-gray-600 rounded px-3 py-1 shadow"
      >
        ☰
      </button>
      {menuOpen && (
        <div className="absolute top-14 right-4 z-50 bg-gray-900 text-white border border-gray-700 rounded shadow p-2">
          <ul className="text-sm space-y-1">
            <li>
              <button
                onClick={() => {
                  onTrigger();
                  setMenuOpen(false);
                }}
                className="hover:underline"
              >
                Run ARP Scan
              </button>
            </li>
            <li>
              <button onClick={handleExport} className="hover:underline">
                Export Network Data
              </button>
            </li>
            <li>
              <label className="hover:underline cursor-pointer">
                Import Network Data
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImport}
                  className="hidden"
                />
              </label>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}

function App() {
  const location = useLocation();
  const [devices, setDevices] = useState([]);

  const refreshDevices = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/devices');
      setDevices(res.data.devices || []);
    } catch (err) {
      console.error("Failed to refresh devices:", err);
    }
  };

  useEffect(() => {
    refreshDevices();
  }, []);

  useEffect(() => {
    if (location.pathname === '/') {
      refreshDevices();
    }
  }, [location]);

  const triggerArpScan = async () => {
    try {
      const res = await axios.post('http://localhost:8000/api/devices/scan');
      setDevices(res.data.devices || []);
      alert('ARP scan completed.');
    } catch (err) {
      console.error('ARP scan failed:', err);
      alert('ARP scan failed.');
    }
  };

  const showMenu = location.pathname === '/';

  return (
    <div className="h-screen w-screen bg-gray-100 flex relative">
      {showMenu && <MenuButton onTrigger={triggerArpScan} onRefresh={refreshDevices} />}
      <Routes>
        <Route path="/" element={
          <>
            <Sidebar devices={devices} />
            <main className="flex-grow overflow-hidden">
              <Topology devices={devices} />
            </main>
          </>
        } />
        <Route path="/device/:ip" element={<DevicePage onTypeChange={refreshDevices} />} />
      </Routes>
    </div>
  );
}

export default App;
