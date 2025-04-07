# RailTrack Project Guide: Storage (Database)

## What It Does

The **Storage** component of RailTrack acts as a central repository for all data related to trains, tracks, and simulations. It utilizes SQLite, a lightweight database system, to store information in a file named `railway.db`. Upon initialization, RailTrack creates the necessary tables and populates them with sample data, such as a train route from Soweto to Pretoria, to facilitate testing and development.

## Why It Matters

This storage solution is essential for:

* **Efficient data retrieval:** Allows quick access to train and track information.
* **Persistent data storage:** Ensures simulation results and other data are saved for future reference.
* **Realistic simulation planning:** Provides a foundation for testing and refining rail operations.

## How It’s Organized

The database is structured into nine primary tables:

* **Routes:** Stores information about railway routes, including name, total length, and description.
* **Stations:** Contains details about stations along each route, such as name and kilometer marker.
* **Curves:** Records data about track curves, including radius, degree, and direction.
* **Bridges:** Stores information about bridges along routes, such as name, length, and type.
* **Switches:** Details about rail switches, including type and direction.
* **Trains:** Holds train specifications and operational data, such as weight, speed, and daily runs.
* **Rail Conditions:** Tracks rail wear and condition at specific points along routes.
* **Simulations:** Stores records of each simulation run, including parameters and results.
* **Wear Details:** Contains detailed wear output data for each simulation segment.

These tables are interconnected using foreign keys to maintain data integrity and relationships.

## What’s In It Now

The database is pre-populated with:

* A 95 km route from Soweto to Pretoria with 6 stations.
* 4 curves, 2 bridges, and 3 switches along the route.
* A "Metro Commuter" train with operational parameters.
* Initial rail condition data at 0.5 km intervals along the route.

## What You Can Do Now

* **Utilize the sample data:** Experiment with the Soweto-Pretoria route and the Metro Commuter train.
* **Store simulation data:** Save new simulation results to the database.
* **Retrieve stored data:** Access past simulation results and track condition data.

## What’s Coming Next

* **Expanded sample data:** Inclusion of additional routes and trains.
* **Enhanced wear modeling:** Integration of curve and bridge data into wear calculations.
* **Performance optimization:** Implementation of indexing and caching for faster data retrieval.

## Why It’s Helpful

* **Organized data storage:** Ensures data integrity and accessibility.
* **Scalability:** Facilitates future expansion with additional data.
* **Practical starting point:** Provides a realistic dataset for initial testing.

## How It Works (In Simple Terms)

The database functions as a digital librarian:

* It creates organized storage spaces (tables) for rail-related information.
* It populates these spaces with an initial set of data (Soweto-Pretoria route).
* It records and stores data from each simulation run.