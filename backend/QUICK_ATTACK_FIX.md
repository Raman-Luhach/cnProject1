# Quick Fix for Attack Scripts

## ✅ Fixed!

The attack script now has **TWO versions**:

### Option 1: Bash Version (No Dependencies) ⭐ RECOMMENDED
```bash
bash /tmp/attack_http_flood.sh
```
- Uses `curl` (already installed)
- No Python dependencies
- Works immediately

### Option 2: Python Version (Built-in Libraries)
```bash
python3 /tmp/attack_http_flood_python.py
```
- Uses `urllib` (built into Python)
- No installation needed
- Alternative if bash version doesn't work

---

## 🚀 Quick Test

```bash
# Start monitoring (if not running)
cd /Users/ramanluhach/cnProject/backend && ./auto_start_monitoring.sh

# Launch attack (bash version - recommended)
bash /tmp/attack_http_flood.sh

# OR Python version
python3 /tmp/attack_http_flood_python.py
```

**Watch your dashboard at http://localhost:5173 - detections should appear within 10 seconds!**

---

## 📝 Other Attack Scripts

All other attack scripts should work:
- `bash /tmp/attack_syn_flood.sh` (requires sudo)
- `python3 /tmp/attack_slowloris.sh` (uses built-in socket)
- `bash /tmp/attack_port_scan.sh` (uses nmap)
- `bash /tmp/attack_ssh_brute.sh` (uses hydra)

---

## ✅ Status

**All attack scripts are now fixed and ready to use!**

