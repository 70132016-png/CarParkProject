"""
Database Demonstration Script for Evaluators
This script shows the complete database structure and current data
"""

import sqlite3
from datetime import datetime
import os

DATABASE = 'parkease.db'

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def show_database_location():
    """Show where the database file is located"""
    print_section("DATABASE LOCATION")
    db_path = os.path.abspath(DATABASE)
    print(f"\n📁 Database File: {DATABASE}")
    print(f"📍 Full Path: {db_path}")
    
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        modified = datetime.fromtimestamp(os.path.getmtime(db_path))
        print(f"💾 Size: {size:,} bytes ({size/1024:.2f} KB)")
        print(f"📅 Last Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ Database file exists and is accessible")
    else:
        print("❌ Database file not found!")

def show_table_structure():
    """Show all tables and their structure"""
    print_section("DATABASE SCHEMA (Tables & Structure)")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n📊 Total Tables: {len(tables)}\n")
    
    for table_name in tables:
        table_name = table_name[0]
        print(f"\n🔷 Table: {table_name.upper()}")
        print("-" * 80)
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"{'Column Name':<25} {'Type':<15} {'Nullable':<10} {'Key':<10}")
        print("-" * 80)
        for col in columns:
            col_id, name, col_type, not_null, default, pk = col
            nullable = "NO" if not_null else "YES"
            key = "PRIMARY" if pk else ""
            print(f"{name:<25} {col_type:<15} {nullable:<10} {key:<10}")
    
    conn.close()

def show_table_counts():
    """Show record counts for all tables"""
    print_section("DATA SUMMARY (Record Counts)")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n{'Table Name':<25} {'Total Records':<15}")
    print("-" * 40)
    
    for table_name in tables:
        table_name = table_name[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name:<25} {count:<15}")
    
    conn.close()

def show_sample_data(table_name, limit=5):
    """Show sample data from a specific table"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        if rows:
            print(f"\n📋 Sample Records from {table_name.upper()} (showing up to {limit} records):")
            print("-" * 80)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            for i, row in enumerate(rows, 1):
                print(f"\nRecord {i}:")
                for col in columns:
                    value = row[col]
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    print(f"  {col:<20}: {value}")
        else:
            print(f"\n⚠️  No records found in {table_name}")
    
    except sqlite3.Error as e:
        print(f"\n❌ Error reading {table_name}: {e}")
    
    conn.close()

def show_parking_stats():
    """Show current parking statistics"""
    print_section("REAL-TIME PARKING STATISTICS")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Total spots
        cursor.execute("SELECT COUNT(*) FROM spots")
        total_spots = cursor.fetchone()[0]
        
        # Available spots
        cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'available'")
        available = cursor.fetchone()[0]
        
        # Occupied spots
        cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'occupied'")
        occupied = cursor.fetchone()[0]
        
        # Reserved spots
        cursor.execute("SELECT COUNT(*) FROM spots WHERE status = 'reserved'")
        reserved = cursor.fetchone()[0]
        
        # Active bookings
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'active'")
        active_bookings = cursor.fetchone()[0]
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        print(f"""
🅿️  PARKING SPOTS:
   Total Spots:      {total_spots}
   Available:        {available} ({available/total_spots*100:.1f}%)
   Occupied:         {occupied} ({occupied/total_spots*100:.1f}%)
   Reserved:         {reserved} ({reserved/total_spots*100:.1f}%)

📝 BOOKINGS:
   Active Bookings:  {active_bookings}

👥 USERS:
   Total Users:      {total_users}
""")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()

def show_recent_activity():
    """Show recent parking activity"""
    print_section("RECENT ACTIVITY")
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Recent bookings
        cursor.execute("""
            SELECT spot_label, user_name, car_type, arrival_time, status 
            FROM bookings 
            ORDER BY booking_time DESC 
            LIMIT 5
        """)
        bookings = cursor.fetchall()
        
        if bookings:
            print("\n📅 Recent Bookings:")
            print("-" * 80)
            for booking in bookings:
                print(f"  Spot {booking['spot_label']}: {booking['user_name']} - {booking['car_type']} - Status: {booking['status']}")
        else:
            print("\n⚠️  No bookings found")
        
        # Recent logs
        cursor.execute("""
            SELECT spot_label, action, user_name, timestamp 
            FROM parking_logs 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        logs = cursor.fetchall()
        
        if logs:
            print("\n📜 Recent Parking Logs:")
            print("-" * 80)
            for log in logs:
                print(f"  {log['timestamp']}: {log['action']} - Spot {log['spot_label']}")
        else:
            print("\n⚠️  No logs found")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()

def main():
    """Main demonstration function"""
    print("\n" + "="*80)
    print("  🚗 PARKEASE DATABASE DEMONSTRATION")
    print("  Smart Parking Management System")
    print("="*80)
    
    # 1. Show database location
    show_database_location()
    
    # 2. Show table structure
    show_table_structure()
    
    # 3. Show record counts
    show_table_counts()
    
    # 4. Show parking statistics
    show_parking_stats()
    
    # 5. Show recent activity
    show_recent_activity()
    
    # 6. Show sample data from key tables
    print_section("SAMPLE DATA FROM KEY TABLES")
    
    important_tables = ['users', 'spots', 'bookings', 'parking_logs']
    for table in important_tables:
        show_sample_data(table, limit=3)
    
    print("\n" + "="*80)
    print("  ✅ Database Demonstration Complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
