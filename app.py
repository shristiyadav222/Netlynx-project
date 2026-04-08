import cv2
import numpy as np
import mss
import pyautogui
import time
import threading
import os
import socket
import subprocess
import webbrowser
import tkinter as tk
import psutil
import secrets
from flask import Flask, Response, render_template_string, render_template, request, jsonify

SECURITY_TOKEN = secrets.token_hex(16)

# Initialize Flask app
app = Flask(__name__)

# Global variables for screen sharing
server_running = True
screen_width, screen_height = pyautogui.size()
resolution = (1920, 1080)

# Fix-Mate batch file handling
class BatchFileManager:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.batch_dir = os.path.join(self.script_dir, "Batch file")
        self.create_batch_files()
        
        # Define batch commands for each fix
        self.batch_commands = {
            "WiFi Fix": self.get_wifi_fix_commands(),
            "Display Fix": self.get_display_fix_commands(),
            "Cache Clear": self.get_cache_clear_commands(),
            "Video Help": self.get_video_help_commands(),
            "Screen Share": self.get_screen_share_commands(),
        }
    
    def create_batch_files(self):
        """Create batch files directory and sample batch files if they don't exist"""
        try:
            # Create batch directory if it doesn't exist
            os.makedirs(self.batch_dir, exist_ok=True)
            
            # Create sample batch files
            batch_files = {
                "wifi.bat": self.create_wifi_batch(),
                "display.bat": self.create_display_batch(),
                "cache.bat": self.create_cache_batch(),
                "yt.bat": self.create_video_help_batch(),
                "share.bat": self.create_screen_share_batch(),
            }
            
            for filename, content in batch_files.items():
                filepath = os.path.join(self.batch_dir, filename)
                if not os.path.exists(filepath):
                    with open(filepath, 'w') as f:
                        f.write(content)
                    print(f"Created batch file: {filepath}")
                    
        except Exception as e:
            print(f"Warning: Could not create batch files: {e}")
    
    def create_wifi_batch(self):
        """Create WiFi fix batch file"""
        return """@echo off
echo Fixing WiFi issues...
echo.
echo Resetting WiFi adapter...

:: Reset TCP/IP stack
netsh int ip reset
netsh winsock reset

:: Release and renew IP
ipconfig /release
ipconfig /renew

:: Flush DNS
ipconfig /flushdns

:: Restart WiFi service
net stop WlanSvc
timeout /t 3 /nobreak >nul
net start WlanSvc

echo.
echo WiFi fix completed!
echo Please restart your computer if issues persist.
timeout /t 5 /nobreak >nul
"""
    
    def create_display_batch(self):
        """Create Display fix batch file"""
        return """@echo off
echo Fixing display issues...
echo.

:: Check display drivers
echo Checking display drivers...
devcon status *display* | findstr /C:"Driver is running"

:: Restart Windows Explorer
taskkill /f /im explorer.exe
start explorer.exe

echo.
echo Display fix completed!
echo If issues persist, try updating your graphics drivers.
timeout /t 5 /nobreak >nul
"""
    
    def create_cache_batch(self):
        """Create Cache clear batch file"""
        return """@echo off
echo Clearing system cache...
echo.

:: Clear temporary files
del /q /f %temp%\\*.*
rd /s /q %temp%

:: Clear DNS cache
ipconfig /flushdns

:: Clear Windows Update cache
net stop wuauserv
rd /s /q C:\\Windows\\SoftwareDistribution
net start wuauserv

echo.
echo Cache cleared successfully!
timeout /t 3 /nobreak >nul
"""
    
    def create_video_help_batch(self):
        """Create Video Help batch file"""
        return """@echo off
echo Opening video help resources...
echo.

:: Open YouTube troubleshooting videos
start https://www.youtube.com/results?search_query=windows+troubleshooting
start https://www.youtube.com/results?search_query=wifi+fix+tutorial

echo.
echo Video resources opened in browser!
timeout /t 3 /nobreak >noul
"""
    
    def create_screen_share_batch(self):
        """Create Screen Share batch file"""
        return """@echo off
echo Setting up screen sharing...
echo.

echo Screen sharing requires the main application to be running.
echo Please use the web interface for screen sharing features.
echo.

echo Opening screen sharing guide...
start https://support.microsoft.com/en-us/windows/screen-sharing-in-windows-11-90e5ee2e-a5d5-4cf4-bf5a-2b2a17ec4c73

timeout /t 5 /nobreak >nul
"""
    
    def get_wifi_fix_commands(self):
        """Get commands for WiFi fix"""
        return [
            'netsh int ip reset',
            'netsh winsock reset',
            'ipconfig /release',
            'ipconfig /renew',
            'ipconfig /flushdns',
            'net stop WlanSvc',
            'timeout 3',
            'net start WlanSvc'
        ]
    
    def get_display_fix_commands(self):
        """Get commands for Display fix"""
        return [
            'taskkill /f /im explorer.exe',
            'start explorer.exe',
            'echo Display reset completed.'
        ]
    
    def get_cache_clear_commands(self):
        """Get commands for Cache clear"""
        return [
            'del /q /f %temp%\\*.*',
            'rd /s /q %temp%',
            'ipconfig /flushdns',
            'net stop wuauserv',
            'rd /s /q C:\\Windows\\SoftwareDistribution',
            'net start wuauserv'
        ]
    
    def get_video_help_commands(self):
        """Get commands for Video Help"""
        return [
            'start https://www.youtube.com/results?search_query=windows+troubleshooting',
            'start https://www.youtube.com/results?search_query=wifi+fix+tutorial'
        ]
    
    def get_screen_share_commands(self):
        """Get commands for Screen Share"""
        return [
            'echo Screen sharing is available in the web interface',
            'start https://support.microsoft.com/en-us/windows/screen-sharing-in-windows-11-90e5ee2e-a5d5-4cf4-bf5a-2b2a17ec4c73'
        ]
    
    def run_batch_commands(self, script_name):
        """Run batch commands directly"""
        if script_name in self.batch_commands:
            commands = self.batch_commands[script_name]
            try:
                for cmd in commands:
                    subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return True, f"{script_name} executed successfully!"
            except Exception as e:
                return False, f"Error executing {script_name}: {str(e)}"
        else:
            return False, f"Unknown script: {script_name}"
    
    def run_batch_file(self, script_name):
        """Run batch file if it exists"""
        batch_files = {
            "WiFi Fix": "wifi.bat",
            "Display Fix": "display.bat",
            "Cache Clear": "cache.bat",
            "Video Help": "yt.bat",
            "Screen Share": "share.bat",
        }
        
        if script_name in batch_files:
            filename = batch_files[script_name]
            filepath = os.path.join(self.batch_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    # Run the batch file
                    result = subprocess.run(
                        filepath,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=self.batch_dir
                    )
                    return True, f"{script_name} executed from {filename}"
                except Exception as e:
                    return False, f"Error running batch file: {str(e)}"
            else:
                # If batch file doesn't exist, run commands directly
                return self.run_batch_commands(script_name)
        return False, "Invalid script name"

# Initialize batch file manager
batch_manager = BatchFileManager()

# HTML Templates (same as before, kept for brevity)
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fix-Mate Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            color: white;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            width: 90%;
            max-width: 1200px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .dashboard {
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
            width: 90%;
            max-width: 1200px;
        }
        
        .panel {
            flex: 1;
            min-width: 300px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .panel h2 {
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .button-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .btn {
            padding: 12px 20px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn-fix {
            background: linear-gradient(45deg, #4ecdc4, #44a08d);
        }
        
        .btn-fix:hover {
            background: linear-gradient(45deg, #44a08d, #4ecdc4);
        }
        
        .btn-stream {
            background: linear-gradient(45deg, #ff6b6b, #ff8e53);
        }
        
        .btn-stream:hover {
            background: linear-gradient(45deg, #ff8e53, #ff6b6b);
        }
        
        .btn-stop {
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
        }
        
        .btn-stop:hover {
            background: linear-gradient(45deg, #ff4b2b, #ff416c);
        }
        
        .video-container {
            background: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            overflow: hidden;
            margin-top: 15px;
        }
        
        .video-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        select {
            padding: 10px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 5px;
            color: white;
            font-size: 14px;
            min-width: 120px;
        }
        
        select option {
            background: #667eea;
            color: white;
        }
        
        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            font-size: 14px;
        }
        
        .footer {
            margin-top: 40px;
            text-align: center;
            padding: 20px;
            opacity: 0.7;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .panel {
                min-width: 100%;
            }
            
            .button-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Fix-Mate Dashboard</h1>
        <p>All-in-one tool for system fixes and screen sharing</p>
    </div>
    
    <div class="dashboard">
        <div class="panel">
            <h2>System Fixes</h2>
            <p style="margin-bottom: 20px; opacity: 0.9;">Click any fix to run the corresponding script:</p>
            <div class="button-grid">
                {% for script in scripts %}
                <a href="/run/{{ script }}" class="btn btn-fix">{{ script }}</a>
                {% endfor %}
            </div>
            <div class="status">
                <strong>Status:</strong> <span id="fix-status">Ready to run fixes</span>
            </div>
        </div>
        
        <div class="panel">
            <h2>Screen Sharing</h2>
            <p style="margin-bottom: 20px; opacity: 0.9;">Stream your screen in real-time:</p>
            
            <a href="/screen" class="btn btn-stream" style="margin-bottom: 20px;">Open Screen Sharing</a>
            
            <div class="controls">
                <select id="resolution" onchange="changeResolution()">
                    <option value="480">480p</option>
                    <option value="720">720p</option>
                    <option value="1080" selected>1080p</option>
                </select>
                <button onclick="stopStream()" class="btn btn-stop">Stop Stream</button>
            </div>
            
            <div class="status">
                <strong>Stream Status:</strong> <span id="stream-status">Not active</span>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Fix-Mate v2.0 | Combined Dashboard | Accessible at: {{ ip_address }}:5000</p>
    </div>

    <script>
        function changeResolution() {
            let resolution = document.getElementById('resolution').value;
            fetch('/set_resolution?value=' + resolution)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('stream-status').textContent = 
                        `Resolution changed to ${data.resolution}`;
                });
        }
        
        function stopStream() {
            fetch('/stop_stream')
                .then(() => {
                    document.getElementById('stream-status').textContent = 'Stream stopped';
                    alert("Screen sharing has been stopped.");
                });
        }
        
        // Update status when a fix is clicked
        document.querySelectorAll('.btn-fix').forEach(button => {
            button.addEventListener('click', function(e) {
                document.getElementById('fix-status').textContent = 
                    `Running ${this.textContent}...`;
                
                // Show notification
                fetch(this.href)
                    .then(response => response.text())
                    .then(html => {
                        // Create a temporary div to show success message
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = html;
                        const message = tempDiv.querySelector('h1')?.textContent || 'Script started';
                        alert(message);
                        
                        // Update status
                        document.getElementById('fix-status').textContent = 
                            `${this.textContent} completed!`;
                    })
                    .catch(error => {
                        document.getElementById('fix-status').textContent = 
                            `Error running ${this.textContent}`;
                        alert('Error: ' + error);
                    });
                
                e.preventDefault();
            });
        });
    </script>
</body>
</html>
"""

SCREEN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Screen Stream</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background-color: #181818;
            color: white;
            font-family: 'Arial', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 1400px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            width: 100%;
        }
        
        .header h1 {
            color: #ff6b6b;
            margin-bottom: 10px;
        }
        
        .header a {
            color: #4ecdc4;
            text-decoration: none;
            font-size: 16px;
        }
        
        .header a:hover {
            text-decoration: underline;
        }
        
        .video-container {
            background-color: black;
            width: 100%;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px;
        }
        
        .video-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            width: 100%;
        }
        
        select, button {
            padding: 12px 20px;
            font-size: 16px;
            background-color: #282828;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 150px;
        }
        
        select:hover, button:hover {
            background-color: #383838;
            transform: translateY(-2px);
        }
        
        button {
            font-weight: 500;
        }
        
        .btn-dashboard {
            background: linear-gradient(45deg, #4ecdc4, #44a08d);
        }
        
        .btn-dashboard:hover {
            background: linear-gradient(45deg, #44a08d, #4ecdc4);
        }
        
        .btn-stop {
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
        }
        
        .btn-stop:hover {
            background: linear-gradient(45deg, #ff4b2b, #ff416c);
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            text-align: center;
            width: 100%;
        }
        
        @media (max-width: 768px) {
            .controls {
                flex-direction: column;
                align-items: center;
            }
            
            select, button {
                width: 100%;
                max-width: 300px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔴 Live Screen Stream</h1>
            <p>Real-time screen sharing from your computer</p>
            <a href="/">← Back to Dashboard</a>
        </div>
        
        <div class="video-container">
            <img src="/video_feed" alt="Live Screen">
        </div>
        
        <div class="controls">
            <label for="resolution">Quality:</label>
            <select id="resolution" onchange="changeResolution()">
                <option value="480">480p</option>
                <option value="720">720p</option>
                <option value="1080" selected>1080p</option>
            </select>
            
            <button onclick="goToDashboard()" class="btn-dashboard">Dashboard</button>
            <button onclick="stopStream()" class="btn-stop">End Stream</button>
        </div>
        
        <div class="status">
            <p><strong>Stream URL:</strong> {{ stream_url }}</p>
            <p><strong>Resolution:</strong> <span id="current-res">1920x1080</span></p>
            <p><strong>Status:</strong> <span id="stream-status">Live</span></p>
        </div>
    </div>

    <script>
        function changeResolution() {
            let resolution = document.getElementById('resolution').value;
            fetch('/set_resolution?value=' + resolution)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('current-res').textContent = 
                        `${data.resolution[0]}x${data.resolution[1]}`;
                    document.getElementById('stream-status').textContent = 
                        `Live (${data.resolution[0]}x${data.resolution[1]})`;
                });
        }
        
        function stopStream() {
            fetch('/stop_stream')
                .then(() => {
                    document.getElementById('stream-status').textContent = 'Stream ended';
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
                });
        }
        
        function goToDashboard() {
            window.location.href = '/';
        }
        
        // Auto-refresh image every 5 seconds to prevent freezing
        setInterval(() => {
            const img = document.querySelector('img');
            if (img) {
                const src = img.src;
                img.src = '';
                setTimeout(() => img.src = src, 100);
            }
        }, 5000);
    </script>
</body>
</html>
"""

SCRIPT_STARTED_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Script Started</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            margin-bottom: 30px;
        }
        a {
            display: inline-block;
            padding: 10px 20px;
            background: #4ecdc4;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        a:hover {
            background: #44a08d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ Script Started</h1>
        <p>{{ message }}</p>
        <a href="/">Back to Dashboard</a>
    </div>
</body>
</html>
"""

ERROR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            margin-bottom: 30px;
        }
        a {
            display: inline-block;
            padding: 10px 20px;
            background: #ff6b6b;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        a:hover {
            background: #ff5252;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>❌ Error</h1>
        <p>{{ error }}</p>
        <a href="/">Back to Dashboard</a>
    </div>
</body>
</html>
"""

def capture_screen():
    """Capture screen frames for streaming"""
    global server_running, resolution
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": screen_width, "height": screen_height}

        while server_running:
            start_time = time.time()
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Resize to selected resolution
            frame = cv2.resize(frame, resolution, interpolation=cv2.INTER_AREA)

            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

            elapsed_time = time.time() - start_time
            time.sleep(max(1/60 - elapsed_time, 0))  # Fixed to 60 FPS

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    ip_address = get_local_ip()
    return render_template(
        'index.html', 
        scripts=list(batch_manager.batch_commands.keys()),
        ip_address=ip_address,
        token=SECURITY_TOKEN
    )

@app.route('/api/stats')
def api_stats():
    token = request.args.get('token')
    if token != SECURITY_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403

    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\')
    
    processes = []
    for p in sorted(psutil.process_iter(['pid', 'name', 'memory_percent', 'status']),
                    key=lambda p: p.info['memory_percent'] if p.info['memory_percent'] else 0, 
                    reverse=True)[:10]:
        try:
            processes.append({
                "pid": p.info['pid'],
                "name": p.info['name'],
                "memory": round(p.info['memory_percent'], 1) if p.info['memory_percent'] else 0,
                "status": p.info['status']
            })
        except:
            pass
            
    return jsonify({
        "cpu": cpu,
        "memory_used": memory.used,
        "memory_total": memory.total,
        "memory_percent": memory.percent,
        "disk_used": disk.used,
        "disk_total": disk.total,
        "disk_percent": disk.percent,
        "network_connected": True,
        "processes": processes
    })

@app.route('/screen')
def screen_page():
    """Screen sharing page"""
    return index()

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(capture_screen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/run/<script_name>')
def run_script(script_name):
    """Run a batch script"""
    token = request.args.get('token')
    if token != SECURITY_TOKEN:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    success, message = batch_manager.run_batch_file(script_name)
    return jsonify({"success": success, "message": message})

@app.route('/set_resolution')
def set_resolution():
    """Set screen streaming resolution"""
    token = request.args.get('token')
    if token != SECURITY_TOKEN:
        return jsonify({"status": "Unauthorized"}), 403

    global resolution
    res_value = int(request.args.get('value', 1080))

    if res_value == 480:
        resolution = (854, 480)
    elif res_value == 720:
        resolution = (1280, 720)
    else:
        resolution = (1920, 1080)

    return jsonify({"status": "Resolution updated", "resolution": resolution})

@app.route('/stop_stream')
def stop_stream():
    """Stop the screen streaming"""
    token = request.args.get('token')
    if token != SECURITY_TOKEN:
        return jsonify({"status": "Unauthorized"}), 403

    global server_running
    server_running = False
    return jsonify({"status": "Stream stopped"})

@app.route('/kill')
def kill_script():
    """Kill the entire application"""
    threading.Thread(target=shutdown_server).start()
    return "<h2>Fix-Mate has been terminated!</h2>"

def shutdown_server():
    """Shutdown the server"""
    time.sleep(1)
    os._exit(0)

def launch_gui():
    """Launch the GUI window"""
    root = tk.Tk()
    root.title("Fix-Mate Dashboard")
    root.geometry("500x300")
    
    # Set window style
    root.configure(bg='#f0f0f0')
    
    # Header
    header_frame = tk.Frame(root, bg='#667eea', height=80)
    header_frame.pack(fill='x', side='top')
    
    title = tk.Label(header_frame, text="Fix-Mate", font=("Arial", 24, "bold"), 
                    fg="white", bg='#667eea')
    title.pack(pady=20)
    
    # Content
    content_frame = tk.Frame(root, bg='#f0f0f0')
    content_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    ip_address = get_local_ip()
    web_link = f"http://{ip_address}:5000/"
    
    info_label = tk.Label(content_frame, text="Fix-Mate is running successfully!", 
                         font=("Arial", 12), bg='#f0f0f0')
    info_label.pack(pady=10)
    
    link_label = tk.Label(content_frame, text=f"Access Dashboard:\n{web_link}", 
                         font=("Arial", 10), fg="blue", cursor="hand2", 
                         bg='#f0f0f0')
    link_label.pack(pady=10)
    
    def open_web():
        webbrowser.open(web_link)
    
    link_label.bind("<Button-1>", lambda e: open_web())
    
    # Info text
    info_text = tk.Label(content_frame, 
                        text="✓ Batch files created automatically\n✓ System fixes ready to use\n✓ Screen sharing available",
                        font=("Arial", 9), 
                        bg='#f0f0f0',
                        justify='left')
    info_text.pack(pady=10)
    
    # Buttons frame
    button_frame = tk.Frame(content_frame, bg='#f0f0f0')
    button_frame.pack(pady=20)
    
    open_btn = tk.Button(button_frame, text="Open Dashboard", command=open_web,
                        bg='#4ecdc4', fg='white', font=("Arial", 10, "bold"),
                        padx=20, pady=10)
    open_btn.pack(side='left', padx=5)
    
    exit_btn = tk.Button(button_frame, text="Exit", command=root.quit,
                        bg='#ff6b6b', fg='white', font=("Arial", 10, "bold"),
                        padx=20, pady=10)
    exit_btn.pack(side='left', padx=5)
    
    root.mainloop()

def main():
    """Main function to start the application"""
    print("=" * 60)
    print("Fix-Mate Dashboard with Screen Sharing")
    print("=" * 60)
    
    print("\n📁 Creating batch files...")
    print("✓ WiFi Fix")
    print("✓ Display Fix")
    print("✓ Cache Clear")
    print("✓ Video Help")
    print("✓ Screen Share")
    
    ip_address = get_local_ip()
    print(f"\n🌐 Local IP Address: {ip_address}")
    print(f"🔗 Dashboard URL: http://{ip_address}:5000")
    print(f"📺 Screen Sharing: http://{ip_address}:5000/screen")
    print("\nStarting server...")
    
    print("🚀 Starting server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    print("✅ Server started successfully!")
    print("📱 Open your browser and navigate to the URLs above")
    print("💡 Press Ctrl+C in this terminal to stop the server\n")

if __name__ == '__main__':
    main()