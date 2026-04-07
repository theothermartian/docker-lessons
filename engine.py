"""
Docker Lesson Engine — quiz engine, scoring, hints, progress persistence.
Pure Python 3, no external dependencies.
"""
import json
import shutil
import subprocess
from pathlib import Path


# ─── ANSI Colors ───────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"

def green(s):  return f"{C.GREEN}{s}{C.RESET}"
def red(s):    return f"{C.RED}{s}{C.RESET}"
def cyan(s):   return f"{C.CYAN}{s}{C.RESET}"
def yellow(s): return f"{C.YELLOW}{s}{C.RESET}"
def bold(s):   return f"{C.BOLD}{s}{C.RESET}"
def dim(s):    return f"{C.DIM}{s}{C.RESET}"


# ─── Session State ─────────────────────────────────────────────────────────────

class Session:
    def __init__(self, student_name: str):
        self.name = student_name
        self.hints_remaining = 3
        self.module_score = 0
        self.module_max = 0


# ─── Challenge Base ────────────────────────────────────────────────────────────

class Challenge:
    points: int = 1
    hint_text: str = ""

    def run(self, session: Session) -> bool:
        raise NotImplementedError


# ─── Hint System ───────────────────────────────────────────────────────────────

def offer_hint(session: Session, hint_text: str) -> bool:
    """Offer a hint before the student answers. Returns True if hint was used."""
    if not hint_text:
        return False
    if session.hints_remaining <= 0:
        return False
    choice = input(dim(f"  [H]int (-1pt, {session.hints_remaining} left) or Enter to answer: ")).strip().lower()
    if choice == "h":
        print(yellow(f"  HINT: {hint_text}"))
        session.hints_remaining -= 1
        return True
    return False


# ─── Multiple Choice ───────────────────────────────────────────────────────────

class MultipleChoice(Challenge):
    def __init__(self, question, options, correct, explanation, hint_text="", points=1):
        self.question = question
        self.options = options
        self.correct = correct  # 0-indexed
        self.explanation = explanation
        self.hint_text = hint_text
        self.points = points

    def run(self, session: Session) -> bool:
        print()
        print(bold(f"  {self.question}"))
        letters = "ABCD"
        for i, opt in enumerate(self.options):
            marker = letters[i]
            print(f"    {marker}) {opt}")

        used_hint = offer_hint(session, self.hint_text)

        for attempt in range(3):
            ans = input(bold("  > ")).strip().upper()
            if ans in letters[:len(self.options)]:
                idx = letters.index(ans)
                if idx == self.correct:
                    pts = max(1, self.points - (1 if used_hint else 0))
                    print(green(f"  ✓ Correct! (+{pts} pts)"))
                    session.module_score += pts
                    session.module_max += self.points
                    return True
                else:
                    print(red("  ✗ Wrong."))
                    print(yellow(f"  {self.explanation}"))
                    session.module_max += self.points
                    return False
            else:
                print(dim(f"  Please enter {'/'.join(letters[:len(self.options)])}"))
        # exhausted attempts
        print(red("  ✗ No valid answer given."))
        print(yellow(f"  {self.explanation}"))
        session.module_max += self.points
        return False


# ─── Fill-in-the-Command ──────────────────────────────────────────────────────

class FillCommand(Challenge):
    def __init__(self, prompt, accepted, explanation, hint_text="", points=2):
        self.prompt = prompt
        self.accepted = accepted
        self.explanation = explanation
        self.hint_text = hint_text
        self.points = points

    def run(self, session: Session) -> bool:
        print()
        print(bold(f"  {self.prompt}"))
        used_hint = offer_hint(session, self.hint_text)

        ans = input(bold("  $ ")).strip()
        normalized = " ".join(ans.lower().split())
        for valid in self.accepted:
            if normalized == " ".join(valid.lower().split()):
                pts = max(1, self.points - (1 if used_hint else 0))
                print(green(f"  ✓ Command accepted! (+{pts} pts)"))
                session.module_score += pts
                session.module_max += self.points
                return True

        print(red("  ✗ Not quite."))
        print(yellow(f"  Expected: {self.accepted[0]}"))
        print(yellow(f"  {self.explanation}"))
        session.module_max += self.points
        return False


# ─── Scenario Challenge ───────────────────────────────────────────────────────

class ScenarioChallenge(Challenge):
    def __init__(self, setup, question, accepted, explanation, hint_text="", points=3):
        self.setup = setup
        self.question = question
        self.accepted = accepted
        self.explanation = explanation
        self.hint_text = hint_text
        self.points = points

    def run(self, session: Session) -> bool:
        print()
        print(cyan(f"  SCENARIO: {self.setup}"))
        print(bold(f"  {self.question}"))
        used_hint = offer_hint(session, self.hint_text)

        ans = input(bold("  > ")).strip().lower()
        for valid in self.accepted:
            if valid.lower() in ans or ans == valid.lower():
                pts = max(1, self.points - (1 if used_hint else 0))
                print(green(f"  ✓ Correct! (+{pts} pts)"))
                session.module_score += pts
                session.module_max += self.points
                return True

        print(red("  ✗ Not quite."))
        print(yellow(f"  {self.explanation}"))
        session.module_max += self.points
        return False


# ─── Spot the Bug ─────────────────────────────────────────────────────────────

class SpotTheBug(Challenge):
    def __init__(self, code_block, question, accepted_keywords, explanation, hint_text="", points=3):
        self.code_block = code_block
        self.question = question
        self.accepted_keywords = accepted_keywords
        self.explanation = explanation
        self.hint_text = hint_text
        self.points = points

    def run(self, session: Session) -> bool:
        print()
        lines = self.code_block.strip().split("\n")
        width = max(len(l) for l in lines) + 4
        print(f"  ┌{'─' * width}┐")
        for line in lines:
            print(f"  │  {line.ljust(width - 2)}│")
        print(f"  └{'─' * width}┘")
        print(bold(f"  {self.question}"))
        used_hint = offer_hint(session, self.hint_text)

        ans = input(bold("  > ")).strip().lower()
        for kw in self.accepted_keywords:
            if kw.lower() in ans:
                pts = max(1, self.points - (1 if used_hint else 0))
                print(green(f"  ✓ Correct! (+{pts} pts)"))
                session.module_score += pts
                session.module_max += self.points
                return True

        print(red("  ✗ Not quite."))
        print(yellow(f"  {self.explanation}"))
        session.module_max += self.points
        return False


# ─── Live Execution ───────────────────────────────────────────────────────────

class LiveExecution(Challenge):
    def __init__(self, prompt, command_to_run, success_substring, explanation, hint_text="", points=2):
        self.prompt = prompt
        self.command_to_run = command_to_run
        self.success_substring = success_substring
        self.explanation = explanation
        self.hint_text = hint_text
        self.points = points

    def run(self, session: Session) -> bool:
        print()
        if not shutil.which("docker"):
            print(yellow("  [SKIPPED] Docker not installed — no penalty."))
            return True

        print(bold(f"  {self.prompt}"))
        print(cyan(f"  Command: {self.command_to_run}"))
        input(dim("  Press Enter when ready..."))

        try:
            result = subprocess.run(
                self.command_to_run.split(),
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout + result.stderr
            if self.success_substring.lower() in output.lower():
                print(green(f"  ✓ Verified! (+{self.points} pts)"))
                session.module_score += self.points
                session.module_max += self.points
                return True
            else:
                print(red("  ✗ Expected output not found."))
                print(yellow(f"  {self.explanation}"))
                session.module_max += self.points
                return False
        except subprocess.TimeoutExpired:
            print(red("  ✗ Command timed out (30s)."))
            session.module_max += self.points
            return False
        except Exception as e:
            print(red(f"  ✗ Error: {e}"))
            session.module_max += self.points
            return False


# ─── Module Runner ─────────────────────────────────────────────────────────────

def run_module(name: str, lesson_text: str, challenges: list, session: Session) -> dict:
    """Run a full module: lesson recap, challenges, score summary."""
    # Reset module score
    session.module_score = 0
    session.module_max = 0
    session.hints_remaining = 3

    # Header
    print()
    print(f"  {'═' * 60}")
    print(bold(f"  {name}"))
    print(f"  {'═' * 60}")
    print(cyan(lesson_text))
    print(f"  {'─' * 60}")

    missed = []
    for i, ch in enumerate(challenges, 1):
        print(dim(f"\n  ── Challenge {i}/{len(challenges)} ──"))
        result = ch.run(session)
        if not result:
            missed.append((i, ch))

    # Score summary
    total = session.module_score
    maximum = session.module_max
    pct = (total / maximum * 100) if maximum > 0 else 0
    passed = pct >= 70

    print()
    print(f"  {'═' * 60}")
    if passed:
        print(green(f"  Score: {total}/{maximum} ({pct:.0f}%) — PASSED ✓"))
    else:
        print(red(f"  Score: {total}/{maximum} ({pct:.0f}%) — FAILED ✗"))
        print(yellow("  You need 70% to pass. Review the material and try again!"))

    if missed:
        print()
        print(yellow("  Questions to review:"))
        for num, ch in missed:
            label = getattr(ch, "question", getattr(ch, "prompt", f"Challenge {num}"))
            print(yellow(f"    • #{num}: {label}"))

    print(f"  {'═' * 60}")

    return {"score": total, "max": maximum, "passed": passed}


# ─── Progress Persistence ─────────────────────────────────────────────────────

PROGRESS_FILE = Path(__file__).parent / "progress.json"

def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"students": {}}

def save_progress(data: dict):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def record_module(student: str, module_id: str, result: dict):
    data = load_progress()
    if student not in data["students"]:
        data["students"][student] = {}
    data["students"][student][module_id] = result
    save_progress(data)
