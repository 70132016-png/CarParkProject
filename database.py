import sqlite3
from datetime import datetime
import json
import os

# Check if running on Render (PostgreSQL) or locally (SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
    # Fix for Render's postgres:// URL (should be postgresql://)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    PARAM_PLACEHOLDER = '%s'
else:
    # Use absolute path for SQLite database in local development
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parkease.db')
    PARAM_PLACEHOLDER = '?'

def get_db():
    try:
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        else:
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Adjust SQL syntax based on database type
    if USE_POSTGRES:
        id_type = "SERIAL PRIMARY KEY"
        text_type = "VARCHAR"
        timestamp_default = "DEFAULT CURRENT_TIMESTAMP"
    else:
        id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        text_type = "TEXT"
        timestamp_default = "DEFAULT CURRENT_TIMESTAMP"
    
    # Users table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            email {text_type} UNIQUE NOT NULL,
            password_hash {text_type} NOT NULL,
            name {text_type} NOT NULL,
            phone {text_type} NOT NULL,
            created_at TIMESTAMP {timestamp_default}
        )
    ''')
    
    # Parking spots table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS spots (
            id {id_type},
            spot_label {text_type} UNIQUE NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            status {text_type} DEFAULT 'available',
            location {text_type} DEFAULT 'Main Parking',
            last_updated TIMESTAMP {timestamp_default}
        )
    ''')
    
    # Bookings table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS bookings (
            id {id_type},
            spot_label {text_type} NOT NULL,
            user_name {text_type} NOT NULL,
            user_phone {text_type} NOT NULL,
            user_email {text_type},
            car_type {text_type} NOT NULL,
            arrival_time TIMESTAMP NOT NULL,
            duration INTEGER NOT NULL,
            booking_time TIMESTAMP {timestamp_default},
            status {text_type} DEFAULT 'active',
            grace_period_end TIMESTAMP
        )
    ''')
    
    # Parking logs table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS parking_logs (
            id {id_type},
            spot_label {text_type} NOT NULL,
            action {text_type} NOT NULL,
            user_name {text_type},
            timestamp TIMESTAMP {timestamp_default},
            details {text_type}
        )
    ''')
    
    # Feedback table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS feedback (
            id {id_type},
            user_name {text_type} NOT NULL,
            rating INTEGER NOT NULL,
            comment {text_type},
            timestamp TIMESTAMP {timestamp_default}
        )
    ''')
    
    # Wait list table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS waitlist (
            id {id_type},
            user_name {text_type} NOT NULL,
            user_phone {text_type} NOT NULL,
            user_email {text_type},
            car_type {text_type} NOT NULL,
            requested_time TIMESTAMP {timestamp_default},
            status {text_type} DEFAULT 'waiting'
        )
    ''')
    
    # Favorites table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS favorites (
            id {id_type},
            user_phone {text_type} NOT NULL,
            location {text_type} NOT NULL,
            timestamp TIMESTAMP {timestamp_default}
        )
    ''')
    
    # Analytics table for tracking occupancy
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS occupancy_stats (
            id {id_type},
            timestamp TIMESTAMP {timestamp_default},
            total_spots INTEGER,
            occupied_spots INTEGER,
            available_spots INTEGER,
            reserved_spots INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    
    db_location = DATABASE_URL if USE_POSTGRES else DATABASE
    print(f"Database initialized successfully at: {db_location}")

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
            
            query = f'''
                INSERT INTO spots (spot_label, x, y, width, height, status)
                VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, 'available')
            '''
            cursor.execute(query, (label, pos[0], pos[1], 103, 43))
            labels.append(label)
        
        conn.commit()
        print(f"Initialized {len(sorted_positions)} parking spots")
    
    conn.close()

def update_spot_status(spot_label, status):
    """Update the status of a parking spot"""
    conn = get_db()
    cursor = conn.cursor()
    query = f'''
        UPDATE spots 
        SET status = {PARAM_PLACEHOLDER}, last_updated = CURRENT_TIMESTAMP
        WHERE spot_label = {PARAM_PLACEHOLDER}
    '''
    cursor.execute(query, (status, spot_label))
    conn.commit()
    conn.close()

def get_all_spots():
    """Get all parking spots"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM spots ORDER BY spot_label')
    spots = cursor.fetchall()
    conn.close()
    
    if USE_POSTGRES:
        columns = ['id', 'spot_label', 'x', 'y', 'width', 'height', 'status', 'location', 'last_updated']
        return [dict(zip(columns, spot)) for spot in spots]
    else:
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
    query = f'SELECT * FROM spots WHERE spot_label = {PARAM_PLACEHOLDER}'
    cursor.execute(query, (spot_label,))
    spot = cursor.fetchone()
    conn.close()
    
    if spot:
        if USE_POSTGRES:
            columns = ['id', 'spot_label', 'x', 'y', 'width', 'height', 'status', 'location', 'last_updated']
            return dict(zip(columns, spot))
        else:
            return dict(spot)
    return None

def create_booking(spot_label, user_name, user_phone, user_email, car_type, arrival_time, duration):
    """Create a new booking"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Create booking
        query = f'''
            INSERT INTO bookings (spot_label, user_name, user_phone, user_email, car_type, arrival_time, duration)
            VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
        '''
        cursor.execute(query, (spot_label, user_name, user_phone, user_email, car_type, arrival_time, duration))
        
        # Update spot status to reserved
        query = f'''
            UPDATE spots SET status = 'reserved', last_updated = CURRENT_TIMESTAMP
            WHERE spot_label = {PARAM_PLACEHOLDER}
        '''
        cursor.execute(query, (spot_label,))
        
        # Log the booking
        query = f'''
            INSERT INTO parking_logs (spot_label, action, user_name, details)
            VALUES ({PARAM_PLACEHOLDER}, 'booked', {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
        '''
        cursor.execute(query, (spot_label, user_name, f"Reserved for {duration} hours"))
        
        conn.commit()
        
        if USE_POSTGRES:
            cursor.execute('SELECT lastval()')
            booking_id = cursor.fetchone()[0]
        else:
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
    
    if USE_POSTGRES:
        booking_columns = ['id', 'spot_label', 'user_name', 'user_phone', 'user_email', 'car_type', 'arrival_time', 'duration', 'booking_time', 'status', 'grace_period_end']
        bookings_dict = {dict(zip(booking_columns, b))['spot_label']: dict(zip(booking_columns, b)) for b in real_bookings}
    else:
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
    query = f'SELECT * FROM bookings WHERE id = {PARAM_PLACEHOLDER}'
    cursor.execute(query, (booking_id,))
    booking = cursor.fetchone()
    
    if booking:
        # Update booking status
        query = f'''
            UPDATE bookings SET status = 'cancelled'
            WHERE id = {PARAM_PLACEHOLDER}
        '''
        cursor.execute(query, (booking_id,))
        
        # Update spot status back to available
        query = f'''
            UPDATE spots SET status = 'available', last_updated = CURRENT_TIMESTAMP
            WHERE spot_label = {PARAM_PLACEHOLDER}
        '''
        cursor.execute(query, (booking_dict['spot_label'],))
        
        # Log the cancellation
        if USE_POSTGRES:
            booking_columns = ['id', 'spot_label', 'user_name', 'user_phone', 'user_email', 'car_type', 'arrival_time', 'duration', 'booking_time', 'status', 'grace_period_end']
            booking_dict = dict(zip(booking_columns, booking))
        else:
            booking_dict = dict(booking)
        
        query = f'''
            INSERT INTO parking_logs (spot_label, action, user_name, details)
            VALUES ({PARAM_PLACEHOLDER}, 'cancelled', {PARAM_PLACEHOLDER}, 'Booking cancelled by user')
        '''
        cursor.execute(query, (booking_dict['spot_label'], booking_dict['user_name']))
        
        conn.commit()
    
    conn.close()

def add_to_waitlist(user_name, user_phone, user_email, car_type):
    """Add user to waitlist"""
    conn = get_db()
    cursor = conn.cursor()
    query = f'''
        INSERT INTO waitlist (user_name, user_phone, user_email, car_type)
        VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
    '''
    cursor.execute(query, (user_name, user_phone, user_email, car_type))
    conn.commit()
    conn.close()

def add_feedback(user_name, rating, comment):
    """Add user feedback"""
    conn = get_db()
    cursor = conn.cursor()
    query = f'''
        INSERT INTO feedback (user_name, rating, comment)
        VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
    '''
    cursor.execute(query, (user_name, rating, comment))
    conn.commit()
    conn.close()

def get_all_feedback():
    """Get all feedback"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedback ORDER BY timestamp DESC')
    feedback = cursor.fetchall()
    conn.close()
    
    if USE_POSTGRES:
        columns = ['id', 'user_name', 'rating', 'comment', 'timestamp']
        return [dict(zip(columns, f)) for f in feedback]
    else:
        return [dict(f) for f in feedback]

def get_parking_logs(limit=100):
    """Get recent parking logs"""
    conn = get_db()
    cursor = conn.cursor()
    query = f'SELECT * FROM parking_logs ORDER BY timestamp DESC LIMIT {PARAM_PLACEHOLDER}'
    cursor.execute(query, (limit,))
    logs = cursor.fetchall()
    conn.close()
    
    if USE_POSTGRES:
        columns = ['id', 'spot_label', 'action', 'user_name', 'timestamp', 'details']
        return [dict(zip(columns, log)) for log in logs]
    else:
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
    
    query = f'''
        INSERT INTO occupancy_stats (total_spots, occupied_spots, available_spots, reserved_spots)
        VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
    '''
    cursor.execute(query, (total, occupied, available, reserved))
    
    conn.commit()
    conn.close()

def get_occupancy_trends(hours=24):
    """Get occupancy trends for the last N hours"""
    conn = get_db()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        query = f'''
            SELECT * FROM occupancy_stats 
            WHERE timestamp >= NOW() - INTERVAL '{hours} hours'
            ORDER BY timestamp ASC
        '''
        cursor.execute(query)
    else:
        query = f'''
            SELECT * FROM occupancy_stats 
            WHERE timestamp >= datetime('now', '-' || {PARAM_PLACEHOLDER} || ' hours')
            ORDER BY timestamp ASC
        '''
        cursor.execute(query, (hours,))
    
    stats = cursor.fetchall()
    conn.close()
    
    if USE_POSTGRES:
        columns = ['id', 'timestamp', 'total_spots', 'occupied_spots', 'available_spots', 'reserved_spots']
        return [dict(zip(columns, stat)) for stat in stats]
    else:
        return [dict(stat) for stat in stats]

# User Authentication Functions
def create_user(email, password_hash, name, phone):
    """Create a new user account"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        query = f'''
            INSERT INTO users (email, password_hash, name, phone)
            VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
        '''
        cursor.execute(query, (email, password_hash, name, phone))
        conn.commit()
        
        if USE_POSTGRES:
            # PostgreSQL doesn't have lastrowid, need to fetch it
            cursor.execute('SELECT lastval()')
            user_id = cursor.fetchone()[0]
        else:
            user_id = cursor.lastrowid
            
        conn.close()
        return user_id
    except (sqlite3.IntegrityError if not USE_POSTGRES else psycopg2.IntegrityError):
        conn.close()
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.close()
        return None

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db()
    cursor = conn.cursor()
    query = f'SELECT * FROM users WHERE email = {PARAM_PLACEHOLDER}'
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        if USE_POSTGRES:
            # Convert tuple to dict for PostgreSQL
            columns = ['id', 'email', 'password_hash', 'name', 'phone', 'created_at']
            return dict(zip(columns, user))
        else:
            return dict(user)
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    query = f'SELECT * FROM users WHERE id = {PARAM_PLACEHOLDER}'
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        if USE_POSTGRES:
            # Convert tuple to dict for PostgreSQL
            columns = ['id', 'email', 'password_hash', 'name', 'phone', 'created_at']
            return dict(zip(columns, user))
        else:
            return dict(user)
    return None
