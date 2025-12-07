import React from 'react';

const FlowTable = ({ detections }) => {
  const recentFlows = detections.slice(0, 20);

  return (
    <div className="flow-table card">
      <h2>Network Flows</h2>
      <div className="table-container">
        {recentFlows.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Source</th>
                <th>Destination</th>
                <th>Protocol</th>
                <th>Packets</th>
                <th>Prediction</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {recentFlows.map((flow, index) => (
                <tr key={index}>
                  <td>{new Date(flow.timestamp).toLocaleTimeString()}</td>
                  <td>{flow.src_ip}:{flow.src_port}</td>
                  <td>{flow.dst_ip}:{flow.dst_port}</td>
                  <td>{flow.protocol}</td>
                  <td>{flow.packet_count}</td>
                  <td className={flow.is_attack ? 'attack' : 'benign'}>
                    {flow.prediction}
                  </td>
                  <td>{(flow.confidence * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="table-placeholder">
            <p>No flows to display</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlowTable;
