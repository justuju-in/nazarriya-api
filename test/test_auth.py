#!/usr/bin/env python3
"""
Test script for JWT authentication system
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test the complete authentication flow."""
    print("Testing JWT Authentication System...")
    print("=" * 50)
    
    # Test 1: User Registration
    print("\n1. Testing User Registration...")
    
    # Use a unique email to avoid conflicts
    import time
    unique_email = f"test_{int(time.time())}@example.com"
    
    register_data = {
        "email": unique_email,
        "password": "testpassword123",
        "phone_number": "1234567890",
        "first_name": "Test",
        "age": 25,
        "gender": "M",
        "preferred_language": "English",
        "state": "California",
        "preferred_bot": "N"
    }
    
    print(f"   Using email: {unique_email}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Registration successful! User ID: {user['id']}")
            print(f"   Gender: {user['gender']}")
            print(f"   Preferred Bot: {user['preferred_bot']}")
            
            # Verify the new fields are present in registration response
            if user.get('gender') == 'M' and user.get('preferred_bot') == 'N':
                print("✅ New fields (gender and preferred_bot) are properly returned in registration!")
            else:
                print("❌ New fields not properly returned in registration response!")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running.")
        return
    
    # Test 2: User Login
    print("\n2. Testing User Login...")
    login_data = {
        "email": unique_email,
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print(f"✅ Login successful! Token received.")
            print(f"   Token type: {token_data['token_type']}")
            print(f"   User: {token_data['user']['email']}")
            print(f"   User Gender: {token_data['user']['gender']}")
            print(f"   User Preferred Bot: {token_data['user']['preferred_bot']}")
            
            # Verify the new fields are present in login response
            if token_data['user'].get('gender') == 'M' and token_data['user'].get('preferred_bot') == 'N':
                print("✅ New fields (gender and preferred_bot) are properly returned in login!")
            else:
                print("❌ New fields not properly returned in login response!")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
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
            
            # Verify the new fields are present
            if user_profile.get('gender') == 'M' and user_profile.get('preferred_bot') == 'N':
                print("✅ New fields (gender and preferred_bot) are properly set!")
            else:
                print("❌ New fields not properly set in profile!")
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
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system test completed!")

if __name__ == "__main__":
    test_authentication()
