/**
 * Flow Table Component - Table of recent network flows
 */
import React from 'react';

const FlowTable = ({ flows }) => {
  return (
    <div className="flow-table-container">
      <h2>Recent Network Flows</h2>
      {flows.length === 0 ? (
        <p className="no-data">No flows captured yet</p>
      ) : (
        <table className="flow-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Source</th>
              <th>Destination</th>
              <th>Protocol</th>
              <th>Classification</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {flows.slice(0, 50).map((flow, index) => (
              <tr key={index} className={flow.type === 'Benign' ? 'benign-row' : 'attack-row'}>
                <td>{new Date(flow.timestamp * 1000).toLocaleTimeString()}</td>
                <td>{flow.source_ip}:{flow.source_port}</td>
                <td>{flow.dest_ip}:{flow.dest_port}</td>
                <td>{flow.protocol}</td>
                <td>
                  <span className={flow.type === 'Benign' ? 'badge-benign' : 'badge-attack'}>
                    {flow.type}
                  </span>
                </td>
                <td>{(flow.confidence * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default FlowTable;

