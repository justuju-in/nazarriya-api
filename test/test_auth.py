#!/usr/bin/env python3
"""
Test script for JWT authentication system
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def cleanup_test_data(access_token):
    """Clean up test data created during tests"""
    if not access_token:
        print("⚠️ No access token available for cleanup")
        return
    
    try:
        print("\n🧹 Cleaning up test data...")
        
        # Get current user to identify test data
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            user_email = user_data.get('email', '')
            
            # Only clean up if this is a test user
            if user_email.startswith('test_') or user_email.startswith('duplicate_'):
                print(f"   Found test user: {user_email}")
                
                # Try to delete the user (if delete endpoint exists)
                # For now, we'll just log that cleanup would be needed
                print(f"   Test user {user_email} would be cleaned up here")
                print("   Note: User deletion endpoint not implemented yet")
            else:
                print("✅ No test users found to clean up")
        else:
            print("⚠️ Could not verify user for cleanup")
            
    except Exception as e:
        print(f"⚠️ Warning during cleanup: {e}")

def test_authentication():
    """Test the complete authentication flow."""
    print("Testing JWT Authentication System...")
    print("=" * 50)
    
    access_token = None
    
    try:
        # Test 1: User Registration
        print("\n1. Testing User Registration...")
        
        # Use a unique email to avoid conflicts
        import time
        unique_email = f"test_{int(time.time())}@example.com"
        unique_phone = f"1234567{int(time.time())}"
        
        register_data = {
            "email": unique_email,
            "password": "testpassword123",
            "phone_number": unique_phone,
            "first_name": "Test",
            "age": 25,
            "gender": "M",
            "preferred_language": "English",
            "state": "California",
            "preferred_bot": "N"
        }
        
        print(f"   Using email: {unique_email}")
        print(f"   Using phone: {unique_phone}")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code == 200:
                user = response.json()
                print(f"✅ Registration successful! User ID: {user['id']}")
                print(f"   Gender: {user['gender']}")
                print(f"   Preferred Bot: {user['preferred_bot']}")
                print(f"   Phone Number: {user['phone_number']}")
                
                # Verify the new fields are present in registration response
                if user.get('gender') == 'M' and user.get('preferred_bot') == 'N':
                    print("✅ New fields (gender and preferred_bot) are properly returned in registration!")
                else:
                    print("❌ New fields not properly returned in registration response!")
                    
                # Verify phone number is present
                if user.get('phone_number') == unique_phone:
                    print("✅ Phone number is properly returned in registration!")
                else:
                    print("❌ Phone number not properly returned in registration response!")
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure the server is running.")
            return
        
        # Test 2: User Login by Email
        print("\n2. Testing User Login by Email...")
        login_data = {
            "email_or_phone": unique_email,
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data['access_token']
                print(f"✅ Login by email successful! Token received.")
                print(f"   Token type: {token_data['token_type']}")
                print(f"   User: {token_data['user']['email']}")
                print(f"   User Gender: {token_data['user']['gender']}")
                print(f"   User Preferred Bot: {token_data['user']['preferred_bot']}")
                print(f"   User Phone Number: {token_data['user']['phone_number']}")
                
                # Verify the new fields are present in login response
                if token_data['user'].get('gender') == 'M' and token_data['user'].get('preferred_bot') == 'N':
                    print("✅ New fields (gender and preferred_bot) are properly returned in login!")
                else:
                    print("❌ New fields not properly returned in login response!")
                    
                # Verify phone number is present
                if token_data['user'].get('phone_number') == unique_phone:
                    print("✅ Phone number is properly returned in login!")
                else:
                    print("❌ Phone number not properly returned in login response!")
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        # Test 2b: User Login by Phone Number
        print("\n2b. Testing User Login by Phone Number...")
        login_by_phone_data = {
            "email_or_phone": unique_phone,
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_by_phone_data)
            if response.status_code == 200:
                token_data = response.json()
                phone_access_token = token_data['access_token']
                print(f"✅ Login by phone number successful! Token received.")
                print(f"   Token type: {token_data['token_type']}")
                print(f"   User: {token_data['user']['email']}")
                print(f"   User Phone Number: {token_data['user']['phone_number']}")
                
                # Verify both tokens are the same (same user)
                if access_token == phone_access_token:
                    print("✅ Login by email and phone number return the same user!")
                else:
                    print("❌ Login by email and phone number return different users!")
            else:
                print(f"❌ Login by phone number failed: {response.status_code} - {response.text}")
                return
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        # Test 2c: Test Phone Number Uniqueness
        print("\n2c. Testing Phone Number Uniqueness...")
        duplicate_phone_data = {
            "email": f"duplicate_{int(time.time())}@example.com",
            "password": "testpassword123",
            "phone_number": unique_phone,  # Same phone number as first user
            "first_name": "Duplicate",
            "age": 30,
            "gender": "F",
            "preferred_language": "English",
            "state": "New York",
            "preferred_bot": "R"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=duplicate_phone_data)
            if response.status_code == 400:
                error_detail = response.json().get('detail', '')
                if 'phone number already registered' in error_detail.lower():
                    print("✅ Phone number uniqueness properly enforced!")
                else:
                    print(f"❌ Wrong error message for duplicate phone: {error_detail}")
            else:
                print(f"❌ Duplicate phone number registration should have failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        # Test 2d: Test Email Uniqueness
        print("\n2d. Testing Email Uniqueness...")
        duplicate_email_data = {
            "email": unique_email,  # Same email as first user
            "password": "testpassword123",
            "phone_number": f"9876543{int(time.time())}",
            "first_name": "Duplicate",
            "age": 30,
            "gender": "F",
            "preferred_language": "English",
            "state": "New York",
            "preferred_bot": "R"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=duplicate_email_data)
            if response.status_code == 400:
                error_detail = response.json().get('detail', '')
                if 'email already registered' in error_detail.lower():
                    print("✅ Email uniqueness properly enforced!")
                else:
                    print(f"❌ Wrong error message for duplicate email: {error_detail}")
            else:
                print(f"❌ Duplicate email registration should have failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return

        # Test 3: Get Current User Profile
        print("\n3. Testing Get Current User Profile...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code == 200:
                user_profile = response.json()
                print(f"✅ Profile retrieved successfully!")
                print(f"   Email: {user_profile['email']}")
                print(f"   Name: {user_profile['first_name']}")
                print(f"   Gender: {user_profile['gender']}")
                print(f"   Preferred Bot: {user_profile['preferred_bot']}")
                print(f"   Phone Number: {user_profile['phone_number']}")
                
                # Verify the new fields are present
                if user_profile.get('gender') == 'M' and user_profile.get('preferred_bot') == 'N':
                    print("✅ New fields (gender and preferred_bot) are properly set!")
                else:
                    print("❌ New fields not properly set in profile!")
                    
                # Verify phone number is present
                if user_profile.get('phone_number') == unique_phone:
                    print("✅ Phone number is properly set in profile!")
                else:
                    print("❌ Phone number not properly set in profile!")
            else:
                print(f"❌ Profile retrieval failed: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        # Test 4: Test Chat Endpoint with Authentication
        print("\n4. Testing Chat Endpoint with Authentication...")
        chat_data = {
            "message": "Hello, this is a test message!",
            "session_id": None
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat", json=chat_data, headers=headers)
            if response.status_code == 200:
                chat_response = response.json()
                print(f"✅ Chat successful!")
                print(f"   Session ID: {chat_response['session_id']}")
                print(f"   Response: {chat_response['response']}")
            else:
                print(f"❌ Chat failed: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        # Test 5: Test Profile Update
        print("\n5. Testing Profile Update...")
        profile_update_data = {
            "gender": "F",
            "preferred_bot": "R",
            "age": 26
        }
        
        try:
            response = requests.put(f"{BASE_URL}/auth/profile", json=profile_update_data, headers=headers)
            if response.status_code == 200:
                updated_profile = response.json()
                print(f"✅ Profile update successful!")
                print(f"   Updated gender: {updated_profile['gender']}")
                print(f"   Updated preferred_bot: {updated_profile['preferred_bot']}")
                print(f"   Updated age: {updated_profile['age']}")
                
                # Verify the changes were actually saved
                if (updated_profile['gender'] == 'F' and 
                    updated_profile['preferred_bot'] == 'R' and 
                    updated_profile['age'] == 26):
                    print("✅ All profile updates verified!")
                else:
                    print("❌ Profile updates not properly saved!")
            else:
                print(f"❌ Profile update failed: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        # Test 6: Test Invalid Token
        print("\n6. Testing Invalid Token...")
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        
        try:
            response = requests.get(f"{BASE_URL}/auth/me", headers=invalid_headers)
            if response.status_code == 401:
                print("✅ Invalid token correctly rejected!")
            else:
                print(f"❌ Invalid token not rejected: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        # Test 7: Test Invalid Login Credentials
        print("\n7. Testing Invalid Login Credentials...")
        
        # Test with non-existent email
        invalid_email_login = {
            "email_or_phone": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=invalid_email_login)
            if response.status_code == 401:
                print("✅ Invalid email login correctly rejected!")
            else:
                print(f"❌ Invalid email login not rejected: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        # Test with non-existent phone number
        invalid_phone_login = {
            "email_or_phone": "9999999999",
            "password": "wrongpassword"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=invalid_phone_login)
            if response.status_code == 401:
                print("✅ Invalid phone number login correctly rejected!")
            else:
                print(f"❌ Invalid phone number login not rejected: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server.")
            return
        
        print("\n" + "=" * 50)
        print("🎉 Authentication system test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error during test: {e}")
        return False
        
    finally:
        # Always clean up test data, even if tests fail
        cleanup_test_data(access_token)

if __name__ == "__main__":
    success = test_authentication()
    exit(0 if success else 1)
