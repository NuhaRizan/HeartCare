#!/usr/bin/env python3
"""
Test script to verify download link functionality
"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, LOCAL_SERVER_PROTOCOL

def test_download_link():
    """Test if download links are accessible"""
    
    print("🧪 Testing Download Link Accessibility")
    print("=" * 50)
    
    # Test the base server
    base_url = f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}"
    test_report_id = "test-123"
    download_url = f"{base_url}/download_report/{test_report_id}"
    
    print(f"🌐 Base URL: {base_url}")
    print(f"🔗 Test Download URL: {download_url}")
    print()
    
    # Test base server
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✅ Base server accessible - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Base server not accessible: {str(e)}")
        return False
    
    # Test download link (should return 404 for test ID, but server should be reachable)
    try:
        response = requests.get(download_url, timeout=5)
        if response.status_code == 404:
            print(f"✅ Download link endpoint accessible - Status: {response.status_code} (expected for test ID)")
        else:
            print(f"⚠️  Download link endpoint responded with: {response.status_code}")
    except Exception as e:
        print(f"❌ Download link not accessible: {str(e)}")
        return False
    
    return True

def generate_sample_links():
    """Generate sample download links for testing"""
    
    print("\n📋 Sample Download Links")
    print("=" * 30)
    
    sample_report_id = "sample-uuid-456"
    
    # Generate links with different configurations
    links = [
        f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}",
        f"{LOCAL_SERVER_PROTOCOL}://localhost:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}",
        f"{LOCAL_SERVER_PROTOCOL}://127.0.0.1:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}"
    ]
    
    for i, link in enumerate(links, 1):
        print(f"{i}. {link}")
    
    print()
    print("💡 These are the types of links that will be sent in emails")

if __name__ == "__main__":
    print("🔗 Download Link Test")
    print("=" * 30)
    
    success = test_download_link()
    generate_sample_links()
    
    if success:
        print("\n✅ Download links should work properly!")
        print("📧 Try sending an email with report download link now.")
    else:
        print("\n❌ There are issues with the download links.")
        print("🔧 Make sure your Flask app is running on the correct port.")
        print("   python app.py") 