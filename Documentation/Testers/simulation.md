# RailTrack Project Guide: Simulation Area

## What It Does

The **Simulation Area** is the core of RailTrack, where you can configure and test train simulations. It's designed to help you plan train operations and understand the impact on rail infrastructure. You can select trains, define routes, set operational parameters (speed, weight, frequency), and then RailTrack calculates the effects, including rail wear. It also maintains a history of the last 10 simulations for review. All data is stored in a database for persistence.

## Why It Matters

This area is crucial for:

* **Planning train runs:** Test different scenarios to optimize operations.
* **Assessing rail health:** Evaluate potential wear and tear on the tracks.
* **Maintaining records:** Review past simulations to identify trends and plan maintenance.

## How It Looks

The Simulation Area is divided into two main sections:

1.  **Setup Box (Simulation Configuration):**
    * A white container labeled "Simulation Configuration" for inputting simulation parameters.
    * Dropdown menus for selecting trains, routes, and start/end stations.
    * Input fields for speed, weight, and frequency.
    * A display for the calculated distance between stations.
    * Buttons: "Calculate" (to compute distance), "Reset" (to clear inputs), and "Run Simulation" (to execute the simulation).

2.  **Past Runs Table (Recent Simulations):**
    * A white container labeled "Recent Simulations" displaying a table of the last 10 simulations.
    * Columns: Date, Train, Route, Distance, Status (green for success, red for failure), and "View Wear" (link to detailed wear outputs).

## What You Can Do Now

* **Configure simulations:** Select trains, routes, and stations, and input speed, weight, and frequency (or use random values).
* **Calculate distance:** Click "Calculate" to display the distance between selected stations.
* **Run simulations:** Click "Run Simulation" to execute simulations and store results.
* **Review past simulations:** View the history table and click "View Wear" for detailed wear data.

## How It Figures Things Out (Calculations)

Here’s a simplified explanation of the calculations performed by RailTrack:

1.  **Distance Calculation:**
    * **What:** Determines the distance between start and end stations.
    * **How:**
        * Extracts kilometer markers from station data.
        * Calculates the absolute difference between the markers: `distance = |endKm - startKm|`.
        * Displays the result in the setup box and stores it in the database.
    * **Where:** Client-side (for display) and server-side (for validation/storage).

2.  **Frequency Calculation:**
    * **What:** Calculates the frequency of wheel passes.
    * **How:**
        * Uses train data: `frequency = (train.axle_count * train.daily_runs) / 1000`.
        * **Where:** Client-side only.
    * **Why:** Provides a metric for train frequency, but does not affect wear calculation currently.

3.  **Wear Calculations (Per Segment):**
    * **What:** Estimates rail wear per 0.5 km segment.
    * **How:**
        * Inputs: speed, weight, and segment length (0.5 km).
        * Calculates wear metrics using simplified linear formulas:
            * `Crown Wear (crw_l/r)`: `0.01 * speed / 100`.
            * `Side Wear (side_l/r)`: `0.005 * weight / 100000`.
            * `Remaining Life (remlife_l/r)`: `-0.1 * speed * weight / 1000000`.
            * `Width Change (wid_l/r)`: `-0.001 * weight / 100000`.
            * `Tilt Difference (tiltdiff_l/r)`: `0.0005 * speed / 100`.
            * `Gauge Difference (gaugediff)`: `0.0002 * weight / 100000`.
        * Stores wear data in the database.
    * **Where:** Server-side, executed in 0.5 km intervals.
    * **Why:** Simulates rail degradation per segment.

4.  **Alternative Wear Calculation (Aggregate):**
    * **What:** Estimates total wear over the entire route.
    * **How:**
        * Inputs: speed, weight, start/end kilometer markers, train data.
        * Uses factors: `speed_factor`, `weight_factor`, `distance_factor`.
        * Calculates aggregate wear.
    * **Where:** Separate server-side endpoint (not used by `run_simulation`).
    * **Why:** Provides a quick, overall wear estimate.

**Note:** The current wear calculations are simplified and may be refined in future updates to incorporate more complex factors.