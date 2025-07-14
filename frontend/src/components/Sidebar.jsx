import React from 'react';
import { Link } from 'react-router-dom';

function Sidebar({ devices }) {
  if (!devices) return null;

  return (
    <aside className="w-1/5 bg-gray-900 text-white p-4 overflow-auto h-screen">
      <h2 className="text-xl font-bold mb-4">Devices</h2>
      {devices.map((device, index) => (
        <Link
          key={index}
          to={`/device/${device.ip}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <div className="relative bg-gray-800 p-3 mb-3 rounded hover:bg-gray-700 transition">
            <span
              className={`absolute top-2 right-2 w-3 h-3 rounded-full ${
                device.device_status ? 'bg-green-500' : 'bg-red-500'
              }`}
              title={device.device_status ? 'Online' : 'Offline'}
            ></span>
            <p className="font-mono text-sm">{device.ip}</p>
            <p className="font-mono text-xs text-gray-400">{device.mac}</p>
          </div>
        </Link>
      ))}
    </aside>
  );
}

export default Sidebar;
