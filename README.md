# Shortest Path Algorithm Analysis

An interactive tool built with **Python + Streamlit** to analyze and compare shortest path algorithms for Sri Lankan cities.  
It allows you to explore graph paths, test algorithms, and visualize results in real time.

---

## 📌 Features

- **Graph Input**

  - Load cities & roads from CSV files.
  - Choose **Directed** or **Undirected** graphs.
  - Switch weight mode: **Distance (km)** or **Travel Time (min)**.

- **Algorithms Implemented**

  - **Dijkstra’s Algorithm**
  - **Bellman–Ford Algorithm**
  - **A\* Algorithm** (with heuristics support).

- **Visualization**

  - Interactive map plotting of paths.
  - Dropdown menus for **Start** and **End** cities.
  - Display all possible paths in a popup.

- **Analysis & Results**
  - Computation time.
  - Passes / iterations.
  - Relaxations performed.
  - Edges scanned.
  - Route summary (distance, travel time, city count, stops list).

---

## 📂 Project Structure

```bash
.
├── algorithms/            # Algorithm implementations
│   ├── a_star.py
│   ├── bellman_ford.py
│   └── dijkstras.py
│
├── core/                  # Core graph utilities
│   ├── graph.py
│   ├── heuristics.py
│   └── vizualize.py
│
├── data/                  # Input datasets
│   ├── cities.csv
│   ├── edges.csv
│   └── diff_paths_directed_vs_undirected.csv
│
├── service/               # Service layer
│   └── run_all.py
│
├── app.py                 # Streamlit entry point
├── requirements.txt       # Dependencies
└── README.md
```

---

## ⚡ Installation

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd SHORTEST-PATH-ANALYSIS-CITIES-SL
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv .venv

   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

---

## 📊 Input & Output

**Input**

- CSV files from the `data/` folder.
- User selections (source, target, directed/undirected, distance/time).

**Output**

- Shortest path visualization on a map.
- Algorithm statistics (iterations, relaxations, edges scanned).
- Route summary details.

---

## 🖥️ User Guide

1. Run the Streamlit app (`streamlit run app.py`).
2. Open the UI in your browser.
3. Select:
   - Start city
   - End city
   - Weight mode (distance or time)
   - Graph type (directed/undirected)
4. View results in:
   - **Map visualization**
   - **Algorithm analysis panel**
   - **Route details panel**

---

## 🔧 Technology Stack

- **Language:** Python 3.10+
- **Framework:** Streamlit
- **Algorithms:** Dijkstra, Bellman–Ford, A\*
- **Data Format:** CSV

---

## 🚀 Future Enhancements

- Add Floyd–Warshall algorithm.
- Support JSON graph import/export.
- Integration with **OpenStreetMap** datasets.
- Multi-criteria optimization (distance + time).
- Export results as PDF/Excel.

---

## 👨‍💻 Author

**Menura Andrahennedi**  
B.Comp Hons in Computer Science
University of Sri Jayewardenepura

**Suneth Chathuranga**  
B.Comp Hons in Computer Science
University of Sri Jayewardenepura

**Chamodi Thennakoon**  
B.Comp Hons in Computer Science
University of Sri Jayewardenepura
