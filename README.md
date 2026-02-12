# PARKEASE - Smart Parking Management System

**Park at your own ~~risk~~ choice!**

## 🚀 Features

- **Interactive Parking Diagram** - Visual representation of all 69 parking spots
- **Real-Time Detection** - OpenCV-based occupancy detection from video feed
- **Pre-Booking System** - Reserve spots in advance with automatic conflict prevention
- **Waitlist Management** - Join queue when parking is full
- **Email Notifications** - Booking confirmations and reminders
- **User Feedback** - Rate and review parking experience
- **Admin Dashboard** - Complete analytics with charts and logs
- **Mobile Responsive** - Works perfectly on all devices

## 📋 Prerequisites

- Python 3.8 or higher
- All required packages (automatically installed)

## 🛠️ Installation & Setup

### Step 1: Install Required Packages

The virtual environment is already configured. Install any missing packages:

```bash
.venv-1\Scripts\python.exe -m pip install flask flask-cors opencv-python cvzone numpy
```

### Step 2: Initialize the Web Application

Run the Flask web server:

```bash
.venv-1\Scripts\python.exe app.py
```

This will:
- Create the SQLite database (`parkease.db`)
- Initialize all 69 parking spots with labels (A1-A23, B1-B23, C1-C23)
- Start the web server on `http://localhost:5000`

### Step 3: Run the Detection System (Optional for Admin View)

In a separate terminal, run the parking detection:

```bash
.venv-1\Scripts\python.exe main_detection.py
```

This will:
- Process the video feed
- Detect occupied/available spots
- Update the database in real-time
- Show the admin detection window

## 🌐 Accessing the System

### User Interface
- **Homepage**: http://localhost:5000
- **Parking View**: http://localhost:5000/parking/main
- **My Bookings**: http://localhost:5000/my-bookings

### Admin Panel
- **Admin Login**: http://localhost:5000/admin/login
- **Credentials**:
  - Username: `admin@parkease.com`
  - Password: `admin123`

## 📖 How to Use

### For Users:

1. **Select Location** - Choose "Main Parking" from homepage
2. **View Available Spots** - See real-time availability on the interactive diagram
3. **Book a Spot**:
   - Click on any green (available) spot
   - Fill in your details (name, phone, car type, arrival time, duration)
   - Confirm booking
   - Receive email confirmation (if email provided)
4. **Join Waitlist** - If no spots available, join the waitlist
5. **Rate Experience** - Provide feedback after parking

### For Administrators:

1. **Login** - Use admin credentials
2. **View Dashboard**:
   - Real-time statistics
   - Occupancy trends chart
   - Active bookings list
   - Activity logs
   - User feedback
3. **Run Detection** - Use `main_detection.py` to see live feed processing

## 🎨 Color Legend

- 🟢 **Green** - Available spots (click to book)
- 🔴 **Red** - Occupied spots
- 🟡 **Yellow/Orange** - Reserved spots (pre-booked)

## ⚙️ Configuration

### Email Notifications (Optional)

To enable email notifications, edit `app.py`:

```python
EMAIL_USER = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'
```

**Note**: Use Gmail App Password, not your regular password.

### Database

The SQLite database (`parkease.db`) stores:
- Parking spots and their status
- Bookings and reservations
- Activity logs
- User feedback
- Occupancy statistics

## 📊 Database Schema

- **spots** - All parking spots with coordinates and status
- **bookings** - Active and historical bookings
- **parking_logs** - Activity history
- **feedback** - User ratings and comments
- **waitlist** - Users waiting for available spots
- **favorites** - User's favorite locations
- **occupancy_stats** - Historical occupancy data for analytics

## 🔧 Troubleshooting

### Port Already in Use
If port 5000 is busy, edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Issues
Delete `parkease.db` and restart `app.py` to recreate:
```bash
del parkease.db
.venv-1\Scripts\python.exe app.py
```

### Video Not Found
Ensure `carPark.mp4` is in the project directory.

## 📁 Project Structure

```
CarParkProject/
├── app.py                  # Flask web application
├── database.py             # Database models and functions
├── main_detection.py       # OpenCV detection (integrated with DB)
├── main.py                 # Original detection (standalone)
├── parkingSpacePicker.py   # Utility to mark parking spots
├── CarParkPos              # Pickle file with spot coordinates
├── carPark.mp4             # Video file
├── carParkImg.png          # Reference image
├── templates/              # HTML templates
│   ├── index.html
│   ├── parking.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── my_bookings.html
└── static/                 # CSS and JavaScript
    ├── css/
    │   └── style.css
    └── js/
        ├── parking.js
        └── admin.js
```

## 🎯 Key Features Explained

### Pre-Booking System
- Users can reserve spots in advance
- 10-minute grace period for late arrivals
- Automatic conflict prevention
- Email confirmations

### Real-Time Updates
- Database updated every frame during detection
- Web interface refreshes every 3 seconds
- Admin dashboard refreshes every 10 seconds

### Smart Status Management
- Reserved spots are never overridden by detection
- Only updates database when status changes
- Reduces unnecessary database writes

### Analytics Dashboard
- Line chart showing 24-hour occupancy trends
- Pie chart for current status distribution
- Real-time booking and activity logs
- User feedback display

## 🚀 For Your FYP Presentation

### Demo Flow:
1. Open homepage - show 3 locations (only 1 active)
2. Navigate to Main Parking - show live diagram
3. Click available spot - demonstrate booking process
4. Show admin login and dashboard
5. Run detection window - show real-time updates
6. Demonstrate waitlist and feedback features

### Key Points to Mention:
- Computer vision integration (OpenCV)
- Full-stack web development (Flask + JavaScript)
- Database management (SQLite)
- Real-time synchronization
- User experience focus
- Scalable architecture

## 📝 Future Enhancements

- Multiple active locations with different videos
- Mobile app (React Native)
- Payment gateway integration
- SMS notifications
- License plate recognition
- Navigation to spot once inside

## 👨‍💻 Developer

Created for Final Year Project (FYP)
Phase 2 - Smart Parking Management System

---

**PARKEASE** - Making parking smarter, one spot at a time! 🚗
