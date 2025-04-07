import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('railway.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS routes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  total_length REAL NOT NULL,
                  description TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS stations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  km_marker REAL NOT NULL,
                  route_id INTEGER NOT NULL,
                  FOREIGN KEY(route_id) REFERENCES routes(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS curves
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  route_id INTEGER NOT NULL,
                  km_marker REAL NOT NULL,
                  radius REAL NOT NULL,
                  degree REAL NOT NULL,
                  direction TEXT CHECK(direction IN ('left', 'right')),
                  FOREIGN KEY(route_id) REFERENCES routes(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bridges
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  route_id INTEGER NOT NULL,
                  km_marker REAL NOT NULL,
                  name TEXT,
                  length REAL NOT NULL,
                  type TEXT,
                  FOREIGN KEY(route_id) REFERENCES routes(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS rail_switches
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  route_id INTEGER NOT NULL,
                  km_marker REAL NOT NULL,
                  type TEXT,
                  direction TEXT CHECK(direction IN ('left', 'right', 'both')),
                  FOREIGN KEY(route_id) REFERENCES routes(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS trains
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  model TEXT NOT NULL,
                  operator TEXT,
                  total_weight REAL NOT NULL,
                  axle_weight REAL NOT NULL,
                  axle_count INTEGER NOT NULL,
                  length REAL NOT NULL,
                  avg_speed REAL NOT NULL,
                  max_speed REAL NOT NULL,
                  tractive_force REAL,
                  acceleration REAL,
                  deceleration REAL,
                  emergency_brakes_last_year INTEGER,
                  daily_runs INTEGER,
                  route_id INTEGER,
                  FOREIGN KEY(route_id) REFERENCES routes(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS rail_conditions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  route_id INTEGER NOT NULL,
                  km_marker REAL NOT NULL,
                  crw_l REAL DEFAULT 1.0,
                  crw_r REAL DEFAULT 1.0,
                  side_l REAL DEFAULT 1.0,
                  side_r REAL DEFAULT 1.0,
                  remlife_l REAL DEFAULT 100.0,
                  remlife_r REAL DEFAULT 100.0,
                  wid_l REAL DEFAULT 55.0,
                  wid_r REAL DEFAULT 55.0,
                  tiltdiff_l REAL DEFAULT 0.1,
                  tiltdiff_r REAL DEFAULT 0.1,
                  type_l REAL DEFAULT 50.0,
                  type_r REAL DEFAULT 50.0,
                  gaugediff REAL DEFAULT 0.0,
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(route_id) REFERENCES routes(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS simulations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  train_id INTEGER NOT NULL,
                  route_id INTEGER NOT NULL,
                  start_station_id INTEGER,
                  end_station_id INTEGER,
                  speed REAL,
                  weight REAL,
                  frequency REAL,
                  distance REAL,
                  status TEXT CHECK(status IN ('successful', 'unsuccessful')),
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(train_id) REFERENCES trains(id),
                  FOREIGN KEY(route_id) REFERENCES routes(id),
                  FOREIGN KEY(start_station_id) REFERENCES stations(id),
                  FOREIGN KEY(end_station_id) REFERENCES stations(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS wear_outputs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  simulation_id INTEGER NOT NULL,
                  km_marker REAL NOT NULL,
                  crw_l REAL DEFAULT 0.0,
                  crw_r REAL DEFAULT 0.0,
                  side_l REAL DEFAULT 0.0,
                  side_r REAL DEFAULT 0.0,
                  remlife_l REAL DEFAULT 0.0,
                  remlife_r REAL DEFAULT 0.0,
                  wid_l REAL DEFAULT 0.0,
                  wid_r REAL DEFAULT 0.0,
                  tiltdiff_l REAL DEFAULT 0.0,
                  tiltdiff_r REAL DEFAULT 0.0,
                  gaugediff REAL DEFAULT 0.0,
                  FOREIGN KEY(simulation_id) REFERENCES simulations(id))''')
    
    # Add this table to your init_db() function
    c.execute('''CREATE TABLE IF NOT EXISTS original_rail_conditions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  route_id INTEGER NOT NULL,
                  km_marker REAL NOT NULL,
                  crw_l REAL DEFAULT 1.0,
                  crw_r REAL DEFAULT 1.0,
                  side_l REAL DEFAULT 1.0,
                  side_r REAL DEFAULT 1.0,
                  remlife_l REAL DEFAULT 100.0,
                  remlife_r REAL DEFAULT 100.0,
                  wid_l REAL DEFAULT 55.0,
                  wid_r REAL DEFAULT 55.0,
                  tiltdiff_l REAL DEFAULT 0.1,
                  tiltdiff_r REAL DEFAULT 0.1,
                  type_l REAL DEFAULT 50.0,
                  type_r REAL DEFAULT 50.0,
                  gaugediff REAL DEFAULT 0.0,
                  FOREIGN KEY(route_id) REFERENCES routes(id))''')

    # Insert Soweto-Pretoria Metro Line data
    c.execute('''INSERT INTO routes (name, total_length, description) 
                 VALUES (?, ?, ?)''', 
                 ('Soweto-Pretoria Metro Line', 95, 'Urban commuter route with multiple curves and bridges'))
    
    route_id = c.lastrowid
    
    # Insert stations
    stations = [
        (route_id, 'Soweto Naledi Station', 0.0),
        (route_id, 'Johannesburg Park Station', 20.0),
        (route_id, 'Sandton Station', 35.0),
        (route_id, 'Midrand Station', 55.0),
        (route_id, 'Centurion Station', 75.0),
        (route_id, 'Pretoria Station', 95.0)
    ]
    c.executemany('INSERT INTO stations (route_id, name, km_marker) VALUES (?, ?, ?)', stations)
    
    # Insert curves
    curves = [
        (route_id, 5.0, 500, 15, 'right'),  # Curve after Soweto
        (route_id, 25.0, 800, 10, 'left'),   # Curve approaching Johannesburg
        (route_id, 40.0, 300, 20, 'right'),  # Curve after Sandton
        (route_id, 80.0, 600, 12, 'left')    # Curve before Pretoria
    ]
    c.executemany('INSERT INTO curves (route_id, km_marker, radius, degree, direction) VALUES (?, ?, ?, ?, ?)', curves)
    
    # Insert bridges
    bridges = [
        (route_id, 38.0, 'M1 Highway Bridge', 0.5, 'elevated'),
        (route_id, 78.0, 'Hennops River Bridge', 0.3, 'river')
    ]
    c.executemany('INSERT INTO bridges (route_id, km_marker, name, length, type) VALUES (?, ?, ?, ?, ?)', bridges)
    
    # Insert rail switches
    switches = [
        (route_id, 0.0, 'junction', 'both'),   # Soweto Naledi
        (route_id, 20.0, 'junction', 'both'),  # Johannesburg Park
        (route_id, 95.0, 'terminal', 'both')   # Pretoria
    ]
    c.executemany('INSERT INTO rail_switches (route_id, km_marker, type, direction) VALUES (?, ?, ?, ?)', switches)
    
    # Insert Metro Commuter train
    c.execute('''INSERT INTO trains 
                 (name, model, operator, total_weight, axle_weight, axle_count, length, 
                  avg_speed, max_speed, tractive_force, acceleration, deceleration, 
                  emergency_brakes_last_year, daily_runs, route_id)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 ('Metro Commuter', 'METRO-500', 'JustRail', 300000, 18000, 20, 100,
                  60, 90, 50000, 1.0, 1.5, 10, 60, route_id))
    
    # Initialize rail conditions for the entire route (every 0.5 km)
    km_markers = [x * 0.5 for x in range(int(95 * 2) + 1)]
    for km in km_markers:
        c.execute('''INSERT INTO rail_conditions 
                     (route_id, km_marker, crw_l, crw_r, side_l, side_r, remlife_l, remlife_r, 
                      wid_l, wid_r, tiltdiff_l, tiltdiff_r, type_l, type_r, gaugediff)
                     VALUES (?, ?, 1.0, 1.0, 1.0, 1.0, 100.0, 100.0, 55.0, 55.0, 0.1, 0.1, 50.0, 50.0, 0.0)''',
                     (route_id, km))
        # After creating rail_conditions, populate original_rail_conditions with the same data
        c.execute('''INSERT INTO original_rail_conditions 
                     (route_id, km_marker, crw_l, crw_r, side_l, side_r, remlife_l, remlife_r, 
                      wid_l, wid_r, tiltdiff_l, tiltdiff_r, type_l, type_r, gaugediff)
                     SELECT route_id, km_marker, crw_l, crw_r, side_l, side_r, remlife_l, remlife_r, 
                         wid_l, wid_r, tiltdiff_l, tiltdiff_r, type_l, type_r, gaugediff
                     FROM rail_conditions 
                     WHERE route_id = ? AND km_marker = ?''',
                     (route_id, km))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully with sample data.")