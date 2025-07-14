import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import TrafficPieChart from './TrafficPieChart';
import BandwidthGraph from './BandwidthGraph';

function formatUptime(seconds) {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${d}d ${h}h ${m}m ${s}s`;
}

function DevicePage({ onTypeChange }) {
  const { ip } = useParams();
  const [device, setDevice] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [submenuOpen, setSubmenuOpen] = useState(false);

  const fetchDevice = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/devices`);
      const json = await res.json();
      const match = json.devices.find((d) => d.ip === ip);
      setDevice(match);
    } catch (err) {
      console.error('Failed to fetch device:', err);
    }
  };

  useEffect(() => {
    fetchDevice();
  }, [ip]);

  const enrich = async (type) => {
    if (!device) return;
    let url;
    if (type === 'nmap') {
      url = `http://localhost:8000/api/devices/enrich/nmap?ip=${device.ip}`;
    } else if (type === 'snmp') {
      url = `http://localhost:8000/api/devices/enrich/snmp?ip=${device.ip}`;
    } else if (type === 'both') {
      url = `http://localhost:8000/api/devices/enrich/both?ip=${device.ip}`;
    }
    try {
      await fetch(url, { method: 'POST' });
      await fetchDevice();
      alert(`Enrichment (${type}) completed.`);
    } catch (err) {
      alert(`Enrichment failed: ${err.message}`);
    }
  };

  const handleTypeChange = async (tag) => {
    const newType = tag.charAt(0).toUpperCase() + tag.slice(1);
    const confirmed = window.confirm(`Change device type to ${newType}?`);
    if (!confirmed) return;

    try {
      const res = await fetch(`http://localhost:8000/api/devices/${device.ip}/change_type`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_type: newType }),
      });
      if (!res.ok) throw new Error("Type change failed");
      await fetchDevice();
      alert("Device type changed.");

      if (onTypeChange) {
        onTypeChange();
      }
    } catch (err) {
      alert(`Failed to change type: ${err.message}`);
    }
  };

  if (!device) {
    return (
      <div className="flex items-center justify-center h-screen text-xl text-red-500">
        Device not found.
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-gray-900 text-white p-6 space-y-6 relative">
      {/* Menu */}
      <div className="absolute top-4 right-4 z-50">
        <button
          onClick={() => setMenuOpen((prev) => !prev)}
          className="bg-gray-800 border border-gray-600 px-3 py-1 rounded shadow text-sm"
        >
          ☰
        </button>

        {menuOpen && (
          <div className="absolute mt-2 right-0 bg-gray-800 border border-gray-600 rounded shadow text-sm">
            <button
              onClick={() => setSubmenuOpen((prev) => !prev)}
              className="block w-full text-left px-3 py-1 hover:bg-gray-700"
            >
              Enrich
            </button>
            {submenuOpen && (
              <div className="absolute top-0 right-full mr-1 bg-gray-800 border border-gray-600 rounded shadow w-48">
                <button onClick={() => enrich('nmap')} className="block w-full text-left px-3 py-1 hover:bg-gray-700">Nmap</button>
                <button onClick={() => enrich('snmp')} className="block w-full text-left px-3 py-1 hover:bg-gray-700">SNMP</button>
                <button onClick={() => enrich('both')} className="block w-full text-left px-3 py-1 hover:bg-gray-700">Nmap + SNMP</button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex flex-col lg:flex-row gap-6 w-full">
        {/* General Info */}
        <div className="flex-1 border border-gray-700 bg-gray-800 p-4 shadow rounded">
          <h2 className="font-bold mb-2 text-lg text-white">General Info</h2>
          <p><strong>Type:</strong> {device.type}</p>
          <p><strong>IP:</strong> {device.ip}</p>
          <p><strong>MAC:</strong> {device.mac}</p>
          <p><strong>Hostname:</strong> {device.hostname}</p>
          <p><strong>Vendor:</strong> {device.vendor}</p>
          <p><strong>OS:</strong> {device.os}</p>
          <p><strong>Status:</strong> <span className={device.device_status ? "text-green-400" : "text-red-400"}>{device.device_status ? 'Online' : 'Offline'}</span></p>
          <p><strong>Uptime:</strong> {formatUptime(device.device_uptime)}</p>
          <p><strong>SNMP Version:</strong> {device.snmp_version || 'Not Supported'}</p>
          <p className="mt-2"><strong>Tags:</strong></p>
          <ul className="text-sm list-disc ml-5 text-gray-300">
            {device.tags.length ? (
              device.tags.map((tag, i) => {
                const isPromotable = ["Computer", "Switch", "Router"].includes(tag.charAt(0).toUpperCase() + tag.slice(1));
                return (
                  <li
                    key={i}
                    className={`cursor-pointer ${isPromotable ? "text-blue-400 hover:underline" : ""}`}
                    onClick={() => isPromotable && handleTypeChange(tag)}
                  >
                    {tag}
                  </li>
                );
              })
            ) : (
              <li><em>None</em></li>
            )}
          </ul>
        </div>

        {/* Port Table */}
        <div className="flex-1 border border-gray-700 bg-gray-800 p-4 shadow rounded overflow-auto">
          <h2 className="font-bold mb-2 text-lg text-white">Port Table</h2>
          <table className="w-full text-sm text-gray-200">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-600">
                <th className="pr-2">Port</th>
                <th className="pr-2">Protocol</th>
                <th className="pr-2">Status</th>
                <th className="pr-2">Service</th>
                <th className="pr-2">Product</th>
                <th className="pr-2">Version</th>
              </tr>
            </thead>
            <tbody>
              {(device.ports || []).map((port, idx) => (
                <tr key={idx} className="border-t border-gray-700">
                  <td>{port.port}</td>
                  <td>{port.protocol}</td>
                  <td>{port.status}</td>
                  <td>{port.service}</td>
                  <td>{port.product}</td>
                  <td>{port.version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Traffic Breakdown */}
        <div className="border border-gray-700 bg-gray-800 p-4 shadow rounded">
          <h2 className="font-bold mb-2 text-white">Traffic Breakdown</h2>
          <TrafficPieChart />
        </div>
      </div>

      {/* Bandwidth Graph */}
      <div className="w-full">
        <BandwidthGraph ip={device.ip} mac={device.mac} />
      </div>
    </div>
  );
}

export default DevicePage;
