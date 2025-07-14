import React, { useEffect, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import './Topology.css';
import axios from 'axios';

const CustomNode = ({ data }) => (
  <div className={`custom-node ${data.status ? 'online-node' : 'offline-node'}`}>
    <Handle type="target" position={Position.Top} id="t" />
    <Handle type="target" position={Position.Left} id="l" />
    <img src={data.icon} alt="Device Icon" className="device-icon" draggable={false} />
    <div className="device-name">{data.name}</div>
    <div className="device-ip">{data.ip}</div>
    <Handle type="source" position={Position.Right} id="r" />
    <Handle type="source" position={Position.Bottom} id="b" />
  </div>
);

const nodeTypes = { custom: CustomNode };

const typeToIcon = {
  router: '/icons/router.png',
  switch: '/icons/switch.png',
  computer: '/icons/computer.png',
  lan: '/icons/generic.png',
};

const Topology = ({ devices }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [cidrBlock, setCidrBlock] = useState('');

  useEffect(() => {
    // Fetch CIDR block from backend
    axios.get('http://localhost:8000/api/devices/cidr')
      .then((res) => setCidrBlock(res.data.cidr || ''))
      .catch((err) => {
        console.error('Failed to fetch CIDR block:', err);
        setCidrBlock('Unknown');
      });
  }, []);

  useEffect(() => {
    if (!devices || devices.length === 0) return;

    const newNodes = devices.map((device, index) => {
      const normalizedType = (device.type || '').toLowerCase();
      return {
        id: device.id || `${index + 1}`,
        type: 'custom',
        position: { x: 150 * index, y: 150 },
        data: {
          name: `Device ${index + 1}`,
          ip: device.ip,
          icon: typeToIcon[normalizedType] || typeToIcon['lan'],
          status: device.device_status,
        },
      };
    });

    setNodes(newNodes);
    setEdges([]);
  }, [devices]);

  const onConnect = (params) => {
    setEdges((eds) => addEdge({ ...params }, eds));
  };

  return (
    <div className="relative h-full w-full bg-gray-900">
      {/* CIDR Display */}
      <div className="absolute top-2 left-4 z-50 text-white bg-gray-800 px-3 py-1 rounded shadow text-sm">
        CIDR: {cidrBlock}
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        nodesDraggable
        nodesConnectable
        elementsSelectable
        panOnDrag
      >
        <Background gap={20} size={1} color="#444" />
        <Controls className="custom-controls" />
      </ReactFlow>
    </div>
  );
};

export default Topology;
