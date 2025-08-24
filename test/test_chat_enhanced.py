#!/usr/bin/env python3
"""
Test script for enhanced chat functionality with user isolation and security.
This script tests the new session management features.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

class ChatTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
    
    def login(self, email: str, password: str) -> bool:
        """Login and get access token."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                print(f"✅ Login successful for user: {email}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_create_session(self) -> str:
        """Test creating a new chat session."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/sessions",
                json={"title": "Test Session"}
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data["session_id"]
                print(f"✅ Session created: {session_id}")
                return session_id
            else:
                print(f"❌ Session creation failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            return None
    
    def test_chat_message(self, session_id: str, message: str) -> bool:
        """Test sending a chat message."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={"message": message, "session_id": session_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat message sent: {data['response'][:50]}...")
                return True
            else:
                print(f"❌ Chat message failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Chat message error: {e}")
            return False
    
    def test_get_sessions(self) -> bool:
        """Test getting user sessions."""
        try:
            response = self.session.get(f"{self.base_url}/api/sessions")
            
            if response.status_code == 200:
                sessions = response.json()
                print(f"✅ Retrieved {len(sessions)} sessions")
                for session in sessions[:3]:  # Show first 3 sessions
                    print(f"   - {session['title']} ({session['message_count']} messages)")
                return True
            else:
                print(f"❌ Get sessions failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get sessions error: {e}")
            return False
    
    def test_get_session_history(self, session_id: str) -> bool:
        """Test getting session history."""
        try:
            response = self.session.get(f"{self.base_url}/api/sessions/{session_id}/history")
            
            if response.status_code == 200:
                data = response.json()
                history = data["history"]
                print(f"✅ Retrieved session history: {len(history)} messages")
                for msg in history:
                    print(f"   - {msg['sender']}: {msg['text'][:50]}...")
                return True
            else:
                print(f"❌ Get history failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get history error: {e}")
            return False
    
    def test_update_session_title(self, session_id: str, new_title: str) -> bool:
        """Test updating session title."""
        try:
            response = self.session.put(
                f"{self.base_url}/api/sessions/{session_id}/title",
                json={"title": new_title}
            )
            
            if response.status_code == 200:
                print(f"✅ Session title updated to: {new_title}")
                return True
            else:
                print(f"❌ Update title failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Update title error: {e}")
            return False
    
    def test_delete_session(self, session_id: str) -> bool:
        """Test deleting a session."""
        try:
            response = self.session.delete(f"{self.base_url}/api/sessions/{session_id}")
            
            if response.status_code == 200:
                print(f"✅ Session deleted: {session_id}")
                return True
            else:
                print(f"❌ Delete session failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Delete session error: {e}")
            return False
    
    def run_full_test(self):
        """Run the complete test suite."""
        print("🚀 Starting Enhanced Chat System Test Suite")
        print("=" * 50)
        
        # Test 1: Login
        if not self.login(TEST_EMAIL, TEST_PASSWORD):
            print("❌ Cannot proceed without login")
            return
        
        # Test 2: Create session
        session_id = self.test_create_session()
        if not session_id:
            print("❌ Cannot proceed without session")
            return
        
        # Test 3: Send chat messages
        print("\n📝 Testing chat functionality...")
        self.test_chat_message(session_id, "Hello, this is a test message!")
        time.sleep(1)
        self.test_chat_message(session_id, "This is another test message to verify the system works.")
        
        # Test 4: Get sessions list
        print("\n📋 Testing session listing...")
        self.test_get_sessions()
        
        # Test 5: Get session history
        print("\n📚 Testing session history...")
        self.test_get_session_history(session_id)
        
        # Test 6: Update session title
        print("\n✏️ Testing title update...")
        self.test_update_session_title(session_id, "Updated Test Session")
        
        # Test 7: Create another session and verify isolation
        print("\n🆕 Testing session isolation...")
        session_id_2 = self.test_create_session()
        if session_id_2:
            self.test_chat_message(session_id_2, "This is in a different session")
            self.test_get_sessions()
        
        # Test 8: Delete session
        print("\n🗑️ Testing session deletion...")
        self.test_delete_session(session_id_2 if session_id_2 else session_id)
        
        print("\n" + "=" * 50)
        print("✅ Enhanced Chat System Test Suite Completed!")

def main():
    """Main function to run the test suite."""
    tester = ChatTester(BASE_URL)
    tester.run_full_test()

if __name__ == "__main__":
    main()
