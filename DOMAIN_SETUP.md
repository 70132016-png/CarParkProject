# 🌐 PARKEASE - Custom Domain Setup

## Option 1: Local Custom Domain (Recommended for Demo)

### For Windows:

1. **Edit Hosts File:**
   - Open Notepad as Administrator
   - File → Open: `C:\Windows\System32\drivers\etc\hosts`
   - Add this line at the end:
   ```
   127.0.0.1    parkease.local
   127.0.0.1    www.parkease.local
   ```
   - Save the file

2. **Access Your Site:**
   - **Homepage:** http://parkease.local:5000
   - **Parking:** http://parkease.local:5000/parking/main
   - **Admin:** http://parkease.local:5000/admin/login

### Benefits:
✅ Professional URL for presentation
✅ Easy to remember
✅ Works offline
✅ No internet required

---

## Option 2: Access from Other Devices (Same Network)

Your Flask app is already accessible at:
- **Local:** http://localhost:5000
- **Network:** http://192.168.18.116:5000

### How to Access from Phone/Tablet/Other PC:

1. **Find Your PC's IP Address:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.18.116)

2. **On Other Device:**
   - Connect to **same WiFi network**
   - Open browser and go to: `http://YOUR-PC-IP:5000`
   - Example: `http://192.168.18.116:5000`

### Test URLs for Other Devices:
- Homepage: http://192.168.18.116:5000
- Parking: http://192.168.18.116:5000/parking/main
- Admin: http://192.168.18.116:5000/admin/login

✅ **Yes, you can access from anywhere on the same network!**

---

## Option 3: Public URL (For Remote Access)

### Using Ngrok (Free):

1. **Download Ngrok:**
   - Visit: https://ngrok.com/download
   - Download for Windows
   - Extract to a folder

2. **Start Your Flask App:**
   ```bash
   python.exe app.py
   ```

3. **In Another Terminal, Run Ngrok:**
   ```bash
   ngrok http 5000
   ```

4. **Get Public URL:**
   - Ngrok will show a URL like: `https://abc123.ngrok.io`
   - Share this URL with anyone
   - They can access from anywhere in the world!

### Example Output:
```
Forwarding    https://parkease-demo.ngrok.io -> http://localhost:5000
```

---

## Option 4: Professional Domain (For Production)

### If You Want Real Domain:

1. **Buy Domain:**
   - Register: parkease.com, parkease.online, etc.
   - Cost: $10-15/year

2. **Deploy to Cloud:**
   - Heroku (Free tier)
   - PythonAnywhere (Free tier)
   - AWS/Azure (Paid)

3. **Point Domain to Server:**
   - Configure DNS settings
   - SSL certificate for HTTPS

---

## 📱 Current Access Summary:

### Local Development (You):
- http://localhost:5000
- http://127.0.0.1:5000
- http://parkease.local:5000 (after hosts file edit)

### Same Network (Phone/Tablet/Other PC):
- http://192.168.18.116:5000
- Replace IP with your actual IP from `ipconfig`

### Public Internet (Using Ngrok):
- https://random-name.ngrok.io (changes each time)
- Can upgrade ngrok for custom subdomain

---

## 🎯 Recommended for FYP Presentation:

**Best Setup:**
1. Use `http://parkease.local:5000` for demos (edit hosts file)
2. Show mobile access using `http://192.168.18.116:5000`
3. Mention "scalable to public cloud" in presentation

**Why This Works:**
✅ Professional-looking URL
✅ Shows mobile compatibility
✅ No internet dependency
✅ Easy to demonstrate

---

## 🔧 Quick Setup Commands:

### Edit Hosts File (Windows):
```bash
notepad C:\Windows\System32\drivers\etc\hosts
```

Add:
```
127.0.0.1    parkease.local
```

### Check Your IP:
```bash
ipconfig | findstr IPv4
```

### Start App:
```bash
cd D:\FYP\CarParkProject
.venv-1\Scripts\python.exe app.py
```

---

## 🌟 Pro Tip for Demo:

Show evaluators:
1. Desktop browser: `http://parkease.local:5000`
2. Your phone: `http://192.168.18.116:5000`
3. Say: "Deployable to cloud for public access"

This demonstrates:
- Professional branding
- Mobile responsiveness  
- Scalability understanding

**You're set for an impressive demo!** 🚀
