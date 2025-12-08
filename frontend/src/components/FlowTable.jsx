import React from 'react';

const FlowTable = ({ detections }) => {
  const recentFlows = detections.slice(0, 50); // Increased to 50 for better view

  return (
    <div className="flow-table card">
      <div className="card-header">
        <h2>🔍 Network Flows</h2>
        <p className="card-subtitle">
          Detailed view of recent network flows • Showing {recentFlows.length} flows from last 5 minutes
        </p>
      </div>
      
      <div className="table-container">
        {recentFlows.length > 0 ? (
          <table className="modern-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Source</th>
                <th>Destination</th>
                <th>Protocol</th>
                <th>Packets</th>
                <th>Bytes</th>
                <th>Classification</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {recentFlows.map((flow, index) => (
                <tr key={flow.flow_id || index} className={flow.is_attack ? 'row-attack' : 'row-benign'}>
                  <td className="td-time">{new Date(flow.timestamp).toLocaleTimeString()}</td>
                  <td className="td-endpoint">{flow.src_ip}:{flow.src_port}</td>
                  <td className="td-endpoint">{flow.dst_ip}:{flow.dst_port}</td>
                  <td className="td-protocol">
                    <span className="protocol-badge">{flow.protocol}</span>
                  </td>
                  <td className="td-count">{flow.packet_count}</td>
                  <td className="td-count">{(flow.byte_count / 1024).toFixed(2)} KB</td>
                  <td className="td-prediction">
                    <span className={`prediction-badge ${flow.is_attack ? 'badge-attack' : 'badge-benign'}`}>
                      {flow.is_attack ? '🚨' : '✅'} {flow.prediction}
                    </span>
                  </td>
                  <td className="td-confidence">
                    <div className="confidence-bar-wrapper">
                      <div 
                        className="confidence-bar" 
                        style={{ 
                          width: `${flow.confidence * 100}%`,
                          backgroundColor: flow.is_attack ? '#dc3545' : '#198754'
                        }}
                      />
                      <span className="confidence-text">{(flow.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">📊</div>
            <div className="empty-state-text">No network flows to display</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlowTable;
