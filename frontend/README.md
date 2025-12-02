# IDS Frontend - React Dashboard

Real-time dashboard for the IDS Monitoring System built with React and Vite.

## Features

- Real-time attack visualization
- Interactive controls for monitoring
- Attack launcher interface
- Statistics and analytics
- Flow table and charts
- WebSocket real-time updates

## Structure

```
src/
├── components/                 # React components
│   ├── Dashboard.jsx          # Main dashboard
│   ├── Statistics.jsx         # Stats cards
│   ├── AttackAlerts.jsx       # Attack notifications
│   ├── AttackChart.jsx        # Pie chart
│   ├── TimelineChart.jsx      # Line chart
│   ├── FlowTable.jsx          # Flow table
│   └── Controls.jsx           # Control panel
├── services/                   # API clients
│   ├── api.js                 # REST API client
│   └── websocket.js           # WebSocket client
├── styles/                     # CSS files
│   └── dashboard.css          # Main styles
└── utils/                      # Utilities
    └── constants.js           # Constants
```

## Installation

```bash
# Install dependencies
npm install
```

## Running

```bash
# Development mode
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## Development

```bash
# Run development server
npm run dev

# Lint
npm run lint

# Format
npm run format
```

## Building

```bash
# Build for production
npm run build

# Output will be in dist/ folder
```

## Deployment

Deploy the `dist/` folder to any static hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront
- Nginx/Apache
```
