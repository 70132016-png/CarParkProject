from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from flask_cors import CORS
from datetime import datetime, timedelta
import pickle
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time
import cv2
import numpy as np
import cvzone
import hashlib

from database import (
    init_db, initialize_spots, get_all_spots, get_spot_by_label,
    create_booking, get_active_bookings, cancel_booking, update_spot_status,
    add_to_waitlist, add_feedback, get_all_feedback, get_parking_logs,
    record_occupancy_stats, get_occupancy_trends, get_available_spots_count,
    get_db, create_user, get_user_by_email, get_user_by_id
)

app = Flask(__name__)
app.secret_key = 'parkease_secret_key_2026'
CORS(app)

# Admin credentials
ADMIN_USERNAME = 'admin@parkease.com'
ADMIN_PASSWORD = 'admin123'

# Simple password hashing (for demo - use bcrypt in production)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

# Email configuration (using Gmail SMTP)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'your_email@gmail.com'  # Replace with your email
EMAIL_PASSWORD = 'your_app_password'  # Replace with app password

def send_email(to_email, subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

@app.route('/')
def index():
    """Homepage - location selection"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for debugging"""
    try:
        from database import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM spots")
        spot_count = cursor.fetchone()[0]
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'users': user_count,
            'spots': spot_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# User Authentication Routes
@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    """User registration"""
    if request.method == 'POST':
        try:
            import re
            
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Server-side validation
            
            # Check password confirmation
            if password != confirm_password:
                return render_template('user_register.html', error='Passwords do not match')
            
            # Validate name - only letters and spaces
            if not re.match(r'^[A-Za-z\s]+$', name):
                return render_template('user_register.html', error='Name should only contain letters and spaces')
            
            # Validate email format
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return render_template('user_register.html', error='Invalid email format')
            
            # Validate phone - must be 9 digits (03 is added separately)
            if not re.match(r'^[0-9]{9}$', phone):
                return render_template('user_register.html', error='Phone number must be exactly 9 digits')
            
            # Validate password strength
            if len(password) < 8:
                return render_template('user_register.html', error='Password must be at least 8 characters')
            
            if not re.search(r'[A-Z]', password):
                return render_template('user_register.html', error='Password must contain at least one uppercase letter')
            
            if not re.search(r'[a-z]', password):
                return render_template('user_register.html', error='Password must contain at least one lowercase letter')
            
            if not re.search(r'[0-9]', password):
                return render_template('user_register.html', error='Password must contain at least one number')
            
            if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', password):
                return render_template('user_register.html', error='Password must contain at least one special character')
            
            # Combine phone with 03 prefix
            full_phone = '03' + phone
            
            # Check if user already exists
            existing_user = get_user_by_email(email)
            if existing_user:
                return render_template('user_register.html', error='Email already registered')
            
            # Create user
            password_hash = hash_password(password)
            user_id = create_user(email, password_hash, name, full_phone)
            
            if user_id:
                # Auto-login after registration
                session['user_id'] = user_id
                session['user_name'] = name
                session['user_email'] = email
                return redirect('/parking/main')
            else:
                return render_template('user_register.html', error='Registration failed. Please try again.')
        except Exception as e:
            print(f"Registration error: {e}")
            import traceback
            traceback.print_exc()
            # Show detailed error in development/debugging
            error_msg = f'An error occurred during registration: {str(e)}'
            return render_template('user_register.html', error=error_msg)
    
    return render_template('user_register.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """User login"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = get_user_by_email(email)
            
            if user and verify_password(password, user['password_hash']):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                return redirect('/parking/main')
            else:
                return render_template('user_login.html', error='Invalid email or password')
        except Exception as e:
            print(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            return render_template('user_login.html', error='An error occurred during login. Please try again.')
    
    return render_template('user_login.html')

@app.route('/user/logout')
def user_logout():
    """User logout"""
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    return redirect('/')

@app.route('/parking/<location>')
def parking(location):
    """Parking diagram page for specific location"""
    # Require login to access parking
    if 'user_id' not in session:
        return redirect('/user/login')
    
    spots = get_all_spots()
    return render_template('parking.html', location=location, spots=spots)

@app.route('/api/spots')
def api_spots():
    """API endpoint to get all spots status"""
    spots = get_all_spots()
    available_count = sum(1 for spot in spots if spot['status'] == 'available')
    occupied_count = sum(1 for spot in spots if spot['status'] == 'occupied')
    reserved_count = sum(1 for spot in spots if spot['status'] == 'reserved')
    
    return jsonify({
        'spots': spots,
        'stats': {
            'total': len(spots),
            'available': available_count,
            'occupied': occupied_count,
            'reserved': reserved_count
        }
    })

@app.route('/api/book', methods=['POST'])
def api_book():
    """API endpoint to book a spot"""
    data = request.json
    
    spot_label = data.get('spot_label')
    user_name = data.get('user_name')
    user_phone = data.get('user_phone')
    user_email = data.get('user_email', '')
    car_type = data.get('car_type')
    arrival_time = data.get('arrival_time')
    duration = int(data.get('duration'))
    
    # Validate spot is available
    spot = get_spot_by_label(spot_label)
    if not spot:
        return jsonify({'success': False, 'message': 'Spot not found'}), 404
    
    if spot['status'] != 'available':
        return jsonify({'success': False, 'message': 'Spot is not available'}), 400
    
    try:
        booking_id = create_booking(
            spot_label, user_name, user_phone, user_email,
            car_type, arrival_time, duration
        )
        
        # Send confirmation email
        if user_email:
            email_body = f"""
            <h2>Booking Confirmation - PARKEASE</h2>
            <p>Dear {user_name},</p>
            <p>Your parking spot has been successfully reserved!</p>
            <ul>
                <li><strong>Spot:</strong> {spot_label}</li>
                <li><strong>Arrival Time:</strong> {arrival_time}</li>
                <li><strong>Duration:</strong> {duration} hours</li>
                <li><strong>Car Type:</strong> {car_type}</li>
            </ul>
            <p><strong>Important:</strong> Please arrive within 10 minutes of your scheduled time or your booking may be cancelled.</p>
            <p style="margin-top: 20px; font-style: italic;">Park at your own <s>risk</s> choice!</p>
            <p>- PARKEASE Team</p>
            """
            send_email(user_email, 'Parking Reservation Confirmed', email_body)
        
        return jsonify({
            'success': True,
            'message': 'Booking successful!',
            'booking_id': booking_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cancel/<int:booking_id>', methods=['POST'])
def api_cancel_booking(booking_id):
    """API endpoint to cancel a booking"""
    try:
        cancel_booking(booking_id)
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/waitlist', methods=['POST'])
def api_waitlist():
    """API endpoint to join waitlist"""
    data = request.json
    try:
        add_to_waitlist(
            data.get('user_name'),
            data.get('user_phone'),
            data.get('user_email', ''),
            data.get('car_type')
        )
        return jsonify({'success': True, 'message': 'Added to waitlist'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """API endpoint to submit feedback"""
    data = request.json
    try:
        add_feedback(
            data.get('user_name'),
            int(data.get('rating')),
            data.get('comment', '')
        )
        return jsonify({'success': True, 'message': 'Thank you for your feedback!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    spots = get_all_spots()
    bookings = get_active_bookings()
    logs = get_parking_logs(50)
    feedback = get_all_feedback()
    
    return render_template('admin_dashboard.html',
                         spots=spots,
                         bookings=bookings,
                         logs=logs,
                         feedback=feedback)

@app.route('/admin/api/analytics')
def admin_analytics():
    """API endpoint for analytics data"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    trends = get_occupancy_trends(24)
    
    return jsonify({
        'trends': trends,
        'success': True
    })

@app.route('/admin/video-feed')
def admin_video_feed():
    """Admin video feed viewer"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin_video.html')

def generate_frames():
    """Generate video frames with detection overlay"""
    try:
        cap = cv2.VideoCapture('carPark.mp4')
        width, height = 103, 43
        
        # Load parking positions
        with open('CarParkPos', 'rb') as f:
            posList = pickle.load(f)
        
        # Create spot mapping
        spots = get_all_spots()
        spots.sort(key=lambda s: s['spot_label'])
        spot_mapping = {}
        for i, spot in enumerate(spots):
            if i < len(posList):
                spot_mapping[i] = spot['spot_label']
        
        while True:
            success, img = cap.read()
            if not success:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
                continue
            
            # Process frame
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
            imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, 25, 16)
            imgThres = cv2.medianBlur(imgThres, 5)
            kernel = np.ones((3, 3), np.uint8)
            imgThres = cv2.dilate(imgThres, kernel, iterations=1)
            
            # Check spaces and draw rectangles
            spaces = 0
            for i, pos in enumerate(posList):
                x, y = pos
                w, h = width, height
                imgCrop = imgThres[y:y + h, x:x + w]
                count = cv2.countNonZero(imgCrop)
                
                spot_label = spot_mapping.get(i, f"SPOT{i}")
                spot = get_spot_by_label(spot_label)
                
                if spot:
                    if spot['status'] == 'reserved':
                        color = (0, 165, 255)  # Orange
                        thic = 5
                    elif count < 900:
                        color = (0, 200, 0)  # Green
                        thic = 5
                        spaces += 1
                    else:
                        color = (0, 0, 200)  # Red
                        thic = 2
                    
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, thic)
                    cv2.putText(img, spot_label, (x + 5, y + 25), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Add counter
            cvzone.putTextRect(img, f'Free: {spaces}/{len(posList)}', (50, 60), 
                             thickness=3, offset=20, colorR=(0, 200, 0))
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            time.sleep(0.03)  # ~30 FPS
    
    except Exception as e:
        print(f"Error in video stream: {e}")
    finally:
        if 'cap' in locals():
            cap.release()

@app.route('/video_stream')
def video_stream():
    """Video streaming route"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/my-bookings')
def my_bookings():
    """User's booking history page"""
    return render_template('my_bookings.html')

@app.route('/api/my-bookings')
def api_my_bookings():
    """API endpoint to get user's bookings by phone number"""
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Phone number required'}), 400
    
    try:
        bookings_list = []
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, spot_label, user_name, user_phone, user_email,
                   car_type, arrival_time, duration, booking_time, status
            FROM bookings
            WHERE user_phone = ?
            ORDER BY booking_time DESC
        ''', (phone,))
        
        rows = cursor.fetchall()
        for row in rows:
            bookings_list.append({
                'id': row[0],
                'spot_label': row[1],
                'user_name': row[2],
                'user_phone': row[3],
                'car_type': row[5],
                'arrival_time': row[6],
                'duration': row[7],
                'booking_time': row[8],
                'status': row[9] if row[9] else 'active'
            })
        
        conn.close()
        return jsonify({'success': True, 'bookings': bookings_list})
    except Exception as e:
        print(f"Error in my-bookings API: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def background_tasks():
    """Background tasks for auto-release and stats recording"""
    while True:
        try:
            # Record occupancy stats every 5 minutes
            record_occupancy_stats()
            
            # Check for expired grace periods
            # TODO: Implement grace period check and auto-release
            
            time.sleep(300)  # 5 minutes
        except Exception as e:
            print(f"Background task error: {e}")
            time.sleep(60)

# Initialize database on startup
def initialize_app():
    """Initialize the application"""
    init_db()
    
    # Load parking spots from pickle file
    try:
        with open('CarParkPos', 'rb') as f:
            spot_positions = pickle.load(f)
        initialize_spots(spot_positions)
    except Exception as e:
        print(f"Error loading parking spots: {e}")
        # Create some default spots if pickle file doesn't exist
        print("Creating default parking spots...")
    
    # Seed sample data for realistic display
    try:
        from seed_sample_data import seed_sample_data
        seed_sample_data()
    except Exception as e:
        print(f"Note: Sample data seeding skipped: {e}")
    
    # Start background tasks
    bg_thread = threading.Thread(target=background_tasks, daemon=True)
    bg_thread.start()

# Initialize on module import (for Gunicorn/production)
initialize_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
