# RailTrack Project Documentation: Simulation Component

## Purpose

The **Simulation Component** is a key part of the RailTrack application, designed to allow users to set up and run train simulations. It's where you configure train routes, operational parameters, and view the results of past simulations. This component adds interactive features and data-driven elements to the basic dashboard setup.

## Structure

The Simulation Component is organized into two main sections:

1.  **Simulation Configuration:** This section provides a form for users to input and adjust simulation parameters.
2.  **Recent Simulations:** This section displays a table showing the history and results of previously run simulations.

## Code Breakdown

### 1. HTML Structure

* **Simulation Configuration:**
    * A container with input fields for selecting trains, routes, start/end stations, speed, weight, and frequency.
    * A display for the calculated distance between stations.
    * Buttons for "Calculate," "Reset," and "Run Simulation."
* **Recent Simulations:**
    * A table listing past simulations with details like date, train, route, distance, status, and actions.
    * Uses templating to dynamically populate the table with data from the backend.

### 2. Simulation Configuration Details

* **Train Selection:**
    * A dropdown menu (`#trainSelect`) populated with train options.
    * Selecting a train triggers the loading of related route and station data.
* **Route Selection:**
    * A dropdown menu (`#routeSelect`) that becomes active after a train is chosen.
* **Speed, Weight, and Frequency Inputs:**
    * Numeric input fields (`#speedInput`, `#weightInput`, `#frequencyInput`) with randomize buttons.
    * Default values are set based on the selected train.
* **Start and End Stations:**
    * Dropdown menus (`#startStationSelect`, `#endStationSelect`) that become active after a route is chosen.
* **Distance Display:**
    * A read-only field (`#distanceDisplay`) showing the calculated distance between selected stations.
* **Action Buttons:**
    * **Calculate:** Computes the distance between stations.
    * **Reset:** Clears all input fields and resets dropdowns.
    * **Run Simulation:** Sends the simulation parameters to the backend for processing.

### 3. Recent Simulations Table

* **Columns:** Date, Train, Route, Distance, Status, and Actions.
* **Status:** Color-coded to indicate simulation success or failure.
* **Actions:** Includes a "View Wear" link to detailed simulation outputs.
* **Dynamic Data:** Populated using a templating engine, showing data from the backend.

### 4. JavaScript Functionality

* **Initialization:**
    * Sets up the date picker (inherited from the dashboard).
    * Handles sidebar toggling and navigation highlighting.
* **Train Selection:**
    * Fetches route and station data from the backend (`/get_route_data/${trainId}`).
    * Populates dropdowns and sets default input values.
* **Randomize Buttons:**
    * Generates random values for speed, weight, and frequency.
* **Calculate Button:**
    * Extracts kilometer markers from station options and calculates the distance.
* **Run Simulation Button:**
    * Collects form data and sends it to the backend (`/run_simulation`).
* **Reset Button:**
    * Clears all form fields and resets the dropdown menus.

### 5. Styling

* **Tailwind CSS:**
    * Provides responsive grid layouts and card styling.
    * Styles buttons and tables for readability.
* **Custom Behavior:**
    * Adds focus effects to input fields.
    * Styles the random buttons.

## Features

* **Interactive Configuration:** Allows users to select trains, routes, and stations, with dependent fields enabling progressively.
* **Randomization:** Enables randomizing speed, weight, and frequency for testing.
* **Distance Calculation:** Computes the distance between selected stations.
* **Simulation Execution:** Sends data to the backend for processing simulations.
* **Recent Simulations Display:** Shows a history of simulations with status and detailed output links.

## Planned Enhancements

* **Real-Time Validation:** Checks for invalid inputs.
* **Loading States:** Shows loading indicators during data fetching or simulation runs.
* **Error Handling:** Displays user-friendly error messages.
* **Dynamic Updates:** Refreshes the recent simulations table without page reloads.

## Code Snippet

```html
<main class="p-6">
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Simulation Configuration</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            </div>
        <div class="flex justify-end space-x-3 mt-6">
            <button id="calculateBtn">Calculate</button>
            <button id="resetBtn">Reset</button>
            <button id="runSimulationBtn">Run Simulation</button>
        </div>
    </div>
    <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Recent Simulations</h3>
        <table class="min-w-full divide-y divide-gray-200">
            </table>
    </div>
</main>
<script>
    // JavaScript for interactivity
</script>