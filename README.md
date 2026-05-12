# 🎓 JIIT Timetable Scheduler using Genetic Algorithm

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Algorithm](https://img.shields.io/badge/Algorithm-Genetic%20Algorithm-green?style=flat)
![Output](https://img.shields.io/badge/Output-Interactive%20HTML-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

> An AI-powered automatic timetable generation system for the AI & Data Science department at **Jaypee Institute of Information Technology (JIIT), Noida** — built using Genetic Algorithm.

---

## 📌 About the Project

University timetable scheduling is a complex combinatorial optimization problem. Assigning teachers, subjects, classrooms, and time slots while satisfying multiple hard constraints makes the search space astronomically large — making manual or exhaustive methods practically infeasible.

This system uses a **Genetic Algorithm (GA)** to automatically generate a **conflict-free timetable**, eliminating manual scheduling effort entirely.

---

## ⚙️ How It Works

- Takes **4 structured CSV files** as input: `subjects`, `teachers`, `rooms`, and `sections` (loaded via Pandas)
- Each complete timetable is represented as a **chromosome**
- Each class assignment (subject + teacher + room + day + time slot + section) is a **gene**
- The GA evolves a population of timetable solutions over generations until a conflict-free schedule is found

---

## ✅ Key Features

- **Hard Constraint Enforcement:**
  - No teacher double-booking
  - No room clashes
  - No section overlaps
  - Only qualified teachers assigned to their subjects

- **GA Techniques Used:**
  - Tournament Selection (k=5)
  - Single-point Crossover
  - Adaptive Mutation
  - Four-pass Repair Operator
  - Elitism

- **4 Automated Visualizations:**
  - Fitness evolution over generations
  - Conflict reduction with adaptive mutation
  - Room utilization
  - Teacher workload distribution

- **Output:** Fully interactive **standalone HTML timetable file**

---

## 📊 Dataset

| Entity    | Count |
|-----------|-------|
| Subjects  | 12    |
| Teachers  | 12    |
| Rooms     | 9     |
| Sections  | 3 (AIDS-A Sem2, AIDS-B Sem2, AIDS-A Sem4) |
| Genes/Chromosome | 102 |

Dataset is based on the actual **JIIT AI&DS curriculum**.

---

## 📈 Results

| Parameter         | Value          |
|-------------------|----------------|
| Population Size   | 100            |
| Max Generations   | 300            |
| Crossover Rate    | 0.85           |
| Mutation Rate     | 0.15 (adaptive)|
| Initial Conflicts | ~43            |
| Final Conflicts   | **0**          |
| Convergence       | **14 generations** |
| Final Fitness     | **1.0 (perfect)** |

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Libraries:** Pandas, NumPy, Matplotlib
- **Algorithm:** Genetic Algorithm
- **Output Format:** Standalone HTML

---

## 📁 Project Structure

```
├── data/
│   ├── subjects.csv
│   ├── teachers.csv
│   ├── rooms.csv
│   └── sections.csv
├── src/
│   ├── genetic_algorithm.py
│   ├── fitness.py
│   ├── crossover.py
│   ├── mutation.py
│   └── repair.py
├── output/
│   └── timetable.html
├── SC_Project_Report.docx
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/JIIT-Timetable-Scheduler.git
   cd JIIT-Timetable-Scheduler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the scheduler**
   ```bash
   python src/genetic_algorithm.py
   ```

4. **View the output**
   - Open `output/timetable.html` in any browser

---

## 👨‍💻 Team Members

| Name | Roll Number | Program |
|------|-------------|---------|
| Rahul Kushwaha | 2503310020 | M.Tech AI & DS |
| Kartikay Gautam | 2503310028 | M.Tech AI & DS |
| Ritik Dadwal | 2503310018 | M.Tech AI & DS |
| Abhay Gaur | 2503310009 | M.Tech AI & DS |

---

## 👩‍🏫 Supervisors

- **Sayani Ghosal** — Assistant Professor (Senior Grade), Dept. of CSE & IT, JIIT Noida
- **Kavita Pandey** — Assistant Professor (Senior Grade), Dept. of CSE & IT, JIIT Noida

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🏫 Institution

**Jaypee Institute of Information Technology (JIIT), Noida**
Department of Computer Science & Engineering and Information Technology
*Major Project — M.Tech in Artificial Intelligence and Data Science (2026)*
