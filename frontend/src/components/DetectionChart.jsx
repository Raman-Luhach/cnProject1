import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

const DetectionChart = ({ timelineData }) => {
  // Separate attack and benign data for different visualization
  const attackData = timelineData.filter(d => d.isAttack);
  const benignData = timelineData.filter(d => !d.isAttack);

  return (
    <div className="detection-chart card">
      <div className="card-header">
        <h2>📈 Detection Timeline</h2>
        <p className="card-subtitle">
          Confidence levels over time • {attackData.length} attacks, {benignData.length} benign flows
        </p>
      </div>
      
      {timelineData && timelineData.length > 0 ? (
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={timelineData}>
              <defs>
                <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0d6efd" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#0d6efd" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#dee2e6" />
              <XAxis 
                dataKey="index" 
                label={{ value: 'Detection Sequence', position: 'insideBottom', offset: -5 }}
                stroke="#495057"
              />
              <YAxis 
                label={{ value: 'Confidence (%)', angle: -90, position: 'insideLeft' }}
                stroke="#495057"
              />
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="chart-tooltip">
                        <div className="tooltip-header">
                          <strong>{data.isAttack ? '🚨' : '✅'} {data.attack}</strong>
                        </div>
                        <div className="tooltip-body">
                          <p><span className="tooltip-label">Confidence:</span> {data.confidence}%</p>
                          <p><span className="tooltip-label">Time:</span> {data.timestamp}</p>
                          <p><span className="tooltip-label">Type:</span> {data.isAttack ? 'Attack' : 'Benign'}</p>
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
                contentStyle={{
                  background: '#ffffff',
                  border: '1px solid #dee2e6',
                  borderRadius: '8px',
                  padding: '12px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend 
                wrapperStyle={{
                  paddingTop: '20px'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="confidence" 
                stroke="#0d6efd" 
                strokeWidth={2}
                fill="url(#colorConfidence)"
                name="Detection Confidence"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">📉</div>
          <div className="empty-state-text">No detection data to visualize yet</div>
        </div>
      )}
    </div>
  );
};

export default DetectionChart;

