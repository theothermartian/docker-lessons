# Docker Interactive Lesson System

A self-contained Python CLI app that teaches Docker through interactive, scenario-based terminal challenges. Students work through 8 progressive modules covering Docker fundamentals, from "why containers exist" to daily command fluency. **44 challenges** across 6 challenge types, with scoring, hints, and persistent progress tracking.

**Zero external dependencies** — pure Python 3 stdlib.

```
python3 run.py
```

---

## Project Structure

```
docker-lessons/
  run.py                  # Entry point: banner, student name, main menu, module selector
  engine.py               # Quiz engine: challenge classes, scoring, hints, progress I/O
  progress.json           # Auto-created at runtime; persists per-student scores
  modules/
    __init__.py
    01_problem.py          # The Problem Docker Solves
    02_history.py          # History & Timeline
    03_mental_model.py     # Containers vs VMs
    04_core_concepts.py    # Images, Layers, Dockerfile, Volumes, Networks
    05_compose.py          # Docker Compose
    06_industry.py         # CI/CD, Microservices, ML/DS Use Cases
    07_homelab.py          # Self-Hosting & Home Lab
    08_commands.py         # Command Reference & Debugging
```

---

## How It Works

### User Flow

1. Student launches `python3 run.py`
2. ASCII whale banner and title are displayed
3. Student enters their name (persisted across sessions)
4. Main menu shows all 8 modules with completion status (passed/failed/not attempted)
5. Student picks a module (1-8), runs all in order (A), or quits (Q)
6. Each module prints a brief lesson recap, then runs its challenges sequentially
7. After each module: score summary, pass/fail, review of missed questions
8. On quit or after running all: cumulative score + certification banner if >= 80%

### Module Loading

Modules are loaded dynamically via `importlib.import_module(f"modules.{mod_id}")`. Each module file exports:

- `LESSON` (str) — 2-4 sentence professor-style recap of the topic
- `CHALLENGES` (list) — ordered list of `Challenge` subclass instances
- `run(session)` — calls `engine.run_module()` with the module's content

This pattern means adding a new module is just:
1. Create `modules/09_new_topic.py` following the same structure
2. Add `("09_new_topic", "Display Name")` to the `MODULES` list in `run.py`

---

## Engine Architecture (`engine.py`)

### Challenge Types

The engine defines 5 challenge subclasses, each with distinct interaction patterns:

| Class | Default Points | Input Style | Matching Logic |
|---|---|---|---|
| `MultipleChoice` | 1 | A/B/C/D letter | Exact index match; 3 attempts for valid input |
| `FillCommand` | 2 | Free-text command | Normalized: lowercase, collapsed whitespace, compared against accepted list |
| `ScenarioChallenge` | 3 | Free-text answer | Loose: any accepted keyword found as substring (case-insensitive) |
| `SpotTheBug` | 3 | Free-text explanation | Keyword match: any keyword from `accepted_keywords` in answer |
| `LiveExecution` | 2 | Press Enter to run | Runs command via `subprocess.run()`, checks for success substring in output |

**`MultipleChoice`** — Standard A/B/C/D. Accepts upper or lowercase. Invalid input re-prompts up to 3 times. Shows explanation on wrong answer.

**`FillCommand`** — Student types a Docker command (e.g., `docker run -d -p 80:80 nginx`). Normalization strips whitespace and lowercases before comparing against a list of accepted variants. The `accepted` list should include common flag-order permutations.

**`ScenarioChallenge`** — Prints a narrative setup (cyan) then asks a question (bold). Uses loose substring matching so students can answer naturally ("I'd use a volume" matches `["volume"]`).

**`SpotTheBug`** — Displays a code block inside a Unicode box (`┌─┐│└┘`). Student identifies the bug. Checks if any keyword from `accepted_keywords` appears anywhere in the answer.

**`LiveExecution`** — Checks if Docker is installed via `shutil.which("docker")`. If not found, skips gracefully with no penalty. If found, runs the command with a 30-second timeout and checks stdout+stderr for a success substring.

### Hint System

- **3 hints per module** (reset when a new module starts)
- Before each challenge, the student sees: `[H]int (-1pt, N left) or Enter to answer:`
- Using a hint costs 1 point but **never reduces a correct answer below 1 point** (`max(1, points - 1)`)
- Hints are only offered if `hint_text` is non-empty and hints remain

### Scoring

- Each challenge adds its `points` value to `session.module_max` regardless of outcome
- Correct answers add earned points (base minus hint penalty) to `session.module_score`
- **Module pass threshold: 70%**
- **Overall certification threshold: 80%** across all completed modules

### Module Runner (`run_module()`)

Orchestrates a complete module session:

1. Resets `session.module_score`, `session.module_max`, and `session.hints_remaining`
2. Prints a bold header banner with module name
3. Prints the lesson text in cyan
4. Runs each challenge in sequence, tracking missed ones
5. Prints final score: `Score: X/Y (Z%) — PASSED/FAILED`
6. Lists missed questions for review
7. Returns `{"score": int, "max": int, "passed": bool}`

### Progress Persistence

Progress is stored in `progress.json` (auto-created in the project root):

```json
{
  "students": {
    "Alice": {
      "01_problem": { "score": 8, "max": 10, "passed": true },
      "02_history": { "score": 6, "max": 9, "passed": false }
    }
  }
}
```

- `load_progress()` — reads the file; returns `{"students": {}}` if it doesn't exist
- `save_progress(data)` — writes JSON with 2-space indentation
- `record_module(student, module_id, result)` — load, update student's module entry, save
- Re-running a module **overwrites** the previous score for that module

---

## Module Curriculum

### Learning Progression

The 8 modules follow a deliberate pedagogical sequence:

**Phase 1 — Motivation (Modules 1-3):** *Why does Docker exist?*
- Module 1 establishes the core problem (environment inconsistency, "it works on my machine")
- Module 2 provides historical context (chroot -> cgroups -> Docker)
- Module 3 builds the mental model (containers vs VMs, apartment vs house analogy)

**Phase 2 — Core Hands-On (Modules 4-5):** *How does Docker work?*
- Module 4 teaches primitives: images, containers, layers, volumes, networks
- Module 5 builds on Module 4 with multi-service orchestration via Compose

**Phase 3 — Real-World Application (Modules 6-7):** *Where is Docker used?*
- Module 6 covers enterprise: CI/CD, microservices, ML reproducibility, serverless
- Module 7 covers personal: self-hosting, home lab, replacing SaaS subscriptions

**Phase 4 — Mastery (Module 8):** *Command fluency for daily work*
- References concepts from all previous modules
- Heavy focus on `FillCommand` and `ScenarioChallenge` for practical recall

### Challenge Distribution

| Module | MC | Scenario | FillCmd | SpotBug | LiveExec | Total |
|---|---|---|---|---|---|---|
| 1 — Problem | 3 | 1 | 1 | 0 | 0 | **5** |
| 2 — History | 4 | 1 | 0 | 0 | 0 | **5** |
| 3 — Mental Model | 3 | 2 | 0 | 0 | 0 | **5** |
| 4 — Core Concepts | 1 | 3 | 1 | 1 | 1 | **6** |
| 5 — Compose | 2 | 2 | 1 | 1 | 0 | **6** |
| 6 — Industry | 3 | 2 | 0 | 0 | 0 | **5** |
| 7 — Homelab | 3 | 1 | 0 | 1 | 0 | **5** |
| 8 — Commands | 1 | 3 | 2 | 0 | 0 | **7** (largest) |
| **Total** | **18** | **15** | **6** | **3** | **1** | **44** |

Early modules lean on MultipleChoice for conceptual grounding. Middle modules introduce SpotTheBug and LiveExecution. Later modules emphasize ScenarioChallenge and FillCommand for practical recall.

---

## Terminal UI

### Colors (ANSI escape codes, no dependencies)

| Color | Usage |
|---|---|
| **Cyan** | Lesson text, scenario setups, welcome/goodbye messages |
| **Green** | Correct answers, passed modules, certification banner |
| **Red** | Wrong answers, failed modules |
| **Yellow** | Hints, explanations, missed question reviews |
| **Bold** | Headers, prompts, questions |
| **Dim** | Challenge counters, optional hint prompts |

### Visual Elements

- ASCII whale banner on startup
- Box-drawing characters (`═ ─ ╔ ╗ ╚ ╝ ║`) for headers and score banners
- Unicode box (`┌ ─ ┐ │ └ ┘`) around SpotTheBug code blocks
- Checkmarks and crosses (`✓ ✗`) for pass/fail indicators

---

## Adding a New Module

1. Create `modules/09_your_topic.py`:

```python
from engine import MultipleChoice, FillCommand, ScenarioChallenge, SpotTheBug, LiveExecution, Session, run_module

LESSON = """
  Brief professor-style recap of the topic.
"""

CHALLENGES = [
    MultipleChoice(
        question="Your question here?",
        options=["A option", "B option", "C option", "D option"],
        correct=1,  # 0-indexed
        explanation="Why B is correct.",
        hint_text="Optional hint.",
    ),
    # Add more challenges...
]

def run(session: Session):
    return run_module("Module 9: Your Topic", LESSON, CHALLENGES, session)
```

2. Add to `MODULES` in `run.py`:
```python
("09_your_topic", "Your Topic Name"),
```

That's it. The menu, scoring, and progress tracking handle the rest automatically.

---

## Design Decisions

**Why pure stdlib?** The target audience is Docker beginners who may not have `pip` workflows set up. `python3 run.py` just works.

**Why loose matching for scenarios?** Students learning Docker shouldn't be penalized for natural language phrasing. "I'd use a volume" and "volume" both demonstrate understanding.

**Why 3 hints per module?** Enough to get unstuck without trivializing the challenge. The 1-point cost creates a meaningful tradeoff without harsh punishment.

**Why `importlib` for modules?** Decouples the engine from module content. Modules are self-contained — you can add, remove, or reorder them without touching engine code.

**Why `LiveExecution` is optional?** Not every student has Docker installed (some are in lecture-only settings). Graceful skip with `shutil.which("docker")` means no one gets penalized for their environment.

**Why overwrite scores on re-run?** Students should be able to improve. The latest attempt is the one that counts.
