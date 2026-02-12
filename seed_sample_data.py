"""
Seed database with realistic sample data
Makes the system look active and realistic with occupied/reserved spots,
active bookings, and activity logs
"""
from database import (
    get_db, get_all_spots, update_spot_status, create_booking,
    record_occupancy_stats, USE_POSTGRES, PARAM_PLACEHOLDER
)
from datetime import datetime, timedelta
import random

def seed_sample_data():
    """Seed the database with realistic sample data"""
    print("\n" + "="*60)
    print("SEEDING SAMPLE DATA FOR REALISTIC DISPLAY")
    print("="*60)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute('SELECT COUNT(*) FROM bookings')
    existing_bookings = cursor.fetchone()[0]
    
    if existing_bookings > 5:  # Already has data
        print("✓ Sample data already exists, skipping seed...")
        conn.close()
        return
    
    print("\n[1] Setting up realistic parking spot statuses...")
    
    # Get all spots
    spots = get_all_spots()
    if len(spots) == 0:
        print("✗ No spots found, skipping seed")
        conn.close()
        return
    
    # Sample names and data
    names = [
        'Ali Khan', 'Sara Ahmed', 'Hassan Malik', 'Fatima Noor', 'Usman Shah',
        'Ayesha Iqbal', 'Bilal Raza', 'Zainab Ali', 'Ahmed Hussain', 'Maryam Siddiq',
        'Kamran Abbas', 'Hira Farooq', 'Imran Yousaf', 'Nida Rasheed', 'Faisal Tariq',
        'Sana Butt', 'Adnan Riaz', 'Rabia Khan', 'Shahid Aziz', 'Noor Fatima'
    ]
    
    car_types = ['Sedan', 'SUV', 'Hatchback', 'Pickup', 'Coupe']
    
    # Randomly occupy 30-40% of spots
    num_to_occupy = int(len(spots) * 0.35)  # 35% occupied
    num_to_reserve = int(len(spots) * 0.15)  # 15% reserved
    
    occupied_spots = random.sample(spots, num_to_occupy)
    available_for_reserve = [s for s in spots if s not in occupied_spots]
    reserved_spots = random.sample(available_for_reserve, min(num_to_reserve, len(available_for_reserve)))
    
    # Set occupied spots
    for spot in occupied_spots:
        update_spot_status(spot['spot_label'], 'occupied')
    
    print(f"✓ Set {len(occupied_spots)} spots as occupied")
    
    # Create bookings for reserved spots
    bookings_created = 0
    for spot in reserved_spots:
        name = random.choice(names)
        phone = f"03{random.randint(10000000, 99999999)}"
        email = f"{name.lower().replace(' ', '.')}@gmail.com"
        car_type = random.choice(car_types)
        
        # Arrival time: some past, some future
        hours_offset = random.randint(-2, 8)
        arrival_time = datetime.now() + timedelta(hours=hours_offset)
        duration = random.choice([1, 2, 3, 4])
        
        try:
            booking_id = create_booking(
                spot['spot_label'], name, phone, email, 
                car_type, arrival_time, duration
            )
            if booking_id:
                bookings_created += 1
        except:
            pass
    
    print(f"✓ Created {bookings_created} active bookings")
    
    print("\n[2] Adding historical parking logs...")
    
    # Add some historical logs
    log_actions = ['occupied', 'vacated', 'booked', 'cancelled']
    logs_to_create = 30
    
    for i in range(logs_to_create):
        spot = random.choice(spots)
        name = random.choice(names)
        action = random.choice(log_actions)
        hours_ago = random.randint(1, 48)
        
        details_map = {
            'occupied': f'Vehicle parked',
            'vacated': f'Vehicle left after {random.randint(1,4)} hours',
            'booked': f'Reserved for {random.randint(1,4)} hours',
            'cancelled': 'Booking cancelled by user'
        }
        
        query = f'''
            INSERT INTO parking_logs (spot_label, action, user_name, timestamp, details)
            VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
        '''
        
        if USE_POSTGRES:
            timestamp = f"NOW() - INTERVAL '{hours_ago} hours'"
            cursor.execute(
                f'''INSERT INTO parking_logs (spot_label, action, user_name, timestamp, details)
                VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, NOW() - INTERVAL '{hours_ago} hours', {PARAM_PLACEHOLDER})''',
                (spot['spot_label'], action, name, details_map[action])
            )
        else:
            timestamp = (datetime.now() - timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(query, (spot['spot_label'], action, name, timestamp, details_map[action]))
    
    conn.commit()
    print(f"✓ Added {logs_to_create} historical log entries")
    
    print("\n[3] Recording occupancy statistics...")
    
    # Add historical occupancy stats
    for hours_ago in range(24, 0, -2):  # Every 2 hours for last 24 hours
        total_spots = len(spots)
        occupied = random.randint(int(total_spots * 0.2), int(total_spots * 0.6))
        reserved = random.randint(int(total_spots * 0.1), int(total_spots * 0.25))
        available = total_spots - occupied - reserved
        
        if USE_POSTGRES:
            cursor.execute(f'''
                INSERT INTO occupancy_stats (timestamp, total_spots, occupied_spots, available_spots, reserved_spots)
                VALUES (NOW() - INTERVAL '{hours_ago} hours', {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
            ''', (total_spots, occupied, available, reserved))
        else:
            timestamp = (datetime.now() - timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f'''
                INSERT INTO occupancy_stats (timestamp, total_spots, occupied_spots, available_spots, reserved_spots)
                VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
            ''', (timestamp, total_spots, occupied, available, reserved))
    
    conn.commit()
    print(f"✓ Added 12 occupancy trend data points")
    
    print("\n[4] Adding sample feedback...")
    
    # Add some positive feedback
    feedback_data = [
        ("Ali Khan", 5, "Excellent parking system! Very easy to find spots."),
        ("Sara Ahmed", 4, "Great experience, booking was smooth."),
        ("Hassan Malik", 5, "Love the real-time availability feature!"),
        ("Ayesha Iqbal", 4, "Very convenient and user-friendly interface."),
    ]
    
    for name, rating, comment in feedback_data:
        query = f'''
            INSERT INTO feedback (user_name, rating, comment)
            VALUES ({PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER}, {PARAM_PLACEHOLDER})
        '''
        cursor.execute(query, (name, rating, comment))
    
    conn.commit()
    print(f"✓ Added {len(feedback_data)} feedback entries")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ SAMPLE DATA SEEDED SUCCESSFULLY!")
    print("="*60)
    print(f"  - {len(occupied_spots)} spots occupied")
    print(f"  - {bookings_created} active bookings")
    print(f"  - {logs_to_create} activity logs")
    print(f"  - 12 occupancy trend points")
    print(f"  - {len(feedback_data)} feedback entries")
    print("="*60 + "\n")

if __name__ == '__main__':
    from database import init_db, initialize_spots
    import pickle
    
    # Initialize database first
    init_db()
    
    # Load and initialize spots
    try:
        with open('CarParkPos', 'rb') as f:
            spot_positions = pickle.load(f)
        initialize_spots(spot_positions)
    except:
        print("Using existing spots")
    
    # Seed sample data
    seed_sample_data()
