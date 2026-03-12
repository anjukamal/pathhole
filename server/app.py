import sqlite3
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Database file location
DB_FILE = os.path.join(os.path.dirname(__file__), 'potholes.db')

def init_db():
    """Initializes the SQLite database with the required schema."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            depth_cm REAL NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            g_force REAL DEFAULT 0.0
        )
    ''')
    
    # Safely add g_force column if it doesn't exist from an older version
    try:
        cursor.execute('ALTER TABLE detections ADD COLUMN g_force REAL DEFAULT 0.0')
    except sqlite3.OperationalError:
        pass # Column already exists
        
    conn.commit()
    conn.close()

# Initialize DB when the app starts
init_db()

@app.route('/')
def dashboard():
    """Renders the dashboard with recent pothole detections."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Return dict-like rows
    cursor = conn.cursor()
    
    # Fetch the 50 most recent detections
    cursor.execute('SELECT * FROM detections ORDER BY timestamp DESC LIMIT 50')
    detections = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', detections=detections)


@app.route('/api/pothole', methods=['POST'])
def receive_pothole_data():
    """API endpoint to receive POST requests from the ESP32."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    
    # Extract data with default fallbacks
    device_id = data.get('device_id', 'Unknown')
    depth_cm = data.get('depth_cm')
    status = data.get('status', 'detected')

    # Basic validation
    if depth_cm is None:
        return jsonify({"error": "Missing depth_cm field"}), 400

    try:
        # Save to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO detections (device_id, depth_cm, status) VALUES (?, ?, ?)',
            (device_id, depth_cm, status)
        )
        conn.commit()
        conn.close()
        
        print(f"Recorded pothole from {device_id} with depth {depth_cm}cm")
        return jsonify({"message": "Data received and stored successfully"}), 201
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to store data"}), 500

# Global variable to store the latest live distance
latest_live_data = {"distance_cm": 0, "timestamp": "Wait..."}

@app.route('/api/live', methods=['POST'])
def receive_live_data():
    """API endpoint to receive live distance updates strictly for the dashboard heartbeat."""
    global latest_live_data
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
        
    data = request.get_json()
    distance_cm = data.get('distance_cm')
    
    if distance_cm is not None:
        import datetime
        latest_live_data = {
            "distance_cm": round(distance_cm, 1),
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
        return jsonify({"message": "Live data updated"}), 200
    return jsonify({"error": "Missing distance"}), 400

@app.route('/api/clear', methods=['POST'])
def clear_detections():
    """API endpoint to clear all pothole records from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM detections')
        conn.commit()
        conn.close()
        return jsonify({"message": "All warnings cleared"}), 200
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to clear data"}), 500

@app.route('/api/live_status', methods=['GET'])
def get_live_status():
    """API endpoint for the dashboard to fetch the latest distance without reloading the page."""
    global latest_live_data
    return jsonify(latest_live_data)

if __name__ == '__main__':
    # Run the server on all available interfaces (0.0.0.0) so the ESP32 can connect
    app.run(host='0.0.0.0', port=5000, debug=True)
