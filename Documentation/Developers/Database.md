# RailTrack Project Documentation: Database Component

## Purpose

The **Database Component** serves as the persistent storage layer for the RailTrack application, managing data related to railway infrastructure, trains, simulations, and rail wear conditions. It uses SQLite as the database engine, stored in `railway.db`, and is initialized with a schema and sample data to support simulation and analysis features. The database is designed to track routes, stations, track features (curves, bridges, switches), trains, rail conditions, and simulation results.

## Structure

The database is initialized via the `init_db()` function, which creates nine tables and populates them with sample data for the "Soweto-Pretoria Metro Line." The schema uses foreign keys to enforce relationships between entities, and default values ensure rail conditions start in a pristine state.

## Code Breakdown

### 1. Database Initialization (`init_db()`)

* **Connection:** Establishes a connection to `railway.db` using SQLite3.
* **Execution:** Creates tables if they don’t exist and inserts sample data.
* **Commit:** Saves changes and closes the connection.

### 2. Schema

* **Table: `routes`**
    * **Purpose:** Stores railway routes.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `name` (TEXT, NOT NULL): Route name (e.g., "Soweto-Pretoria Metro Line").
        * `total_length` (REAL, NOT NULL): Total length in kilometers (e.g., 95).
        * `description` (TEXT): Optional description (e.g., "Urban commuter route...").

* **Table: `stations`**
    * **Purpose:** Stores stations along routes.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `name` (TEXT, NOT NULL): Station name (e.g., "Soweto Naledi Station").
        * `km_marker` (REAL, NOT NULL): Distance from route start in kilometers (e.g., 0.0).
        * `route_id` (INTEGER, NOT NULL, FOREIGN KEY): References `routes(id)`.
    * **Relationships:** Linked to `routes` via `route_id`.

* **Table: `curves`**
    * **Purpose:** Stores curve details for track geometry.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `route_id` (INTEGER, NOT NULL, FOREIGN KEY): References `routes(id)`.
        * `km_marker` (REAL, NOT NULL): Location along the route.
        * `radius` (REAL, NOT NULL): Curve radius in meters (e.g., 500).
        * `degree` (REAL, NOT NULL): Curve degree (e.g., 15).
        * `direction` (TEXT, CHECK: 'left' or 'right'): Curve direction.
    * **Relationships:** Linked to `routes` via `route_id`.

* **Table: `bridges`**
    * **Purpose:** Stores bridge details along routes.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `route_id` (INTEGER, NOT NULL, FOREIGN KEY): References `routes(id)`.
        * `km_marker` (REAL, NOT NULL): Location along the route.
        * `name` (TEXT): Bridge name (e.g., "M1 Highway Bridge").
        * `length` (REAL, NOT NULL): Bridge length in kilometers (e.g., 0.5).
        * `type` (TEXT): Bridge type (e.g., "elevated").
    * **Relationships:** Linked to `routes` via `route_id`.

* **Table: `rail_switches`**
    * **Purpose:** Stores rail switch details.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `route_id` (INTEGER, NOT NULL, FOREIGN KEY): References `routes(id)`.
        * `km_marker` (REAL, NOT NULL): Location along the route.
        * `type` (TEXT): Switch type (e.g., "junction").
        * `direction` (TEXT, CHECK: 'left', 'right', 'both'): Switch direction.
    * **Relationships:** Linked to `routes` via `route_id`.

* **Table: `trains`**
    * **Purpose:** Stores train specifications and operational data.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `name` (TEXT, NOT NULL): Train name (e.g., "Metro Commuter").
        * `model` (TEXT, NOT NULL): Train model (e.g., "METRO-500").
        * `operator` (TEXT): Operator name (e.g., "JustRail").
        * `total_weight` (REAL, NOT NULL): Total weight in kg (e.g., 300000).
        * `axle_weight` (REAL, NOT NULL): Weight per axle in kg (e.g., 18000).
        * `axle_count` (INTEGER, NOT NULL): Number of axles (e.g., 20).
        * `length` (REAL, NOT NULL): Train length in meters (e.g., 100).
        * `avg_speed` (REAL, NOT NULL): Average speed in km/h (e.g., 60).
        * `max_speed` (REAL, NOT NULL): Maximum speed in km/h (e.g., 90).
        * `tractive_force` (REAL): Tractive force in Newtons (e.g., 50000).
        * `acceleration` (REAL): Acceleration in m/s² (e.g., 1.0).
        * `deceleration` (REAL): Deceleration in m/s² (e.g., 1.5).
        * `emergency_brakes_last_year` (INTEGER): Number of emergency brake uses (e.g., 10).
        * `daily_runs` (INTEGER): Daily trips (e.g., 60).
        * `route_id` (INTEGER, FOREIGN KEY): References `routes(id)`.
    * **Relationships:** Linked to `routes` via `route_id`.

* **Table: `rail_conditions`**
    * **Purpose:** Tracks rail wear and condition at specific points.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `route_id` (INTEGER, NOT NULL, FOREIGN KEY): References `routes(id)`.
        * `km_marker` (REAL, NOT NULL): Location along the route.
        * `crw_l` (REAL, DEFAULT 1.0): Left crown wear (mm).
        * `crw_r` (REAL, DEFAULT 1.0): Right crown wear (mm).
        * `side_l` (REAL, DEFAULT 1.0): Left side wear (mm).
        * `side_r` (REAL, DEFAULT 1.0): Right side wear (mm).
        * `remlife_l` (REAL, DEFAULT 100.0): Left remaining life (% or time).
        * `remlife_r` (REAL, DEFAULT 100.0): Right remaining life (% or time).
        * `wid_l` (REAL, DEFAULT 55.0): Left rail width (mm).
        * `wid_r` (REAL, DEFAULT 55.0): Right rail width (mm).
        * `tiltdiff_l` (REAL, DEFAULT 0.1): Left tilt difference (degrees/radians).
        * `tiltdiff_r` (REAL, DEFAULT 0.1): Right tilt difference (degrees/radians).
        * `type_l` (REAL, DEFAULT 50.0): Left rail type/spec (possibly height in mm).
        * `type_r` (REAL, DEFAULT 50.0): Right rail type/spec (possibly height in mm).
        * `gaugediff` (REAL, DEFAULT 0.0): Gauge difference (mm).
        * `last_updated` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Last update time.
    * **Relationships:** Linked to `routes` via `route_id`.

* **Table: `simulations`**
    * **Purpose:** Stores simulation records.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `train_id` (INTEGER, NOT NULL, FOREIGN KEY): References `trains(id)`.
        * `route_id` (INTEGER, NOT NULL, FOREIGN KEY): References `routes(id)`.
        * `start_station_id` (INTEGER, FOREIGN KEY): References `stations(id)`.
        * `end_station_id` (INTEGER, FOREIGN KEY): References `stations(id)`.
        * `speed` (REAL): Simulation speed (km/h).
        * `weight` (REAL): Simulation weight (kg).
        * `frequency` (REAL): Simulation frequency (Hz).
        * `distance` (REAL): Calculated distance (km).
        * `status` (TEXT, CHECK: 'successful', 'unsuccessful'): Simulation outcome.
        * `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Creation time.
    * **Relationships:** Linked to `trains`, `routes`, and `stations`.

* **Table: `wear_outputs`**
    * **Purpose:** Stores detailed wear results per simulation segment.
    * **Columns:**
        * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier.
        * `simulation_id` (INTEGER, NOT NULL, FOREIGN KEY): References `simulations(id)`.
        * `km_marker` (REAL, NOT NULL): Location along the route.
        * `crw_l` (REAL, DEFAULT 0.0): Left crown wear (mm).
        * `crw_r` (REAL, DEFAULT 0.0): Right crown wear (mm).
        * `side_l` (REAL, DEFAULT 0.0): Left side wear (mm).
        * `side_r` (REAL, DEFAULT 0.0): Right side wear (mm).
        * `remlife_l` (REAL, DEFAULT 0.0): Left remaining life change.
        * `remlife_r` (REAL, DEFAULT 0.0): Right remaining life change.
        * `wid_l` (REAL, DEFAULT 0.0): Left width change (mm).
        * `wid_r` (REAL, DEFAULT 0.0): Right width change (mm).
        * `tiltdiff_l` (REAL, DEFAULT 0.0): Left tilt difference change.
        * `tiltdiff_r` (REAL, DEFAULT 0.0): Right tilt difference change.
        * `gaugediff` (REAL, DEFAULT 0.0): Gauge difference change (mm).
    * **Relationships:** Linked to `simulations` via `simulation_id`.

### 3. Sample Data

* **Route:** "Soweto-Pretoria Metro Line" (95 km).
* **Stations:** 6 stations from Soweto Naledi (0.0 km) to Pretoria (95.0 km).
* **Curves:** 4 curves with varying radii and directions.
* **Bridges:** 2 bridges (M1 Highway, Hennops River).
* **Switches:** 3 switches at key junctions/terminals.
* **Train:** "Metro Commuter" (METRO-500, 300000 kg, 60 km/h avg speed).
* **Rail Conditions:** Initialized every 0.5 km along the 95 km route with default wear values.

## Features

* **Relational Design:** Foreign keys ensure data integrity across tables.
* **Granular Tracking:** Rail conditions and wear outputs recorded at fine intervals (0.5 km).
* **Sample Data:** Pre-populated with a realistic urban route for testing.
* **Extensibility:** Tables like `curves`, `bridges`, and `rail_switches` allow for future feature integration (e.g., wear influenced by track geometry).

## Planned Enhancements

* **Indexes:** Add indexes on `km_marker` and `route_id` for faster queries.
* **Constraints:** Enforce unique `km_marker` per `route_id` in some tables.
* **Additional Data:** Expand sample data to include multiple routes and trains.
* **Wear Integration:** Link `curves`, `bridges`, and `rail_switches` to wear calculations.
* **Triggers:** Automate updates (e.g., `last_updated` in `rail_conditions`).

## Code Snippet

```python
def init_db():
    conn = sqlite3.connect('railway.db')
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS routes ...''')
    c.execute('''CREATE TABLE IF NOT EXISTS stations ...''')
    # ... other tables ...

    # Insert sample data
    c.execute('''INSERT INTO routes ...''', ('Soweto-Pretoria Metro Line', 95, ...))
    c.executemany('INSERT INTO stations ...', stations)
    # ... other inserts ...

    conn.commit()
    conn.close()