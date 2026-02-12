"""Test the updated database with dual PostgreSQL/SQLite support"""
from database import init_db, create_user, get_user_by_email, USE_POSTGRES, DATABASE_URL
import hashlib

print("="*60)
print("DATABASE CONFIGURATION TEST")
print("="*60)
print(f"Using PostgreSQL: {USE_POSTGRES}")
if USE_POSTGRES:
    print(f"Database URL: {DATABASE_URL[:30]}..." if DATABASE_URL else "None")
else:
    from database import DATABASE
    print(f"SQLite Database: {DATABASE}")

print("\n" + "="*60)
print("INITIALIZING DATABASE")
print("="*60)
init_db()

print("\n" + "="*60)
print("TESTING USER REGISTRATION")
print("="*60)

# Test data
test_email = "rendertest@gmail.com"
test_password = "TestPass123!"
test_name = "Render Test User"
test_phone = "0398765432"

# Check if user exists
existing = get_user_by_email(test_email)
if existing:
    print(f"✓ User '{test_email}' already exists")
    print(f"  Name: {existing['name']}")
    print(f"  Phone: {existing['phone']}")
else:
    print(f"Creating new user: {test_email}")
    password_hash = hashlib.sha256(test_password.encode()).hexdigest()
    user_id = create_user(test_email, password_hash, test_name, test_phone)
    
    if user_id:
        print(f"✓ User created successfully with ID: {user_id}")
        
        # Verify
        user = get_user_by_email(test_email)
        if user:
            print(f"✓ User verified:")
            print(f"  ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['name']}")
            print(f"  Phone: {user['phone']}")
        else:
            print("✗ User not found after creation")
    else:
        print("✗ User creation failed")

print("\n" + "="*60)
print("TEST COMPLETED SUCCESSFULLY")
print("="*60)
