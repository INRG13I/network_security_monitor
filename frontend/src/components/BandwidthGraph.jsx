import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Legend,
  Tooltip,
  CategoryScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(LineElement, PointElement, LinearScale, TimeScale, Legend, Tooltip, CategoryScale);

function BandwidthGraph({ ip, mac }) {
  const [dataPoints, setDataPoints] = useState([]);
  const intervalRef = useRef(null);

  useEffect(() => {
    const fetchBandwidth = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/devices/${ip}/bandwidth?mac=${mac}`
        );
        const { in_kbps, out_kbps } = response.data;

        setDataPoints(prev => [
          ...prev.slice(-59),
          {
            time: new Date(),
            in_kbps,
            out_kbps,
          },
        ]);
      } catch (err) {
        console.error('Error fetching bandwidth: ', err);
      }
    };

    intervalRef.current = setInterval(fetchBandwidth, 1000);
    return () => clearInterval(intervalRef.current);
  }, [ip, mac]);

  const chartData = {
    labels: dataPoints.map(dp => dp.time),
    datasets: [
      {
        label: 'Inbound (Kbps)',
        data: dataPoints.map(dp => dp.in_kbps),
        borderColor: 'lightgreen',
        backgroundColor: 'rgba(144, 238, 144, 0.2)',
        tension: 0.2,
      },
      {
        label: 'Outbound (Kbps)',
        data: dataPoints.map(dp => dp.out_kbps),
        borderColor: 'lightblue',
        backgroundColor: 'rgba(173, 216, 230, 0.2)',
        tension: 0.2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'second',
          tooltipFormat: 'HH:mm:ss',
        },
        ticks: {
          color: '#aaa',
        },
        grid: {
          color: '#444',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Kbps',
          color: '#ccc',
        },
        ticks: {
          color: '#aaa',
        },
        grid: {
          color: '#444',
        },
      },
    },
    plugins: {
      legend: {
        labels: {
          color: '#ddd',
        },
      },
      tooltip: {
        bodyColor: '#fff',
        backgroundColor: '#333',
        borderColor: '#666',
        borderWidth: 1,
      },
    },
  };

  return (
    <div className="w-full h-full bg-gray-800 p-4 shadow rounded border border-gray-700">
      <h2 className="font-bold text-xl mb-4 text-white">Bandwidth Usage</h2>
      <div style={{ height: '300px' }}>
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}

export default BandwidthGraph;
