# JIIT Timetable Scheduler using Genetic Algorithm

## About the Project

University timetable scheduling is a complex optimization problem. Manually assigning teachers, subjects, classrooms, and time slots while satisfying multiple constraints is time-consuming and often leads to conflicts. This project automates the process using a Genetic Algorithm (GA) to generate a conflict-free timetable for the AI and Data Science department at Jaypee Institute of Information Technology, Noida.

## How It Works

The system takes four CSV files as input — subjects, teachers, rooms, and sections — loaded using the Pandas library. Each complete timetable is treated as a chromosome and each class assignment (subject, teacher, room, day, time slot, section) is a gene. The GA evolves a population of timetable solutions over multiple generations until it finds a schedule with zero conflicts.

## Features

- No teacher is assigned to two classes at the same time
- No room is double-booked
- No section has overlapping classes
- Only qualified teachers are assigned to their respective subjects
- Uses tournament selection, single-point crossover, adaptive mutation, four-pass repair operator, and elitism
- Generates 4 visualizations: fitness evolution, conflict reduction, room utilization, and teacher workload
- Final timetable is exported as a standalone interactive HTML file

## Dataset

The dataset is based on the actual JIIT AI and DS curriculum and includes 12 subjects, 12 teachers, 9 rooms, and 3 sections (AIDS-A Sem2, AIDS-B Sem2, AIDS-A Sem4). Each chromosome contains 102 genes.

## GA Parameters and Results

Population size: 100  
Maximum generations: 300  
Crossover rate: 0.85  
Mutation rate: 0.15 (adaptive)  
Initial conflicts: approximately 43  
Final conflicts: 0  
Convergence: within 14 generations  
Final fitness score: 1.0

## Tech Stack

Python 3, Pandas, NumPy, Matplotlib, Genetic Algorithm, HTML output

## Project Structure

```
data/
    subjects.csv
    teachers.csv
    rooms.csv
    sections.csv
src/
    genetic_algorithm.py
    fitness.py
    crossover.py
    mutation.py
    repair.py
output/
    timetable.html
SC_Project_Report.docx
requirements.txt
README.md
```

## How to Run

Clone the repository and navigate into the project folder. Install the required dependencies using pip install -r requirements.txt. Then run the main script using python src/genetic_algorithm.py. Once done, open the output/timetable.html file in any browser to view the generated timetable.

## Team Members

Rahul Kushwaha — Roll No. 2503310020  
Kartikay Gautam — Roll No. 2503310028  
Ritik Dadwal — Roll No. 2503310018  
Abhay Gaur — Roll No. 2503310009  

Program: M.Tech in Artificial Intelligence and Data Science, JIIT Noida

## Supervisors

Sayani Ghosal, Assistant Professor (Senior Grade), Dept. of CSE and IT, JIIT Noida  
Kavita Pandey, Assistant Professor (Senior Grade), Dept. of CSE and IT, JIIT Noida

## License

This project is licensed under the MIT License.

## Institution

Jaypee Institute of Information Technology, Noida  
Department of Computer Science and Engineering and Information Technology  
Major Project, M.Tech in Artificial Intelligence and Data Science, 2026
