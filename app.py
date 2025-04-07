from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import math

app = Flask(__name__)

DATABASE = 'railway.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('simulation'))

@app.route('/simulation')
def simulation():
    conn = get_db_connection()
    
    # Get trains for dropdown
    trains = conn.execute('SELECT * FROM trains').fetchall()
    
    # Get recent simulations
    recent_simulations = conn.execute('''
        SELECT s.id, s.created_at, t.name as train_name, r.name as route_name, 
               s.distance, s.status, s.start_station_id, s.end_station_id
        FROM simulations s
        JOIN trains t ON s.train_id = t.id
        JOIN routes r ON s.route_id = r.id
        ORDER BY s.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('simulation.html', 
                         trains=trains,
                         recent_simulations=recent_simulations)

@app.route('/get_route_data/<int:train_id>')
def get_route_data(train_id):
    conn = get_db_connection()
    
    # Get the train's default route
    train = conn.execute('SELECT * FROM trains WHERE id = ?', (train_id,)).fetchone()
    
    if not train or not train['route_id']:
        conn.close()
        return jsonify({'error': 'No route assigned to this train'}), 404
    
    # Get route details
    route = conn.execute('SELECT * FROM routes WHERE id = ?', (train['route_id'],)).fetchone()
    
    # Get stations for this route
    stations = conn.execute('''
        SELECT * FROM stations 
        WHERE route_id = ? 
        ORDER BY km_marker
    ''', (train['route_id'],)).fetchall()
    
    # Get initial rail conditions for the first station
    start_conditions = conn.execute('''
        SELECT * FROM rail_conditions 
        WHERE route_id = ? 
        ORDER BY ABS(km_marker - ?)
        LIMIT 1
    ''', (train['route_id'], stations[0]['km_marker'])).fetchone()
    
    conn.close()
    
    return jsonify({
        'route': dict(route),
        'stations': [dict(s) for s in stations],
        'initial_conditions': dict(start_conditions) if start_conditions else None,
        'train': dict(train)
    })

@app.route('/get_rail_conditions/<int:route_id>/<float:km_marker>')
def get_rail_conditions(route_id, km_marker):
    conn = get_db_connection()
    
    conditions = conn.execute('''
        SELECT * FROM rail_conditions 
        WHERE route_id = ? 
        ORDER BY ABS(km_marker - ?)
        LIMIT 1
    ''', (route_id, km_marker)).fetchone()
    
    conn.close()
    
    if not conditions:
        return jsonify({'error': 'No conditions found for this location'}), 404
    
    return jsonify(dict(conditions))

@app.route('/calculate_wear', methods=['POST'])
def calculate_wear():
    data = request.json
    
    # Basic validation
    if not all(k in data for k in ['train_id', 'route_id', 'start_km', 'end_km', 'speed', 'weight']):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    conn = get_db_connection()
    
    # Get train data
    train = conn.execute('SELECT * FROM trains WHERE id = ?', (data['train_id'],)).fetchone()
    
    # Calculate distance
    distance = abs(float(data['end_km']) - float(data['start_km']))
    
    # Calculate basic wear factors (simplified for example)
    speed_factor = float(data['speed']) / train['max_speed']
    weight_factor = float(data['weight']) / train['total_weight']
    distance_factor = distance / 100  # per 100 km
    
    # Calculate wear amounts (these would be more complex in reality)
    wear_data = {
        'crw_l': 0.5 * speed_factor * weight_factor * distance_factor,
        'crw_r': 0.5 * speed_factor * weight_factor * distance_factor,
        'side_l': 0.3 * speed_factor * weight_factor * distance_factor,
        'side_r': 0.3 * speed_factor * weight_factor * distance_factor,
        'remlife_l': -10 * speed_factor * weight_factor * distance_factor,
        'remlife_r': -10 * speed_factor * weight_factor * distance_factor,
        'wid_l': -0.05 * speed_factor * weight_factor * distance_factor,
        'wid_r': -0.05 * speed_factor * weight_factor * distance_factor,
        'tiltdiff_l': 0.01 * speed_factor * weight_factor * distance_factor,
        'tiltdiff_r': 0.01 * speed_factor * weight_factor * distance_factor,
        'gaugediff': 0.02 * speed_factor * weight_factor * distance_factor
    }
    
    conn.close()
    
    return jsonify({
        'wear_data': wear_data,
        'distance': distance,
        'calculation_factors': {
            'speed_factor': speed_factor,
            'weight_factor': weight_factor,
            'distance_factor': distance_factor
        }
    })

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.form
    
    # Basic validation
    required_fields = ['train_id', 'route_id', 'start_station_id', 'end_station_id', 
                      'speed', 'weight', 'frequency']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    conn = get_db_connection()
    
    try:
        # Get station km markers
        start_station = conn.execute('SELECT km_marker FROM stations WHERE id = ?', 
                                   (data['start_station_id'],)).fetchone()
        end_station = conn.execute('SELECT km_marker FROM stations WHERE id = ?', 
                                 (data['end_station_id'],)).fetchone()
        
        if not start_station or not end_station:
            raise ValueError("Invalid station selection")
        
        distance = abs(end_station['km_marker'] - start_station['km_marker'])
        
        # Create simulation record
        cur = conn.execute('''
            INSERT INTO simulations 
            (train_id, route_id, start_station_id, end_station_id, 
             speed, weight, frequency, distance, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['train_id'], data['route_id'], data['start_station_id'], 
            data['end_station_id'], data['speed'], data['weight'], 
            data['frequency'], distance, 'successful'
        ))
        
        simulation_id = cur.lastrowid
        
        # Calculate wear for each km segment along the route
        step = 0.5  # km intervals
        current_km = min(start_station['km_marker'], end_station['km_marker'])
        end_km = max(start_station['km_marker'], end_station['km_marker'])
        
        while current_km <= end_km:
            # Calculate wear for this segment (simplified)
            wear_amounts = {
                'crw_l': 0.01 * float(data['speed']) / 100,
                'crw_r': 0.01 * float(data['speed']) / 100,
                'side_l': 0.005 * float(data['weight']) / 100000,
                'side_r': 0.005 * float(data['weight']) / 100000,
                'remlife_l': -0.1 * float(data['speed']) * float(data['weight']) / 1000000,
                'remlife_r': -0.1 * float(data['speed']) * float(data['weight']) / 1000000,
                'wid_l': -0.001 * float(data['weight']) / 100000,
                'wid_r': -0.001 * float(data['weight']) / 100000,
                'tiltdiff_l': 0.0005 * float(data['speed']) / 100,
                'tiltdiff_r': 0.0005 * float(data['speed']) / 100,
                'gaugediff': 0.0002 * float(data['weight']) / 100000
            }
            
            # Record wear output
            conn.execute('''
                INSERT INTO wear_outputs 
                (simulation_id, km_marker, crw_l, crw_r, side_l, side_r, 
                 remlife_l, remlife_r, wid_l, wid_r, tiltdiff_l, tiltdiff_r, gaugediff)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                simulation_id, current_km, 
                wear_amounts['crw_l'], wear_amounts['crw_r'],
                wear_amounts['side_l'], wear_amounts['side_r'],
                wear_amounts['remlife_l'], wear_amounts['remlife_r'],
                wear_amounts['wid_l'], wear_amounts['wid_r'],
                wear_amounts['tiltdiff_l'], wear_amounts['tiltdiff_r'],
                wear_amounts['gaugediff']
            ))
            
            # Update rail conditions
            conn.execute('''
                UPDATE rail_conditions 
                SET 
                    crw_l = crw_l + ?,
                    crw_r = crw_r + ?,
                    side_l = side_l + ?,
                    side_r = side_r + ?,
                    remlife_l = remlife_l + ?,
                    remlife_r = remlife_r + ?,
                    wid_l = wid_l + ?,
                    wid_r = wid_r + ?,
                    tiltdiff_l = tiltdiff_l + ?,
                    tiltdiff_r = tiltdiff_r + ?,
                    gaugediff = gaugediff + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE route_id = ? AND ABS(km_marker - ?) < 0.25
            ''', (
                wear_amounts['crw_l'], wear_amounts['crw_r'],
                wear_amounts['side_l'], wear_amounts['side_r'],
                wear_amounts['remlife_l'], wear_amounts['remlife_r'],
                wear_amounts['wid_l'], wear_amounts['wid_r'],
                wear_amounts['tiltdiff_l'], wear_amounts['tiltdiff_r'],
                wear_amounts['gaugediff'],
                data['route_id'], current_km
            ))
            
            current_km += step
        
        conn.commit()
        return redirect(url_for('simulation'))
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@app.route('/get_wear_outputs/<int:simulation_id>')
def get_wear_outputs(simulation_id):
    conn = get_db_connection()
    
    wear_outputs = conn.execute('''
        SELECT * FROM wear_outputs 
        WHERE simulation_id = ?
        ORDER BY km_marker
    ''', (simulation_id,)).fetchall()
    
    simulation = conn.execute('''
        SELECT s.*, t.name as train_name, r.name as route_name
        FROM simulations s
        JOIN trains t ON s.train_id = t.id
        JOIN routes r ON s.route_id = r.id
        WHERE s.id = ?
    ''', (simulation_id,)).fetchone()
    
    conn.close()
    
    return render_template('wear_outputs.html',
                         wear_outputs=wear_outputs,
                         simulation=simulation)

@app.route('/get_simulations')
def get_simulations():
    conn = get_db_connection()
    simulations = conn.execute('''
        SELECT s.id, s.created_at, t.name as train_name, r.name as route_name,
               st1.name as start_point, st2.name as end_point
        FROM simulations s
        JOIN trains t ON s.train_id = t.id
        JOIN routes r ON s.route_id = r.id
        LEFT JOIN stations st1 ON s.start_station_id = st1.id
        LEFT JOIN stations st2 ON s.end_station_id = st2.id
        ORDER BY s.created_at DESC
    ''').fetchall()
    conn.close()
    return jsonify({'simulations': [dict(sim) for sim in simulations]})

@app.route('/get_visualization_data/<int:simulation_id>')
def get_visualization_data(simulation_id):
    conn = get_db_connection()
    
    # Get simulation details
    simulation = conn.execute('''
        SELECT s.*, t.name as train_name, r.name as route_name
        FROM simulations s
        JOIN trains t ON s.train_id = t.id
        JOIN routes r ON s.route_id = r.id
        WHERE s.id = ?
    ''', (simulation_id,)).fetchone()
    
    if not simulation:
        conn.close()
        return jsonify({'error': 'Simulation not found'}), 404
    
    # Get wear outputs with original conditions
    wear_outputs = conn.execute('''
        SELECT wo.*, 
               rc.crw_l as original_crw_l, rc.crw_r as original_crw_r,
               rc.side_l as original_side_l, rc.side_r as original_side_r,
               rc.remlife_l as original_remlife_l, rc.remlife_r as original_remlife_r,
               rc.wid_l as original_wid_l, rc.wid_r as original_wid_r,
               rc.tiltdiff_l as original_tiltdiff_l, rc.tiltdiff_r as original_tiltdiff_r,
               rc.type_l as original_type_l, rc.type_r as original_type_r,
               rc.gaugediff as original_gaugediff,
               (rc.crw_l + rc.side_l) as original_wear_depth,
               (wo.crw_l + wo.side_l) as wear_depth
        FROM wear_outputs wo
        JOIN original_rail_conditions rc ON wo.km_marker = rc.km_marker 
            AND rc.route_id = (SELECT route_id FROM simulations WHERE id = ?)
        WHERE wo.simulation_id = ?
        ORDER BY wo.km_marker
    ''', (simulation_id, simulation_id)).fetchall()
    
    conn.close()
    
    return jsonify({
        'simulation': dict(simulation),
        'wear_outputs': [dict(wo) for wo in wear_outputs]
    })

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/visualization')
def visualization():
    conn = get_db_connection()
    simulations = conn.execute('''
        SELECT s.id, s.created_at, t.name as train_name, r.name as route_name
        FROM simulations s
        JOIN trains t ON s.train_id = t.id
        JOIN routes r ON s.route_id = r.id
        ORDER BY s.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('visualization.html', simulations=simulations)

@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

if __name__ == '__main__':
    app.run(debug=True)