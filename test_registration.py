"""Test script to verify registration functionality"""
from database import init_db, create_user, get_user_by_email
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database
init_db()
print("✓ Database initialized")

# Test data
test_email = "test@gmail.com"
test_password = "TestPass123!"
test_name = "Test User"
test_phone = "0312345678"

# Check if user already exists
existing_user = get_user_by_email(test_email)
if existing_user:
    print(f"✗ User with email '{test_email}' already exists")
    print(f"  Existing user: {dict(existing_user)}")
else:
    print(f"✓ Email '{test_email}' is available")

# Try to create user
password_hash = hash_password(test_password)
user_id = create_user(test_email, password_hash, test_name, test_phone)

if user_id:
    print(f"✓ User created successfully with ID: {user_id}")
    
    # Verify user was created
    created_user = get_user_by_email(test_email)
    if created_user:
        print(f"✓ User verified in database:")
        print(f"  ID: {created_user['id']}")
        print(f"  Email: {created_user['email']}")
        print(f"  Name: {created_user['name']}")
        print(f"  Phone: {created_user['phone']}")
    else:
        print("✗ User not found after creation")
else:
    print("✗ User creation failed")

print("\n" + "="*50)
print("Registration test completed")
print("="*50)
