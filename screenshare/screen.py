import cv2
import numpy as np
import mss
import pyautogui
import time
import threading
import os
from flask import Flask, Response, render_template_string, request, jsonify

app = Flask(__name__)
server_running = True  

# Default screen size
screen_width, screen_height = pyautogui.size()
#cursor_img = cv2.imread("cursor.png", cv2.IMREAD_UNCHANGED)

#if cursor_img is None:
#    raise FileNotFoundError("cursor.png not found!")

#cursor_size = 32
#cursor_img = cv2.resize(cursor_img, (cursor_size, cursor_size), interpolation=cv2.INTER_AREA)

# Default resolution (1080p)
resolution = (1920, 1080)

# YouTube-Like UI
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Stream</title>
    <style>
        body {
            background-color: #181818;
            color: white;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .video-container {
            background-color: black;
            width: 90%;
            max-width: 1280px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5);
        }
        img {
            width: 100%;
            height: auto;
            display: block;
        }
        .controls {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        select, button {
            padding: 10px 15px;
            font-size: 16px;
            background-color: #282828;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: 0.2s;
        }
        select:hover, button:hover {
            background-color: #383838;
        }
        .stop {
            background-color: red;
        }
        .stop:hover {
            background-color: #b30000;
        }
    </style>
</head>
<body>
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
        <button class="stop" onclick="stopServer()">End Stream</button>
    </div>

    <script>
        function changeResolution() {
            let resolution = document.getElementById('resolution').value;
            fetch('/set_resolution?value=' + resolution);
        }

        function stopServer() {
            fetch('/stop').then(() => alert("Stream has ended."));
        }
    </script>
</body>
</html>
"""

def capture_screen():
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

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    return Response(capture_screen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_resolution')
def set_resolution():
    global resolution
    res_value = int(request.args.get('value', 1080))

    if res_value == 480:
        resolution = (854, 480)
    elif res_value == 720:
        resolution = (1280, 720)
    else:
        resolution = (1920, 1080)

    return jsonify({"status": "Resolution updated", "resolution": resolution})

@app.route('/stop')
def stop_server():
    global server_running
    server_running = False
    threading.Thread(target=shutdown_server).start()
    return "Server shutting down..."

def shutdown_server():
    time.sleep(1)
    os._exit(0)  # <-- Kills the Python script

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
