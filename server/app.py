import os
import datetime
from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    'host': 'mysql-4bba7a8-anjukamal204-ecf2.f.aivencloud.com',
    'port': 15262,
    'user': 'avnadmin',
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': 'defaultdb',
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create detections table using VARCHAR for timestamp to match your previous string formatting
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(255),
            depth_cm FLOAT,
            status VARCHAR(50),
            timestamp VARCHAR(255),
            g_force FLOAT
        )
    ''')
    # Create live_state table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS live_state (
            id INT PRIMARY KEY,
            distance_cm FLOAT,
            timestamp VARCHAR(50)
        )
    ''')
    # Initialize live state if empty
    cursor.execute('SELECT COUNT(*) FROM live_state WHERE id=1')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO live_state (id, distance_cm, timestamp) VALUES (1, 0, 'Wait...')")
    
    conn.commit()
    cursor.close()
    conn.close()

try:
    init_db()
except Exception as e:
    print("Database init error:", e)


@app.route('/')
def dashboard():
    try:
        conn = get_db_connection()
        # Fetch dictionary so we can access columns by name (like x['timestamp'] in your template)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM detections ORDER BY id DESC LIMIT 50')
        sorted_detections = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', detections=sorted_detections)
    except Exception as e:
        return f"Database error: {e}", 500


@app.route('/api/pothole', methods=['POST'])
def receive_pothole_data():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    
    device_id = data.get('device_id', 'Unknown')
    depth_cm = data.get('depth_cm')
    status = data.get('status', 'detected')
    g_force = data.get('g_force', 0.0)

    if depth_cm is None:
        return jsonify({"error": "Missing depth_cm field"}), 400
        
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")+"+05:30"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO detections (device_id, depth_cm, status, timestamp, g_force) VALUES (%s, %s, %s, %s, %s)',
            (device_id, depth_cm, status, timestamp_str, g_force)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Recorded pothole from {device_id} with depth {depth_cm}cm to MySQL")
        return jsonify({"message": "Data received and stored in MySQL database seamlessly"}), 201
    except Exception as e:
        print("Error saving pothole:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/live', methods=['POST'])
def receive_live_data():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
        
    data = request.get_json()
    distance_cm = data.get('distance_cm')
    
    if distance_cm is not None:
        timestamp_str = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE live_state SET distance_cm = %s, timestamp = %s WHERE id = 1',
                (round(distance_cm, 1), timestamp_str)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"message": "Live data updated in MySQL database"}), 200
        except Exception as e:
            print("Error updating live status:", e)
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Missing distance"}), 400


@app.route('/api/clear', methods=['POST'])
def clear_detections():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('TRUNCATE TABLE detections')
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "All database warnings cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/live_status', methods=['GET'])
def get_live_status():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT distance_cm, timestamp FROM live_state WHERE id = 1')
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return jsonify(row)
        return jsonify({"distance_cm": 0, "timestamp": "Wait..."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
