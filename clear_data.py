from database import get_db

conn = get_db()
cursor = conn.cursor()

cursor.execute('DELETE FROM bookings')
cursor.execute('DELETE FROM parking_logs')
cursor.execute('DELETE FROM occupancy_stats')
cursor.execute('DELETE FROM feedback')
cursor.execute("UPDATE spots SET status = 'available'")

conn.commit()
conn.close()

print("✓ Database cleared for fresh seed")
