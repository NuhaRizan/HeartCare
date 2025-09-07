from flask import Flask
from flask_cors import CORS
from controllers.main_controller import main_blueprint
from controllers.auth_controller import auth_blueprint
from controllers.admin_controller import admin_blueprint
import os
import socket
from config import SECRET_KEY, LOCAL_SERVER_HOST, LOCAL_SERVER_PORT

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = SECRET_KEY

# Enable CORS for all domains and routes
CORS(app, origins=['http://localhost:4600', 'http://192.168.8.117:4600', 'http://localhost:3002', 'http://192.168.8.117:3002'], supports_credentials=True)

# Register blueprints
app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)

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

if __name__ == '__main__':
    # Get local IP address
    local_ip = get_local_ip()
    
    print("\nStarting HeartCare+ Flask App")
    print("=" * 50)
    print(f"Local IP: {local_ip}")
    print(f"Port: {LOCAL_SERVER_PORT}")
    print(f"Network URL: http://{local_ip}:{LOCAL_SERVER_PORT}")
    print(f"Local URL: http://localhost:{LOCAL_SERVER_PORT}")
    print("=" * 50 + "\n")
    
    # Run on network (accessible from other devices)
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=int(LOCAL_SERVER_PORT),
        debug=True
    )
