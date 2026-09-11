# IDIECS – Flood Prediction and Evacuation Routing System

**Integrated Disaster Intelligence and Emergency Coordination System (IDIECS)**

An AI-powered flood risk prediction and evacuation routing system that combines historical weather and flood-event data with real-time weather information to estimate flood risk and identify suitable evacuation routes.

---

## 📌 Project Overview

Floods are one of the most frequent natural disasters and can cause severe damage to life, infrastructure, and transportation networks. Early identification of flood risk and efficient evacuation planning can help reduce the impact of such disasters.

**IDIECS** is designed to provide:

* 🌧️ Flood risk prediction using machine learning
* 📊 Analysis of historical rainfall and weather data
* 🌐 Real-time weather data retrieval through an API
* 🗺️ Road-network-based evacuation routing
* 🚨 Flood probability and risk-level classification
* 🚗 Shortest evacuation route calculation using Dijkstra's algorithm

The system combines **Machine Learning + Real-Time Weather Data + OpenStreetMap Road Networks** to support disaster-response decision making.

---

## 🎯 Objectives

1. Predict the probability of a flood occurrence using historical weather and flood-event data.
2. Classify locations into different flood-risk levels.
3. Integrate real-time weather information into the prediction workflow.
4. Represent road networks using OpenStreetMap data.
5. Identify an efficient evacuation route using Dijkstra's shortest-path algorithm.
6. Provide a practical prototype for real-time flood-risk monitoring and evacuation support.

---

## 🏗️ System Architecture

```text
                HISTORICAL DATA
                     │
        ┌────────────┴────────────┐
        │                         │
 Historical Weather          Flood Events
        │                         │
        └────────────┬────────────┘
                     ↓
              Data Preprocessing
                     ↓
              Feature Engineering
                     ↓
               XGBoost Model
                     ↓
              flood_model.pkl
                     │
                     │
                     ↓
              FLOOD PREDICTION
                     ↑
                     │
              Real-Time Weather
                     │
              Weather API
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     Rainfall     Humidity    Temperature
        │            │            │
        └────────────┼────────────┘
                     ↓
              Flood Probability
                     ↓
                 Risk Level
          ┌──────────┼──────────┐
          ↓          ↓          ↓
         LOW       MEDIUM      HIGH
                                │
                                ↓
                     OpenStreetMap
                      Road Network
                                ↓
                         Dijkstra Algorithm
                                ↓
                     Evacuation Route
```

---

## 🔬 Methodology

### 1. Data Collection

The project uses historical weather, rainfall, and flood-event information for model development.

The project contains datasets such as:

* Historical weather data
* Rainfall data
* Flood-event data
* State/city weather data
* Training datasets
* Prototype datasets

Satellite imagery from **SEN12FLOOD** is also used as part of the project data resources.

> **Note:** The SEN12FLOOD satellite dataset is not included in this GitHub repository because its local dataset size is approximately 17+ GB. It can be stored separately and referenced when required.

---

### 2. Data Preprocessing

The collected datasets are processed to make them suitable for machine-learning training.

Major preprocessing operations include:

* Handling missing values
* Removing invalid records
* Date-based data processing
* Combining weather and flood-event information
* Generating rainfall-related features
* Preparing the target flood label
* Creating training and testing datasets

---

### 3. Feature Engineering

Rainfall-related temporal features are generated from the weather data.

Important features include:

* `rainfall_1day`
* `rainfall_3day`
* `rainfall_7day`

These features represent rainfall accumulated over different time periods and help the model identify rainfall patterns associated with flood events.

Other weather-related features include:

* Temperature
* Humidity
* Atmospheric pressure
* Wind speed

---

## 🤖 Machine Learning Model

The project uses **XGBoost (Extreme Gradient Boosting)** for flood prediction.

The model is trained using historical weather and flood-event information.

### Input

The model can use weather-related features such as:

```text
Rainfall
Rainfall over recent days
Temperature
Humidity
Pressure
Wind Speed
```

### Output

The model produces a **flood probability**, which is then converted into a flood-risk category.

```text
Weather Features
       ↓
    XGBoost
       ↓
Flood Probability
       ↓
Risk Classification
       ↓
LOW / MEDIUM / HIGH
```

The trained model is stored as:

```text
ml/flood_model.pkl
```

---

## 🚨 Flood Risk Classification

The predicted probability is interpreted to determine the flood-risk level.

```text
Flood Probability
        │
        ├── Low probability   → LOW RISK
        │
        ├── Moderate probability → MEDIUM RISK
        │
        └── High probability  → HIGH RISK
```

The exact thresholds used by the implementation are defined in the prediction module.

---

## 🌐 Real-Time Weather Integration

The system can retrieve current weather information using a weather API.

The real-time weather module obtains information such as:

* Temperature
* Relative humidity
* Atmospheric pressure
* Wind speed
* Rainfall/weather information

The real-time values can then be passed through the trained flood prediction pipeline.

Relevant implementation:

```text
backend/weather_api.py
ml/test_weather_api.py
```

---

## 🗺️ Evacuation Routing

After identifying flood risk, the system uses a road network for evacuation planning.

The road network is obtained from **OpenStreetMap**.

The routing process is:

```text
Source Location
      ↓
Road Network
      ↓
Flood-Risk Information
      ↓
Identify Suitable/Accessible Roads
      ↓
Dijkstra Algorithm
      ↓
Shortest Evacuation Route
      ↓
Safe Destination
```

The routing implementation is available in:

```text
backend/routing.py
```

---

## 🧪 Testing Modules

The project contains separate modules for testing different components.

Examples include:

```text
ml/test_prediction.py
ml/test_probability.py
ml/test_weather_api.py
```

These modules are used to verify:

* Flood prediction
* Probability generation
* Weather API connectivity
* Model behaviour

---

## 📂 Project Structure

```text
CAPSTONE/
│
├── backend/
│   ├── main.py
│   ├── prediction.py
│   ├── routing.py
│   └── weather_api.py
│
├── data/
│   ├── flood/
│   │   └── emdat.csv
│   │
│   ├── weather/
│   │   ├── cities.csv
│   │   ├── clean_weather.csv
│   │   ├── historical_weather.csv
│   │   ├── state_weather.csv
│   │   └── weather.csv
│   │
│   ├── balanced_training_data.csv
│   ├── flood_events.csv
│   ├── flood_events_clean.csv
│   ├── prototype_training_data.csv
│   └── training_data.csv
│
├── ml/
│   ├── balance_dataset.py
│   ├── download_state_weather.py
│   ├── download_weather.py
│   ├── flood_model.pkl
│   ├── inspect_weather.py
│   ├── map_cities.py
│   ├── merge_data.py
│   ├── predict_flood.py
│   ├── preprocess.py
│   ├── process_flood.py
│   ├── test_prediction.py
│   ├── test_probability.py
│   ├── test_weather_api.py
│   └── train_model.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🛠️ Technologies Used

### Programming

* Python
* JavaScript *(if used by the frontend)*

### Machine Learning

* XGBoost
* Scikit-learn
* Pandas
* NumPy
* Joblib

### Data Processing

* Pandas
* NumPy

### Weather

* Weather API
* Historical weather datasets

### Mapping & Routing

* OpenStreetMap
* Dijkstra's shortest-path algorithm

### Development

* Visual Studio Code
* Git
* GitHub

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/HEMAPRIYAKV/CAPSTONE.git
cd CAPSTONE
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Windows

```powershell
venv\Scripts\activate
```

#### Linux/macOS

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

### Run the backend

From the project root:

```bash
python backend/main.py
```

If the backend is implemented using FastAPI/UvicORN, the corresponding server command can be used according to the implementation.

---

## 🧪 Testing

### Test weather API

```bash
python ml/test_weather_api.py
```

### Test flood prediction

```bash
python ml/test_prediction.py
```

### Test flood probability

```bash
python ml/test_probability.py
```

---

## 📊 Dataset Information

The repository contains processed datasets required for the machine-learning pipeline.

Important datasets include:

| Dataset                       | Purpose                          |
| ----------------------------- | -------------------------------- |
| `weather.csv`                 | Weather/rainfall information     |
| `clean_weather.csv`           | Cleaned weather data             |
| `historical_weather.csv`      | Historical weather information   |
| `state_weather.csv`           | State-level weather information  |
| `cities.csv`                  | City information                 |
| `flood_events.csv`            | Flood-event records              |
| `flood_events_clean.csv`      | Processed flood-event data       |
| `training_data.csv`           | Model training dataset           |
| `balanced_training_data.csv`  | Balanced training dataset        |
| `prototype_training_data.csv` | Prototype training dataset       |
| `emdat.csv`                   | Flood/disaster event information |

### SEN12FLOOD

The SEN12FLOOD satellite imagery dataset is maintained separately because of its large size.

```text
SEN12FLOOD
≈ 17+ GB
```

It is therefore excluded from the GitHub repository through `.gitignore`.

---

## 📈 Machine Learning Pipeline

```text
Historical Weather Data
          +
Flood Event Data
          ↓
Data Cleaning
          ↓
Feature Engineering
          ↓
Training Dataset
          ↓
XGBoost Training
          ↓
Model Evaluation
          ↓
flood_model.pkl
          ↓
Real-Time Weather Input
          ↓
Flood Probability
          ↓
Risk Level
```

---

## 🚗 Evacuation Pipeline

```text
User/Source Location
        ↓
Current Flood Risk
        ↓
OpenStreetMap Road Network
        ↓
Road Graph
        ↓
Dijkstra Shortest Path
        ↓
Evacuation Route
        ↓
Safe Destination
```

---

## 🔐 Data and Repository Notes

The following are intentionally excluded from GitHub:

```text
venv/
data/SEN12FLOOD/
__pycache__/
.env
node_modules/
build/
dist/
```

The Python virtual environment is excluded because dependencies can be recreated using `requirements.txt`.

The SEN12FLOOD dataset is excluded because of its large storage requirement.

---

## 🚀 Future Enhancements

Potential future improvements include:

* Integration of satellite-based flood segmentation
* More extensive real-time rainfall monitoring
* Live flood-risk maps
* Dynamic road closure detection
* Traffic-aware evacuation routing
* Multiple evacuation destinations
* Mobile application integration
* Real-time emergency alerts
* Improved model performance using additional flood-related features
* Integration with additional disaster-management data sources

---

## 🎓 Academic Project

This project was developed as a **capstone project** focused on applying Artificial Intelligence, Machine Learning, weather data, geospatial information, and graph-based routing to flood disaster management.

### Core Technologies

```text
Machine Learning
        +
Real-Time Weather
        +
Geospatial Data
        +
OpenStreetMap
        +
Shortest-Path Routing
        ↓
Flood Risk Prediction & Evacuation Support
```

---

## 📄 License

This project is developed for academic and educational purposes.
