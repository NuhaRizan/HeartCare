#!/usr/bin/env python3
"""
Test script to verify network configuration for Flask app
"""

import socket
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, LOCAL_SERVER_PROTOCOL

def get_network_ip():
    """Get the actual network IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        network_ip = s.getsockname()[0]
        s.close()
        return network_ip
    except Exception:
        return LOCAL_SERVER_HOST

def test_network_config():
    """Test network configuration"""
    
    print("🌐 Network Configuration Test")
    print("=" * 40)
    
    network_ip = get_network_ip()
    
    print(f"🔧 Config Settings:")
    print(f"   Protocol: {LOCAL_SERVER_PROTOCOL}")
    print(f"   Port: {LOCAL_SERVER_PORT}")
    print(f"   Default Host: {LOCAL_SERVER_HOST}")
    print()
    
    print(f"🌐 Network Detection:")
    print(f"   Detected IP: {network_ip}")
    print()
    
    print(f"📱 URLs for Download Links:")
    print(f"   Network URL: {LOCAL_SERVER_PROTOCOL}://{network_ip}:{LOCAL_SERVER_PORT}")
    print(f"   Local URL: {LOCAL_SERVER_PROTOCOL}://localhost:{LOCAL_SERVER_PORT}")
    print()
    
    # Test sample download link
    sample_report_id = "test-uuid-123"
    sample_download_url = f"{LOCAL_SERVER_PROTOCOL}://{network_ip}:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}"
    
    print(f"📋 Sample Download Link:")
    print(f"   {sample_download_url}")
    print()
    
    print("💡 Benefits of Network Configuration:")
    print("   ✅ Download links work from any device on network")
    print("   ✅ WhatsApp/SMS links accessible from phones")
    print("   ✅ Email links work from any device")
    print("   ✅ No need to use localhost")

if __name__ == "__main__":
    test_network_config() 