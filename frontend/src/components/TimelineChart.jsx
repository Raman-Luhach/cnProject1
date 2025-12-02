/**
 * Timeline Chart Component - Line chart showing attacks over time
 */
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const TimelineChart = ({ timelineData }) => {
  if (timelineData.length === 0) {
    return (
      <div className="chart-card">
        <h2>Traffic Timeline</h2>
        <p className="no-data">No timeline data yet</p>
      </div>
    );
  }

  return (
    <div className="chart-card">
      <h2>Traffic Timeline</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={timelineData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis dataKey="time" stroke="#aaa" />
          <YAxis stroke="#aaa" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #444' }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="attacks" 
            stroke="#ff4444" 
            strokeWidth={2}
            name="Attacks"
          />
          <Line 
            type="monotone" 
            dataKey="benign" 
            stroke="#4caf50" 
            strokeWidth={2}
            name="Benign"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TimelineChart;

