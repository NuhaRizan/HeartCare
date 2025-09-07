#!/usr/bin/env python3
"""
Setup script for local server configuration
"""

import socket
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, LOCAL_SERVER_PROTOCOL

def get_local_ip():
    """Get the local IP address of your PC"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def test_local_server():
    """Test if the local server is accessible"""
    
    print("🧪 Testing Local Server Configuration")
    print("=" * 50)
    
    local_ip = get_local_ip()
    
    print(f"🖥️  Local IP Address: {local_ip}")
    print(f"🌐 Configured Host: {LOCAL_SERVER_HOST}")
    print(f"🔌 Configured Port: {LOCAL_SERVER_PORT}")
    print(f"🔗 Configured Protocol: {LOCAL_SERVER_PROTOCOL}")
    print()
    
    test_urls = [
        f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}",
        f"{LOCAL_SERVER_PROTOCOL}://{local_ip}:{LOCAL_SERVER_PORT}",
        f"{LOCAL_SERVER_PROTOCOL}://127.0.0.1:{LOCAL_SERVER_PORT}",
        f"{LOCAL_SERVER_PROTOCOL}://localhost:{LOCAL_SERVER_PORT}"
    ]
    
    print("📡 Testing server accessibility:")
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {url} - Server is running!")
                return url
            else:
                print(f"   ⚠️  {url} - Server responded with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {url} - Connection failed")
        except requests.exceptions.Timeout:
            print(f"   ⏰ {url} - Connection timeout")
        except Exception as e:
            print(f"   ❌ {url} - Error: {str(e)}")
    
    return None

def generate_sample_download_link():
    """Generate a sample download link"""
    
    print("\n🔗 Sample Download Link Generation")
    print("=" * 40)
    
    sample_report_id = "test-uuid-123"
    local_ip = get_local_ip()
    
    sample_links = [
        f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}",
        f"{LOCAL_SERVER_PROTOCOL}://{local_ip}:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}",
        f"{LOCAL_SERVER_PROTOCOL}://127.0.0.1:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}",
        f"{LOCAL_SERVER_PROTOCOL}://localhost:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}"
    ]
    
    print("📋 Sample download links:")
    for i, link in enumerate(sample_links, 1):
        print(f"   {i}. {link}")
    
    print()
    print("💡 These links will be sent in WhatsApp messages")

if __name__ == "__main__":
    print("🚀 Local Server Setup for WhatsApp Download Links")
    print("=" * 60)
    print()
    
    working_url = test_local_server()
    generate_sample_download_link()
    
    print()
    print("🎉 Setup complete!")
    if working_url:
        print("✅ Your local server is accessible!")
        print(f"🌐 Working URL: {working_url}")
    else:
        print("⚠️  Local server not accessible. Make sure Flask app is running:")
        print("   python app.py")
    
    print()
    print("📱 WhatsApp messages will now use your local server for download links!") 