# Quick Start Guide - IDS Real-Time Monitoring System

Get up and running in minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Multipass installed (`brew install multipass`)
- [ ] Target VM running (192.168.64.2)

## Step 1: Setup Target VM (5 minutes)

```bash
# Create VM
multipass launch --name target-vm --mem 2G --disk 20G

# Get IP
VM_IP=$(multipass info target-vm | grep IPv4 | awk '{print $2}')
echo "VM IP: $VM_IP"

# Setup services
multipass exec target-vm -- bash -c "
sudo apt update -qq && 
sudo apt install -y apache2 openssh-server vsftpd mysql-server php libapache2-mod-php &&
sudo systemctl start apache2 ssh vsftpd mysql &&
sudo systemctl enable apache2 ssh vsftpd mysql &&
sudo mkdir -p /var/www/html/test &&
echo '<?php if(isset(\$_GET[\"id\"])) echo \"<h2>User ID: \" . \$_GET[\"id\"] . \"</h2>\"; ?>' | sudo tee /var/www/html/test/index.php
"
```

## Step 2: Start Backend (2 minutes)

```bash
cd backend

# Create venv and install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run (may need sudo for packet capture)
sudo venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend running at: http://localhost:8000

## Step 3: Start Frontend (2 minutes)

Open a new terminal:

```bash
cd frontend

# Install and run
npm install
npm run dev
```

Frontend running at: http://localhost:5173

## Step 4: Use the Dashboard

1. Open browser: http://localhost:5173
2. Enter settings:
   - Interface: `bridge100` (Multipass) or `en0` (Wi-Fi)
   - Target IP: `192.168.64.2` (your VM IP)
3. Click "Start Monitoring"
4. Select attack type and click "Launch Attack"
5. Watch real-time detection!

## Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Try different port
uvicorn app.main:app --port 8001
```

### Permission denied (packet capture)

```bash
# Run with sudo
sudo venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend can't connect

- Check backend is running: `curl http://localhost:8000/health`
- Check WebSocket: `wscat -c ws://localhost:8000/ws`
- Verify CORS settings in backend

### No attacks detected

- Verify VM IP is correct
- Check network interface matches Multipass setup
- Ensure monitoring is started
- Try benign traffic first: `curl http://192.168.64.2/test/`

## What's Next?

- Try all 13 attack types
- Monitor the statistics and charts
- Check the API docs: http://localhost:8000/docs
- Review the flow table for detailed analysis
- Export data for reports

## Need Help?

- Check main README.md for detailed docs
- Review API documentation at /docs
- Check console logs for errors
- Ensure all services are running

## Success Checklist

- [ ] Target VM running and accessible
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Dashboard loads successfully
- [ ] Monitoring can be started
- [ ] Attacks can be launched
- [ ] Real-time updates working

Enjoy your IDS monitoring system!

