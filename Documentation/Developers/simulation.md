```markdown
# RailTrack Project Documentation: Simulation Component

## Purpose

The **Simulation Component** is a central feature of the RailTrack application, designed to facilitate the configuration and execution of train simulations. It integrates with a Flask backend to retrieve train and route data, calculate rail wear, and store simulation results in a SQLite database (railway.db). Users can set simulation parameters through a form and review past simulations in a table, with links to detailed wear outputs.

## Structure

The Simulation Component is composed of:

1.  **Simulation Configuration:** A form for inputting simulation parameters (train, route, stations, speed, weight, frequency).
2.  **Recent Simulations:** A table displaying the 10 most recent simulation records.

The backend, developed with Flask, manages data fetching, simulation execution, and wear calculations, utilizing a SQLite database.

## Code Breakdown

### 1. Frontend (HTML + JavaScript)

* **Simulation Configuration:**
    * **Train Selection:** Dynamically populated from the `trains` table via the `/` route.
    * **Route Selection:** Fetched from `/get_route_data/<train_id>` upon train selection.
    * **Stations:** Populated from route data, including kilometer markers.
    * **Parameters:** Inputs for speed, weight, and frequency, with randomization options and default values from train data.
    * **Distance:** Calculated client-side using station kilometer markers.
    * **Buttons:**
        * **Calculate:** Updates the distance display.
        * **Reset:** Clears all input fields.
        * **Run Simulation:** Sends data to `/run_simulation` via POST.
* **Recent Simulations:**
    * Table populated from the `simulations`, `trains`, and `routes` tables via the `/` route.
    * Includes "View Wear" links to `/get_wear_outputs/<simulation_id>`.
* **JavaScript:**
    * Fetches route data and populates dropdowns.
    * Handles parameter randomization.
    * Submits simulation data and redirects on success.

### 2. Backend (Flask)

* **Database Schema (Assumed):**
    * `trains`: id, name, route_id, max_speed, total_weight, avg_speed, axle_count, daily_runs.
    * `routes`: id, name.
    * `stations`: id, route_id, name, km_marker.
    * `simulations`: id, train_id, route_id, start_station_id, end_station_id, speed, weight, frequency, distance, status, created_at.
    * `rail_conditions`: route_id, km_marker, crw_l, crw_r, side_l, side_r, remlife_l, remlife_r, wid_l, wid_r, tiltdiff_l, tiltdiff_r, gaugediff, last_updated.
    * `wear_outputs`: simulation_id, km_marker, crw_l, crw_r, side_l, side_r, remlife_l, remlife_r, wid_l, wid_r, tiltdiff_l, tiltdiff_r, gaugediff.
* **Routes:**
    * `/`: Renders `simulation.html` with train and simulation data.
    * `/get_route_data/<train_id>`: Returns route, station, rail condition, and train data.
    * `/get_rail_conditions/<route_id>/<km_marker>`: Retrieves rail conditions near a kilometer marker.
    * `/calculate_wear`: Calculates wear (simplified model).
    * `/run_simulation`:
        * Validates form data.
        * Calculates distance.
        * Inserts simulation record.
        * Computes wear at 0.5 km intervals, updating `wear_outputs` and `rail_conditions`.
        * Redirects to the simulation page.
    * `/get_wear_outputs/<simulation_id>`: Renders `wear_outputs.html` with wear data.

### 3. Simulation Logic

* **Wear Calculation:**
    * Uses simplified formulas based on speed, weight, and distance.
    * Calculates wear at 0.5 km intervals.
    * Updates rail conditions and stores wear outputs.
* **Parameters:**
    * Speed: Linear influence on wear.
    * Weight: Proportional impact on wear.
    * Frequency: Used in frontend but not directly in wear (expandable).
* **Output Metrics:**
    * `crw_l/r`: Crown wear (left/right).
    * `side_l/r`: Side wear (left/right).
    * `remlife_l/r`: Remaining life (left/right).
    * `wid_l/r`: Width change (left/right).
    * `tiltdiff_l/r`: Tilt difference (left/right).
    * `gaugediff`: Gauge difference.

### 4. Calculations

1.  **Distance Calculation**
    * **Where:** Performed both client-side (for display) and server-side (for validation/storage).
    * **How:**
        * **Client-Side (JavaScript):**
            * Extracts kilometer markers from station options using regex: `/\\(([\\d.]+) km\\)/`.
            * Formula: `distance = |endKm - startKm|`.
            * Result displayed in `#distanceDisplay`.
        * **Server-Side (Flask):**
            * Queries kilometer markers from the `stations` table.
            * Formula: `distance = abs(end_station['km_marker'] - start_station['km_marker'])`.
            * Stored in the `simulations` table.
    * **Purpose:** Determines route segment length for wear calculations.

2.  **Frequency Calculation**
    * **Where:** Client-side only (JavaScript).
    * **How:**
        * Fetches `axle_count` and `daily_runs` from train data.
        * Formula: `frequency = (train.axle_count * train.daily_runs) / 1000`.
        * Result displayed in `#frequencyInput`.
    * **Purpose:** Provides a simplified frequency metric (Hz), not used in wear calculations.

3.  **Wear Calculations (Flask /run_simulation)**
    * **Where:** Server-side, executed in 0.5 km intervals.
    * **How:**
        * Inputs: `speed`, `weight`, segment length (0.5 km).
        * Iterates from `min(start_km, end_km)` to `max(start_km, end_km)`.
        * Calculates wear metrics using simplified linear formulas:
            * `crw_l/r`: `0.01 * speed / 100`.
            * `side_l/r`: `0.005 * weight / 100000`.
            * `remlife_l/r`: `-0.1 * speed * weight / 1000000`.
            * `wid_l/r`: `-0.001 * weight / 100000`.
            * `tiltdiff_l/r`: `0.0005 * speed / 100`.
            * `gaugediff`: `0.0002 * weight / 100000`.
        * Stores wear data in `wear_outputs` and updates `rail_conditions`.
    * **Purpose:** Simulates rail degradation per segment.

4.  **Alternative Wear Calculation (Flask /calculate_wear)**
    * **Where:** Separate endpoint, not used by `/run_simulation`.
    * **How:**
        * Inputs: `speed`, `weight`, `start_km`, `end_km`, `train_id`.
        * Factors: `speed_factor`, `weight_factor`, `distance_factor`.
        * Calculates aggregate wear over the full distance.
    * **Purpose:** Provides a simplified, aggregate wear estimate.

### 5. Styling

* **Tailwind CSS:** Responsive grid, card layouts, and button styles.
* **Dynamic States:** Focus and hover effects for inputs and buttons.

## Features

* **Dynamic Configuration:** Database-driven train, route, and station selection.
* **Randomization:** Client-side parameter randomization.
* **Distance Calculation:** Client and server-side distance calculation.
* **Simulation Execution:** Wear calculations and database updates.
* **Recent Simulations:** Display of recent simulations with wear output links.
* **Wear Tracking:** Detailed wear data per kilometer segment.

## Backend Integration

* **Data Flow:**
    * `/` provides initial train and simulation data.
    * `/get_route_data/<train_id>` populates route and station options.
    * `/run_simulation` processes and stores simulation results.
    * `/get_wear_outputs/<simulation_id>` shows detailed wear data.
* **Error Handling:** Returns JSON errors for invalid requests; rolls back on exceptions.

## Planned Enhancements

* **Advanced Wear Model:** Incorporate more factors like frequency and physics.
* **Validation:** Add checks for station order and parameter ranges.
* **Visualization:** Integrate wear data into charts.
* **Optimization:** Cache frequent queries.
