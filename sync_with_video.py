"""
Script to manually sync database with video occupancy status
This simulates what main_detection.py does automatically
"""
import sqlite3

def sync_database_with_video():
    """Update database to match the carPark.mp4 video's actual occupancy"""
    
    # Based on visual inspection of carPark.mp4, these spots are typically OCCUPIED
    # You can adjust this list based on what you see in your video
    occupied_spots = [
        'A3', 'A5', 'A8', 'A9', 'A12', 'A15', 'A18', 'A21',
        'B2', 'B4', 'B7', 'B10', 'B13', 'B16', 'B19', 'B22',
        'C1', 'C6', 'C11', 'C14', 'C17', 'C20'
    ]
    
    conn = sqlite3.connect('parkease.db')
    cursor = conn.cursor()
    
    # First, set all spots to available
    print("Setting all spots to available...")
    cursor.execute("UPDATE spots SET status = 'available'")
    
    # Then mark the occupied ones
    print(f"Marking {len(occupied_spots)} spots as occupied...")
    for spot in occupied_spots:
        cursor.execute("""
            UPDATE spots 
            SET status = 'occupied'
            WHERE spot_label = ?
        """, (spot,))
        print(f"  - {spot}: OCCUPIED")
    
    conn.commit()
    
    # Show summary
    cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'available'")
    available = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'occupied'")
    occupied = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'reserved'")
    reserved = cursor.fetchone()[0]
    
    print("\n" + "="*50)
    print("DATABASE UPDATED!")
    print("="*50)
    print(f"✅ Available: {available}")
    print(f"🚗 Occupied: {occupied}")
    print(f"📅 Reserved: {reserved}")
    print(f"📊 Total: {available + occupied + reserved}")
    print("\n🔄 Refresh your browser to see changes!")
    print("="*50)
    
    conn.close()

if __name__ == "__main__":
    sync_database_with_video()
