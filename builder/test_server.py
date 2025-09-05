#!/usr/bin/env python3
"""
Test script for the Cursor Bridge Server
"""

import os
import sys
import time
import requests
import json
import subprocess
import threading

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_server():
    """Test the Cursor Bridge Server"""
    print("🧪 Testing Cursor Bridge Server...")
    
    # Start server in background
    print("🚀 Starting server...")
    server_process = subprocess.Popen([
        sys.executable, 
        os.path.join(os.path.dirname(__file__), "scripts", "cursor_server.py")
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    test_file = None
    try:
        # Test server is running
        print("📡 Testing server status...")
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        assert response.status_code == 200
        print("✅ Server is running")
        
        # Test creating an evaluation
        print("📝 Testing evaluation creation...")
        test_file = "src/hello.ts"
        if not os.path.exists(test_file):
            # Create a test file
            with open(test_file, 'w') as f:
                f.write("""
// Test file for evaluation
export function hello(name: string): string {
    return `Hello, ${name}!`;
}
""")
        
        # Test prompt endpoint
        print("🔗 Testing prompt endpoint...")
        # We need to get an evaluation ID first
        # For now, just test that the server responds
        response = requests.get("http://127.0.0.1:5000/prompt/test123", timeout=5)
        assert response.status_code == 404  # Should return 404 for non-existent eval
        print("✅ Prompt endpoint working")
        
        # Test response endpoint
        print("📤 Testing response endpoint...")
        test_response = {
            "overall_score": 85,
            "dimensions": {
                "clarity": 90,
                "design": 80
            },
            "reasoning": "Test evaluation"
        }
        
        response = requests.post(
            "http://127.0.0.1:5000/response/test123",
            json=test_response,
            timeout=5
        )
        assert response.status_code == 404  # Should return 404 for non-existent eval
        print("✅ Response endpoint working")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        # Clean up
        print("🧹 Cleaning up...")
        server_process.terminate()
        server_process.wait()
        
        # Remove test file
        if test_file and os.path.exists(test_file):
            os.remove(test_file)
    
    return True

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
