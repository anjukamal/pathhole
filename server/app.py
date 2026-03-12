import mysql.connector
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Database connection pool settings (Aiven MySQL URL)
def get_db_connection():
    # Example format expected: mysql://user:password@host:port/dbname
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("DATABASE_URL environment variable not set!")
        return None
        
    try:
        # Parse the connection string aiven format
        from urllib.parse import urlparse
        result = urlparse(db_url)
        
        conn = mysql.connector.connect(
            host=result.hostname,
            user=result.username,
            password=result.password,
            port=result.port,
            database=result.path[1:] # strip the leading '/'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    """Initializes the MySQL database with the required schema."""
    conn = get_db_connection()
    if conn is None: return
    
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id VARCHAR(255) NOT NULL,
            depth_cm FLOAT NOT NULL,
            status VARCHAR(255) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            g_force FLOAT DEFAULT 0.0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS live_status (
            id INT PRIMARY KEY,
            distance_cm FLOAT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')
    
    # Ensure there is exactly one row in live_status
    cursor.execute('SELECT COUNT(*) as cnt FROM live_status')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO live_status (id, distance_cm) VALUES (1, 0.0)')
        
    # Safely add g_force column if it doesn't exist from an older version
    try:
        cursor.execute("SHOW COLUMNS FROM detections LIKE 'g_force'")
        if not cursor.fetchone():
            cursor.execute('ALTER TABLE detections ADD COLUMN g_force FLOAT DEFAULT 0.0')
    except mysql.connector.Error:
        pass # Column already exists or error
        
    conn.commit()
    cursor.close()
    conn.close()

# Initialize DB when the app starts
init_db()

@app.route('/')
def dashboard():
    """Renders the dashboard with recent pothole detections."""
    conn = get_db_connection()
    if conn is None:
        return "Database Connection Failed - Set DATABASE_URL in Vercel", 500
        
    # Return dict-like rows
    cursor = conn.cursor(dictionary=True)
    
    # Fetch the 50 most recent detections
    cursor.execute('SELECT * FROM detections ORDER BY timestamp DESC LIMIT 50')
    detections = cursor.fetchall()
    
    cursor.close()
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
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to DB"}), 500
            
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO detections (device_id, depth_cm, status) VALUES (%s, %s, %s)',
            (device_id, depth_cm, status)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Recorded pothole from {device_id} with depth {depth_cm}cm")
        return jsonify({"message": "Data received and stored successfully"}), 201
        
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to store data"}), 500

# Remove global variable, we now use the DB

@app.route('/api/live', methods=['POST'])
def receive_live_data():
    """API endpoint to receive live distance updates strictly for the dashboard heartbeat."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
        
    data = request.get_json()
    distance_cm = data.get('distance_cm')
    
    if distance_cm is not None:
        try:
            conn = get_db_connection()
            if conn is None: return jsonify({"error": "DB error"}), 500
            
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE live_status SET distance_cm = %s WHERE id = 1',
                (round(distance_cm, 1),)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({"message": "Live data updated"}), 200
        except mysql.connector.Error as e:
            print(f"Database error updating live: {e}")
            return jsonify({"error": "Failed to update live distance"}), 500
            
    return jsonify({"error": "Missing distance"}), 400

@app.route('/api/clear', methods=['POST'])
def clear_detections():
    """API endpoint to clear all pothole records from the database."""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to DB"}), 500
            
        cursor = conn.cursor()
        cursor.execute('DELETE FROM detections')
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "All warnings cleared"}), 200
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to clear data"}), 500

@app.route('/api/live_status', methods=['GET'])
def get_live_status():
    """API endpoint for the dashboard to fetch the latest distance without reloading the page."""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"distance_cm": "--", "timestamp": "DB Error"})
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT distance_cm, updated_at FROM live_status WHERE id = 1')
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if row:
            # Format time from datetime object
            timestamp_str = row['updated_at'].strftime("%H:%M:%S") if row['updated_at'] else "Wait..."
            return jsonify({
                "distance_cm": row['distance_cm'],
                "timestamp": timestamp_str
            })
    except mysql.connector.Error as e:
        print(f"Database error fetching live status: {e}")
        
    return jsonify({"distance_cm": "--", "timestamp": "Error fetching data"})

if __name__ == '__main__':
    # Run the server on all available interfaces (0.0.0.0) so the ESP32 can connect
    app.run(host='0.0.0.0', port=5000, debug=True)
