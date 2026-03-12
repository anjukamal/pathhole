import os
import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# --- IN-MEMORY DATA STORAGE ---
# Vercel serverless functions are ephemeral. This data will vanish frequently,
# but provides the absolute maximum speed (10-30ms) for hardware interactions.
detections_db = []
latest_live_data = {"distance_cm": 0, "timestamp": "Wait..."}
detection_id_counter = 1

@app.route('/')
def dashboard():
    """Renders the dashboard with recent pothole detections (from memory)."""
    # Sort detections newest to oldest and take the last 50
    sorted_detections = sorted(detections_db, key=lambda x: x['timestamp'], reverse=True)[:50]
    return render_template('index.html', detections=sorted_detections)


@app.route('/api/pothole', methods=['POST'])
def receive_pothole_data():
    """API endpoint to receive POST requests from the ESP32 (Instant RAM write)."""
    global detection_id_counter
    
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    
    device_id = data.get('device_id', 'Unknown')
    depth_cm = data.get('depth_cm')
    status = data.get('status', 'detected')

    if depth_cm is None:
        return jsonify({"error": "Missing depth_cm field"}), 400

    # Save to memory
    new_detection = {
        "id": detection_id_counter,
        "device_id": device_id,
        "depth_cm": depth_cm,
        "status": status,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")+"+05:30",
        "g_force": data.get('g_force', 0.0)
    }
    
    detections_db.append(new_detection)
    detection_id_counter += 1
    
    print(f"Recorded pothole from {device_id} with depth {depth_cm}cm")
    return jsonify({"message": "Data received and stored in RAM seamlessly"}), 201


@app.route('/api/live', methods=['POST'])
def receive_live_data():
    """API endpoint to receive live distance updates (Instant memory overwrite)."""
    global latest_live_data
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
        
    data = request.get_json()
    distance_cm = data.get('distance_cm')
    
    if distance_cm is not None:
        latest_live_data = {
            "distance_cm": round(distance_cm, 1),
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
        return jsonify({"message": "Live data updated"}), 200
    return jsonify({"error": "Missing distance"}), 400


@app.route('/api/clear', methods=['POST'])
def clear_detections():
    """API endpoint to clear all pothole records from memory."""
    global detections_db, detection_id_counter
    detections_db = []
    detection_id_counter = 1
    return jsonify({"message": "All warnings cleared"}), 200


@app.route('/api/live_status', methods=['GET'])
def get_live_status():
    """API endpoint for the dashboard to fetch the latest distance instantly."""
    return jsonify(latest_live_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
