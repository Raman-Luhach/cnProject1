# Comprehensive Logging Guide

## What You'll See Now

### 1. When You Start Monitoring

```
============================================================
Real-Time IDS Monitoring Started
============================================================
Target VM IP: 192.168.64.2
Interface: bridge100
============================================================

🔍 Starting flow analysis thread...
```

### 2. When Packets Are Captured

```
📦 Captured 50 packets so far...
📦 Captured 100 packets so far...
📦 Captured 150 packets so far...
```

### 3. When Attacks Are Launched

```
======================================================================
🚀 LAUNCHING ATTACK
======================================================================
Attack Type: DDOS attack-HOIC
Target: 192.168.64.2
Duration: 60 seconds
======================================================================

🎯 Attack Orchestrator: Processing DDOS attack-HOIC
✅ Found attack function: ddos_hoic
🔥 Executing attack for 60 seconds...
🚨 Starting HOIC DDoS attack on 192.168.64.2
   Duration: 60 seconds
   Threads: 100
   Target URL: http://192.168.64.2
   ✅ HOIC attack threads launched
   📊 HOIC: Sent 100 requests...
   📊 HOIC: Sent 200 requests...
```

### 4. When Flows Are Analyzed (Every 5 Seconds)

```
======================================================================
🔬 ANALYZING 15 FLOWS (Cycle #1)
======================================================================

📊 Flow: 192.168.1.100:54321 → 192.168.64.2:80 (TCP)
   Packets: 150 (Fwd: 100, Bwd: 50)
   Bytes: 75,000
   🔧 Extracting features...
   ✅ Extracted 82 features
   🤖 Running ML model prediction...
   📈 Top 3 Predictions:
      DDOS attack-HOIC: 95.23%
      DDoS attacks-LOIC-HTTP: 3.45%
      Benign: 1.32%

   🚨 ⚠️  ATTACK DETECTED! ⚠️  🚨
   ╔══════════════════════════════════════════════════════════════════╗
   ║ Attack Type: DDOS attack-HOIC                                    ║
   ║ Confidence:  95.23%                                              ║
   ║ Source:      192.168.1.100:54321                                 ║
   ║ Target:      192.168.64.2:80                                     ║
   ╚══════════════════════════════════════════════════════════════════╝
   ✅ Alert sent to dashboard
======================================================================
```

### 5. When Benign Traffic Is Detected

```
📊 Flow: 192.168.1.50:45678 → 192.168.64.2:443 (TCP)
   Packets: 10 (Fwd: 5, Bwd: 5)
   Bytes: 5,000
   🔧 Extracting features...
   ✅ Extracted 82 features
   🤖 Running ML model prediction...
   📈 Top 3 Predictions:
      Benign: 98.76%
      DDOS attack-HOIC: 0.89%
      SQL Injection: 0.35%
   ✅ BENIGN Traffic (98.76%)
```

## Complete Flow Example

1. **Start Monitoring** → See initialization messages
2. **Packets Start Being Captured** → See packet count updates
3. **Launch Attack** → See detailed attack info
4. **Flow Analysis Begins** → Every 5 seconds, see detailed analysis
5. **Attack Detected** → See prediction confidence and alert box
6. **Dashboard Updates** → Alert sent via WebSocket

## Log Interpretation

### Emojis Legend
- 🔍 = Analysis
- 📦 = Packet capture
- 🚀 = Attack launch
- 🎯 = Attack processing
- 🔧 = Feature extraction
- 🤖 = ML prediction
- 📈 = Prediction scores
- 🚨 = Attack detected
- ✅ = Success/Benign
- ⚠️  = Warning
- ❌ = Error

### Understanding Predictions

**Top 3 Predictions** shows:
1. Most likely class with confidence
2. Second most likely
3. Third most likely

If top prediction > 50% and != "Benign" → ATTACK DETECTED

### Flow Information
- **Fwd packets**: From attacker to target
- **Bwd packets**: From target back to attacker
- **Total bytes**: Size of all packets in flow
- **82 features**: Extracted for ML model
- **Confidence**: Model's certainty (higher = more confident)

## Troubleshooting

### No Flows Detected
```
⏳ Waiting for traffic... (Analysis cycle #6)
```
**Reason**: No traffic to/from target VM
**Solution**: Launch an attack or generate traffic

### Feature Extraction Failed
```
⚠️  Feature extraction failed
```
**Reason**: Insufficient flow data
**Solution**: Normal - some flows too small to analyze

### Error During Analysis
```
❌ ERROR analyzing flow: <error message>
<full traceback>
```
**Reason**: Unexpected error
**Solution**: Check traceback for details

## Performance Notes

- Logs every 50 packets (not every packet - would be too much)
- Flow analysis every 5 seconds
- Attack status every 100 requests
- Only top 3 predictions shown (not all 13 classes)

This keeps logs informative but not overwhelming!
