from flask import Flask, request, jsonify
import logging
from collections import deque
import queue
import threading
import time



# --- Flask App ---
app = Flask(__name__)

# --- Configure Logging ---
# Log to stdout so Docker logs can capture it
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- State Variables ---
logs_queue = deque()  # Store logs received from camera
command_queue = queue.Queue()  # Queue for commands to the camera
active_camera_connection = False
connection_lock = threading.Lock()

# --- Endpoint to Receive Data ---
@app.route('/poll', methods=['POST'])
def long_polling_endpoint():
    """
    Long polling endpoint for the camera. This holds the connection open
    until there's a command for the camera, or until timeout.
    """
    global active_camera_connection
    global logs_queue

    if not request.is_json:
        app.logger.warning("Received non-JSON request")
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    #if request contains actual logs and isnt just an empty connection
    data = request.get_json()
    if data and isinstance(data, list) and len(data) > 0:
        app.logger.info(f"Received data: {data}")
        logs_queue.extend(data)
        return jsonify({"status": "success", "message": "Logs received"}), 200
    
    with connection_lock:
        active_camera_connection = True
    
    try:
        cmd = command_queue.get(timeout=30)
        app.logger.info(f"Sending command to camera: {cmd}")
        return jsonify({
            "command":cmd
        })
    except queue.Empty:
        pass
    finally:
        with connection_lock:
            active_camera_connection = False

    # Return a keep-alive response if no command was issued
    return jsonify({"status": "timeout", "message": "No commands available"}), 200

@app.route('/logs', methods=['GET'])
def request_logs():
    """
    Endpoint for clients to request logs from the camera.
    It triggers a command to the camera to send logs and waits for the response.
    """
    global logs_queue

    logs_queue.clear()

    with connection_lock:
        if not active_camera_connection:
            return jsonify({'error':'No camera detected'}), 503
        
        command_queue.put("send_logs")
    
    wait_start = time.time()
    timeout = 10

    while time.time() - wait_start < timeout:
        if logs_queue:
            #Return recieved logs
            logs = list(logs_queue)
            logs_queue.clear()
            return jsonify({'logs': logs}), 200
        time.sleep(0.1)
    
    # If we timed out waiting for logs
    return jsonify({"error": "Timeout waiting for camera logs"}), 504
            
        


    

@app.route('/')
def index():
    """ Basic status page """
    return "Long Poll Data Receiver is running."

# --- Main Execution ---
if __name__ == '__main__':
    app.logger.info("Starting data receiver server...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)