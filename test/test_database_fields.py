#!/usr/bin/env python3
"""
Test script to verify that the new gender and preferred_bot fields exist in the database
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Global counter for unique phone numbers
_phone_counter = 0

def _unique_phone_number():
    """Generate a unique phone number for this test"""
    global _phone_counter
    _phone_counter += 1
    # Use process ID + counter to ensure uniqueness
    return f"1234567{os.getpid()}{_phone_counter}"

def test_database_fields():
    """Test that the new fields exist in the database."""
    print("Testing Database Fields...")
    print("=" * 50)
    
    # Get database connection details from environment
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'nazarriya')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', '')
    
    if not db_password:
        print("❌ POSTGRES_PASSWORD environment variable not set")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Connected to database successfully")
        
        # Test 1: Check if the new columns exist
        print("\n1. Checking if new columns exist...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('gender', 'preferred_bot', 'phone_number')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        expected_columns = {'gender', 'preferred_bot', 'phone_number'}
        found_columns = {col['column_name'] for col in columns}
        
        if expected_columns.issubset(found_columns):
            print("✅ All new columns exist!")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']}, nullable: {col['is_nullable']}")
        else:
            missing = expected_columns - found_columns
            print(f"❌ Missing columns: {missing}")
            return False
        
        # Test 2: Check if we can insert data with the new fields
        print("\n2. Testing data insertion with new fields...")
        test_email = f"test_db_{int(os.getpid())}@example.com"
                
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, phone_number, first_name, age, gender, preferred_language, state, preferred_bot)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, email, phone_number, gender, preferred_bot
        """, (
            test_email, 
            'hashed_password_123', 
            _unique_phone_number(),
            'Test User', 
            30, 
            'F', 
            'English', 
            'Test State', 
            'R'
        ))
        
        inserted_user = cursor.fetchone()
        print(f"✅ Data insertion successful!")
        print(f"   User ID: {inserted_user['id']}")
        print(f"   Email: {inserted_user['email']}")
        print(f"   Phone Number: {inserted_user['phone_number']}")
        print(f"   Gender: {inserted_user['gender']}")
        print(f"   Preferred Bot: {inserted_user['preferred_bot']}")
        
        # Test 3: Check if we can query the new fields
        print("\n3. Testing data retrieval with new fields...")
        cursor.execute("""
            SELECT id, email, phone_number, first_name, age, gender, preferred_language, state, preferred_bot
            FROM users 
            WHERE email = %s
        """, (test_email,))
        
        retrieved_user = cursor.fetchone()
        if retrieved_user:
            print("✅ Data retrieval successful!")
            print(f"   Retrieved phone_number: {retrieved_user['phone_number']}")
            print(f"   Retrieved gender: {retrieved_user['gender']}")
            print(f"   Retrieved preferred_bot: {retrieved_user['preferred_bot']}")
            
            # Verify the data matches what we inserted
            if (retrieved_user['gender'] == 'F' and retrieved_user['preferred_bot'] == 'R'):
                print("✅ Retrieved data matches inserted data!")
            else:
                print("❌ Retrieved data doesn't match inserted data!")
                return False
        else:
            print("❌ Could not retrieve inserted data")
            return False
        
        # Test 4: Test nullable behavior
        print("\n4. Testing nullable behavior...")
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, phone_number)
            VALUES (gen_random_uuid(), %s, %s, %s)
            RETURNING id, email, gender, preferred_bot
        """, (
            f"test_null_{int(os.getpid())}@example.com", 
            'hashed_password_123', 
            _unique_phone_number()
        ))
        
        null_user = cursor.fetchone()
        print(f"✅ Null field insertion successful!")
        print(f"   User ID: {null_user['id']}")
        print(f"   Gender: {null_user['gender']}")
        print(f"   Preferred Bot: {null_user['preferred_bot']}")
        
        # Verify null values are handled correctly
        if null_user['gender'] is None and null_user['preferred_bot'] is None:
            print("✅ Null values are properly handled!")
        else:
            print("❌ Null values not properly handled!")
            return False
        
        # Clean up test data
        print("\n5. Cleaning up test data...")
        try:
            # First delete any related chat sessions
            cursor.execute("DELETE FROM chat_sessions WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'test_%')")
            # Then delete the users
            cursor.execute("DELETE FROM users WHERE email LIKE 'test_%'")
            conn.commit()
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Warning during cleanup: {e}")
            # Continue anyway since the test was successful
        
        cursor.close()
        conn.close()
        print("✅ Database connection closed")
        
        print("\n" + "=" * 50)
        print("🎉 Database fields test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during database test: {e}")
        return False

if __name__ == "__main__":
    success = test_database_fields()
    sys.exit(0 if success else 1)
