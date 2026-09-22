# IDIECS – Integrated Disaster Intelligence and Emergency Coordination

## Integrated Disaster Intelligence and Emergency Coordination Using XGBoost Flood Prediction and Risk-Aware A* Routing

**IDIECS** is an AI-driven disaster intelligence and emergency coordination system designed to support flood-risk assessment and evacuation planning.

The system combines **XGBoost-based flood prediction, real-time weather information, spatial flood-hazard data, OpenStreetMap road networks, risk-aware A* routing, shelter evaluation, dynamic rerouting, and emergency alerts** into an integrated disaster-response pipeline.

---

## 📌 Project Overview

Floods can affect not only residential areas and infrastructure but also the accessibility and safety of transportation networks. A useful evacuation-support system therefore needs to consider both the **probability of flooding** and the **risk associated with individual road segments**.

IDIECS addresses this by connecting flood prediction with geospatial risk-aware routing.

The current system provides:

- 🌧️ Flood probability prediction using XGBoost
- 📊 Historical weather and flood-event analysis
- 🌐 Real-time weather integration
- 🚨 Flood-risk classification
- 🗺️ OpenStreetMap-based real road networks
- 🌊 Spatial flood-hazard exposure for road segments
- 🛣️ Risk-aware evacuation routing using A* search
- 🏠 Shelter candidate evaluation
- 🔄 Dynamic route recalculation when flood probability changes
- 📢 Risk-based emergency alert generation

The overall system combines:

**Machine Learning + Real-Time Weather + Geospatial Flood Data + OpenStreetMap + Graph Routing**

to provide an integrated flood evacuation decision-support prototype.

---

# 🎯 Objectives

The main objectives of IDIECS are:

1. Predict flood probability using historical weather and flood-event data.
2. Integrate current weather conditions into the flood-prediction pipeline.
3. Classify predicted flood probability into LOW, MEDIUM, and HIGH risk levels.
4. Represent real road networks using OpenStreetMap data.
5. Incorporate spatial flood-hazard information into road segments.
6. Calculate effective road risk using flood probability and spatial road exposure.
7. Identify evacuation routes using risk-aware A* search.
8. Evaluate evacuation shelters using route distance, flood exposure, capacity, and accessibility.
9. Support dynamic rerouting when flood probability changes significantly.
10. Generate emergency alerts according to the identified flood-risk level.

---

# 🏗️ System Architecture

```text
                  HISTORICAL WEATHER DATA
                           +
                    FLOOD EVENT DATA
                           │
                           ▼
                  DATA PREPROCESSING
                           │
                           ▼
                   FEATURE ENGINEERING
                           │
                           ▼
                    XGBOOST TRAINING
                           │
                           ▼
                    FLOOD MODEL (.pkl)
                           │
                           │
                           ▼
                ┌─────────────────────┐
                │   REAL-TIME WEATHER │
                │        API          │
                └──────────┬──────────┘
                           │
                           ▼
                   CURRENT WEATHER
                           │
                           ▼
                    XGBOOST MODEL
                           │
                           ▼
                  FLOOD PROBABILITY
                           │
                           ▼
                    RISK ENGINE
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
           LOW          MEDIUM          HIGH
             │             │             │
             │             │             ▼
             │             │       EVACUATION
             │             │          SUPPORT
             │             │             │
             └─────────────┴─────────────┘
                           │
                           ▼
                 FLOOD HAZARD DATA
                           │
                           ▼
                 SPATIAL ROAD EXPOSURE
                           │
                           ▼
                 OPENSTREETMAP NETWORK
                           │
                           ▼
                 RISK-AWARE A* ROUTING
                           │
                           ▼
                  SHELTER EVALUATION
                           │
                           ▼
                 RECOMMENDED ROUTE
                           +
                 SHELTER INFORMATION
                           │
                           ▼
                  ALERT GENERATION
                           │
                           ▼
                  DYNAMIC REROUTING

🔬 Methodology
1. Data Collection

The project uses historical weather, rainfall, and flood-event information for model development.

The repository contains datasets including:

Historical weather data
Rainfall data
Flood-event data
State/city weather data
Training datasets
Prototype datasets

The project also uses a Chennai flood-hazard dataset containing spatial flood-risk polygons.

The SEN12FLOOD satellite dataset is maintained separately because of its large size and is excluded from the GitHub repository.

2. Data Preprocessing

The collected datasets are processed before model training.

Major preprocessing operations include:

Handling missing values
Removing invalid records
Date-based processing
Combining weather and flood-event information
Generating rainfall-related features
Preparing flood labels
Creating model-ready training datasets
3. Feature Engineering

Rainfall accumulation features are generated to represent recent precipitation patterns.

Important features include:

rainfall_1day
rainfall_3day
rainfall_7day

Additional weather features include:

Temperature
Humidity
Pressure
Wind Speed

The implementation also uses:

actual
normal
deviation

where rainfall deviation represents the difference between observed rainfall and the historical normal.

🤖 XGBoost Flood Prediction

The flood prediction component uses XGBoost (Extreme Gradient Boosting).

The trained model learns relationships between weather/rainfall conditions and historical flood events.

Model Input

The current prediction implementation uses:

actual
rainfall_1day
rainfall_3day
rainfall_7day
normal
deviation
temperature
humidity
pressure
wind_speed
Prediction Process
Current Weather
      │
      ▼
Feature Construction
      │
      ▼
XGBoost Model
      │
      ▼
predict_proba()
      │
      ▼
Flood Probability

The trained model is stored as:

ml/flood_model.pkl
🚨 Flood Risk Assessment

The predicted probability is passed to the risk engine.

The current prototype uses configurable thresholds:

Probability < 0.30
        ↓
      LOW

0.30 ≤ Probability < 0.70
        ↓
     MEDIUM

Probability ≥ 0.70
        ↓
      HIGH

The risk engine also generates an appropriate action message.

LOW
No immediate evacuation required;
continue monitoring conditions.
MEDIUM
Monitor the situation and prepare
for possible evacuation.
HIGH
Evacuate to a safe shelter using
the recommended route.

Implementation:

backend/risk_engine.py
🌐 Real-Time Weather Integration

The system can retrieve current weather conditions through the weather API.

The current weather pipeline obtains information such as:

Temperature
Humidity
Rainfall
Atmospheric pressure
Wind speed

The current weather values are transformed into the same feature structure expected by the trained XGBoost model.

Weather API
    ↓
Current Weather
    ↓
Feature Construction
    ↓
XGBoost
    ↓
Flood Probability
    ↓
Risk Level

Relevant implementation:

backend/weather_api.py
backend/prediction.py
backend/main.py
🌊 Spatial Flood Hazard Integration

A major extension of the current system is the integration of spatial flood-hazard information into the road network.

The Chennai flood-hazard dataset contains polygons classified as:

VERY LOW
LOW
MODERATE
HIGH
VERY HIGH

These categories are converted into normalized exposure values.

VERY LOW   → 0.10
LOW        → 0.30
MODERATE   → 0.50
HIGH       → 0.75
VERY HIGH  → 0.95

Road segments are spatially evaluated against the flood-hazard polygons.

Flood Hazard Polygons
          │
          ▼
     Spatial Join
          │
          ▼
    Road Segments
          │
          ▼
    Flood Exposure

Implementation:

backend/flood_exposure.py

The large KML dataset is intentionally excluded from GitHub and must be provided locally.

🛣️ Real Road Network

The system uses OpenStreetMap road data through OSMnx.

The road network is represented as a graph:

Road Intersections → Nodes
Road Segments       → Edges

Each road segment can contain information such as:

Length
Flood Exposure
Road Condition
Risk Level
Routing Cost

Implementation:

backend/road_network.py
⚠️ Road Risk Calculation

Road risk combines the predicted flood probability with the spatial flood exposure of the individual road segment.

The prototype calculates effective risk as:

Effective Risk =
    0.7 × Flood Probability
    +
    0.3 × Road Flood Exposure

The resulting value is classified as:

LOW
MEDIUM
HIGH

Blocked roads are assigned infinite routing cost and are therefore excluded from the route.

Implementation:

backend/road_risk.py

The weights and penalties are configurable prototype parameters and should be further calibrated using experimental validation before being interpreted as universally optimal values.

🧭 Risk-Aware A* Evacuation Routing

Unlike a conventional shortest-path algorithm, IDIECS does not consider distance alone.

The routing system evaluates:

Distance
+
Flood Risk
+
Road Exposure
+
Road Condition

The routing process is:

Source Location
       │
       ▼
Nearest Road Node
       │
       ▼
OpenStreetMap Road Graph
       │
       ▼
Flood Exposure Information
       │
       ▼
Risk-Aware Edge Cost
       │
       ▼
A* Search
       │
       ▼
Evacuation Route

The implementation uses the A* search strategy to identify a route while considering the risk-adjusted cost of road segments.

Implementation:

backend/routing.py
🏠 Shelter Evaluation

The system includes a prototype shelter-selection component.

Shelter candidates are evaluated using factors including:

Route distance
Average route flood exposure
Available capacity
Accessibility

The prototype shelter score is calculated from these factors.

Shelter Candidate
       │
       ├── Route Distance
       ├── Flood Exposure
       ├── Capacity
       └── Accessibility
              │
              ▼
        Shelter Score
              │
              ▼
       Shelter Selection

Implementation:

backend/shelter.py
backend/shelter_service.py
Current data status

The current data/shelters.csv contains development-only prototype shelter records.

These should not be interpreted as verified live emergency-shelter availability.

Future integration will replace the prototype records with verified disaster-management/relief-centre data.

🔄 Dynamic Rerouting

Flood conditions can change during an evacuation.

The system therefore includes a dynamic route-management component.

Initial Flood Probability
          │
          ▼
     Calculate Route
          │
          ▼
   Monitor New Probability
          │
          ▼
   Probability Changed?
       /          \
     YES           NO
      │             │
      ▼             ▼
 Recalculate      Keep Route
    Route

The current prototype triggers route recalculation when the flood probability changes by at least:

0.05

Implementation:

backend/dynamic_routing.py
📢 Emergency Alerts

The alert module generates messages according to the current flood-risk level.

Flood Probability
       │
       ▼
Risk Classification
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
LOW  MEDIUM  HIGH
 │     │      │
 ▼     ▼      ▼
Monitor  Prepare  Evacuate

Implementation:

backend/alerts.py
🔗 Integrated Disaster Workflow

The complete implemented decision-support flow is:

Real-Time Weather
       │
       ▼
Feature Construction
       │
       ▼
XGBoost Flood Prediction
       │
       ▼
Flood Probability
       │
       ▼
Risk Engine
       │
       ▼
Flood Risk Level
       │
       ├───────────────┐
       │               │
       ▼               ▼
Monitoring       Evacuation Support
                       │
                       ▼
              Flood Hazard Map
                       │
                       ▼
              Road Flood Exposure
                       │
                       ▼
             OpenStreetMap Graph
                       │
                       ▼
              Risk-Aware A* Search
                       │
                       ▼
                Shelter Evaluation
                       │
                       ▼
              Evacuation Route
                       │
                       ▼
                Alert Generation
                       │
                       ▼
               Dynamic Rerouting
🧪 Testing Modules

The current implementation contains component-level testing modules:

backend/test_road_network.py
backend/test_flood_exposure.py
backend/test_risk_routing.py
backend/test_real_routing.py
backend/test_shelter_routing.py

These tests are used to verify:

Road-network loading
Flood-hazard loading
Spatial road exposure
Risk-aware routing
Real road-network routing
Shelter evaluation
Evacuation-route generation
📊 Current Prototype Results

The current implementation was tested using a Chennai road network and flood-hazard dataset.

The spatial flood-exposure processing successfully loaded:

7,453 flood polygons

and classified road segments into multiple exposure levels.

A risk-aware routing experiment demonstrated a trade-off between route distance and flood exposure.

Example prototype result:

Shortest-distance route:
Distance              = 13.196 km
Average flood exposure = 0.3219

Risk-aware route:
Distance              = 26.17 km
Average flood exposure = 0.1523

Additional distance   = 12.974 km

This demonstrates that the routing system can select a longer route when the route's spatial flood exposure is lower.

These values represent prototype experimental results for the tested network and parameter configuration, not universal routing guarantees.

📂 Project Structure
CAPSTONE/
│
├── backend/
│   ├── main.py
│   ├── prediction.py
│   ├── weather_api.py
│   ├── risk_engine.py
│   ├── road_risk.py
│   ├── road_network.py
│   ├── flood_exposure.py
│   ├── routing.py
│   ├── shelter.py
│   ├── shelter_service.py
│   ├── evacuation_service.py
│   ├── dynamic_routing.py
│   ├── alerts.py
│   ├── disaster_service.py
│   │
│   └── tests/
│       ├── test_flood_exposure.py
│       ├── test_real_routing.py
│       ├── test_risk_routing.py
│       ├── test_road_network.py
│       └── test_shelter_routing.py
│
├── data/
│   ├── flood/
│   │   ├── README.md
│   │   └── chennai_flood_hazard.kml
│   │
│   ├── weather/
│   ├── shelters.csv
│   ├── balanced_training_data.csv
│   ├── flood_events.csv
│   ├── flood_events_clean.csv
│   ├── prototype_training_data.csv
│   └── training_data.csv
│
├── ml/
│   ├── flood_model.pkl
│   ├── preprocess.py
│   ├── predict_flood.py
│   ├── merge_data.py
│   ├── balance_dataset.py
│   └── ...
│
├── frontend/
│
├── .gitignore
├── README.md
└── requirements.txt
🛠️ Technologies Used
Programming
Python
JavaScript (if used by the frontend)
Machine Learning
XGBoost
Scikit-learn
Pandas
NumPy
Joblib
Geospatial Processing
GeoPandas
Shapely
OSMnx
OpenStreetMap
Graph and Routing
NetworkX
A* search
Risk-aware edge-cost calculation
Weather
Weather API
Historical weather datasets
Development
Visual Studio Code
Git
GitHub
⚙️ Installation
1. Clone the repository
git clone https://github.com/HEMAPRIYAKV/CAPSTONE.git
cd CAPSTONE
2. Create a virtual environment
python -m venv venv
3. Activate the virtual environment
Windows
venv\Scripts\activate
Linux/macOS
source venv/bin/activate
4. Install dependencies
pip install -r requirements.txt
🌊 Flood Hazard Dataset Setup

The Chennai flood-hazard KML is approximately 38 MB and is intentionally excluded from the GitHub repository.

Place the dataset locally at:

data/flood/chennai_flood_hazard.kml

Refer to:

data/flood/README.md

for dataset information.

▶️ Running the Project

From the project root:

python backend/main.py

If the backend uses FastAPI/Uvicorn, the corresponding server command can be used according to the current backend configuration.

🧪 Running Tests
Test road network
python -m backend.test_road_network
Test flood exposure
python -m backend.test_flood_exposure
Test risk-aware routing
python -m backend.test_risk_routing
Test real road routing
python -m backend.test_real_routing
Test shelter routing
python -m backend.test_shelter_routing
📊 Dataset Information

Important datasets include:

Dataset	Purpose
weather.csv	Weather and rainfall information
clean_weather.csv	Cleaned weather data
historical_weather.csv	Historical weather information
state_weather.csv	State-level weather information
cities.csv	City information
flood_events.csv	Flood-event records
flood_events_clean.csv	Processed flood-event data
training_data.csv	Model training dataset
balanced_training_data.csv	Balanced training dataset
prototype_training_data.csv	Prototype training dataset
emdat.csv	Disaster-event information
chennai_flood_hazard.kml	Spatial flood-hazard polygons
🛰️ SEN12FLOOD

The SEN12FLOOD satellite imagery dataset is maintained separately because of its large size.

SEN12FLOOD
≈ 17+ GB

It is excluded from the GitHub repository through .gitignore.

📈 Machine Learning Pipeline
Historical Weather Data
          +
Flood Event Data
          │
          ▼
Data Cleaning
          │
          ▼
Feature Engineering
          │
          ▼
Training Dataset
          │
          ▼
XGBoost Training
          │
          ▼
Model Evaluation
          │
          ▼
flood_model.pkl
          │
          ▼
Real-Time Weather
          │
          ▼
Feature Construction
          │
          ▼
Flood Probability
          │
          ▼
Risk Classification
🚗 Risk-Aware Evacuation Pipeline
Source Location
      │
      ▼
Current Flood Probability
      │
      ▼
Flood Hazard Map
      │
      ▼
Road Flood Exposure
      │
      ▼
OpenStreetMap Road Graph
      │
      ▼
Risk-Aware Edge Cost
      │
      ▼
A* Search
      │
      ▼
Candidate Evacuation Routes
      │
      ▼
Shelter Evaluation
      │
      ▼
Recommended Evacuation Route
🔄 Dynamic Emergency Coordination

The system is designed as an integrated decision-support workflow rather than an isolated flood-prediction model.

Prediction
    ↓
Risk Assessment
    ↓
Spatial Risk
    ↓
Route Planning
    ↓
Shelter Evaluation
    ↓
Alert
    ↓
Flood Probability Update
    ↓
Route Recalculation

This allows the prediction component to provide the risk information required by the downstream evacuation components.

🔐 Data and Repository Notes

The following are intentionally excluded from GitHub:

venv/
.venv/
__pycache__/
.env
node_modules/
build/
dist/
cache/
results/
data/SEN12FLOOD/
data/flood/chennai_flood_hazard.kml

The Python virtual environment is excluded because dependencies can be recreated using requirements.txt.

The SEN12FLOOD dataset and large flood-hazard KML are excluded because of their storage requirements.

🚀 Future Enhancements

Potential future improvements include:

Integration of verified official relief-centre data
Real-time shelter operational-status integration
Live shelter capacity/occupancy information where available
Satellite-based flood segmentation
Real-time rainfall monitoring
Live flood-risk maps
Dynamic road-closure detection
Traffic-aware evacuation routing
Multi-destination evacuation planning
Mobile application integration
Real-time emergency notifications
Improved model calibration
Risk-penalty parameter optimization
Larger-scale routing evaluation
Integration with additional disaster-management data sources
🎓 Academic Project

IDIECS is developed as an academic capstone project focused on combining:

Artificial Intelligence
        +
Machine Learning
        +
Real-Time Weather
        +
Geospatial Flood Data
        +
OpenStreetMap
        +
Graph-Based Routing
        +
Emergency Coordination
        ↓
Integrated Flood Evacuation Decision Support

The project demonstrates how a flood-probability prediction model can be connected with spatial risk analysis and evacuation routing to create an integrated disaster-response prototype.

📄 License

This project is developed for academic and educational purposes.


