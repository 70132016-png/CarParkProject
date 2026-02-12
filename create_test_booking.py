import sqlite3
from datetime import datetime

conn = sqlite3.connect('parkease.db')
cursor = conn.cursor()

# Create a test booking
cursor.execute('''
    INSERT INTO bookings (spot_label, user_name, user_phone, user_email, car_type, arrival_time, duration, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('A1', 'Test User', '03281781881', 'test@example.com', 'Sedan', datetime.now().isoformat(), 2, 'active'))

# Update spot A1 to reserved
cursor.execute('UPDATE spots SET status = "reserved" WHERE spot_label = "A1"')

conn.commit()

print('✅ Test booking created successfully!')
print('=' * 40)
print('Phone Number: 03281781881')
print('Spot: A1')
print('User: Test User')
print('Status: Active')
print('=' * 40)
print('\n🔍 Go to My Bookings page and enter: 03281781881')

conn.close()
