#!/usr/bin/env python3
"""
Docker Interactive Lesson System
Run: python run.py
"""
import importlib
from engine import Session, load_progress, save_progress, record_module, bold, cyan, green, yellow, red, dim, C

MODULES = [
    ("01_problem",       "The Problem Docker Solves"),
    ("02_history",       "History & Timeline"),
    ("03_mental_model",  "Containers vs VMs"),
    ("04_core_concepts", "Core Concepts"),
    ("05_compose",       "Docker Compose"),
    ("06_industry",      "Industry Use Cases"),
    ("07_homelab",       "Home Lab & Self-Hosting"),
    ("08_commands",      "Command Reference"),
]

WHALE = r"""
        .
       ":"
     ___:____     |"\/"|
   ,'        `.    \  /
   |  O        \___/  |
 ~^~^~^~^~^~^~^~^~^~^~^~
"""

def print_banner():
    print(cyan(WHALE))
    print(bold("  ╔══════════════════════════════════════════════╗"))
    print(bold("  ║   Docker Interactive Lesson System           ║"))
    print(bold("  ║   Learn Docker through hands-on challenges   ║"))
    print(bold("  ╚══════════════════════════════════════════════╝"))
    print()


def main_menu(session, progress):
    student_data = progress.get("students", {}).get(session.name, {})

    print()
    print(bold("  ── Modules ──"))
    for i, (mod_id, mod_name) in enumerate(MODULES, 1):
        status = ""
        if mod_id in student_data:
            entry = student_data[mod_id]
            if entry.get("passed"):
                status = green(" ✓ PASSED")
            else:
                status = red(f" ✗ {entry.get('score', 0)}/{entry.get('max', 0)}")
        print(f"    {i}. {mod_name}{status}")

    print()
    print(f"    {bold('A')} — Run all modules in order")
    print(f"    {bold('Q')} — Quit")
    print()

    choice = input(bold("  Choose (1-8, A, Q): ")).strip().lower()

    if choice == "q":
        return "quit"
    elif choice == "a":
        return "all"
    elif choice.isdigit() and 1 <= int(choice) <= 8:
        return MODULES[int(choice) - 1][0]
    else:
        print(red("  Invalid choice."))
        return main_menu(session, progress)


def run_single_module(mod_id, session, progress):
    mod = importlib.import_module(f"modules.{mod_id}")
    result = mod.run(session)
    record_module(session.name, mod_id, result)
    # Refresh progress in memory
    progress.update(load_progress())


def show_final_score(session, progress):
    student_data = progress.get("students", {}).get(session.name, {})
    if not student_data:
        return

    total_score = sum(m.get("score", 0) for m in student_data.values())
    total_max = sum(m.get("max", 0) for m in student_data.values())
    if total_max == 0:
        return

    pct = total_score / total_max * 100
    print()
    print(bold("  ╔══════════════════════════════════════════════╗"))
    print(bold(f"  ║  Final Score: {total_score}/{total_max} ({pct:.0f}%)".ljust(49) + "║"))
    if pct >= 80:
        print(green("  ║                                              ║"))
        print(green("  ║   🐳  DOCKER CERTIFIED  🐳                   ║"))
        print(green("  ║   Congratulations, " + session.name + "!".ljust(27) + "║"))
        print(green("  ║                                              ║"))
    print(bold("  ╚══════════════════════════════════════════════╝"))


def main():
    print_banner()
    name = input(bold("  Enter your name: ")).strip() or "Student"
    session = Session(name)
    progress = load_progress()

    print(cyan(f"\n  Welcome, {name}! Let's learn Docker.\n"))

    while True:
        choice = main_menu(session, progress)
        if choice == "quit":
            show_final_score(session, progress)
            print(cyan("\n  Thanks for learning Docker! See you next time.\n"))
            break
        elif choice == "all":
            for mod_id, mod_name in MODULES:
                run_single_module(mod_id, session, progress)
            show_final_score(session, progress)
        else:
            run_single_module(choice, session, progress)


if __name__ == "__main__":
    main()
