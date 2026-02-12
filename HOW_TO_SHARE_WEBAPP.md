# 🌐 How to Share Your Web App on Local Network

## ✅ Good News!
Your Flask app is already configured with `host='0.0.0.0'` which means it CAN be accessed from other devices on the same network!

## 📱 Steps to Share Your Web App:

### Step 1: Find Your Computer's IP Address

**Run this command in your terminal:**
```powershell
ipconfig
```

**Look for:** `IPv4 Address` under your active network adapter (WiFi or Ethernet)
- Example: `192.168.1.100` or `10.0.0.50`

### Step 2: Start Your Flask App
```powershell
python app.py
```

You should see output like:
```
* Running on http://0.0.0.0:5000
* Running on http://192.168.1.100:5000  ← This is your shareable link!
```

### Step 3: Share the Link

**Send this URL format to anyone on the same WiFi/Network:**
```
http://YOUR_IP_ADDRESS:5000
```

**Example:**
```
http://192.168.1.100:5000
```

## 🔥 Quick Test Script

Run this to get your shareable link instantly:
```powershell
python get_network_link.py
```

## ⚠️ Important Requirements:

### ✅ MUST Have (Both Devices):
1. **Same WiFi/Network**: Your laptop and their laptop must be on the same WiFi network
2. **Firewall**: Windows Firewall may block port 5000 (see fix below)

### ❌ Won't Work If:
- They're on different WiFi (use ngrok for that - see below)
- They're on mobile data
- Your firewall blocks the port
- Your router has isolation enabled

## 🛡️ Fix Firewall (If They Can't Connect):

**Run PowerShell as Administrator:**
```powershell
New-NetFirewallRule -DisplayName "Flask App Port 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

## 🌍 Share with ANYONE (Internet Access):

If you want to share with people NOT on your network, use **ngrok**:

### Install ngrok:
```powershell
pip install pyngrok
```

### Update your app.py:
```python
from pyngrok import ngrok

# Add before app.run():
public_url = ngrok.connect(5000)
print(f" * Public URL: {public_url}")
```

This gives you a public URL like: `https://abc123.ngrok.io`

## 📊 Demo Checklist for Evaluators:

- [ ] Show them your IP address
- [ ] Start Flask app: `python app.py`
- [ ] Open on your laptop: `http://localhost:5000`
- [ ] Open on their laptop: `http://YOUR_IP:5000`
- [ ] Both can use the app simultaneously!
- [ ] Show real-time updates (one person books, other sees it update)

## 🎯 Pro Tips:

1. **Keep your laptop plugged in** - WiFi might disconnect if it sleeps
2. **Don't close the terminal** - Flask must keep running
3. **Test beforehand** - Try it with a friend's phone first
4. **Network display** - Open same URL on projector for presentation

## 💡 For Presentation Day:

**Best Setup:**
1. Connect your laptop to university WiFi
2. Have evaluators connect to same WiFi  
3. Share: `http://YOUR_IP:5000`
4. Everyone can interact simultaneously!

**Backup Plan (No Network):**
- Use your laptop's hotspot
- Connect evaluators' devices to your hotspot
- Share the link!
