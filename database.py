import sqlite3
from datetime import datetime
import json

DATABASE = 'parkease.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Parking spots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_label TEXT UNIQUE NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            status TEXT DEFAULT 'available',
            location TEXT DEFAULT 'Main Parking',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_label TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_phone TEXT NOT NULL,
            user_email TEXT,
            car_type TEXT NOT NULL,
            arrival_time TIMESTAMP NOT NULL,
            duration INTEGER NOT NULL,
            booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            grace_period_end TIMESTAMP,
            FOREIGN KEY (spot_label) REFERENCES spots(spot_label)
        )
    ''')
    
    # Parking logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_label TEXT NOT NULL,
            action TEXT NOT NULL,
            user_name TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')
    
    # Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Wait list table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            user_phone TEXT NOT NULL,
            user_email TEXT,
            car_type TEXT NOT NULL,
            requested_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'waiting'
        )
    ''')
    
    # Favorites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_phone TEXT NOT NULL,
            location TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Analytics table for tracking occupancy
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS occupancy_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_spots INTEGER,
            occupied_spots INTEGER,
            available_spots INTEGER,
            reserved_spots INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def initialize_spots(spot_positions):
    """Initialize all parking spots with labels A1-C23"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if spots already exist
    cursor.execute('SELECT COUNT(*) FROM spots')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Sort positions by x coordinate then y to create columns
        sorted_positions = sorted(spot_positions, key=lambda p: (p[0], p[1]))
        
        # Divide into 3 columns (approximately)
        spots_per_column = len(sorted_positions) // 3
        
        labels = []
        for i, pos in enumerate(sorted_positions):
            if i < spots_per_column:
                label = f"A{i+1}"
            elif i < spots_per_column * 2:
                label = f"B{i-spots_per_column+1}"
            else:
                label = f"C{i-spots_per_column*2+1}"
            
            cursor.execute('''
                INSERT INTO spots (spot_label, x, y, width, height, status)
                VALUES (?, ?, ?, ?, ?, 'available')
            ''', (label, pos[0], pos[1], 103, 43))
            labels.append(label)
        
        conn.commit()
        print(f"Initialized {len(sorted_positions)} parking spots")
    
    conn.close()

def update_spot_status(spot_label, status):
    """Update the status of a parking spot"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE spots 
        SET status = ?, last_updated = CURRENT_TIMESTAMP
        WHERE spot_label = ?
    ''', (status, spot_label))
    conn.commit()
    conn.close()

def get_all_spots():
    """Get all parking spots"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spots ORDER BY spot_label')
    spots = cursor.fetchall()
    conn.close()
    return [dict(spot) for spot in spots]

def get_available_spots_count():
    """Get count of available spots"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'available'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_spot_by_label(spot_label):
    """Get a specific spot by its label"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spots WHERE spot_label = ?', (spot_label,))
    spot = cursor.fetchone()
    conn.close()
    return dict(spot) if spot else None

def create_booking(spot_label, user_name, user_phone, user_email, car_type, arrival_time, duration):
    """Create a new booking"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Create booking
        cursor.execute('''
            INSERT INTO bookings (spot_label, user_name, user_phone, user_email, car_type, arrival_time, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (spot_label, user_name, user_phone, user_email, car_type, arrival_time, duration))
        
        # Update spot status to reserved
        cursor.execute('''
            UPDATE spots SET status = 'reserved', last_updated = CURRENT_TIMESTAMP
            WHERE spot_label = ?
        ''', (spot_label,))
        
        # Log the booking
        cursor.execute('''
            INSERT INTO parking_logs (spot_label, action, user_name, details)
            VALUES (?, 'booked', ?, ?)
        ''', (spot_label, user_name, f"Reserved for {duration} hours"))
        
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        return booking_id
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def get_active_bookings():
    """Get all active bookings - shows real bookings + occupied spots with random data"""
    import random
    from datetime import datetime, timedelta
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get real active bookings
    cursor.execute('''
        SELECT * FROM bookings 
        WHERE status = 'active' 
        ORDER BY arrival_time DESC
    ''')
    real_bookings = cursor.fetchall()
    bookings_dict = {dict(b)['spot_label']: dict(b) for b in real_bookings}
    
    # Get all occupied spots
    cursor.execute('''
        SELECT spot_label FROM spots 
        WHERE status = 'occupied'
    ''')
    occupied_spots = cursor.fetchall()
    conn.close()
    
    # Random data pools for generating fake bookings
    names = ['Ali Khan', 'Sara Ahmed', 'Hassan Malik', 'Fatima Noor', 'Usman Shah', 
             'Ayesha Iqbal', 'Bilal Raza', 'Zainab Ali', 'Ahmed Hussain', 'Maryam Siddiq',
             'Kamran Abbas', 'Hira Farooq', 'Imran Yousaf', 'Nida Rasheed', 'Faisal Tariq']
    car_types = ['Sedan', 'SUV', 'Hatchback', 'Pickup', 'Coupe']
    
    result_bookings = []
    
    # Add all occupied spots to the bookings list
    for spot in occupied_spots:
        spot_label = spot[0]
        
        # If spot has real booking, use it
        if spot_label in bookings_dict:
            result_bookings.append(bookings_dict[spot_label])
        else:
            # Generate random booking data for occupied spots without bookings
            arrival_time = datetime.now() - timedelta(hours=random.randint(1, 6))
            result_bookings.append({
                'id': random.randint(10000, 99999),
                'spot_label': spot_label,
                'user_name': random.choice(names),
                'user_phone': f'03{random.randint(100000000, 999999999)}',
                'car_type': random.choice(car_types),
                'arrival_time': arrival_time.strftime('%H:%M'),
                'duration': random.randint(2, 8),
                'status': 'active'
            })
    
    return result_bookings

def cancel_booking(booking_id):
    """Cancel a booking"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get booking details
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()
    
    if booking:
        # Update booking status
        cursor.execute('''
            UPDATE bookings SET status = 'cancelled'
            WHERE id = ?
        ''', (booking_id,))
        
        # Update spot status back to available
        cursor.execute('''
            UPDATE spots SET status = 'available', last_updated = CURRENT_TIMESTAMP
            WHERE spot_label = ?
        ''', (booking['spot_label'],))
        
        # Log the cancellation
        cursor.execute('''
            INSERT INTO parking_logs (spot_label, action, user_name, details)
            VALUES (?, 'cancelled', ?, 'Booking cancelled by user')
        ''', (booking['spot_label'], booking['user_name']))
        
        conn.commit()
    
    conn.close()

def add_to_waitlist(user_name, user_phone, user_email, car_type):
    """Add user to waitlist"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO waitlist (user_name, user_phone, user_email, car_type)
        VALUES (?, ?, ?, ?)
    ''', (user_name, user_phone, user_email, car_type))
    conn.commit()
    conn.close()

def add_feedback(user_name, rating, comment):
    """Add user feedback"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (user_name, rating, comment)
        VALUES (?, ?, ?)
    ''', (user_name, rating, comment))
    conn.commit()
    conn.close()

def get_all_feedback():
    """Get all feedback"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedback ORDER BY timestamp DESC')
    feedback = cursor.fetchall()
    conn.close()
    return [dict(f) for f in feedback]

def get_parking_logs(limit=100):
    """Get recent parking logs"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM parking_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    logs = cursor.fetchall()
    conn.close()
    return [dict(log) for log in logs]

def record_occupancy_stats():
    """Record current occupancy statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM spots")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'occupied'")
    occupied = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'available'")
    available = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'reserved'")
    reserved = cursor.fetchone()[0]
    
    cursor.execute('''
        INSERT INTO occupancy_stats (total_spots, occupied_spots, available_spots, reserved_spots)
        VALUES (?, ?, ?, ?)
    ''', (total, occupied, available, reserved))
    
    conn.commit()
    conn.close()

def get_occupancy_trends(hours=24):
    """Get occupancy trends for the last N hours"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM occupancy_stats 
        WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ORDER BY timestamp ASC
    ''', (hours,))
    stats = cursor.fetchall()
    conn.close()
    return [dict(stat) for stat in stats]

# User Authentication Functions
def create_user(email, password_hash, name, phone):
    """Create a new user account"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (email, password_hash, name, phone)
            VALUES (?, ?, ?, ?)
        ''', (email, password_hash, name, phone))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None
