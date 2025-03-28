from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import random
import cv2
import numpy as np
import base64
import io
from PIL import Image

app = Flask(__name__)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('rail_simulation.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database with required tables
def init_db():
    print("Initializing database...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create simulations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_date TEXT NOT NULL,
            start_point TEXT NOT NULL,
            end_point TEXT NOT NULL,
            train_id TEXT NOT NULL,
            speed_gain REAL NOT NULL,
            weight_gain REAL NOT NULL,
            frequency_gain REAL NOT NULL,
            total_distance REAL NOT NULL,
            train_speed REAL NOT NULL,
            time_taken REAL NOT NULL
        )
    ''')

    # Create wear_outputs table with distance_km
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wear_outputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            location TEXT NOT NULL,
            distance_km REAL NOT NULL,
            wear_depth REAL NOT NULL,
            crw_l REAL NOT NULL,
            crw_r REAL NOT NULL,
            side_l REAL NOT NULL,
            side_r REAL NOT NULL,
            remlife_l REAL NOT NULL,
            remlife_r REAL NOT NULL,
            wid_l REAL NOT NULL,
            wid_r REAL NOT NULL,
            tiltdiff_l REAL NOT NULL,
            tiltdiff_r REAL NOT NULL,
            type_l REAL NOT NULL,
            type_r REAL NOT NULL,
            gaugediff REAL NOT NULL,
            FOREIGN KEY (simulation_id) REFERENCES simulations (id)
        )
    ''')

    # Create trains table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_id TEXT NOT NULL UNIQUE,
            base_speed REAL NOT NULL,
            weight_per_car REAL NOT NULL,
            cars INTEGER NOT NULL,
            base_frequency INTEGER NOT NULL
        )
    ''')

    # Insert initial train details
    trains = [
        ("Train A", 160, 20, 6, 10),
        ("Train B", 100, 30, 8, 6),
        ("Train C", 60, 40, 12, 4)
    ]

    for train in trains:
        cursor.execute('''
            INSERT OR IGNORE INTO trains (train_id, base_speed, weight_per_car, cars, base_frequency)
            VALUES (?, ?, ?, ?, ?)
        ''', train)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Initialize the database when the app starts
init_db()

# Define checkpoints and distances (in km)
checkpoints = ["Park City", "Checkpoint 1", "Checkpoint 2", "Checkpoint 3", "Checkpoint 4"]
distances = {
    ("Park City", "Checkpoint 1"): 20,
    ("Checkpoint 1", "Checkpoint 2"): 45,
    ("Checkpoint 2", "Checkpoint 3"): 60,
    ("Checkpoint 3", "Checkpoint 4"): 35,
    ("Checkpoint 4", "Park City"): 20,
}

# Route for the main simulation UI
@app.route('/')
def index():
    return render_template('simulation_ui.html', checkpoints=checkpoints)



# Route to get checkpoint distances
@app.route('/get_checkpoint_distances')
def get_checkpoint_distances():
    try:
        # Calculate distances from Park City to each checkpoint
        distances_from_start = []
        current_distance = 0
        current_point = "Park City"
        
        distances_from_start.append({
            "name": current_point,
            "distance_from_start": current_distance
        })
        
        while True:
            next_point = get_next_checkpoint(current_point, None)  # Get next in sequence
            segment_distance = distances[(current_point, next_point)]
            current_distance += segment_distance
            distances_from_start.append({
                "name": next_point,
                "distance_from_start": current_distance
            })
            current_point = next_point
            if current_point == "Park City":
                break
        
        return jsonify(distances_from_start)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to save simulation parameters and run the simulation
@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    try:
        # Parse input data from the request
        data = request.json
        print("Received data:", data)

        simulation_date = data['simulation_date']
        start_point = data['start_point']
        end_point = data['end_point']
        train_id = data['train_id']
        speed_gain = float(data['speed_gain'])
        weight_gain = float(data['weight_gain'])
        frequency_gain = float(data['frequency_gain'])

        # Fetch train details from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM trains WHERE train_id = ?', (train_id,))
        train_details = cursor.fetchone()

        if not train_details:
            conn.close()
            return jsonify({"error": f"Train {train_id} not found"}), 404

        # Extract train details
        base_speed = train_details['base_speed']
        weight_per_car = train_details['weight_per_car']
        cars = train_details['cars']
        base_frequency = train_details['base_frequency']

        # Calculate total weight of the train
        total_weight = cars * weight_per_car

        # Calculate the total distance and measurement points
        total_distance, measurement_points = calculate_distance(start_point, end_point)
        print(f"Total distance: {total_distance} km")
        print(f"Measurement points: {measurement_points}")

        # Calculate adjusted speed and time taken
        train_speed = base_speed * speed_gain
        time_taken = (total_distance / train_speed) * 3600

        # Save simulation parameters to the database
        cursor.execute('''
            INSERT INTO simulations (
                simulation_date, start_point, end_point, train_id, 
                speed_gain, weight_gain, frequency_gain, 
                total_distance, train_speed, time_taken
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            simulation_date, start_point, end_point, train_id,
            speed_gain, weight_gain, frequency_gain,
            total_distance, train_speed, time_taken
        ))
        simulation_id = cursor.lastrowid

        # Simulate wear outputs for each measurement point
        current_time = datetime.now()
        wear_outputs = []
        
        for i, distance in enumerate(measurement_points):
            # Calculate timestamp for this point
            time_to_point = (distance / train_speed) * 3600 if i > 0 else 0
            timestamp = current_time + timedelta(seconds=time_to_point)

            # Determine location description
            if i == 0:
                location = f"Start at {start_point}"
            elif i == len(measurement_points) - 1:
                location = f"End at {end_point}"
            else:
                location = f"Point {i} between {start_point} and {end_point}"

            # Simulate wear and rail measurements
            wear_depth, rail_measurements = simulate_wear(
                train_id, speed_gain, weight_gain, frequency_gain
            )

            # Insert wear data into the database
            cursor.execute('''
                INSERT INTO wear_outputs (
                    simulation_id, timestamp, location, distance_km, wear_depth,
                    crw_l, crw_r, side_l, side_r, remlife_l, remlife_r,
                    wid_l, wid_r, tiltdiff_l, tiltdiff_r, type_l, type_r, gaugediff
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                simulation_id, timestamp.isoformat(), location, distance, wear_depth,
                rail_measurements['crw_l'], rail_measurements['crw_r'],
                rail_measurements['side_l'], rail_measurements['side_r'],
                rail_measurements['remlife_l'], rail_measurements['remlife_r'],
                rail_measurements['wid_l'], rail_measurements['wid_r'],
                rail_measurements['tiltdiff_l'], rail_measurements['tiltdiff_r'],
                rail_measurements['type_l'], rail_measurements['type_r'],
                rail_measurements['gaugediff']
            ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Simulation completed successfully!",
            "simulation_id": simulation_id,
            "total_distance": total_distance,
            "measurement_points": measurement_points,
            "start_point": start_point,
            "end_point": end_point
        })
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

# Function to calculate the total distance and measurement points
def calculate_distance(start_point, end_point):
    distance = 0
    current_location = start_point
    measurement_points = [0.0]  # Start with 0 km
    
    while current_location != end_point:
        next_location = get_next_checkpoint(current_location, end_point)
        segment_distance = distances[(current_location, next_location)]
        distance += segment_distance
        
        # Calculate intermediate points (25%, 50%, 75% of total distance)
        for i in range(1, 4):
            measurement_points.append(round(distance * (i/4), 1))
        
        current_location = next_location
    
    # Ensure we have exactly 5 points (0%, 25%, 50%, 75%, 100%)
    measurement_points = measurement_points[:5]  # Take first 5 points
    measurement_points[-1] = round(distance, 1)  # Ensure last point is exact distance
    
    return distance, measurement_points
# Function to get the next checkpoint
def get_next_checkpoint(current_location, end_point):
    current_index = checkpoints.index(current_location)
    next_index = (current_index + 1) % len(checkpoints)
    next_location = checkpoints[next_index]
    
    # If we have an end point, make sure we're moving toward it
    if end_point:
        end_index = checkpoints.index(end_point)
        if current_index < end_index or (current_index == len(checkpoints)-1 and end_index == 0):
            # Normal forward progression
            return next_location
        else:
            # Need to wrap around
            return checkpoints[0]
    
    return next_location

# Function to simulate wear and rail measurements
def simulate_wear(train_id, speed_gain, weight_gain, frequency_gain):
    # Fetch train details
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trains WHERE train_id = ?', (train_id,))
    train_details = cursor.fetchone()
    conn.close()

    if not train_details:
        raise ValueError(f"Train {train_id} not found")

    # Extract train details
    base_speed = train_details['base_speed']
    weight_per_car = train_details['weight_per_car']
    cars = train_details['cars']
    base_frequency = train_details['base_frequency']

    # Calculate total weight
    total_weight = cars * weight_per_car

    # Calculate base wear
    base_wear = (total_weight / 100) * (base_speed / 100) * (base_frequency / 10)
    wear_depth = base_wear * speed_gain * weight_gain * frequency_gain
    wear_depth *= random.uniform(0.9, 1.1)  # +/- 10% variability

    # Simulate rail measurements
    rail_measurements = {
        'crw_l': random.uniform(1.0, 2.0) * (total_weight / 100),
        'crw_r': random.uniform(1.0, 2.0) * (total_weight / 100),
        'side_l': random.uniform(0.5, 1.5) * (total_weight / 100),
        'side_r': random.uniform(0.5, 1.5) * (total_weight / 100),
        'remlife_l': random.uniform(100.0, 200.0) / (total_weight / 100),
        'remlife_r': random.uniform(100.0, 200.0) / (total_weight / 100),
        'wid_l': random.uniform(50.0, 60.0),
        'wid_r': random.uniform(50.0, 60.0),
        'tiltdiff_l': random.uniform(0.1, 0.5) * (base_speed / 100),
        'tiltdiff_r': random.uniform(0.1, 0.5) * (base_speed / 100),
        'type_l': random.uniform(40.0, 60.0),
        'type_r': random.uniform(40.0, 60.0),
        'gaugediff': random.uniform(0.0, 1.0) * (total_weight / 100)
    }

    return wear_depth, rail_measurements

# Route to fetch simulation data for visualization
@app.route('/get_simulations')
def get_simulations():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get list of all simulations
    cursor.execute('''
        SELECT id, simulation_date, start_point, end_point, train_id, 
               speed_gain, weight_gain, frequency_gain, total_distance
        FROM simulations
        ORDER BY simulation_date DESC
    ''')
    simulations = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'simulations': [dict(sim) for sim in simulations]
    })

@app.route('/fetch_data')
def fetch_data():
    simulation_id = request.args.get('simulation_id')
    if not simulation_id:
        return jsonify({'error': 'Missing simulation_id parameter'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get simulation parameters
    cursor.execute('SELECT * FROM simulations WHERE id = ?', (simulation_id,))
    simulation = cursor.fetchone()
    
    if not simulation:
        conn.close()
        return jsonify({'error': 'Simulation not found'}), 404
    
    # Get wear data
    cursor.execute('''
        SELECT * FROM wear_outputs 
        WHERE simulation_id = ?
        ORDER BY distance_km ASC
    ''', (simulation_id,))
    wear_outputs = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'simulation': dict(simulation),
        'wear_outputs': [dict(output) for output in wear_outputs]
    })

# Other routes remain the same
@app.route('/analytics_dashboard')
def analytics_dashboard():
    return render_template('analytics_dashboard.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

if __name__ == '__main__':
    app.run(debug=True)

    git init
git add README.md
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/JayboyX/Prev-man-latest-2.0.git
git push -u origin main