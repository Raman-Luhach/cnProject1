/**
 * Attack Chart Component - Pie chart of attacks by type
 */
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { ATTACK_COLORS } from '../utils/constants';

const AttackChart = ({ attacksByType }) => {
  const data = Object.entries(attacksByType).map(([name, value]) => ({
    name,
    value,
  }));

  if (data.length === 0) {
    return (
      <div className="chart-card">
        <h2>Attacks by Type</h2>
        <p className="no-data">No attack data yet</p>
      </div>
    );
  }

  return (
    <div className="chart-card">
      <h2>Attacks by Type</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={ATTACK_COLORS[entry.name] || '#ff4444'} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AttackChart;

