import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const TrafficPieChart = () => {
  const data = {
    labels: ['YouTube', 'Facebook', 'Others'],
    datasets: [
      {
        data: [30, 20, 50],
        backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe'],
        borderWidth: 1,
      },
    ],
  };

  const options = {
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
    <div>
      <div className="h-48 mb-4 bg-gray-800 p-2 rounded">
        <Pie data={data} options={options} />
      </div>
      <ul className="text-sm space-y-1 text-white">
        <li className="flex items-center">
          <span className="inline-block w-3 h-3 bg-[#ff6384] rounded-full mr-2"></span>
          YouTube — 30%
        </li>
        <li className="flex items-center">
          <span className="inline-block w-3 h-3 bg-[#36a2eb] rounded-full mr-2"></span>
          Facebook — 20%
        </li>
        <li className="flex items-center">
          <span className="inline-block w-3 h-3 bg-[#cc65fe] rounded-full mr-2"></span>
          Others — 50%
        </li>
      </ul>
    </div>
  );
};

export default TrafficPieChart;
