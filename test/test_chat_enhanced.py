#!/usr/bin/env python3
"""
Test script for enhanced chat functionality with user isolation and security.
This script tests the new session management features.
"""

import requests
import json
import time
import hashlib
import base64
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"

# Generate unique test user credentials
timestamp = int(time.time())
TEST_EMAIL = f"test_chat_{timestamp}@example.com"
TEST_PASSWORD = "testpassword123"
TEST_PHONE = f"123456{timestamp % 10000:04d}"

class ChatTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.created_sessions = []  # Track created sessions for cleanup
    
    def register_user(self, email: str, password: str, phone: str) -> bool:
        """Register a new test user."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "phone_number": phone,
                    "full_name": "Test User"
                }
            )
            
            if response.status_code == 200:
                print(f"✅ User registered: {email}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False

    def login(self, email: str, password: str) -> bool:
        """Login and get access token."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email_or_phone": email, "password": password}
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
    
    def cleanup_test_data(self):
        """Clean up all test data created during tests"""
        try:
            print("\n🧹 Cleaning up chat test data...")
            
            if not self.access_token:
                print("   No access token available for cleanup")
                return
            
            # Clean up created sessions
            for session_id in self.created_sessions:
                try:
                    response = self.session.delete(f"{self.base_url}/api/sessions/{session_id}")
                    if response.status_code == 200:
                        print(f"   Deleted session: {session_id}")
                    else:
                        print(f"   Failed to delete session {session_id}: {response.status_code}")
                except Exception as e:
                    print(f"   Error deleting session {session_id}: {e}")
            
            # Clear the list
            self.created_sessions.clear()
            print("✅ Chat test data cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Warning during chat cleanup: {e}")
    
    def create_encrypted_message(self, plaintext: str) -> Dict[str, Any]:
        """Create a mock encrypted message for testing."""
        try:
            # Mock encryption - just add a suffix to simulate encryption
            plaintext_bytes = plaintext.encode('utf-8')
            mock_encrypted = plaintext_bytes + b'_encrypted_mock'
            content_hash = hashlib.sha256(mock_encrypted).hexdigest()
            
            return {
                "encrypted_message": base64.b64encode(mock_encrypted).decode('utf-8'),
                "encryption_metadata": {
                    "algorithm": "AES-256-GCM",
                    "key_id": "test_key_123",
                    "iv": base64.b64encode(b'123456789012').decode('utf-8'),  # 12-byte IV
                    "created_at": "2025-01-01T00:00:00.000000"
                },
                "content_hash": content_hash
            }
        except Exception as e:
            print(f"❌ Error creating encrypted message: {e}")
            return None
    
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
                self.created_sessions.append(session_id)  # Track for cleanup
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
            # Create encrypted message
            encrypted_data = self.create_encrypted_message(message)
            if not encrypted_data:
                return False
            
            # Add session_id to the encrypted data
            encrypted_data["session_id"] = session_id
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=encrypted_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat message sent: {data['encrypted_response'][:50]}...")
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
                history = response.json()
                print(f"✅ Retrieved session history: {len(history['history'])} messages")
                return True
            else:
                print(f"❌ Get session history failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Get session history error: {e}")
            return False
    
    def test_update_session_title(self, session_id: str, new_title: str) -> bool:
        """Test updating session title."""
        try:
            response = self.session.put(
                f"{self.base_url}/api/sessions/{session_id}",
                json={"title": new_title}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Session title updated: {data['title']}")
                return True
            else:
                print(f"❌ Update session title failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Update session title error: {e}")
            return False
    
    def test_delete_session(self, session_id: str) -> bool:
        """Test deleting a session."""
        try:
            response = self.session.delete(f"{self.base_url}/api/sessions/{session_id}")
            
            if response.status_code == 200:
                print(f"✅ Session deleted: {session_id}")
                # Remove from tracking list
                if session_id in self.created_sessions:
                    self.created_sessions.remove(session_id)
                return True
            else:
                print(f"❌ Delete session failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Delete session error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all chat tests."""
        print("Testing Enhanced Chat Functionality...")
        print("=" * 50)
        
        try:
            # Register and login first
            if not self.register_user(TEST_EMAIL, TEST_PASSWORD, TEST_PHONE):
                print("❌ Cannot proceed without user registration")
                return False
            
            if not self.login(TEST_EMAIL, TEST_PASSWORD):
                print("❌ Cannot proceed without login")
                return False
            
            # Test session creation
            session_id = self.test_create_session()
            if not session_id:
                print("❌ Session creation failed, cannot continue")
                return False
            
            # Test chat functionality
            self.test_chat_message(session_id, "Hello, this is a test message!")
            time.sleep(1)  # Small delay to ensure message processing
            self.test_chat_message(session_id, "This is another test message to verify the system works.")
            
            # Test session management
            self.test_get_sessions()
            time.sleep(1)
            self.test_get_session_history(session_id)
            time.sleep(1)
            self.test_update_session_title(session_id, "Updated Test Session")
            
            # Test multiple sessions
            session_id_2 = self.test_create_session()
            if session_id_2:
                self.test_chat_message(session_id_2, "This is in a different session")
                self.test_get_sessions()
                time.sleep(1)
                self.test_delete_session(session_id_2)
            
            print("\n" + "=" * 50)
            print("🎉 Chat functionality test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error during chat tests: {e}")
            return False
        
        finally:
            # Always clean up test data, even if tests fail
            self.cleanup_test_data()

def main():
    """Main test runner."""
    tester = ChatTester(BASE_URL)
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
