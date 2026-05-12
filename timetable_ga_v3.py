import random
import copy
import os
import sys
import argparse
from datetime import datetime

import pandas as pd               
import matplotlib
matplotlib.use("Agg")               
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns                

# GLOBAL TIME CONSTANTS
DAYS  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SLOTS = [
    "9:00-10:00", "10:00-11:00", "11:00-12:00",
    "12:00-1:00",  "2:00-3:00",  "3:00-4:00",  "4:00-5:00"
]
TOTAL_SLOTS = len(DAYS) * len(SLOTS)  

# SECTION 1 — PANDAS CSV LOADERS

def load_subjects(path: str) -> list:
    
    df = pd.read_csv(path, dtype=str)
    df.columns = df.columns.str.strip().str.lower()
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    subjects = []
    for _, row in df.iterrows():
        subjects.append({
            "id":      row["subject_id"],
            "name":    row["subject_name"],
            "credits": int(row.get("credits", 3)),
            "dept":    row["department"],
            "hours":   int(row["weekly_hours"]) if "weekly_hours" in row else 3,
        })
    # print(f"  [pandas] Loaded {len(subjects)} subjects  ← {path}")
    return subjects


def load_teachers(path: str) -> list:
    df = pd.read_csv(path, dtype=str)
    df.columns = df.columns.str.strip().str.lower()
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    teachers = []
    for _, row in df.iterrows():
        # Parse comma-separated subject list, strip quotes added by Excel
        raw_subj  = row["subjects"].replace('"', "").replace("'", "")
        subj_list = [s.strip() for s in raw_subj.split(",") if s.strip()]
        teachers.append({
            "id":       row["teacher_id"],
            "name":     row["teacher_name"],
            "subjects": subj_list,
            "dept":     row["department"],
            "max_hrs":  int(row["max_hours_per_week"]) if "max_hours_per_week" in row else 20,
        })
    # print(f"  [pandas] Loaded {len(teachers)} teachers  ← {path}")
    return teachers


def load_rooms(path: str) -> list:
    df = pd.read_csv(path, dtype=str)
    df.columns = df.columns.str.strip().str.lower()
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    rooms = []
    for _, row in df.iterrows():
        rooms.append({
            "id":       row["room_id"],
            "name":     row["room_name"],
            "capacity": int(row["capacity"]),
            "type":     row["room_type"],
            "building": row.get("building", "Main"),
        })
    return rooms


def load_sections(path: str) -> list:
    df = pd.read_csv(path, dtype=str)
    df.columns = df.columns.str.strip().str.lower()
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    sections = []
    for _, row in df.iterrows():
        sections.append({
            "id":       row["section_id"],
            "name":     row["section_name"],
            "semester": int(row["semester"]),
            "dept":     row["department"],
            "strength": int(row["strength"]) if "strength" in row else 40,
        })
    # print(f"  [pandas] Loaded {len(sections)} sections   ← {path}")
    return sections


def save_teachers(teachers: list, path: str):
    rows = [{"teacher_id": t["id"], "teacher_name": t["name"],
             "subjects": ",".join(t["subjects"]),
             "department": t["dept"],
             "max_hours_per_week": t["max_hrs"]} for t in teachers]
    pd.DataFrame(rows).to_csv(path, index=False)
    # print(f"  [pandas] Saved {len(teachers)} teachers → {path}")


def save_rooms(rooms: list, path: str):
    rows = [{"room_id": r["id"], "room_name": r["name"],
             "capacity": r["capacity"], "room_type": r["type"],
             "building": r["building"]} for r in rooms]
    pd.DataFrame(rows).to_csv(path, index=False)
    # print(f"  [pandas] Saved {len(rooms)} rooms → {path}")


def find_csv(hint_path: str, filenames: list, label: str):
    if hint_path:
        if os.path.isfile(hint_path):
            return hint_path
        print(f"  ✗ {label}: '{hint_path}' not found")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    for name in filenames:
        for base in [script_dir, os.path.join(script_dir, "dataset"),
                     os.path.join(script_dir, "data")]:
            p = os.path.join(base, name)
            if os.path.isfile(p):
                return p
    return None

# SECTION 3 — INTERACTIVE ADD TEACHER / ROOM
def add_teacher_interactive(teachers: list, subjects: list) -> list:
    print("\n" + "─"*52)
    print("  ADD NEW TEACHER")
    print("─"*52)
    print("  Available subject IDs:")
    for s in subjects:
        print(f"    {s['id']:<10} {s['name']}")

    tid   = input("\n  Teacher ID   (e.g. T11)          : ").strip()
    name  = input("  Full name    (e.g. Dr. Meera Nair): ").strip()
    subjs = input("  Subject IDs  (comma-separated)    : ").strip()
    dept  = input("  Department   (e.g. CS)            : ").strip()
    hrs   = input("  Max hrs/week (press Enter for 20) : ").strip()

    subj_list = [s.strip() for s in subjs.split(",") if s.strip()]
    valid_ids  = {s["id"] for s in subjects}
    bad = [s for s in subj_list if s not in valid_ids]
    if bad:
        print(f" Unknown subject IDs: {bad}")
        if input("  Continue anyway (y/n): ").strip().lower() != "y":
            return teachers

    teachers.append({
        "id": tid, "name": name, "subjects": subj_list,
        "dept": dept, "max_hrs": int(hrs) if hrs.isdigit() else 20
    })
    print(f" Teacher '{name}' added!")
    return teachers


def add_room_interactive(rooms: list) -> list:
    print("\n" + "─"*52)
    print("  ADD NEW ROOM")
    print("─"*52)

    rid      = input("  Room ID      (e.g. R105)       : ").strip()
    name     = input("  Room name    (e.g. Room 105)   : ").strip()
    cap      = input("  Capacity     (number of seats) : ").strip()
    rtype    = input("  Type         (Lecture/Lab/Seminar): ").strip()
    building = input("  Building     (e.g. Block A)    : ").strip()

    rooms.append({
        "id": rid, "name": name,
        "capacity": int(cap) if cap.isdigit() else 40,
        "type": rtype, "building": building or "Main"
    })
    print(f"Room '{name}' added!")
    return rooms

# SECTION 4 — GENETIC ALGORITHM

class Gene:
    __slots__ = ["subject", "teacher", "room", "day", "slot", "section"]

    def __init__(self, subject, teacher, room, day, slot, section):
        self.subject = subject
        self.teacher = teacher
        self.room    = room
        self.day     = day
        self.slot    = slot
        self.section = section

class Chromosome:
    def __init__(self, genes=None):
        self.genes   = genes if genes is not None else []
        self.fitness = 0.0

    # FITNESS FUNCTION 
    def calculate_fitness(self):

        teacher_slots  = {}   
        room_slots     = {}   
        section_slots  = {}   
        wrong_teacher  = 0

        for g in self.genes:
            tk = (g.teacher["id"], g.day, g.slot)
            rk = (g.room["id"],    g.day, g.slot)
            sk = (g.section["id"], g.day, g.slot)

            teacher_slots[tk]  = teacher_slots.get(tk, 0)  + 1
            room_slots[rk]     = room_slots.get(rk, 0)     + 1
            section_slots[sk]  = section_slots.get(sk, 0)  + 1

            if g.subject["id"] not in g.teacher["subjects"]:
                wrong_teacher += 1

        teacher_clashes = sum(v - 1 for v in teacher_slots.values()  if v > 1)
        room_clashes    = sum(v - 1 for v in room_slots.values()     if v > 1)
        section_clashes = sum(v - 1 for v in section_slots.values()  if v > 1)

        total = teacher_clashes + room_clashes + section_clashes + wrong_teacher
        self.fitness = 1.0 / (1.0 + total)
        return self.fitness

# SMART GENE CREATION
def build_gene_list_for_section(section, subjects, teachers, rooms):
    genes = []
    all_slots = [(d, s) for d in DAYS for s in SLOTS]
    used_section_slots = set() 

    for subj in subjects:
        hours = subj.get("hours", 3)   
        valid_teachers = [t for t in teachers if subj["id"] in t["subjects"]]
        if not valid_teachers:
            valid_teachers = teachers   

        for _ in range(hours):
            free = [sl for sl in all_slots if sl not in used_section_slots]
            if not free:
                free = all_slots 
            day, slot = random.choice(free)
            used_section_slots.add((day, slot))

            teacher = random.choice(valid_teachers)
            room    = random.choice(rooms)
            genes.append(Gene(subj, teacher, room, day, slot, section))

    return genes

# build initialize_population
def initialize_population(pop_size, sections, subjects, teachers, rooms,
                           classes_per_section=None):
    population = []
    for _ in range(pop_size):
        genes = []
        for section in sections:
            for subj in subjects:
                hours = subj.get("hours", 3)
                valid_teachers = [t for t in teachers if subj["id"] in t["subjects"]]
                if not valid_teachers:
                    valid_teachers = teachers
                for _ in range(hours):
                    teacher = random.choice(valid_teachers)
                    room    = random.choice(rooms)
                    day     = random.choice(DAYS)
                    slot    = random.choice(SLOTS)
                    genes.append(Gene(subj, teacher, room, day, slot, section))
        c = Chromosome(genes)
        c.calculate_fitness()
        population.append(c)
    return population


#SELECTION

def tournament_select(population, k=5):
    contestants = random.sample(population, min(k, len(population)))
    return max(contestants, key=lambda c: c.fitness)


#CROSSOVER

def crossover(p1, p2, rate=0.85):
    if random.random() > rate:
        return copy.deepcopy(p1), copy.deepcopy(p2)

    pt = random.randint(1, len(p1.genes) - 1)
    # Deep copy to avoid shared references
    g1 = copy.deepcopy(p1.genes[:pt]) + copy.deepcopy(p2.genes[pt:])
    g2 = copy.deepcopy(p2.genes[:pt]) + copy.deepcopy(p1.genes[pt:])
    return Chromosome(g1), Chromosome(g2)


# MUTATION 

def mutate(chrom, rate, subjects, teachers, rooms):

    for gene in chrom.genes:
        if random.random() >= rate:
            continue

        op = random.choices(
            ["room", "day", "slot", "teacher", "subject"],
            weights=[1, 2, 2, 2, 1], k=1
        )[0]

        if op == "room":
            gene.room = random.choice(rooms)

        elif op == "day":
            gene.day = random.choice(DAYS)

        elif op == "slot":
            gene.slot = random.choice(SLOTS)

        elif op == "teacher":
            valid = [t for t in teachers if gene.subject["id"] in t["subjects"]]
            if valid:
                gene.teacher = random.choice(valid)

        elif op == "subject":
            gene.subject = random.choice(subjects)
            valid = [t for t in teachers if gene.subject["id"] in t["subjects"]]
            if valid:
                gene.teacher = random.choice(valid)

    return chrom


# REPAIR OPERATOR

def repair(chrom, subjects, teachers, rooms):
    
    genes = chrom.genes
    all_slots = [(d, s) for d in DAYS for s in SLOTS]

    for gene in genes:
        if gene.subject["id"] not in gene.teacher["subjects"]:
            valid = [t for t in teachers if gene.subject["id"] in t["subjects"]]
            if valid:
                gene.teacher = random.choice(valid)

    for _ in range(25):
        fixed = False
        seen = {}
        for idx, g in enumerate(genes):
            key = (g.section["id"], g.day, g.slot)
            if key in seen:
                used = {(genes[k].day, genes[k].slot)
                        for k in range(len(genes))
                        if genes[k].section["id"] == g.section["id"] and k != idx}
                free = [sl for sl in all_slots if sl not in used]
                if free:
                    g.day, g.slot = random.choice(free)
                    fixed = True
            else:
                seen[key] = idx
        if not fixed:
            break

    for _ in range(25):
        fixed = False
        seen = {}
        for idx, g in enumerate(genes):
            key = (g.teacher["id"], g.day, g.slot)
            if key in seen:
                # Move this gene to a slot where this teacher is free
                used_t = {(genes[k].day, genes[k].slot)
                          for k in range(len(genes))
                          if genes[k].teacher["id"] == g.teacher["id"] and k != idx}
                # Also must be free for this section
                used_s = {(genes[k].day, genes[k].slot)
                          for k in range(len(genes))
                          if genes[k].section["id"] == g.section["id"] and k != idx}
                free = [sl for sl in all_slots if sl not in used_t and sl not in used_s]
                if free:
                    g.day, g.slot = random.choice(free)
                    fixed = True
            else:
                seen[key] = idx
        if not fixed:
            break

    for _ in range(25):
        fixed = False
        seen = {}
        for idx, g in enumerate(genes):
            key = (g.room["id"], g.day, g.slot)
            if key in seen:
                # Try a different room first
                other_rooms = [r for r in rooms if r["id"] != g.room["id"]]
                if other_rooms:
                    g.room = random.choice(other_rooms)
                    fixed = True
            else:
                seen[key] = idx
        if not fixed:
            break

    return chrom


# MAIN GA LOOP

def genetic_algorithm(sections, subjects, teachers, rooms,
                       pop_size=80, generations=300,
                       mutation_rate=0.15, crossover_rate=0.85,
                       elite_count=3):
    
    # GENETIC ALGORITHM — main loop.
    total_genes = sum(sum(s.get("hours", 3) for s in subjects) for _ in sections)
    print("  RUNNING GENETIC ALGORITHM")
    print(f"  Pop size    : {pop_size}   Generations : {generations}")
    print(f"  Mutation    : {mutation_rate}    Crossover   : {crossover_rate}")
    print(f"  Sections    : {len(sections)}   Subjects    : {len(subjects)}")
    print(f"  Total genes : {total_genes} per chromosome   Elite: {elite_count}")

    # Step 1: Initialize 
    population = initialize_population(pop_size, sections, subjects,
                                       teachers, rooms)
    best_ever  = copy.deepcopy(max(population, key=lambda c: c.fitness))
    history    = []

    stagnant_gens  = 0     # how many gens without improvement
    current_mut    = mutation_rate

    for gen in range(generations):

        for c in population:
            c.calculate_fitness()

        population.sort(key=lambda c: c.fitness, reverse=True)
        best_gen = population[0]

        if best_gen.fitness > best_ever.fitness:
            best_ever     = copy.deepcopy(best_gen)
            stagnant_gens = 0
            current_mut   = mutation_rate  
        else:
            stagnant_gens += 1

        avg_fit = sum(c.fitness for c in population) / len(population)
        n_conflicts = round(1.0 / best_ever.fitness - 1.0)

        history.append({
            "gen":       gen + 1,
            "best":      round(best_ever.fitness, 5),
            "avg":       round(avg_fit, 5),
            "conflicts": n_conflicts,
            "mut_rate":  round(current_mut, 4),
        })

        if (gen + 1) % 25 == 0 or gen == 0:
            print(f"  Gen {gen+1:>4} | best={best_ever.fitness:.5f} "
                  f"| avg={avg_fit:.5f} | conflicts={n_conflicts} "
                  f"| mut={current_mut:.3f}")

        if best_ever.fitness >= 1.0:
            print(f"\n  ✓ Perfect fitness=1.0 achieved at generation {gen+1}!")
            break

        if stagnant_gens > 15:
            current_mut = min(0.5, current_mut * 1.15)

        if stagnant_gens > 35:
            print(f" Restarting at gen {gen+1} "
                  f"(stuck for {stagnant_gens} gens)")
            n_fresh   = int(pop_size * 0.6)
            n_keep    = pop_size - n_fresh
            new_pop   = population[:n_keep]
            fresh     = initialize_population(n_fresh, sections, subjects,
                                              teachers, rooms)
            new_pop  += fresh
            population = new_pop
            stagnant_gens = 0
            current_mut   = mutation_rate
            continue

        new_pop = [copy.deepcopy(population[i]) for i in range(elite_count)]

        while len(new_pop) < pop_size:
            p1 = tournament_select(population, k=5)
            p2 = tournament_select(population, k=5)

            c1, c2 = crossover(p1, p2, crossover_rate)

            c1 = repair(c1, subjects, teachers, rooms)
            c2 = repair(c2, subjects, teachers, rooms)

            c1 = mutate(c1, current_mut, subjects, teachers, rooms)
            c2 = mutate(c2, current_mut, subjects, teachers, rooms)

            c1.calculate_fitness()
            c2.calculate_fitness()

            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)

        population = new_pop

    # Final report
    final_conflicts = round(1.0 / best_ever.fitness - 1.0)
    print(f"\n{'='*62}")
    print(f"  FINAL RESULT")
    print(f"  Best Fitness  : {best_ever.fitness:.5f}")
    print(f"  Conflicts     : {final_conflicts}")
    print(f"  Status        : {' PERFECT — Zero conflicts!' if final_conflicts==0 else 'Near-optimal'}")
    print(f"{'='*62}")

    return best_ever, history


# SECTION 5 — 4 VISUALIZATIONS
def make_visualizations(best, history, out_dir="."):
    os.makedirs(out_dir, exist_ok=True)
    saved = []

    # Shared style
    sns.set_theme(style="whitegrid", font_scale=1.05)
    PALETTE = sns.color_palette("muted")

    # CHART 1: Fitness Evolution over Generations
    fig, ax = plt.subplots(figsize=(9, 4.5))

    gens  = [h["gen"]  for h in history]
    bests = [h["best"] for h in history]
    avgs  = [h["avg"]  for h in history]

    ax.plot(gens, bests, color="#1D4ED8", linewidth=2.2,
            label="Best Fitness", zorder=3)
    ax.fill_between(gens, bests, avgs, alpha=0.12, color="#1D4ED8")
    ax.plot(gens, avgs,  color="#059669", linewidth=1.5,
            linestyle="--", label="Avg Fitness", zorder=2)

    ax.annotate(f"Final: {bests[-1]:.4f}",
                xy=(gens[-1], bests[-1]),
                xytext=(-55, 10), textcoords="offset points",
                fontsize=9, color="#1D4ED8",
                arrowprops=dict(arrowstyle="->", color="#1D4ED8", lw=1))

    ax.axhline(1.0, color="#DC2626", linestyle=":", linewidth=1.2,
               label="Perfect fitness (1.0)", alpha=0.7)

    ax.set_xlabel("Generation", fontsize=11)
    ax.set_ylabel("Fitness Value", fontsize=11)
    ax.set_title("GA Fitness Evolution — Best & Average per Generation",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.08)
    ax.set_xlim(left=1)
    plt.tight_layout()
    p1 = os.path.join(out_dir, "chart1_fitness_evolution.png")
    plt.savefig(p1, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(p1)
    print(f"  [chart 1] Fitness Evolution  → {p1}")

    # CHART 2: Conflict Reduction over Generations
    fig, ax = plt.subplots(figsize=(9, 4.5))

    conflicts = [h["conflicts"] for h in history]
    mut_rates = [h["mut_rate"]  for h in history]

    color_c = "#DC2626"
    color_m = "#D97706"

    ax.bar(gens, conflicts, color=color_c, alpha=0.55, width=0.9,
           label="Conflicts remaining", zorder=2)
    ax.plot(gens, conflicts, color=color_c, linewidth=1.5, zorder=3)

    ax2 = ax.twinx()
    ax2.plot(gens, mut_rates, color=color_m, linewidth=1.5,
             linestyle="-.", label="Mutation rate", alpha=0.85)
    ax2.set_ylabel("Mutation Rate", fontsize=10, color=color_m)
    ax2.tick_params(axis="y", colors=color_m)
    ax2.set_ylim(0, max(mut_rates) * 1.4)

    ax.set_xlabel("Generation", fontsize=11)
    ax.set_ylabel("Number of Conflicts", fontsize=11, color=color_c)
    ax.tick_params(axis="y", colors=color_c)
    ax.set_title("Conflict Reduction & Adaptive Mutation Rate over Generations",
                 fontsize=12, fontweight="bold", pad=12)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper right")
    ax.set_xlim(left=1)
    plt.tight_layout()
    p2 = os.path.join(out_dir, "chart2_conflict_reduction.png")
    plt.savefig(p2, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(p2)
    print(f"  [chart 2] Conflict Reduction → {p2}")

    # CHART 3: Room Utilization (% of available slots used)
    room_usage = {}
    for g in best.genes:
        rn = g.room["name"]
        room_usage[rn] = room_usage.get(rn, 0) + 1

    rooms_sorted  = sorted(room_usage.keys(), key=lambda r: room_usage[r], reverse=True)
    usage_counts  = [room_usage[r] for r in rooms_sorted]
    pct_used      = [round(c / TOTAL_SLOTS * 100, 1) for c in usage_counts]

    colors_bar = ["#1D4ED8" if p >= 60 else "#059669" if p >= 30 else "#D97706"
                  for p in pct_used]

    fig, ax = plt.subplots(figsize=(9, max(3.5, len(rooms_sorted) * 0.55)))
    bars = ax.barh(rooms_sorted, pct_used, color=colors_bar, edgecolor="white",
                   linewidth=0.6, height=0.6)

    # Value labels
    for bar, val, cnt in zip(bars, pct_used, usage_counts):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"{val}%  ({cnt} classes)", va="center", fontsize=9)

    ax.set_xlabel("Utilization (%)", fontsize=11)
    ax.set_title("Room / Classroom Utilization",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xlim(0, 115)
    ax.axvline(50, color="gray", linestyle=":", linewidth=1, alpha=0.6)
    ax.text(50.5, -0.7, "50%", fontsize=8, color="gray")

    legend_patches = [
        mpatches.Patch(color="#1D4ED8", label="High (≥60%)"),
        mpatches.Patch(color="#059669", label="Medium (30–60%)"),
        mpatches.Patch(color="#D97706", label="Low (<30%)"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="lower right")
    plt.tight_layout()
    p3 = os.path.join(out_dir, "chart3_room_utilization.png")
    plt.savefig(p3, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(p3)
    print(f"  [chart 3] Room Utilization   → {p3}")

    # CHART 4: Teacher Workload Distribution
    teacher_load = {}
    teacher_depts = {}
    for g in best.genes:
        tn = g.teacher["name"]
        teacher_load[tn] = teacher_load.get(tn, 0) + 1
        teacher_depts[tn] = g.teacher["dept"]

    teachers_sorted = sorted(teacher_load.keys(),
                             key=lambda t: teacher_load[t], reverse=True)
    loads = [teacher_load[t] for t in teachers_sorted]

    dept_colors = {"CS": "#1D4ED8", "MATH": "#059669",
                   "ECE": "#D97706", "IT": "#7C3AED"}
    bar_colors = [dept_colors.get(teacher_depts[t], "#6B7280")
                  for t in teachers_sorted]

    fig, ax = plt.subplots(figsize=(9, max(4, len(teachers_sorted) * 0.55)))
    bars = ax.barh(teachers_sorted, loads, color=bar_colors,
                   edgecolor="white", linewidth=0.6, height=0.6)

    for bar, val in zip(bars, loads):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"{val}", va="center", fontsize=10, fontweight="500")

    # Average line
    avg_load = sum(loads) / len(loads) if loads else 0
    ax.axvline(avg_load, color="#DC2626", linestyle="--",
               linewidth=1.5, label=f"Avg = {avg_load:.1f}")

    ax.set_xlabel("Number of Classes Assigned", fontsize=11)
    ax.set_title("Teacher Workload Distribution",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xlim(0, max(loads) + 2 if loads else 10)

    legend_patches = [mpatches.Patch(color=v, label=k) for k, v in dept_colors.items()]
    legend_patches.append(
        mpatches.Patch(color="#DC2626", label=f"Avg load ({avg_load:.1f})")
    )
    ax.legend(handles=legend_patches, fontsize=8, loc="lower right")
    plt.tight_layout()
    p4 = os.path.join(out_dir, "chart4_teacher_workload.png")
    plt.savefig(p4, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(p4)
    print(f"  [chart 4] Teacher Workload   → {p4}")

    return saved


# SECTION 6 — HTML TIMETABLE OUTPUT

def generate_html(best, history, chart_paths, output_file="timetable_output.html"):
    """Generate a standalone HTML file with the timetable + embedded charts."""

    sections_list = sorted({g.section["name"] for g in best.genes})
    final_conflicts = round(1.0 / best.fitness - 1.0)
    total_classes   = len(best.genes)
    generated_at    = datetime.now().strftime("%B %d, %Y at %H:%M")

    COLORS = [
        ("#DBEAFE","#1E40AF"), ("#D1FAE5","#065F46"), ("#FEF3C7","#92400E"),
        ("#FCE7F3","#831843"), ("#EDE9FE","#4C1D95"), ("#CCFBF1","#134E4A"),
        ("#FEE2E2","#991B1B"), ("#FEF9C3","#713F12"), ("#F0FDF4","#14532D"),
        ("#F0F9FF","#075985"), ("#FFF7ED","#9A3412"), ("#F5F3FF","#5B21B6"),
    ]
    all_subj   = list({g.subject["id"]: g.subject["name"] for g in best.genes}.items())
    subj_color = {sid: COLORS[i % len(COLORS)] for i, (sid, _) in enumerate(all_subj)}

    def build_grid(sec_name):
        return {(g.day, g.slot): g
                for g in best.genes if g.section["name"] == sec_name}

    tab_btns = "\n".join(
        f'<button class="tab-btn {"active" if i==0 else ""}" onclick="showTab({i})">{sec}</button>'
        for i, sec in enumerate(sections_list)
    )

    panels = ""
    for si, sec_name in enumerate(sections_list):
        cells = build_grid(sec_name)

        grid = '<div class="grid-wrap"><table class="tt"><thead><tr>'
        grid += '<th class="dc">Day</th>'
        for s in SLOTS:
            grid += f"<th>{s}</th>"
        grid += "</tr></thead><tbody>"
        for day in DAYS:
            grid += f'<tr><td class="dl">{day}</td>'
            for slot in SLOTS:
                g = cells.get((day, slot))
                if g:
                    bg, fg = subj_color.get(g.subject["id"], ("#DBEAFE","#1E40AF"))
                    grid += (f'<td><div class="cc" style="background:{bg};border-left:3px solid {fg};">'
                             f'<div class="sc" style="color:{fg};">{g.subject["id"]}</div>'
                             f'<div class="sn">{g.subject["name"]}</div>'
                             f'<div class="sm">{g.teacher["name"]}</div>'
                             f'<div class="sm rt">{g.room["name"]}</div>'
                             f'</div></td>')
                else:
                    grid += '<td><div class="ec">—</div></td>'
            grid += "</tr>"
        grid += "</tbody></table></div>"

        sec_genes = sorted(
            [g for g in best.genes if g.section["name"] == sec_name],
            key=lambda g: (DAYS.index(g.day), SLOTS.index(g.slot))
        )
        lst = '<table class="lt"><thead><tr><th>Day</th><th>Time</th><th>Subject</th><th>Teacher</th><th>Room</th><th>Dept</th></tr></thead><tbody>'
        for g in sec_genes:
            bg, fg = subj_color.get(g.subject["id"], ("#DBEAFE","#1E40AF"))
            lst += (f'<tr><td><span class="dtag">{g.day[:3]}</span></td>'
                    f'<td class="mono">{g.slot}</td>'
                    f'<td><span class="sbadge" style="background:{bg};color:{fg};">{g.subject["id"]}</span> {g.subject["name"]}</td>'
                    f'<td>{g.teacher["name"]}</td>'
                    f'<td>{g.room["name"]}</td>'
                    f'<td><span class="deptag">{g.subject["dept"]}</span></td></tr>')
        lst += "</tbody></table>"

        panels += (f'<div class="panel" id="panel-{si}" style="display:{"block" if si==0 else "none"};">'
                   f'<div class="vtoggle">'
                   f'<button class="vb active" onclick="setView({si},\'grid\',this)">Grid</button>'
                   f'<button class="vb" onclick="setView({si},\'list\',this)">List</button>'
                   f'</div>'
                   f'<div id="grid-{si}">{grid}</div>'
                   f'<div id="list-{si}" style="display:none;">{lst}</div>'
                   f'</div>')

    conflict_html = ""
    genes = best.genes
    seen  = set()
    items = []
    for i in range(len(genes)):
        for j in range(i + 1, len(genes)):
            g1, g2 = genes[i], genes[j]
            if g1.day == g2.day and g1.slot == g2.slot:
                k = tuple(sorted([i, j]))
                if k in seen: continue
                if g1.teacher["id"] == g2.teacher["id"]:
                    items.append(f"Teacher clash: {g1.teacher['name']} on {g1.day} {g1.slot}")
                    seen.add(k)
                if g1.room["id"] == g2.room["id"]:
                    items.append(f"Room clash: {g1.room['name']} on {g1.day} {g1.slot}")
                    seen.add(k)
                if g1.section["id"] == g2.section["id"]:
                    items.append(f"Section clash: {g1.section['name']} on {g1.day} {g1.slot}")
                    seen.add(k)

    if items:
        conflict_html = "".join(f'<div class="cfl">{c}</div>' for c in items)
    else:
        conflict_html = '<div class="ok">✓ Zero conflicts — perfect timetable generated!</div>'

    legend = "".join(
        f'<span class="leg" style="background:{subj_color[sid][0]};color:{subj_color[sid][1]};">{sid}: {sname}</span>'
        for sid, sname in all_subj
    )

    # Charts 
    import base64
    chart_tags = ""
    chart_titles = [
        "Chart 1 — Fitness Evolution over Generations",
        "Chart 2 — Conflict Reduction & Adaptive Mutation",
        "Chart 3 — Room / Classroom Utilization",
        "Chart 4 — Teacher Workload Distribution",
    ]
    for i, cpath in enumerate(chart_paths):
        if os.path.isfile(cpath):
            with open(cpath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            chart_tags += (
                f'<div class="chart-card">'
                f'<div class="chart-title">{chart_titles[i]}</div>'
                f'<img src="data:image/png;base64,{b64}" alt="{chart_titles[i]}" '
                f'style="width:100%;border-radius:6px;">'
                f'</div>'
            )

    evo_rows = "".join(
        f"<tr><td>{h['gen']}</td><td>{h['best']}</td><td>{h['avg']}</td>"
        f"<td>{h['conflicts']}</td><td>{h['mut_rate']}</td></tr>"
        for h in history
    )

    # Assemble full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>JIIT Timetable — GA Output</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#F7F8FA;--sur:#FFF;--bdr:#E2E8F0;--tx:#0F172A;--mu:#64748B;--ac:#1D4ED8}}
body{{font-family:'IBM Plex Sans',sans-serif;background:var(--bg);color:var(--tx);font-size:14px;line-height:1.6}}
.hdr{{background:linear-gradient(135deg,#0F172A,#1E3A5F);color:#fff;padding:2.5rem}}
.hdr h1{{font-size:1.7rem;font-weight:600;letter-spacing:-.02em}}
.hdr-sub{{font-size:.8rem;color:#94A3B8;margin-top:6px}}
.badge{{display:inline-flex;align-items:center;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);color:#BFDBFE;font-size:11px;font-weight:500;padding:4px 12px;border-radius:20px;margin-top:10px}}
.stats{{display:flex;gap:2.5rem;flex-wrap:wrap;margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid rgba(255,255,255,.1)}}
.sl{{font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:.08em}}
.sv{{font-size:1.75rem;font-weight:600;color:#fff;margin-top:2px}}
.sv.g{{color:#4ADE80}}.sv.r{{color:#F87171}}
.main{{max-width:1200px;margin:0 auto;padding:1.5rem}}
.card{{background:var(--sur);border:1px solid var(--bdr);border-radius:10px;margin-bottom:1.25rem;overflow:hidden}}
.ch{{padding:.85rem 1.25rem;border-bottom:1px solid var(--bdr);display:flex;align-items:center;gap:8px;background:#FAFBFC}}
.ch h2{{font-size:.9rem;font-weight:600}}
.cb{{padding:1.25rem}}
.tab-bar{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:1rem}}
.tab-btn{{padding:5px 14px;font-size:12px;font-family:'IBM Plex Sans',sans-serif;font-weight:500;border:1px solid var(--bdr);border-radius:6px;background:#fff;color:var(--mu);cursor:pointer;transition:all .15s}}
.tab-btn.active{{background:#1E293B;color:#fff;border-color:#1E293B}}
.tab-btn:hover:not(.active){{background:#F1F5F9;color:var(--tx)}}
.vtoggle{{display:flex;gap:4px;margin-bottom:12px}}
.vb{{padding:4px 12px;font-size:11px;font-family:'IBM Plex Sans',sans-serif;border:1px solid var(--bdr);border-radius:5px;background:#fff;color:var(--mu);cursor:pointer}}
.vb.active{{background:#0F172A;color:#fff;border-color:#0F172A}}
.grid-wrap{{overflow-x:auto}}
.tt{{width:100%;border-collapse:collapse;min-width:820px;font-size:12px}}
.tt th{{background:#F8FAFC;color:#475569;font-weight:500;padding:9px 5px;text-align:center;border:1px solid var(--bdr);font-size:11px;white-space:nowrap}}
.tt td{{border:1px solid var(--bdr);padding:3px;vertical-align:top;min-width:100px}}
.dc{{width:80px;min-width:80px}}
.dl{{font-weight:600;background:#F8FAFC;font-size:11px;text-align:center;padding:10px 4px}}
.cc{{border-radius:6px;padding:5px 6px;min-height:82px;display:flex;flex-direction:column;gap:2px}}
.sc{{font-size:10px;font-weight:700;font-family:'IBM Plex Mono',monospace}}
.sn{{font-size:10px;font-weight:500;color:#374151;line-height:1.3;margin-top:2px}}
.sm{{font-size:9px;color:#6B7280;margin-top:1px}}
.rt{{background:rgba(0,0,0,.05);border-radius:3px;padding:0 4px;display:inline-block;margin-top:2px}}
.ec{{text-align:center;color:#E2E8F0;font-size:20px;padding:12px 0}}
.lt{{width:100%;border-collapse:collapse;font-size:12px}}
.lt th{{background:#F8FAFC;color:#475569;font-weight:500;padding:8px 12px;text-align:left;border-bottom:2px solid var(--bdr);font-size:11px}}
.lt td{{padding:7px 12px;border-bottom:1px solid #F8FAFC}}
.lt tr:hover td{{background:#F8FAFC}}
.dtag{{display:inline-block;background:#EEF2FF;color:#3730A3;font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px}}
.deptag{{display:inline-block;background:#F0FDF4;color:#166534;font-size:10px;font-weight:500;padding:2px 8px;border-radius:20px}}
.sbadge{{display:inline-block;font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px;margin-right:4px;font-family:'IBM Plex Mono',monospace}}
.mono{{font-family:'IBM Plex Mono',monospace;font-size:11px}}
.leg-wrap{{display:flex;flex-wrap:wrap;gap:6px}}
.leg{{display:inline-block;font-size:10px;font-weight:600;padding:3px 10px;border-radius:5px;font-family:'IBM Plex Mono',monospace}}
.ok{{background:#F0FDF4;border:1px solid #BBF7D0;color:#15803D;border-radius:8px;padding:12px 16px;font-weight:500}}
.cfl{{background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;border-radius:6px;padding:7px 14px;margin-bottom:6px;font-size:12px}}
.charts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1.25rem}}
.chart-card{{background:var(--sur);border:1px solid var(--bdr);border-radius:10px;padding:1rem}}
.chart-title{{font-size:12px;font-weight:500;color:var(--mu);margin-bottom:.75rem}}
.met{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:1.25rem}}
.mc{{background:#F8FAFC;border:1px solid var(--bdr);border-radius:8px;padding:10px 14px}}
.mcl{{font-size:10px;color:var(--mu);text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px}}
.mcv{{font-size:1.5rem;font-weight:600}}
.etbl{{width:100%;border-collapse:collapse;font-size:11px;font-family:'IBM Plex Mono',monospace}}
.etbl th{{background:#F8FAFC;padding:6px 10px;text-align:left;font-size:10px;border-bottom:1px solid var(--bdr);font-family:'IBM Plex Sans',sans-serif;font-weight:500;color:#475569}}
.etbl td{{padding:4px 10px;border-bottom:1px solid #F8FAFC}}
.etbl tr:hover td{{background:#F8FAFC}}
.print-btn{{position:fixed;bottom:1.5rem;right:1.5rem;background:#0F172A;color:#fff;border:none;border-radius:8px;padding:10px 22px;font-family:'IBM Plex Sans',sans-serif;font-size:13px;font-weight:500;cursor:pointer;box-shadow:0 4px 20px rgba(0,0,0,.25);z-index:100}}
.print-btn:hover{{background:#1D4ED8}}
.footer{{text-align:center;color:var(--mu);font-size:11px;padding:2rem 0 4rem}}
.footerp{{text-align:center;color:var(--mu);font-size:11px;}}
@media(max-width:700px){{.charts-grid{{grid-template-columns:1fr}}}}
@media print{{.print-btn,.vtoggle,.tab-bar{{display:none}}.panel{{display:block!important}}.card{{break-inside:avoid}}}}
</style>
</head>
<body>
<div class="hdr">
  <div class="badge"> Genetic Algorithm — Soft Computing Project</div>
  <h1 style="margin-top:.75rem;">JIIT Timetable Schedule</h1>
  <div class="hdr-sub">Generated {generated_at} &nbsp;·&nbsp;</div>
  <div class="stats">
    <div><div class="sl">Best Fitness</div><div class="sv {"g" if final_conflicts==0 else "r"}">{best.fitness:.5f}</div></div>
    <div><div class="sl">Conflicts</div><div class="sv {"g" if final_conflicts==0 else "r"}">{final_conflicts}</div></div>
    <div><div class="sl">Total Classes</div><div class="sv">{total_classes}</div></div>
    <div><div class="sl">Sections</div><div class="sv">{len(sections_list)}</div></div>
    <div><div class="sl">Generations</div><div class="sv">{len(history)}</div></div>
  </div>
</div>

<div class="main">

<div class="card">
  <div class="ch"><span>&#x1F4C5;</span><h2>Section Timetables</h2></div>
  <div class="cb">
    <div class="tab-bar">{tab_btns}</div>
    {panels}
  </div>
</div>

<div class="card">
  <div class="ch"><span>&#x1F3A8;</span><h2>Subject Colour Legend</h2></div>
  <div class="cb"><div class="leg-wrap">{legend}</div></div>
</div>

<div class="card">
  <div class="ch"><span>&#x26A1;</span><h2>Conflict Analysis</h2></div>
  <div class="cb">{conflict_html}</div>
</div>

<div class="card">
  <div class="ch"><span>&#x1F4CA;</span><h2>GA Visualizations</h2></div>
  <div class="cb">
    <div class="charts-grid">{chart_tags}</div>
  </div>
</div>

<div class="card">
  <div class="ch"><span>&#x1F9EC;</span><h2>GA Evolution Log</h2></div>
  <div class="cb">
    <div class="met">
      <div class="mc"><div class="mcl">Best Fitness</div><div class="mcv" style="color:#1D4ED8;">{best.fitness:.5f}</div></div>
      <div class="mc"><div class="mcl">Conflicts</div><div class="mcv" style="color:{'#15803D' if final_conflicts==0 else '#B45309'};">{final_conflicts}</div></div>
      <div class="mc"><div class="mcl">Generations</div><div class="mcv">{len(history)}</div></div>
      <div class="mc"><div class="mcl">Status</div><div class="mcv" style="font-size:.95rem;padding-top:6px;color:{'#15803D' if final_conflicts==0 else '#B45309'};">{'Perfect ✓' if final_conflicts==0 else 'Near-optimal'}</div></div>
    </div>
    <div style="max-height:320px;overflow-y:auto;">
    <table class="etbl">
      <thead><tr><th>Gen</th><th>Best Fitness</th><th>Avg Fitness</th><th>Conflicts</th><th>Mut Rate</th></tr></thead>
      <tbody>{evo_rows}</tbody>
    </table>
    </div>
  </div>
</div>
<b><p class="footerp">TEAM MEMBERS</p></b>
<p class="footerp">RAHUL KUSHWAHA</p>
<p class="footerp">ABHAY GAUR</p>
<p class="footerp">RITIK DADWAL</p>
<p class="footerp">KARTIKAY GAUTAM</p>
<div class="footer">Genetic Algorithm Timetable Scheduler — Soft Computing &nbsp;·&nbsp; {generated_at}</div>
</div>

<button class="print-btn" onclick="window.print()">&#x1F5A8; Print / PDF</button>
<script>
function showTab(i){{document.querySelectorAll('.panel').forEach((p,j)=>p.style.display=j===i?'block':'none');document.querySelectorAll('.tab-btn').forEach((b,j)=>b.classList.toggle('active',j===i));}}
function setView(s,v,btn){{document.getElementById('grid-'+s).style.display=v==='grid'?'block':'none';document.getElementById('list-'+s).style.display=v==='list'?'block':'none';btn.closest('.vtoggle').querySelectorAll('.vb').forEach(b=>b.classList.remove('active'));btn.classList.add('active');}}
</script>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n   HTML timetable → '{output_file}'")
    return output_file


# SECTION 7 — CLI + MAIN

def parse_args():
    p = argparse.ArgumentParser(
        description="GA Timetable Scheduler — Soft Computing Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python timetable_ga.py                    
  python timetable_ga.py --subjects dataset/subjects.csv
  python timetable_ga.py --add-teacher
  python timetable_ga.py --pop-size 120 --generations 400
        """
    )
    p.add_argument("--subjects",    type=str, help="Path to subjects.csv")
    p.add_argument("--teachers",    type=str, help="Path to teachers.csv")
    p.add_argument("--rooms",       type=str, help="Path to rooms.csv")
    p.add_argument("--sections",    type=str, help="Path to sections.csv")
    p.add_argument("--add-teacher", action="store_true")
    p.add_argument("--add-room",    action="store_true")
    p.add_argument("--pop-size",    type=int,   default=80)
    p.add_argument("--generations", type=int,   default=300)
    p.add_argument("--mutation",    type=float, default=0.15)
    p.add_argument("--crossover",   type=float, default=0.85)
    p.add_argument("--elite",       type=int,   default=3)
    p.add_argument("--output",      type=str,   default="timetable_output.html")
    p.add_argument("--charts-dir",  type=str,   default="charts")
    p.add_argument("--seed",        type=int,   default=42)
    return p.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)

    print("JIIT TIMETABLE SCHEDULER VIA GA")

    #Load each CSV
    sp = find_csv(args.subjects, ["subjects.csv"], "subjects")
    tp = find_csv(args.teachers, ["teachers.csv"], "teachers")
    rp = find_csv(args.rooms,    ["rooms.csv"],    "rooms")
    ep = find_csv(args.sections, ["sections.csv"], "sections")

    subjects = load_subjects(sp) if sp else []
    teachers = load_teachers(tp) if tp else []
    rooms    = load_rooms(rp)    if rp else []
    sections = load_sections(ep) if ep else []

    if not all([subjects, teachers, rooms, sections]):
        print("\n  ✗ Could not find one or more CSV files.")
        print("  Place subjects.csv, teachers.csv, rooms.csv, sections.csv")
        print("  in the same folder as this script (or in a 'dataset/' subfolder).")
        sys.exit(1)

    if args.add_teacher:
        teachers = add_teacher_interactive(teachers, subjects)
        if tp: save_teachers(teachers, tp)

    if args.add_room:
        rooms = add_room_interactive(rooms)
        if rp: save_rooms(rooms, rp)

    print(f"\n  Dataset summary:")
    print(f"    Subjects : {len(subjects)}")
    print(f"    Teachers : {len(teachers)}")
    print(f"    Rooms    : {len(rooms)}")
    print(f"    Sections : {len(sections)}")

    #Run GA
    best, history = genetic_algorithm(
        sections       = sections,
        subjects       = subjects,
        teachers       = teachers,
        rooms          = rooms,
        pop_size       = args.pop_size,
        generations    = args.generations,
        mutation_rate  = args.mutation,
        crossover_rate = args.crossover,
        elite_count    = args.elite,
    )

    # Generate 4 visualizations
    print("\n  Generating visualizations...")
    chart_paths = make_visualizations(best, history, out_dir=args.charts_dir)

    #Generate HTML 
    generate_html(best, history, chart_paths, output_file=args.output)

    print(f"\n  All done!  →  Open '{args.output}' in your browser.\n")


if __name__ == "__main__":
    main()
