import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const DetectionChart = ({ timelineData }) => {
  return (
    <div className="detection-chart card">
      <h2>Detection Timeline</h2>
      {timelineData && timelineData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timelineData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="index" 
              label={{ value: 'Detection #', position: 'insideBottom', offset: -5 }} 
            />
            <YAxis 
              label={{ value: 'Confidence %', angle: -90, position: 'insideLeft' }} 
            />
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="custom-tooltip">
                      <p><strong>{payload[0].payload.attack}</strong></p>
                      <p>Confidence: {payload[0].value}%</p>
                      <p>Time: {payload[0].payload.timestamp}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="confidence" 
              stroke="#8884d8" 
              name="Confidence"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="chart-placeholder">
          <p>No data to display</p>
        </div>
      )}
    </div>
  );
};

export default DetectionChart;

