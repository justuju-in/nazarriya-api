#!/usr/bin/env python3
"""
Test script to verify that the new gender and preferred_bot fields exist in the database
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# Global counter for unique phone numbers
_phone_counter = 0

def _unique_phone_number():
    """Generate a unique phone number for this test"""
    global _phone_counter
    _phone_counter += 1
    # Use process ID + timestamp + counter to ensure uniqueness across test runs
    import time
    timestamp = int(time.time() * 1000) % 1000000  # Last 6 digits of timestamp
    return f"1234567{timestamp}{_phone_counter}"

def _unique_phone_number_for_format_test():
    """Generate a unique phone number specifically for format testing"""
    global _phone_counter
    _phone_counter += 1
    import time
    timestamp = int(time.time() * 1000) % 1000000  # Last 6 digits of timestamp
    return f"9876543{timestamp}{_phone_counter}"

def cleanup_test_data(cursor, conn):
    """Clean up all test data created during tests"""
    try:
        print("\n🧹 Cleaning up test data...")
        
        # First, rollback any existing transaction to get to a clean state
        try:
            conn.rollback()
        except:
            pass  # Ignore rollback errors
        
        # Count test users before cleanup
        cursor.execute("SELECT COUNT(*) FROM users WHERE email LIKE 'test_%'")
        test_user_count = cursor.fetchone()[0]
        
        if test_user_count > 0:
            print(f"   Found {test_user_count} test users to clean up")
            
            # First delete any related chat sessions
            cursor.execute("DELETE FROM chat_sessions WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'test_%')")
            chat_sessions_deleted = cursor.rowcount
            if chat_sessions_deleted > 0:
                print(f"   Deleted {chat_sessions_deleted} related chat sessions")
            
            # Then delete the users
            cursor.execute("DELETE FROM users WHERE email LIKE 'test_%'")
            users_deleted = cursor.rowcount
            print(f"   Deleted {users_deleted} test users")
            
            # Also clean up any users with test phone numbers (as a backup)
            cursor.execute("DELETE FROM users WHERE phone_number LIKE '1234567%' OR phone_number LIKE '9876543%'")
            phone_users_deleted = cursor.rowcount
            if phone_users_deleted > 0:
                print(f"   Deleted {phone_users_deleted} users with test phone numbers")
            
            conn.commit()
            print("✅ Test data cleanup completed successfully")
            
            # Verify cleanup worked
            cursor.execute("SELECT COUNT(*) FROM users WHERE email LIKE 'test_%'")
            remaining_users = cursor.fetchone()[0]
            if remaining_users == 0:
                print("✅ Verification: All test users successfully removed")
            else:
                print(f"⚠️ Warning: {remaining_users} test users still remain")
                
        else:
            print("✅ No test users found to clean up")
            
    except Exception as e:
        print(f"⚠️ Warning during cleanup: {e}")
        # Try to rollback if commit failed
        try:
            conn.rollback()
            print("   Rolled back cleanup transaction")
        except:
            pass

def cleanup_with_fresh_connection():
    """Clean up test data using a fresh database connection"""
    try:
        print("\n🧹 Attempting cleanup with fresh connection...")
        
        # Get database connection details from environment
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'nazarriya')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', '')
        
        if not db_password:
            print("   ❌ POSTGRES_PASSWORD environment variable not set")
            return False
        
        # Create fresh connection for cleanup
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = conn.cursor()
        
        try:
            # Count test users
            cursor.execute("SELECT COUNT(*) FROM users WHERE email LIKE 'test_%'")
            test_user_count = cursor.fetchone()[0]
            
            if test_user_count > 0:
                print(f"   Found {test_user_count} test users to clean up")
                
                # First delete any related chat sessions
                cursor.execute("DELETE FROM chat_sessions WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'test_%')")
                chat_sessions_deleted = cursor.rowcount
                if chat_sessions_deleted > 0:
                    print(f"   Deleted {chat_sessions_deleted} related chat sessions")
                
                # Then delete the users
                cursor.execute("DELETE FROM users WHERE email LIKE 'test_%'")
                users_deleted = cursor.rowcount
                print(f"   Deleted {users_deleted} test users")
                
                # Also clean up any users with test phone numbers (as a backup)
                cursor.execute("DELETE FROM users WHERE phone_number LIKE '1234567%' OR phone_number LIKE '9876543%'")
                phone_users_deleted = cursor.rowcount
                if phone_users_deleted > 0:
                    print(f"   Deleted {phone_users_deleted} users with test phone numbers")
                
                conn.commit()
                print("✅ Test data cleanup completed successfully with fresh connection")
                
                # Verify cleanup worked
                cursor.execute("SELECT COUNT(*) FROM users WHERE email LIKE 'test_%'")
                remaining_users = cursor.fetchone()[0]
                if remaining_users == 0:
                    print("✅ Verification: All test users successfully removed")
                else:
                    print(f"⚠️ Warning: {remaining_users} test users still remain")
                    
            else:
                print("✅ No test users found to clean up")
                
        finally:
            cursor.close()
            conn.close()
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error during fresh connection cleanup: {e}")
        return False

def comprehensive_cleanup():
    """Comprehensive cleanup that removes all test data, even from multiple runs"""
    try:
        print("\n🧹 Comprehensive cleanup of all test data...")
        
        # Get database connection details from environment
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'nazarriya')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', '')
        
        if not db_password:
            print("❌ POSTGRES_PASSWORD environment variable not set")
            return False
        
        # Create connection for cleanup
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = conn.cursor()
        
        try:
            # Count all potential test users
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE email LIKE 'test_%' 
                   OR email LIKE 'duplicate_%'
                   OR phone_number LIKE '1234567%' 
                   OR phone_number LIKE '9876543%'
            """)
            total_test_users = cursor.fetchone()[0]
            
            if total_test_users > 0:
                print(f"   Found {total_test_users} test users to clean up")
                
                # First delete any related chat sessions
                cursor.execute("""
                    DELETE FROM chat_sessions 
                    WHERE user_id IN (
                        SELECT id FROM users 
                        WHERE email LIKE 'test_%' 
                           OR email LIKE 'duplicate_%'
                           OR phone_number LIKE '1234567%' 
                           OR phone_number LIKE '9876543%'
                    )
                """)
                chat_sessions_deleted = cursor.rowcount
                if chat_sessions_deleted > 0:
                    print(f"   Deleted {chat_sessions_deleted} related chat sessions")
                
                # Then delete all test users
                cursor.execute("""
                    DELETE FROM users 
                    WHERE email LIKE 'test_%' 
                       OR email LIKE 'duplicate_%'
                       OR phone_number LIKE '1234567%' 
                       OR phone_number LIKE '9876543%'
                """)
                users_deleted = cursor.rowcount
                print(f"   Deleted {users_deleted} test users")
                
                conn.commit()
                print("✅ Comprehensive cleanup completed successfully")
                
                # Verify cleanup worked
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE email LIKE 'test_%' 
                       OR email LIKE 'duplicate_%'
                       OR phone_number LIKE '1234567%' 
                       OR phone_number LIKE '9876543%'
                """)
                remaining_users = cursor.fetchone()[0]
                if remaining_users == 0:
                    print("✅ Verification: All test users successfully removed")
                else:
                    print(f"⚠️ Warning: {remaining_users} test users still remain")
                    
            else:
                print("✅ No test users found to clean up")
                
        finally:
            cursor.close()
            conn.close()
            
        return True
        
    except Exception as e:
        print(f"❌ Error during comprehensive cleanup: {e}")
        return False

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
    
    conn = None
    cursor = None
    
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
        
        # Rollback to clean up test data
        conn.rollback()
        
        # Test 3: Check if we can query the new fields
        print("\n3. Testing data retrieval with new fields...")
        test_email_retrieve = f"test_retrieve_{int(os.getpid())}@example.com"
        
        # Insert a new user for retrieval test
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, phone_number, first_name, age, gender, preferred_language, state, preferred_bot)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, email, phone_number, gender, preferred_bot
        """, (
            test_email_retrieve, 
            'hashed_password_123', 
            _unique_phone_number(),
            'Retrieve User', 
            25, 
            'M', 
            'English', 
            'Test State', 
            'N'
        ))
        
        inserted_retrieve_user = cursor.fetchone()
        
        cursor.execute("""
            SELECT id, email, phone_number, first_name, age, gender, preferred_language, state, preferred_bot
            FROM users 
            WHERE email = %s
        """, (test_email_retrieve,))
        
        retrieved_user = cursor.fetchone()
        if retrieved_user:
            print("✅ Data retrieval successful!")
            print(f"   Retrieved phone_number: {retrieved_user['phone_number']}")
            print(f"   Retrieved gender: {retrieved_user['gender']}")
            print(f"   Retrieved preferred_bot: {retrieved_user['preferred_bot']}")
            
            # Verify the data matches what we inserted
            if (retrieved_user['gender'] == 'M' and retrieved_user['preferred_bot'] == 'N'):
                print("✅ Retrieved data matches inserted data!")
            else:
                print("❌ Retrieved data doesn't match inserted data!")
                return False
        else:
            print("❌ Could not retrieve inserted data")
            return False
        
        # Rollback to clean up test data
        conn.rollback()
        
        # Test 4: Test nullable behavior
        print("\n4. Testing nullable behavior...")
        test_email_null = f"test_null_{int(os.getpid())}@example.com"
        
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, phone_number)
            VALUES (gen_random_uuid(), %s, %s, %s)
            RETURNING id, email, gender, preferred_bot
        """, (
            test_email_null, 
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
        
        # Rollback to clean up test data
        conn.rollback()
        
        # Test 5: Test phone number uniqueness constraint
        print("\n5. Testing phone number uniqueness constraint...")
        duplicate_phone = _unique_phone_number()
        
        # Insert first user with the phone number
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, phone_number)
            VALUES (gen_random_uuid(), %s, %s, %s)
            RETURNING id, email, phone_number
        """, (
            f"test_phone1_{int(os.getpid())}@example.com", 
            'hashed_password_123', 
            duplicate_phone
        ))
        
        first_user = cursor.fetchone()
        print(f"✅ First user with phone {duplicate_phone} inserted successfully!")
        
        # Try to insert second user with same phone number
        try:
            cursor.execute("""
                INSERT INTO users (id, email, hashed_password, phone_number)
                VALUES (gen_random_uuid(), %s, %s, %s)
                RETURNING id, email, phone_number
            """, (
                f"test_phone2_{int(os.getpid())}@example.com", 
                'hashed_password_123', 
                duplicate_phone
            ))
            print("❌ Phone number uniqueness constraint not enforced!")
            return False
        except psycopg2.IntegrityError as e:
            if "phone_number" in str(e) and "unique" in str(e).lower():
                print("✅ Phone number uniqueness constraint properly enforced!")
            else:
                print(f"❌ Unexpected constraint error: {e}")
                return False
        
        # Rollback the transaction to clean up the test data
        conn.rollback()
        
        # Test 6: Test email uniqueness constraint
        print("\n6. Testing email uniqueness constraint...")
        duplicate_email = f"test_email_{int(os.getpid())}@example.com"
        
        # Insert first user with the email
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, phone_number)
            VALUES (gen_random_uuid(), %s, %s, %s)
            RETURNING id, email, phone_number
        """, (
            duplicate_email, 
            'hashed_password_123', 
            _unique_phone_number()
        ))
        
        first_email_user = cursor.fetchone()
        print(f"✅ First user with email {duplicate_email} inserted successfully!")
        
        # Try to insert second user with same email
        try:
            cursor.execute("""
                INSERT INTO users (id, email, hashed_password, phone_number)
                VALUES (gen_random_uuid(), %s, %s, %s)
                RETURNING id, email, phone_number
            """, (
                duplicate_email, 
                'hashed_password_123', 
                _unique_phone_number()
            ))
            print("❌ Email uniqueness constraint not enforced!")
            return False
        except psycopg2.IntegrityError as e:
            if "email" in str(e) and "unique" in str(e).lower():
                print("✅ Email uniqueness constraint properly enforced!")
            else:
                print(f"❌ Unexpected constraint error: {e}")
                return False
        
        # Rollback the transaction to clean up the test data
        conn.rollback()
        
        # Test 7: Testing phone number format validation
        print("\n7. Testing phone number format validation...")
        
        # Test with various phone number formats
        test_phone_numbers = [
            "1234567890",           # Standard 10-digit
            "+1234567890",          # With country code
            "123-456-7890",         # With dashes
            "(123) 456-7890",       # With parentheses and spaces
            "123.456.7890",         # With dots
            "123 456 7890",         # With spaces
        ]
        
        for i, phone_format in enumerate(test_phone_numbers):
            # Generate a unique phone number for each format test
            unique_phone = _unique_phone_number_for_format_test()
            test_email = f"test_phone_format_{i}_{int(time.time())}@example.com"
            
            try:
                cursor.execute("""
                    INSERT INTO users (id, email, hashed_password, phone_number)
                    VALUES (gen_random_uuid(), %s, %s, %s)
                    RETURNING id, email, phone_number
                """, (
                    test_email, 
                    'hashed_password_123', 
                    unique_phone
                ))
                
                inserted_user = cursor.fetchone()
                print(f"✅ Phone number format '{phone_format}' accepted!")
                
            except Exception as e:
                print(f"❌ Phone number format '{phone_format}' rejected: {e}")
                return False
        
        # Rollback to clean up test data
        conn.rollback()
        
        print("\n" + "=" * 50)
        print("🎉 Database fields test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during database test: {e}")
        return False
        
    finally:
        # Always clean up test data, even if tests fail
        if cursor and conn:
            try:
                # Ensure we're in a clean transaction state before cleanup
                try:
                    conn.rollback()
                except:
                    pass  # Ignore rollback errors
                
                cleanup_test_data(cursor, conn)
            except Exception as cleanup_error:
                print(f"⚠️ Error during final cleanup: {cleanup_error}")
                # Try one more rollback to ensure clean state
                try:
                    conn.rollback()
                except:
                    pass
                
                # If main cleanup failed, try with a fresh connection
                print("🔄 Attempting cleanup with fresh connection...")
                cleanup_with_fresh_connection()
        
        # Close connections
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("✅ Database connection closed")

if __name__ == "__main__":
    success = test_database_fields()
    sys.exit(0 if success else 1)

def manual_cleanup():
    """Manual cleanup function that can be run separately"""
    print("🧹 Manual cleanup of test data...")
    success = cleanup_with_fresh_connection()
    if success:
        print("✅ Manual cleanup completed successfully")
    else:
        print("❌ Manual cleanup failed")
    return success

def run_comprehensive_cleanup():
    """Run comprehensive cleanup to remove all accumulated test data"""
    print("🧹 Running comprehensive cleanup...")
    success = comprehensive_cleanup()
    if success:
        print("✅ Comprehensive cleanup completed successfully")
    else:
        print("❌ Comprehensive cleanup failed")
    return success

# # Uncomment one of the lines below to run specific cleanup operations
# if __name__ == "__main__":
#     # manual_cleanup()  # Basic cleanup
#     run_comprehensive_cleanup()  # Comprehensive cleanup
