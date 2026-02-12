# 🎥 Detection Video ↔️ Diagram Synchronization Guide

## Problem: Why Diagram Shows All Available When Video Shows Occupied?

The web diagram and detection video are **TWO SEPARATE PROCESSES** that need to run together!

### How It Works:
```
┌─────────────────┐         ┌──────────────┐         ┌──────────────────┐
│  Video Camera   │  ───>   │   Detection  │  ───>   │    Database      │
│  (carPark.mp4)  │         │  main_det.py │         │  (parkease.db)   │
└─────────────────┘         └──────────────┘         └──────────────────┘
                                                              │
                                                              │ Updates every 3s
                                                              ▼
                                                      ┌──────────────────┐
                                                      │   Web Browser    │
                                                      │  Parking Diagram │
                                                      └──────────────────┘
```

## ✅ Solution: Run BOTH Processes Simultaneously

### Terminal 1: Web Server
```bash
python app.py
```
- Serves the web interface
- Shows parking diagram at http://localhost:5000/parking/main
- Reads from database every 3 seconds

### Terminal 2: Detection Script
```bash
python main_detection.py
```
- Opens video window with parking lot feed
- Analyzes each frame using computer vision
- **Writes** occupied/available status to database
- Shows colored rectangles:
  - 🟢 Green = Available
  - 🔴 Red = Occupied
  - 🟠 Orange = Reserved (from web bookings)

## 🎯 Step-by-Step Demo Instructions

1. **Open TWO terminal windows**
   - Terminal 1: Already running `app.py` ✓
   - Terminal 2: New terminal for detection

2. **Start Detection in Terminal 2:**
   ```bash
   cd D:\FYP\CarParkProject
   .venv-1\Scripts\python.exe main_detection.py
   ```

3. **Watch the Magic:**
   - Video window opens showing parking lot
   - Green/Red rectangles appear on spots
   - Spot labels (A1, B5, etc.) show on video
   - Database updates in real-time

4. **Open Browser:**
   ```
   http://localhost:5000/parking/main
   ```
   - Diagram now matches video!
   - Colors sync every 3 seconds
   - Click available (green) spots to book

## 🔧 How Detection Identifies Occupancy

### Pixel Counting Method:
```python
# For each parking spot rectangle in video:
imgCrop = frame[y:y+h, x:x+w]  # Extract spot area
pixelCount = cv2.countNonZero(imgCrop)  # Count white pixels

if pixelCount < 900:  # Threshold
    status = "AVAILABLE"  # More black pixels (empty space)
else:
    status = "OCCUPIED"   # More white pixels (car detected)
```

### Spot Mapping:
- Video has 69 predefined rectangles (from parkingSpacePicker.py)
- Each rectangle maps to: A1-A23, B1-B23, C1-C23
- Detection updates database: `UPDATE parking_spots SET is_occupied=1 WHERE spot_label='A5'`
- Web diagram reads: `SELECT * FROM parking_spots`

## 🎨 Color Meanings

### In Detection Video Window:
| Color | Status | Description |
|-------|--------|-------------|
| 🟢 Green | Available | No car detected, free to book |
| 🔴 Red | Occupied | Car detected in spot |
| 🟠 Orange | Reserved | Booked via website (protected) |

### In Web Diagram:
| Color | Status | CSS Class |
|-------|--------|-----------|
| Green gradient | available | Can click to book |
| Red gradient | occupied | Cannot book, in use |
| Orange gradient | reserved | Your booking, shows timer |

## ⚡ Quick Test Verification

### Test 1: Check Detection is Running
```bash
# In detection terminal, you should see:
Initialized 69 parking spots
Starting parking detection...
Press 'q' or ESC to quit
```

### Test 2: Verify Database Updates
```bash
# In third terminal:
python -c "import sqlite3; conn = sqlite3.connect('parkease.db'); cursor = conn.cursor(); cursor.execute('SELECT spot_label, is_occupied FROM parking_spots LIMIT 10'); print(cursor.fetchall()); conn.close()"
```

### Test 3: Watch Live Sync
1. Keep detection video window visible
2. Open browser to parking diagram
3. Watch colors change together
4. Note: 3-second delay is normal (refresh interval)

## 🐛 Troubleshooting

### Problem: All spots show available in diagram
**Solution:** Detection script is NOT running
- Check if main_detection.py is running in Terminal 2
- Look for video window titled "PARKEASE - Admin View"

### Problem: Video shows "Error: No video file"
**Solution:** Missing carPark.mp4 file
- Ensure carPark.mp4 is in project root directory
- Check file path in main_detection.py line 12

### Problem: Detection window freezes
**Solution:** Video needs to loop
- Code already handles this (resets to frame 0)
- Press 'q' or ESC to quit cleanly

### Problem: Spots flicker between colors
**Solution:** Lighting/threshold sensitivity
- Adjust trackbars in "Vals" window
- Val1 (25): Adaptive threshold block size
- Val2 (16): Threshold constant
- Val3 (5): Median blur kernel size

## 📊 Performance Notes

- **Detection Speed:** ~30 FPS (smooth video)
- **Database Update:** Only on status change (efficient)
- **Web Refresh:** Every 3 seconds (configurable in parking.js)
- **Memory Usage:** ~50MB for detection, ~20MB for web server

## 🎓 For Presentation/Demo

**Best Demo Flow:**
1. Show homepage with live stats updating
2. Navigate to parking diagram
3. **Point to detection video window** running on second screen/monitor
4. Book a spot on website → Show orange color in video
5. Explain computer vision pixel counting method
6. Show admin dashboard with analytics

**Key Talking Points:**
- "Real-time synchronization between computer vision and web interface"
- "OpenCV analyzes video frame-by-frame to detect occupied spots"
- "Database acts as bridge between detection and web app"
- "3-second refresh provides near real-time updates"

## 🚀 Advanced: Dual Monitor Setup

**Ideal Exhibition Setup:**
```
Monitor 1 (Main Display):           Monitor 2 (Side Display):
┌──────────────────────┐            ┌──────────────────────┐
│                      │            │                      │
│   Web Browser        │            │  Detection Video     │
│   Parking Diagram    │            │  + OpenCV Window     │
│   Interactive Booking│            │  Showing Real Feed   │
│                      │            │                      │
└──────────────────────┘            └──────────────────────┘
```

This shows evaluators the **complete system architecture**!

---

**Remember:** Both processes MUST run simultaneously for full functionality! 🎯
